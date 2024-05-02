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

    ApiAdapter *NewAdapter(const string &, const string &, const string &, float, float);
    int __stdcall HiraganaCallback(EventReasonCode, int32_t, IntPtr);
    int __stdcall SpeechCallback(EventReasonCode, int32_t, uint64_t, IntPtr);
    inline pair<bool, string> WithDirecory(const char *dir, function<pair<bool, string>(void)> yield);
  } // namespace

  Ebyroid::~Ebyroid()
  {
    delete api_adapter_;
  }

  Ebyroid *Ebyroid::Create(const string &base_dir, const string &dllpath, const string &voice, float volume, float speed)
  {

    ApiAdapter *adapter = NewAdapter(base_dir, dllpath, voice, volume, speed);
    Ebyroid *ebyroid = new Ebyroid(adapter);
    return ebyroid;
  }

  int Ebyroid::Hiragana(const unsigned char *inbytes, unsigned char **outbytes, size_t *outsize)
  {
    Response *const response = new Response(api_adapter_);
    printf("1\n");
    TJobParam param;
    param.mode_in_out = IOMODE_PLAIN_TO_AIKANA;
    param.user_data = response;

    char eventname[32];
    std::sprintf(eventname, "TTKLOCK:%p", response);
    printf("12\n");
    HANDLE event = CreateEventA(NULL, TRUE, FALSE, eventname);
    printf("3\n");
    int32_t job_id;
    ResultCode result = api_adapter_->TextToKana(&job_id, &param, (const char *)inbytes);
    printf("4\n");
    if (result != ERR_SUCCESS)
    {
      delete response;
      printf("%d\n", result);
      ResetEvent(event);
      CloseHandle(event);
      static const char *format = "TextToKana failed with the result code %d\n"
                                  "Given inbytes: %s";

      char m[0xFFFF];
      std::snprintf(m, 0xFFFF, format, result, inbytes);
      throw std::runtime_error(m);
    }
    printf("6\n");
    WaitForSingleObject(event, INFINITE);
    ResetEvent(event);
    CloseHandle(event);
    printf("8\n");
    // finalize
    result = api_adapter_->CloseKana(job_id);
    if (result != ERR_SUCCESS)
    {
      delete response;
      throw std::runtime_error("wtf");
    }

    // write to output memory
    vector<unsigned char> buffer = response->End();
    *outsize = buffer.size();
    *outbytes = (unsigned char *)malloc(buffer.size() + 1);
    std::copy(buffer.begin(), buffer.end(), *outbytes);
    *(*outbytes + buffer.size()) = '\0';

    delete response;
    return 0;
  }

  int Ebyroid::Speech(const unsigned char *inbytes,
                      int16_t **outbytes,
                      size_t *outsize,
                      uint32_t mode)
  {
    Response *const response = new Response(api_adapter_);

    TJobParam param;
    param.mode_in_out = mode == 0u ? IOMODE_AIKANA_TO_WAVE : (JobInOut)mode;
    param.user_data = response;

    char eventname[32];
    sprintf(eventname, "TTSLOCK:%p", response);
    HANDLE event = CreateEventA(NULL, TRUE, FALSE, eventname);

    int32_t job_id;
    ResultCode result = api_adapter_->TextToSpeech(&job_id, &param, (const char *)inbytes);

    if (result != ERR_SUCCESS)
    {
      delete response;
      ResetEvent(event);
      CloseHandle(event);
      static const char *format = "TextToSpeech failed with the result code %d\n"
                                  "Given inbytes: %s";
      char m[0xFFFF];
      std::snprintf(m, 0xFFFF, format, result, inbytes);
      throw std::runtime_error(m);
    }

    WaitForSingleObject(event, INFINITE);
    ResetEvent(event);
    CloseHandle(event);

    // finalize
    result = api_adapter_->CloseSpeech(job_id);
    if (result != ERR_SUCCESS)
    {
      delete response;
      throw std::runtime_error("wtf");
    }

    // write to output memory
    vector<int16_t> buffer = response->End16();
    *outsize = buffer.size() * 2; // sizeof(int16_t) == 2
    *outbytes = (int16_t *)malloc(buffer.size() * 2 + 1);
    std::copy(buffer.begin(), buffer.end(), *outbytes);
    *((char *)*outbytes + (buffer.size() * 2)) = '\0';

    delete response;
    return 0;
  }

  void Response::Write(char *bytes, uint32_t size)
  {
    buffer_.insert(std::end(buffer_), bytes, bytes + size);
  }

  void Response::Write16(int16_t *shorts, uint32_t size)
  {
    buffer_16_.insert(std::end(buffer_16_), shorts, shorts + size);
  }

  vector<unsigned char> Response::End()
  {
    return std::move(buffer_);
  }

  vector<int16_t> Response::End16()
  {
    return std::move(buffer_16_);
  }

  namespace
  {

    ApiAdapter *NewAdapter(const string &base_dir, const string &dllpath, const string &voice, float volume, float speed)
    {
      SettingsBuilder builder(base_dir, voice);
      Settings settings = builder.Build();

      ApiAdapter *adapter = ApiAdapter::Create(dllpath.c_str());

      TConfig config;
      config.hz_voice_db = settings.frequency;

      config.msec_timeout = 1000;
      config.path_license = settings.license_path;
      config.dir_voice_dbs = settings.voice_dir;
      config.code_auth_seed = settings.seed;
      config.len_auth_seed = kLenSeedValue;
      ResultCode result = adapter->Init(&config);
      if (result != ERR_SUCCESS)
      {
        config.code_auth_seed = "PROJECT-VOICeVIO-SFE";
        result = adapter->Init(&config);
      }
      printf("init %d\n", result);
      if (result != ERR_SUCCESS)
      {
        delete adapter;
        string message = "API initialization failed with code ";
        message += std::to_string(result);
        throw std::runtime_error(message);
      }
      /*pair<bool, string>xx = WithDirecory(settings.base_dir, [adapter, settings]() {
          ResultCode result = adapter->LangLoad(settings.language_dir);
          printf("laod lang %d\n", result);
          if (result != ERR_SUCCESS) {
              char m[64];
              std::snprintf(m, 64, "API LangLoad failed (could not load language) with code %d", result);
              return pair<bool, string>(true, string(m));
          }
          return pair<bool, string>(false, string());
          });*/
      bool x = SetCurrentDirectoryA(settings.base_dir);
      SetDllDirectoryA(settings.base_dir);
      printf("%d\n", x);
      wchar_t buffer[1000] = {0};
      DWORD sz = 1000;
      GetCurrentDirectoryW(sz, buffer);
      wprintf(L"%s\n", buffer);
      result = adapter->LangLoad(settings.language_dir);
      printf("%s %s \n", settings.base_dir, settings.language_dir);
      printf("loadvoice %d\n", result);
      result = adapter->VoiceLoad(settings.voice_name);
      printf("loadvoice %s %d\n", settings.voice_name, result);
      if (result != ERR_SUCCESS)
      {
        delete adapter;
        string message = "API Load Voice failed (Could not load voice data) with code ";
        message += std::to_string(result);
        throw std::runtime_error(message);
      }
      uint32_t param_size = 0;
      result = adapter->GetParam((void *)0, &param_size);
      if (result != ERR_INSUFFICIENT)
      { // NOTE: Code -20 is expected here
        delete adapter;
        string message = "API Get Param failed (Could not acquire the size) with code ";
        message += std::to_string(result);
        throw std::runtime_error(message);
      }

      printf("param->size %d\n", param_size);
      if (param_size == 500)
      { // voiceroid2
        char *param_buffer = new char[param_size];
        TTtsParam *param = (TTtsParam *)param_buffer;
        // TTtsParam* param = (TTtsParam*) param_buffer;
        param->size = param_size;
        result = adapter->GetParam(param, &param_size);
        printf("%s %d\n", "GetParam", result);
        if (result != ERR_SUCCESS)
        {
          delete[] param_buffer;
          delete adapter;
          string message = "API Get Param failed with code ";
          message += std::to_string(result);
          throw std::runtime_error(message);
        }
        param->extend_format = BOTH;
        param->proc_text_buf = HiraganaCallback;
        param->proc_raw_buf = SpeechCallback;
        param->proc_event_tts = nullptr;
        param->len_raw_buf_bytes = kConfigRawbufSize;

        param->volume = volume;
        printf("1\n");
        param->speaker[0].volume = volume;
        /*param->speaker[0].pitch = 1.111;
        param->speaker[0].pause_middle = 80;
        param->speaker[0].pause_sentence = 200;
        param->speaker[0].pause_long = 100;
        param->speaker[0].range = 0.893;*/
        param->speaker[0].speed = speed;
        printf("2 %d %d\n", volume, speed);
        result = adapter->SetParam(param);
        printf("3 %d\n", result);
        if (result != ERR_SUCCESS)
        {
          delete[] param_buffer;
          delete adapter;
          string message = "API Set Param failed with code ";
          message += std::to_string(result);
          throw std::runtime_error(message);
        }
        printf("3\n");
        delete[] param_buffer;
      }
      else if (param_size == 416)
      { // voiceroid+
        char *param_buffer = new char[param_size];
        AITalk_TTtsParam *param = (AITalk_TTtsParam *)param_buffer;
        // TTtsParam* param = (TTtsParam*) param_buffer;
        param->size = param_size;
        result = adapter->GetParam(param, &param_size);
        if (result != ERR_SUCCESS)
        {
          delete[] param_buffer;
          delete adapter;
          string message = "API Get Param failed with code ";
          message += std::to_string(result);
          throw std::runtime_error(message);
        }
        printf("numSpeakers %d\n", param->numSpeakers);
        param->proc_text_buf = HiraganaCallback;
        param->proc_raw_buf = SpeechCallback;
        param->proc_event_tts = nullptr;
        param->lenRawBufBytes = kConfigRawbufSize;

        param->volume = volume;
        auto f = fopen(R"(C:\Users\wcy\source\repos\ConsoleApplication1\Release\2.txt)", "wb");
        fwrite(param, 1, param_size, f);
        fclose(f);
        result = adapter->SetParam(param);
        printf("SetParam ok %d\n", result);
        if (result != ERR_SUCCESS)
        {
          delete[] param_buffer;
          delete adapter;
          string message = "API Set Param failed with code ";
          message += std::to_string(result);
          printf("%s\n", message.c_str());
          throw std::runtime_error(message);
        }
        delete[] param_buffer;
      }

      printf("%s  \n", "setparam all ok");
      return adapter;
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
      Response *const response = (Response *)user_data;
      ApiAdapter *api_adapter = response->api_adapter();

      if (reason_code != TEXTBUF_FULL && reason_code != TEXTBUF_FLUSH && reason_code != TEXTBUF_CLOSE)
      {
        // unexpected: may possibly lead to memory leak
        return 0;
      }

      static constexpr int kBufferSize = 0x1000;
      char *buffer = new char[kBufferSize];
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
      delete[] buffer;

      if (reason_code == TEXTBUF_CLOSE)
      {
        char eventname[32];
        sprintf(eventname, "TTKLOCK:%p", response);
        HANDLE event = OpenEventA(EVENT_ALL_ACCESS, FALSE, eventname);
        SetEvent(event);
      }
      return 0;
    }

    int __stdcall SpeechCallback(EventReasonCode reason_code,
                                 int32_t job_id,
                                 uint64_t tick,
                                 IntPtr user_data)
    {
      Response *const response = (Response *)user_data;
      ApiAdapter *api_adapter = response->api_adapter();

      if (reason_code != RAWBUF_FULL && reason_code != RAWBUF_FLUSH && reason_code != RAWBUF_CLOSE)
      {
        // unexpected: may possibly lead to memory leak
        return 0;
      }

      static constexpr int kBufferSize = 0xFFFF;
      int16_t *buffer = new int16_t[kBufferSize];
      while (true)
      {
        uint32_t size, pos;
        ResultCode result = api_adapter->GetData(job_id, buffer, kBufferSize, &size);
        if (result != ERR_SUCCESS)
        {
          break;
        }
        response->Write16(buffer, size);
        if (kBufferSize > size)
        {
          break;
        }
      }
      delete[] buffer;

      if (reason_code == RAWBUF_CLOSE)
      {
        char eventname[32];
        sprintf(eventname, "TTSLOCK:%p", response);
        HANDLE event = OpenEventA(EVENT_ALL_ACCESS, FALSE, eventname);
        SetEvent(event);
      }
      return 0;
    }

  } // namespace

} // namespace ebyroid
