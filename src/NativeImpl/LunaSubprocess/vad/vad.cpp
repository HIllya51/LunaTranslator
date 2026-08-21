#include "../../NativeUtils/loopbackaudio/LoopbackCapture.h"
#include "../../wav.hpp"
#include "../pipehost.hpp"
#include <sherpa-onnx/c-api/cxx-api.h>
#include "lockedqueue.hpp"
#include <delayimp.h>

constexpr int SAMPLE_RATE = 16000; // VAD 推理采样率（喂给检测器的单声道）
constexpr int FRAME_SIZE = SAMPLE_RATE / 1000 * 20;
constexpr int CAPTURE_RATE = 44100; // 采集与输出采样率（立体声）
constexpr int CAPTURE_CHANNELS = 2; // 采集与输出声道数

// ============================================================
// 重采样器：立体声 44100 -> 单声道 16000
// 用面积平均（box）做下采样，自带抗混叠（远优于线性插值下采样）。
// 状态（acc_/filled_）跨帧保持，保证各片段拼接处无断点。
// ============================================================
class Resampler
{
public:
    Resampler(int in_rate, int out_rate)
        : ratio_(static_cast<double>(in_rate) / static_cast<double>(out_rate)) {}

    // 立体声 int16 -> 单声道 float[-1,1]（按 out_rate 下采样），追加到 out。
    void Process(const int16_t *stereo, size_t n_frames, std::vector<float> &out)
    {
        for (size_t f = 0; f < n_frames; ++f)
        {
            const double L = stereo[f * 2 + 0];
            const double R = stereo[f * 2 + 1];
            const double x = (L + R) * 0.5; // 下混为单声道（int16 量纲）
            Push(x, out);
        }
    }

private:
    void Push(double x, std::vector<float> &out)
    {
        // 按"输入样本覆盖当前输出窗口的面积"累加；窗口填满则输出均值。
        double remaining = 1.0;
        while (remaining > 1e-9)
        {
            const double space = ratio_ - filled_;
            const double w = (space < remaining) ? space : remaining;
            acc_ += x * w;
            filled_ += w;
            remaining -= w;
            if (filled_ >= ratio_ - 1e-9)
            {
                out.push_back(static_cast<float>(acc_ / ratio_ / 32768.0));
                acc_ = 0.0;
                filled_ = 0.0;
            }
        }
    }

    double ratio_ = 1.0;  // 每个输出样本对应多少个输入样本
    double acc_ = 0.0;    // 当前输出窗口的加权和
    double filled_ = 0.0; // 当前输出窗口已填充的输入时长
};

// ============================================================
// VAD 封装
// 自己维护原始立体声音频（44100/16/2，原样保留，输出 WAV 直接用它），
// 仅把下采样后的 16k 单声道喂给检测器做语音分段；再用检测器给出的
// seg.start / seg.samples.size()（16k 单声道单位）按时间比映射回
// 立体声帧并切片，避免库内部任何处理/精度转换影响输出音质。
// ============================================================
class VadWrapper
{
public:
    explicit VadWrapper(int sample_rate, const std::string &model_path, float threshold = 0.5f, float min_silence_duration = 0.5f, float min_speech_duration = 0.25f)
    {
        sherpa_onnx::cxx::VadModelConfig config;
        config.silero_vad.model = model_path;
        config.silero_vad.threshold = threshold;
        config.silero_vad.min_silence_duration = min_silence_duration;
        config.silero_vad.min_speech_duration = min_speech_duration;
        config.silero_vad.max_speech_duration = 60.0f;
        config.sample_rate = sample_rate;

        detector_ = std::make_unique<sherpa_onnx::cxx::VoiceActivityDetector>(sherpa_onnx::cxx::VoiceActivityDetector::Create(config, 60.0f));

        resampler_ = std::make_unique<Resampler>(CAPTURE_RATE, sample_rate);
        ratio_ = static_cast<double>(CAPTURE_RATE) / static_cast<double>(sample_rate);

        // 检测器内部环形缓冲为 30s（按 16k 计），其 start 回溯不超过该容量；
        // 映射回采集帧后约 30s 的 44100 立体声。保留 60s 采集帧即可安全覆盖。
        max_raw_frames_ = static_cast<size_t>(CAPTURE_RATE) * 120;
    }

