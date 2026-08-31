
#include "engines.h"
#include "aitalked.def.h"
#include <magic_enum/magic_enum.hpp>

namespace magic_enum::customize
{
  template <>
  struct enum_range<ResultCode>
  {
    static constexpr int min = ERR_USERDIC_NOENTRY;
    static constexpr int max = ERR_NOMORE_DATA;
  };
}

using std::function;
using std::pair;
using std::string;
using std::vector;
#ifdef _WIN64
#define AI_FNS(X)                                                                                     \
  X(init, ResultCode (*)(TConfig *), "AITalkAPI_Init")                                                \
  X(end, ResultCode (*)(void), "AITalkAPI_End")                                                       \
  X(voice_load, ResultCode (*)(const char *), "AITalkAPI_VoiceLoad")                                  \
  X(voice_clear, ResultCode (*)(void), "AITalkAPI_VoiceClear")                                        \
  X(lang_clear, ResultCode (*)(void), "AITalkAPI_LangClear")                                          \
  X(set_param, ResultCode (*)(IntPtr), "AITalkAPI_SetParam")                                          \
  X(get_param, ResultCode (*)(IntPtr, uint32_t *), "AITalkAPI_GetParam")                              \
  X(lang_load, ResultCode (*)(const char *), "AITalkAPI_LangLoad")                                    \
  X(text_to_kana, ResultCode (*)(int32_t *, TJobParam *, const char *), "AITalkAPI_TextToKana")       \
  X(close_kana, ResultCode (*)(int32_t, int32_t), "AITalkAPI_CloseKana")                              \
  X(get_kana, ResultCode (*)(int32_t, char *, uint32_t, uint32_t *, uint32_t *), "AITalkAPI_GetKana") \
  X(text_to_speech, ResultCode (*)(int32_t *, TJobParam *, const char *), "AITalkAPI_TextToSpeech")   \
  X(close_speech, ResultCode (*)(int32_t, int32_t), "AITalkAPI_CloseSpeech")                          \
  X(get_data, ResultCode (*)(int32_t, int16_t *, uint32_t, uint32_t *), "AITalkAPI_GetData")

#else
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
#endif
DECLARE_API_STRUCT
#undef AI_FNS

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
  aitalked_impl(const Settings &settings)
  {
    if (!api.load(settings.dllpath.c_str()))
      throw std::runtime_error("load dll failed");
    TConfig config;
    config.hz_voice_db = settings.frequency;
    config.dir_voice_dbs = settings.voice_base_dir.c_str();
    config.msec_timeout = 1000;
    config.path_license = settings.license_path.c_str();
    config.code_auth_seed = settings.seed.c_str();
    ResultCode result = api.init(&config);

#ifndef _WIN64
    if (result != ERR_SUCCESS)
    {
      config.code_auth_seed = "PROJECT-VOICeVIO-SFE";
      result = api.init(&config);
    }
#endif
    iferrorthrow(result);
  }
  void SetVoice(Settings &settings)
  {
    if (settings.language_dir != lastlang_)
    {
      lastlang_ = settings.language_dir;
      api.lang_clear();
      iferrorthrow(api.lang_load(settings.language_dir.c_str()));
    }
    if (hasloadvoice)
      api.voice_clear();
    hasloadvoice = true;
    iferrorthrow(api.voice_load(settings.voice_name.c_str()));
  }
  std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text)
  {
    Setparam(2, _rate, _pitch); // 0.5-4, 0.5-2
    auto sjis = WideStringToString(StringToWideString(text), 932);
    auto &&output = Hiragana(sjis.c_str());
    output.push_back(0);
    return Speek(output.data());
  }
  void Setparam(float volume, float speed, float pitch)
  {
    uint32_t param_size = 0;
    iferrorthrow(api.get_param((void *)0, &param_size));
    if (param_size == sizeof(AITalk_TTtsParamEx))
    { // voiceroid2
      SetparamInternal<AITalk_TTtsParamEx>(volume, speed, pitch);
    }
    else if (param_size == sizeof(AITalk_TTtsParam))
    { // voiceroid+
      SetparamInternal<AITalk_TTtsParam>(volume, speed, pitch);
    }
  }
  std::vector<char> Hiragana(const char *inbytes)
  {
    Response<char> response{&api};
    TJobParam param;
    param.mode_in_out = IOMODE_PLAIN_TO_AIKANA;
    param.user_data = &response;

    int32_t job_id;
    iferrorthrow(api.text_to_kana(&job_id, &param, inbytes));
    WaitForSingleObject(response.event, INFINITE);
    iferrorthrow(api.close_kana(job_id, 0));
    return std::move(response.End());
  }
  std::vector<int16_t> Speek(const char *inbytes, uint32_t mode = 0u)
  {
    Response<int16_t> response{&api};

    TJobParam param;
    param.mode_in_out = mode == 0u ? IOMODE_AIKANA_TO_WAVE : (JobInOut)mode;
    param.user_data = &response;
    int32_t job_id;
    iferrorthrow(api.text_to_speech(&job_id, &param, inbytes));
    WaitForSingleObject(response.event, INFINITE);
    iferrorthrow(api.close_speech(job_id, 0));
    return std::move(response.End());
  }

  void iferrorthrow(ResultCode r)
  {
    if (r != ERR_SUCCESS && r != ERR_ALREADY_LOADED && r != ERR_INSUFFICIENT)
      throw std::runtime_error(std::string(magic_enum::enum_name(r)));
  }

  template <typename T>
  void setExtendFormatIfApplicable(T &param)
  {
    if constexpr (std::is_same_v<T, AITalk_TTtsParamEx>)
      param.extend_format = BOTH;
  }

  template <typename T>
  void SetparamInternal(float volume, float speed, float pitch)
  {
    T param;
    uint32_t param_size = sizeof(T);
    param.size = param_size;
    iferrorthrow(api.get_param(&param, &param_size));
    setExtendFormatIfApplicable(param);
    param.proc_text_buf = HiraganaCallback;
    param.proc_raw_buf = SpeechCallback;
    param.proc_event_tts = nullptr;
    param.lenRawBufBytes = kConfigRawbufSize;

    param.volume = volume;
    param.Speaker[0].volume = volume;
    param.Speaker[0].speed = speed;
    param.Speaker[0].pitch = pitch;
    iferrorthrow(api.set_param(&param));
  }
};

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
