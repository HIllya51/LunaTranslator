
#include "../loopbackaudio/LoopbackCapture.h"
#include <fvad.h>
#include "lockedqueue.hpp"
constexpr int sample_rate = 16000;
constexpr int frame_size = sample_rate / 1000 * 20;
struct __datas
{
    int skip10 = 10;
    std::unique_ptr<SupperRecord> capture;
    Fvad *vad = nullptr;
    bool start = false;
    lockedqueue<std::string> dataqueue;
    std::thread __parstt;

    bool is_speaking = false;
    int silence_counter;
    int speech_counter;
    std::vector<int16_t> input_buffer;            // 处理帧对齐的缓冲
    std::vector<int16_t> current_working_segment; // 当前正在录制的片段
    std::vector<int16_t> last_speech_segment;     // 最终保存的最后一段
    std::mutex last_speech_segment_lock;
    std::optional<std::string> get_wav()
    {
        int bitsPerSample = 16;
        int channels = 1;
        std::lock_guard __(last_speech_segment_lock);
        if (last_speech_segment.empty())
            return {};
        std::string wavData;
        uint32_t dataSize = last_speech_segment.size() * sizeof(int16_t);
        uint32_t totalFileSize = 36 + dataSize;
        uint32_t byteRate = sample_rate * channels * bitsPerSample / 8;
        uint16_t blockAlign = channels * bitsPerSample / 8;

        // 预分配内存，提高性能
        wavData.reserve(44 + dataSize);

        // --- RIFF Header ---
        wavData.append("RIFF", 4);                                         // ChunkID
        wavData.append(reinterpret_cast<const char *>(&totalFileSize), 4); // ChunkSize
        wavData.append("WAVE", 4);                                         // Format

        // --- fmt Sub-chunk ---
        wavData.append("fmt ", 4);   // Subchunk1ID
        uint32_t subchunk1Size = 16; // PCM 格式固定为 16
        wavData.append(reinterpret_cast<const char *>(&subchunk1Size), 4);
        uint16_t audioFormat = 1; // 1 代表 PCM
        wavData.append(reinterpret_cast<const char *>(&audioFormat), 2);
        uint16_t numChannels = (uint16_t)channels;
        wavData.append(reinterpret_cast<const char *>(&numChannels), 2);
        wavData.append(reinterpret_cast<const char *>(&sample_rate), 4);
        wavData.append(reinterpret_cast<const char *>(&byteRate), 4);
        wavData.append(reinterpret_cast<const char *>(&blockAlign), 2);
        uint16_t bits = (uint16_t)bitsPerSample;
        wavData.append(reinterpret_cast<const char *>(&bits), 2);

        // --- data Sub-chunk ---
        wavData.append("data", 4);                                    // Subchunk2ID
        wavData.append(reinterpret_cast<const char *>(&dataSize), 4); // Subchunk2Size

        // 写入原始 PCM 数据
        wavData.append(reinterpret_cast<const char *>(last_speech_segment.data()), dataSize);

        return wavData;
    }
    void handle_state(int v_res, const std::vector<int16_t> &frame)
    {
        const int MIN_SPEECH_FRAMES = 5;   // 连续5帧(100ms)有声音才算开始
        const int MAX_SILENCE_FRAMES = 25; // 连续25帧(500ms)无声才算结束
        if (v_res == 1)
        { // 检测到声音
            speech_counter++;
            silence_counter = 0;

            if (!is_speaking && speech_counter >= MIN_SPEECH_FRAMES)
            {
                // 【关键：新的一段话开始了】
                is_speaking = true;
                current_working_segment.clear(); // 丢弃旧的，开始存新的
            }

            if (is_speaking)
            {
                current_working_segment.insert(current_working_segment.end(), frame.begin(), frame.begin() + frame_size);
            }
        }
        else
        { // 检测到静音
            silence_counter++;
            speech_counter = 0;

            if (is_speaking)
            {
                current_working_segment.insert(current_working_segment.end(), frame.begin(), frame.begin() + frame_size);

                if (silence_counter >= MAX_SILENCE_FRAMES)
                {
                    // 完了
                    is_speaking = false;
                    std::lock_guard __(last_speech_segment_lock);
                    last_speech_segment = current_working_segment; // 保存这一段
                }
            }
        }
    }
    void process_audio(const std::string &raw_data)
    {
        const int16_t *samples = reinterpret_cast<const int16_t *>(raw_data.data());
        size_t count = raw_data.size() / sizeof(int16_t);
        // 2. 存入残留缓冲区
        input_buffer.insert(input_buffer.end(), samples, samples + count);

        // 3. 按帧处理 (每帧 20ms)
        while (input_buffer.size() >= frame_size)
        {
            int res = fvad_process(vad, input_buffer.data(), frame_size);
            if (skip10 > 0)
                res = 0;
            skip10 -= 1;
            handle_state(res, input_buffer);
            input_buffer.erase(input_buffer.begin(), input_buffer.begin() + frame_size);
        }
    }
    void parsethread()
    {
        while (true)
        {
            auto &&data = dataqueue.pop();
            if (data.empty())
                return;
            process_audio(data);
        }
    }
    ~__datas()
    {
        if (start)
            capture->StopCapture();
        dataqueue.push(std::string{});
        if (start)
        {
            __parstt.join();
        }
        if (vad)
            fvad_free(vad);
    }

    __datas()
    {
        capture = std::make_unique<SupperRecord>(sample_rate, 16, 1);
        if (!capture)
            return;
        capture->OnDataCallback = [&](std::string &&data_)
        { dataqueue.push(std::move(data_)); };
        auto hr = capture->StartCaptureAsync(GetCurrentProcessId(), false);
        if (FAILED(hr))
            return;
        start = true;
        vad = fvad_new();
        fvad_set_mode(vad, 0);
        fvad_set_sample_rate(vad, sample_rate);
        __parstt = std::thread([&]()
                               { parsethread(); });
        __parstt.detach();
    }
};

DECLARE_API void record_with_vad_get_last_voice(__datas *data, void (*cb)(const char *, size_t))
{
    if (!data)
        return;
    auto &&_ = data->get_wav();
    if (!_)
        return;
    cb(_.value().c_str(), _.value().size());
}

DECLARE_API __datas *record_with_vad_create()
{
    auto datas = new __datas;
    if (!datas->start)
    {
        delete datas;
        return nullptr;
    }
    return datas;
}
DECLARE_API void record_with_vad_delete(__datas *data)
{
    if (!data)
        return;
    delete data;
}