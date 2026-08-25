
#include "aitalked.h"

using std::function;
using std::pair;
using std::string;
using std::vector;
using namespace ebyroid;

namespace ebyroid
{

  // forward-declaration to avoid including aitalked.h
  class ApiAdapter;

  struct ConvertParams
  {
    bool needs_reload;
    char *base_dir;
    char *voice;
    float volume;
  };

  template <typename T>
  class Response
  {
  public:
    Response(ApiAdapter *adapter) : api_adapter_(adapter)
    {
      event.Create(NULL, FALSE, FALSE, NULL);
    }
    void Write(T *bytes, size_t size)
    {
      buffer_.insert(std::end(buffer_), bytes, bytes + size);
    }
    std::vector<T> End()
    {
      return std::move(buffer_);
    }
    ApiAdapter *api_adapter() { return api_adapter_; };
    CEvent event;

  private:
    ApiAdapter *api_adapter_;
    std::vector<T> buffer_;
  };

} // namespace ebyroid

namespace
{

  ApiAdapter *NewAdapter(const Settings &settings)
  {
    std::unique_ptr<ApiAdapter> adapter{ApiAdapter::Create(settings.dllpath.c_str())};
    TConfig config;
    config.hz_voice_db = settings.frequency;
    config.dir_voice_dbs = settings.voice_base_dir.c_str();
    config.msec_timeout = 1000;
    config.path_license = settings.license_path.c_str();
    config.code_auth_seed = settings.seed.c_str();
    config.len_auth_seed = kLenSeedValue;
    ResultCode result = adapter->Init(&config);
    if (result != ERR_SUCCESS)
    {
      config.code_auth_seed = "PROJECT-VOICeVIO-SFE";
      result = adapter->Init(&config);
    }
    if (result != ERR_SUCCESS)
    {
      string message = "API initialization failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
    return adapter.release();
  }

  int __stdcall HiraganaCallback(EventReasonCode reason_code, int32_t job_id, IntPtr user_data)
  {
    auto response = (Response<char> *)user_data;
    ApiAdapter *api_adapter = response->api_adapter();

    if (reason_code != TEXTBUF_FULL && reason_code != TEXTBUF_FLUSH && reason_code != TEXTBUF_CLOSE)
    {
      // unexpected: may possibly lead to memory leak
      return 0;
    }

    static constexpr int kBufferSize = 0x1000;
    char buffer[kBufferSize];
    while (true)
    {
      uint32_t size, pos;
      ResultCode result = api_adapter->GetKana(job_id, buffer, kBufferSize, &size, &pos);

      if (result != ERR_SUCCESS)
      {
        break;
      }
      response->Write(buffer, size);
      if (kBufferSize > size)
      {
        break;
      }
    }

    if (reason_code == TEXTBUF_CLOSE)
    {
      response->event.Set();
    }
    return 0;
  }

  int __stdcall SpeechCallback(EventReasonCode reason_code,
                               int32_t job_id,
                               uint64_t tick,
                               IntPtr user_data)
  {
    auto response = (Response<int16_t> *)user_data;
    ApiAdapter *api_adapter = response->api_adapter();

    if (reason_code != RAWBUF_FULL && reason_code != RAWBUF_FLUSH && reason_code != RAWBUF_CLOSE)
    {
      // unexpected: may possibly lead to memory leak
      return 0;
    }

    static constexpr int kBufferSize = 0xFFFF;
    int16_t buffer[kBufferSize];
    while (true)
    {
      uint32_t size, pos;
      ResultCode result = api_adapter->GetData(job_id, buffer, kBufferSize, &size);
      if (result != ERR_SUCCESS)
      {
        break;
      }
      response->Write(buffer, size);
      if (kBufferSize > size)
      {
        break;
      }
    }

    if (reason_code == RAWBUF_CLOSE)
    {
      response->event.Set();
    }
    return 0;
  }
} // namespace

aitalked::aitalked(const Settings &settings)
{
  api_adapter_ = NewAdapter(settings);
}
void aitalked::setvoice(Settings &settings)
{
  ResultCode result;

  if (settings.language_dir != lastlang_)
  {
    lastlang_ = settings.language_dir;
    api_adapter_->LangClear();
    result = api_adapter_->LangLoad(settings.language_dir.c_str());
    if (result != ERR_SUCCESS && result != ERR_ALREADY_LOADED)
    {
      string message = "API Load Lang failed (Could not load voice data) with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
  }
  if (hasloadvoice)
    result = api_adapter_->VoiceClear();
  hasloadvoice = true;
  result = api_adapter_->VoiceLoad(settings.voice_name.c_str());
  if (result != ERR_SUCCESS)
  {
    string message = "API Load Voice failed (Could not load voice data) with code ";
    message += std::to_string(result);
    throw std::runtime_error(message);
  }
}
std::vector<int16_t> aitalked::Speech(float _rate, float _pitch, const std::string &text)
{

  Setparam(2, _rate, _pitch); // 0.5-4, 0.5-2
  std::vector<char> output;
  int result = Hiragana(text.c_str(), output);
  output.push_back(0);
  std::vector<int16_t> binary;
  result = Speech(output.data(), binary);
  return binary;
}
aitalked::~aitalked()
{
  delete api_adapter_;
}

int aitalked::Hiragana(const char *inbytes, std::vector<char> &output)
{
  Response<char> response{api_adapter_};
  TJobParam param;
  param.mode_in_out = IOMODE_PLAIN_TO_AIKANA;
  param.user_data = &response;

  int32_t job_id;
  ResultCode result = api_adapter_->TextToKana(&job_id, &param, inbytes);
  if (result != ERR_SUCCESS)
  {
    static const char *format = "TextToKana failed with the result code %d\n"
                                "Given inbytes: %s";

    char m[0xFFFF];
    std::snprintf(m, 0xFFFF, format, result, inbytes);
    throw std::runtime_error(m);
  }
  WaitForSingleObject(response.event, INFINITE);
  // finalize
  result = api_adapter_->CloseKana(job_id);
  if (result != ERR_SUCCESS)
  {
    throw std::runtime_error("wtf");
  }

  // write to output memory
  output = response.End();
  return 0;
}
void aitalked::Setparam(float volume, float speed, float pitch)
{
  uint32_t param_size = 0;
  auto result = api_adapter_->GetParam((void *)0, &param_size);
  if (result != ERR_INSUFFICIENT)
  { // NOTE: Code -20 is expected here
    string message = "API Get Param failed (Could not acquire the size) with code ";
    message += std::to_string(result);
    throw std::runtime_error(message);
  }
  if (param_size == sizeof(TTtsParam))
  { // voiceroid2
    TTtsParam param;
    // TTtsParam* param = (TTtsParam*) param_buffer;
    param.size = param_size;
    result = api_adapter_->GetParam(&param, &param_size);
    if (result != ERR_SUCCESS)
    {
      string message = "API Get Param failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
    param.extend_format = BOTH;
    param.proc_text_buf = HiraganaCallback;
    param.proc_raw_buf = SpeechCallback;
    param.proc_event_tts = nullptr;
    param.len_raw_buf_bytes = kConfigRawbufSize;

    param.volume = volume;
    param.speaker[0].volume = volume;
    /*
    param.speaker[0].pause_middle = 80;
    param.speaker[0].pause_sentence = 200;
    param.speaker[0].pause_long = 100;
    param.speaker[0].range = 0.893;*/
    param.speaker[0].speed = speed;
    param.speaker[0].pitch = pitch;
    result = api_adapter_->SetParam(&param);
    if (result != ERR_SUCCESS)
    {
      string message = "API Set Param failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
  }
  else if (param_size == sizeof(AITalk_TTtsParam))
  { // voiceroid+
    AITalk_TTtsParam param;
    // TTtsParam* param = (TTtsParam*) param_buffer;
    param.size = param_size;
    result = api_adapter_->GetParam(&param, &param_size);
    if (result != ERR_SUCCESS)
    {
      string message = "API Get Param failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
    param.proc_text_buf = HiraganaCallback;
    param.proc_raw_buf = SpeechCallback;
    param.proc_event_tts = nullptr;
    param.lenRawBufBytes = kConfigRawbufSize;

    param.volume = volume;
    param.Speaker[0].volume = volume;
    param.Speaker[0].speed = speed;
    param.Speaker[0].pitch = pitch;
    result = api_adapter_->SetParam(&param);
    if (result != ERR_SUCCESS)
    {
      string message = "API Set Param failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
  }
}
int aitalked::Speech(const char *inbytes, std::vector<int16_t> &output, uint32_t mode)
{
  Response<int16_t> response{api_adapter_};

  TJobParam param;
  param.mode_in_out = mode == 0u ? IOMODE_AIKANA_TO_WAVE : (JobInOut)mode;
  param.user_data = &response;

  int32_t job_id;
  ResultCode result = api_adapter_->TextToSpeech(&job_id, &param, inbytes);

  if (result != ERR_SUCCESS)
  {
    static const char *format = "TextToSpeech failed with the result code %d\n"
                                "Given inbytes: %s";
    char m[0xFFFF];
    std::snprintf(m, 0xFFFF, format, result, inbytes);
    throw std::runtime_error(m);
  }

  WaitForSingleObject(response.event, INFINITE);

  // finalize
  result = api_adapter_->CloseSpeech(job_id);
  if (result != ERR_SUCCESS)
  {
    throw std::runtime_error("wtf");
  }

  // write to output memory
  output = response.End();

  return 0;
}
