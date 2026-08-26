
#include "engines.h"
#include "aitalked.def.h"

using std::function;
using std::pair;
using std::string;
using std::vector;
using namespace ebyroid;

#define AI_FNS(X)                                                                                                  \
  X(init, ResultCode(__stdcall *)(TConfig *), "_AITalkAPI_Init@4")                                                 \
  X(end, ResultCode(__stdcall *)(void), "_AITalkAPI_End@0")                                                        \
  X(voice_load, ResultCode(__stdcall *)(const char *), "_AITalkAPI_VoiceLoad@4")                                   \
  X(voice_clear, ResultCode(__stdcall *)(void), "_AITalkAPI_VoiceClear@0")                                         \
  X(lang_clear, ResultCode(__stdcall *)(void), "_AITalkAPI_LangClear@0")                                           \
  X(set_param, ResultCode(__stdcall *)(IntPtr), "_AITalkAPI_SetParam@4")                                           \
  X(get_param, ResultCode(__stdcall *)(IntPtr, uint32_t *), "_AITalkAPI_GetParam@8")                               \
  X(lang_load, ResultCode(__stdcall *)(const char *), "_AITalkAPI_LangLoad@4")                                     \
  X(text_to_kana, ResultCode(__stdcall *)(int32_t *, TJobParam *, const char *), "_AITalkAPI_TextToKana@12")       \
  X(close_kana, ResultCode(__stdcall *)(int32_t, int32_t), "_AITalkAPI_CloseKana@8")                               \
  X(get_kana, ResultCode(__stdcall *)(int32_t, char *, uint32_t, uint32_t *, uint32_t *), "_AITalkAPI_GetKana@20") \
  X(text_to_speech, ResultCode(__stdcall *)(int32_t *, TJobParam *, const char *), "_AITalkAPI_TextToSpeech@12")   \
  X(close_speech, ResultCode(__stdcall *)(int32_t, int32_t), "_AITalkAPI_CloseSpeech@8")                           \
  X(get_data, ResultCode(__stdcall *)(int32_t, int16_t *, uint32_t, uint32_t *), "_AITalkAPI_GetData@16")
DECLARE_API_STRUCT
#undef AI_FNS

namespace ebyroid
{

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
    Response(Api *adapter) : api_adapter_(adapter)
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
    Api *api_adapter() { return api_adapter_; };
    CEvent event;

  private:
    Api *api_adapter_;
    std::vector<T> buffer_;
  };

} // namespace ebyroid

namespace
{

  int __stdcall HiraganaCallback(EventReasonCode reason_code, int32_t job_id, IntPtr user_data)
  {
    auto response = (Response<char> *)user_data;
    Api *api_adapter = response->api_adapter();

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
      ResultCode result = api_adapter->get_kana(job_id, buffer, kBufferSize, &size, &pos);

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
    Api *api_adapter = response->api_adapter();

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
      ResultCode result = api_adapter->get_data(job_id, buffer, kBufferSize, &size);
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

struct aitalked_impl
{
  Api api;
  std::string lastlang_;
  bool hasloadvoice = false;
  aitalked_impl(const Settings &settings);
  void SetVoice(Settings &settings);
  std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text);
  void Setparam(float volume, float speed, float pitch);
  int Hiragana(const char *inbytes, std::vector<char> &);
  int Speek(const char *inbytes, std::vector<int16_t> &, uint32_t mode = 0u);
};

aitalked_impl::aitalked_impl(const Settings &settings)
{
  if (!api.load(settings.dllpath.c_str()))
    throw std::runtime_error("load dll failed");
  TConfig config;
  config.hz_voice_db = settings.frequency;
  config.dir_voice_dbs = settings.voice_base_dir.c_str();
  config.msec_timeout = 1000;
  config.path_license = settings.license_path.c_str();
  config.code_auth_seed = settings.seed.c_str();
  config.len_auth_seed = kLenSeedValue;
  ResultCode result = api.init(&config);
  if (result != ERR_SUCCESS)
  {
    config.code_auth_seed = "PROJECT-VOICeVIO-SFE";
    result = api.init(&config);
  }
  if (result != ERR_SUCCESS)
  {
    string message = "API initialization failed with code ";
    message += std::to_string(result);
    throw std::runtime_error(message);
  }
}
void aitalked_impl::SetVoice(Settings &settings)
{
  ResultCode result;

  if (settings.language_dir != lastlang_)
  {
    lastlang_ = settings.language_dir;
    api.lang_clear();
    result = api.lang_load(settings.language_dir.c_str());
    if (result != ERR_SUCCESS && result != ERR_ALREADY_LOADED)
    {
      string message = "API Load Lang failed (Could not load voice data) with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
  }
  if (hasloadvoice)
    result = api.voice_clear();
  hasloadvoice = true;
  result = api.voice_load(settings.voice_name.c_str());
  if (result != ERR_SUCCESS)
  {
    string message = "API Load Voice failed (Could not load voice data) with code ";
    message += std::to_string(result);
    throw std::runtime_error(message);
  }
}
std::vector<int16_t> aitalked_impl::Speek(float _rate, float _pitch, const std::string &text)
{
  Setparam(2, _rate, _pitch); // 0.5-4, 0.5-2
  std::vector<char> output;
  auto sjis = WideStringToString(StringToWideString(text), 932);
  int result = Hiragana(sjis.c_str(), output);
  output.push_back(0);
  std::vector<int16_t> binary;
  result = Speek(output.data(), binary);
  return binary;
}

int aitalked_impl::Hiragana(const char *inbytes, std::vector<char> &output)
{
  Response<char> response{&api};
  TJobParam param;
  param.mode_in_out = IOMODE_PLAIN_TO_AIKANA;
  param.user_data = &response;

  int32_t job_id;
  ResultCode result = api.text_to_kana(&job_id, &param, inbytes);
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
  result = api.close_kana(job_id, 0);
  if (result != ERR_SUCCESS)
  {
    throw std::runtime_error("wtf");
  }

  // write to output memory
  output = response.End();
  return 0;
}
void aitalked_impl::Setparam(float volume, float speed, float pitch)
{
  uint32_t param_size = 0;
  auto result = api.get_param((void *)0, &param_size);
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
    result = api.get_param(&param, &param_size);
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
    result = api.set_param(&param);
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
    result = api.get_param(&param, &param_size);
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
    result = api.set_param(&param);
    if (result != ERR_SUCCESS)
    {
      string message = "API Set Param failed with code ";
      message += std::to_string(result);
      throw std::runtime_error(message);
    }
  }
}
int aitalked_impl::Speek(const char *inbytes, std::vector<int16_t> &output, uint32_t mode)
{
  Response<int16_t> response{&api};

  TJobParam param;
  param.mode_in_out = mode == 0u ? IOMODE_AIKANA_TO_WAVE : (JobInOut)mode;
  param.user_data = &response;

  int32_t job_id;
  ResultCode result = api.text_to_speech(&job_id, &param, inbytes);

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
  result = api.close_speech(job_id, 0);
  if (result != ERR_SUCCESS)
  {
    throw std::runtime_error("wtf");
  }

  // write to output memory
  output = response.End();

  return 0;
}

aitalked::aitalked(const Settings &settings)
{
  pimpl = new aitalked_impl(settings);
}
void aitalked::SetVoice(Settings &settings)
{
  pimpl->SetVoice(settings);
}
std::vector<int16_t> aitalked::Speek(float _rate, float _pitch, const std::string &text)
{
  return pimpl->Speek(_rate, _pitch, text);
}
aitalked::~aitalked()
{
  if (pimpl)
    delete pimpl;
}