    // 喂入采集到的立体声 int16（44100/16/2），返回本批次中新完成的所有语音段
    // （从自己维护的原始立体声音频切片，44100/16/2）。
    std::vector<std::vector<int16_t>> Detect(const int16_t *stereo, size_t n_samples)
    {
        std::vector<std::vector<int16_t>> segments;
        if (!detector_ || n_samples == 0)
            return segments;

        const size_t n_frames = n_samples / CAPTURE_CHANNELS;

        // 1) 原样保留原始立体声音频（输出 WAV 直接用它）
        raw_buffer_.insert(raw_buffer_.end(), stereo, stereo + n_samples);

        // 2) 下采样为 16k 单声道喂给检测器（仅用于 VAD 推理，状态跨帧保持）
        std::vector<float> conv;
        conv.reserve(n_frames * SAMPLE_RATE / CAPTURE_RATE + 16);
        resampler_->Process(stereo, n_frames, conv);
        if (!conv.empty())
            detector_->AcceptWaveform(conv.data(), static_cast<int32_t>(conv.size()));

        // 3) 用 seg.start / seg.samples.size()（16k 单声道单位）映射回采集帧并切片。
        //    box 重采样的输出样本 k 对应采集帧窗口 [k*ratio, (k+1)*ratio)。
        while (!detector_->IsEmpty())
        {
            auto seg = detector_->Front();
            detector_->Pop();

            const int64_t vstart = static_cast<int64_t>(seg.start);
            const int64_t vlen = static_cast<int64_t>(seg.samples.size());
            if (vlen <= 0)
                continue;

            const int64_t f0 = static_cast<int64_t>(std::llround(vstart * ratio_));
            const int64_t f1 = static_cast<int64_t>(std::llround((vstart + vlen) * ratio_));

            // 映射到 raw_buffer_ 的 int16 下标（每帧 CAPTURE_CHANNELS 个样本），并夹紧到合法范围
            int64_t i0 = (f0 - raw_base_frames_) * CAPTURE_CHANNELS;
            int64_t i1 = (f1 - raw_base_frames_) * CAPTURE_CHANNELS;
            if (i0 < 0)
                i0 = 0;
            if (i1 > static_cast<int64_t>(raw_buffer_.size()))
                i1 = static_cast<int64_t>(raw_buffer_.size());
            if (i1 > i0)
            {
                segments.emplace_back(raw_buffer_.begin() + static_cast<std::vector<int16_t>::difference_type>(i0),
                                      raw_buffer_.begin() + static_cast<std::vector<int16_t>::difference_type>(i1));
            }
        }

        // 4) 限制原始缓冲的内存占用
        TrimFront();
        return segments;
    }

private:
    void TrimFront()
    {
        const size_t cur_frames = raw_buffer_.size() / CAPTURE_CHANNELS;
        if (cur_frames <= max_raw_frames_)
            return;
        const size_t ntrim_frames = cur_frames - max_raw_frames_;
        const size_t ntrim = ntrim_frames * CAPTURE_CHANNELS;
        raw_buffer_.erase(raw_buffer_.begin(),
                          raw_buffer_.begin() + static_cast<std::vector<int16_t>::difference_type>(ntrim));
        raw_base_frames_ += static_cast<int64_t>(ntrim_frames);
    }

    std::unique_ptr<sherpa_onnx::cxx::VoiceActivityDetector> detector_;
    std::unique_ptr<Resampler> resampler_;
    std::vector<int16_t> raw_buffer_; // 原始立体声 44100 int16（交错）；绝对帧索引 = raw_base_frames_ + offset/2
    int64_t raw_base_frames_ = 0;     // raw_buffer_[0] 对应的绝对采集帧索引
    double ratio_ = 1.0;              // 采集帧 / VAD 样本 = CAPTURE_RATE / SAMPLE_RATE
    size_t max_raw_frames_ = 0;
};

// ============================================================
// WAV 构建（44100 / 16bit / 立体声，与采集格式一致）
// ============================================================
static std::string BuildWav(const std::vector<int16_t> &pcm)
{
    if (pcm.empty())
        return {};

    const uint16_t channels = static_cast<uint16_t>(CAPTURE_CHANNELS);
    const uint16_t bits = 16;
    const uint16_t block_align = static_cast<uint16_t>(channels * bits / 8);
    const uint32_t byte_rate = static_cast<uint32_t>(CAPTURE_RATE) * block_align;
    const uint32_t sample_rate = static_cast<uint32_t>(CAPTURE_RATE);
    const uint32_t data_size = static_cast<uint32_t>(pcm.size() * sizeof(int16_t));

    return wav::BuildHeader(static_cast<uint16_t>(1), channels, sample_rate, byte_rate,
                            block_align, bits, data_size) +
           std::string(reinterpret_cast<const char *>(pcm.data()), data_size);
}

