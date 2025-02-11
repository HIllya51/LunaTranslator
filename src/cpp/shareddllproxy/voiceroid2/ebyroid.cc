#include "ebyroid.h"

#include "api_adapter.h"
#include "api_settings.h"
#include "ebyutil.h"

namespace ebyroid
{

  using std::function;
  using std::pair;
  using std::string;
  using std::vector;

  namespace
  {

    ApiAdapter *NewAdapter(const string &, const string &, const string &, const string &);
    int __stdcall HiraganaCallback(EventReasonCode, int32_t, IntPtr);
    int __stdcall SpeechCallback(EventReasonCode, int32_t, uint64_t, IntPtr);
    inline pair<bool, string> WithDirecory(const char *dir, function<pair<bool, string>(void)> yield);
  } // namespace

  Ebyroid::~Ebyroid()
  {
    delete api_adapter_;
  }

  Ebyroid *Ebyroid::Create(const string &base_dir, const string &dllpath, const string &voice, const string &Lang)
  {
    try
    {
      ApiAdapter *adapter = NewAdapter(base_dir, dllpath, voice, Lang);
      Ebyroid *ebyroid = new Ebyroid(adapter);
      return ebyroid;
    }
    catch (std::exception &e)
    {
      MessageBoxA(0, e.what(), "", 0);
      return nullptr;
    }
  }

  int Ebyroid::Hiragana(const char *inbytes, std::vector<char> &output)
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
  void Ebyroid::Setparam(float volume, float speed, float pitch)
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
  int Ebyroid::Speech(const char *inbytes, std::vector<int16_t> &output, uint32_t mode)
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

  namespace
  {

    ApiAdapter *NewAdapter(const string &base_dir, const string &dllpath, const string &voice, const string &Lang)
    {
      SettingsBuilder builder(base_dir, voice, Lang);
      Settings settings = builder.Build();
      std::unique_ptr<ApiAdapter> adapter{ApiAdapter::Create(dllpath.c_str())};

      TConfig config;
      config.hz_voice_db = settings.frequency;
      config.dir_voice_dbs = settings.voice_dir;
      config.msec_timeout = msec_timeout;
      config.path_license = settings.license_path;
      config.code_auth_seed = settings.seed;
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
      SetDllDirectoryA(base_dir.c_str());
      result = adapter->LangLoad(settings.language_dir);
      result = adapter->VoiceLoad(settings.voice_name);
      if (result != ERR_SUCCESS)
      {
        string message = "API Load Voice failed (Could not load voice data) with code ";
        message += std::to_string(result);
        throw std::runtime_error(message);
      }

      return adapter.release();
    }

    inline pair<bool, string> WithDirecory(const char *dir, function<pair<bool, string>(void)> yield)
    {
      static constexpr size_t kErrMax = 64 + MAX_PATH;
      char org[MAX_PATH];
      DWORD result = GetCurrentDirectoryA(MAX_PATH, org);
      if (result == 0)
      {
        char m[64];
        std::snprintf(m, 64, "Could not get the current directory.\n\tErrorNo = %d", GetLastError());
        return pair<bool, string>(true, string(m));
      }
      BOOL result1 = SetCurrentDirectoryA(dir);
      if (!result1)
      {
        char m[kErrMax];
        std::snprintf(m,
                      kErrMax,
                      "Could not change directory.\n\tErrorNo = %d\n\tTarget path: %s",
                      GetLastError(),
                      dir);
        return pair<bool, string>(true, string(m));
      }
      bool is_error = yield().first;
      string what = yield().second;
      result1 = SetCurrentDirectoryA(org);
      if (!result1 && !is_error)
      {
        char m[kErrMax];
        std::snprintf(m,
                      kErrMax,
                      "Could not change directory.\n\tErrorNo = %d\n\tTarget path: %s",
                      GetLastError(),
                      org);
        return pair<bool, string>(true, string(m));
      }
      if (is_error)
      {
        return pair<bool, string>(true, what);
      }
      return pair<bool, string>(false, string());
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

} // namespace ebyroid