// ============================================================
// 核心处理器
// ============================================================
struct AudioProcessor
{
    std::unique_ptr<SupperRecord> capture;
    std::unique_ptr<VadWrapper> vad;
    lockedqueue<std::string> queue;
    std::thread worker;
    std::atomic<bool> running{false};

    std::vector<int16_t> last_segment;
    std::mutex segment_mutex;

    // ---- 构造 ----
    // targetPid 为采集时"排除"的进程（PROCESS_LOOPBACK_MODE_EXCLUDE_TARGET_PROCESS_TREE），
    // 即录制系统里除该进程树以外的音频（用于录制游戏语音、排除宿主进程的 TTS）。
    explicit AudioProcessor(DWORD targetPid, const std::string &model_path, float threshold, float min_silence_duration, float min_speech_duration)
    {
        capture = std::make_unique<SupperRecord>(CAPTURE_RATE, 16, CAPTURE_CHANNELS);
        if (!capture)
            return;

        capture->OnDataCallback = [this](std::string &&data)
        {
            queue.push(std::move(data));
        };

        if (FAILED(capture->StartCaptureAsync(targetPid, false)))
        {
            return;
        }

        try
        {
            vad = std::make_unique<VadWrapper>(SAMPLE_RATE, model_path, threshold, min_silence_duration, min_speech_duration);
        }
        catch (...)
        {
            return;
        }
        running = true;
        worker = std::thread(&AudioProcessor::WorkerLoop, this);
    }

    // ---- 析构 ----
    ~AudioProcessor()
    {
        running = false;
        queue.push(std::string{}); // 唤醒线程
        if (worker.joinable())
            worker.join();
        if (capture)
            capture->StopCapture();
    }

    // ---- 禁止拷贝 ----
    AudioProcessor(const AudioProcessor &) = delete;
    AudioProcessor &operator=(const AudioProcessor &) = delete;

    // ---- 获取最后语音 WAV ----
    std::optional<std::string> GetLastVoiceWav()
    {
        std::lock_guard<std::mutex> lock(segment_mutex);
        if (last_segment.empty())
            return std::nullopt;
        return BuildWav(last_segment);
    }

    bool IsValid() const { return running && vad != nullptr; }

private:
    void WorkerLoop()
    {
        while (running)
        {
            auto data = queue.pop();
            if (data.empty())
                continue;

            const int16_t *samples = reinterpret_cast<const int16_t *>(data.data());
            size_t count = data.size() / sizeof(int16_t);

            auto segments = vad->Detect(samples, count);
            if (!segments.empty())
            {
                std::lock_guard<std::mutex> lock(segment_mutex);
                last_segment = std::move(segments.back());
            }
        }
    }
};

constexpr size_t VAD_MEM_SIZE = 16 * 1024 * 1024;

int vadwmain(int argc, wchar_t *wargv[])
{
    SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_DEFAULT_DIRS);
    // wargv[5]: sherpa-onnx 运行时 DLL 目录（宿主 os.walk 查找，可能为空）
    AddDllDirectory(wargv[5]);

    lunasp::PipeHost host(wargv[1], wargv[2], wargv[3], VAD_MEM_SIZE);
    if (!host.ok())
        return 1;

    const DWORD targetPid = static_cast<DWORD>(_wtol(wargv[4]));
    // wargv[6]: silero_vad.onnx 模型路径（宿主 os.walk 查找，可能为空）
    const std::string model_path = std::filesystem::path(wargv[6]).string();

    std::unique_ptr<AudioProcessor> proc;
    try
    {
        proc = std::make_unique<AudioProcessor>(targetPid, model_path, std::stof(wargv[7]), std::stof(wargv[8]), std::stof(wargv[9]));
    }
    catch (...)
    {
        proc = nullptr;
    }
    char trigger = 0;
    while (host.read(&trigger, 1))
    {
        int size = 0;
        if (proc && proc->IsValid())
        {
            auto wav = proc->GetLastVoiceWav();
            if (wav.has_value() && wav->size() <= VAD_MEM_SIZE)
            {
                memcpy(host.mem(), wav->data(), wav->size());
                size = static_cast<int>(wav->size());
            }
        }
        host.write(&size, 4);
    }

    proc.reset();
    return 0;
}