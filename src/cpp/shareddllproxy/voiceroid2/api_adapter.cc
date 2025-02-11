#include "api_adapter.h"

#include "ebyutil.h"

namespace ebyroid
{

  namespace
  {

    template <class T>
    inline T LoadProc(const HINSTANCE &handle, const char *proc_name)
    {
      FARPROC proc = GetProcAddress(handle, proc_name);
      if (proc == nullptr)
      {
        FreeLibrary(handle);
        char m[64];
        std::snprintf(m, 64, "Could not find '%s' in the library.", proc_name);
        throw std::runtime_error(m);
      }
      return reinterpret_cast<T>(proc);
    }

  } // namespace

  ApiAdapter *ApiAdapter::Create(const char *dllpath)
  {
    HINSTANCE handle = LoadLibraryA(dllpath);
    if (handle == nullptr)
    {
      char m[128];
      std::snprintf(m,
                    128,
                    "LoadLibrary failed with code %d (Check out the voiceroid path setting)",
                    GetLastError());
      throw new std::runtime_error(m);
    }
    ApiAdapter *adapter = new ApiAdapter(handle);
#ifndef _WIN64
    adapter->init_ = LoadProc<ApiInit>(handle, "_AITalkAPI_Init@4");
    adapter->end_ = LoadProc<ApiEnd>(handle, "_AITalkAPI_End@0");
    adapter->voice_load_ = LoadProc<ApiVoiceLoad>(handle, "_AITalkAPI_VoiceLoad@4");
    adapter->voice_clear_ = LoadProc<ApiVoiceClear>(handle, "_AITalkAPI_VoiceClear@0");
    adapter->set_param_ = LoadProc<ApiSetParam>(handle, "_AITalkAPI_SetParam@4");
    adapter->get_param_ = LoadProc<ApiGetParam>(handle, "_AITalkAPI_GetParam@8");
    adapter->lang_load_ = LoadProc<ApiLangLoad>(handle, "_AITalkAPI_LangLoad@4");
    adapter->text_to_kana_ = LoadProc<ApiTextToKana>(handle, "_AITalkAPI_TextToKana@12");
    adapter->close_kana_ = LoadProc<ApiCloseKana>(handle, "_AITalkAPI_CloseKana@8");
    adapter->get_kana_ = LoadProc<ApiGetKana>(handle, "_AITalkAPI_GetKana@20");
    adapter->text_to_speech_ = LoadProc<ApiTextToSpeech>(handle, "_AITalkAPI_TextToSpeech@12");
    adapter->close_speech_ = LoadProc<ApiCloseSpeech>(handle, "_AITalkAPI_CloseSpeech@8");
    adapter->get_data_ = LoadProc<ApiGetData>(handle, "_AITalkAPI_GetData@16");
#else
    adapter->init_ = LoadProc<ApiInit>(handle, "AITalkAPI_Init");
    adapter->end_ = LoadProc<ApiEnd>(handle, "AITalkAPI_End");
    // adapter->voice_load_ = LoadProc<ApiVoiceLoad>(handle, "AITalkAPI_VoiceLoadFromFullPath");
    adapter->voice_load_ = LoadProc<ApiVoiceLoad>(handle, "AITalkAPI_VoiceLoad");
    adapter->voice_clear_ = LoadProc<ApiVoiceClear>(handle, "AITalkAPI_VoiceClear");
    adapter->set_param_ = LoadProc<ApiSetParam>(handle, "AITalkAPI_SetParam");
    adapter->get_param_ = LoadProc<ApiGetParam>(handle, "AITalkAPI_GetParam");
    adapter->lang_load_ = LoadProc<ApiLangLoad>(handle, "AITalkAPI_LangLoad");
    adapter->text_to_kana_ = LoadProc<ApiTextToKana>(handle, "AITalkAPI_TextToKana");
    adapter->close_kana_ = LoadProc<ApiCloseKana>(handle, "AITalkAPI_CloseKana");
    adapter->get_kana_ = LoadProc<ApiGetKana>(handle, "AITalkAPI_GetKana");
    adapter->text_to_speech_ = LoadProc<ApiTextToSpeech>(handle, "AITalkAPI_TextToSpeech");
    adapter->close_speech_ = LoadProc<ApiCloseSpeech>(handle, "AITalkAPI_CloseSpeech");
    adapter->get_data_ = LoadProc<ApiGetData>(handle, "AITalkAPI_GetData");
#endif
    return adapter;
  }

  ApiAdapter::~ApiAdapter()
  {
    BOOL result = FreeLibrary(dll_instance_);
    if (!result)
    {
      Eprintf("FreeLibrary(HMODULE) failed. Though the program will go on, may lead to fatal error.");
    }
  }

  ResultCode ApiAdapter::Init(TConfig *config)
  {
    return init_(config);
  }

  ResultCode ApiAdapter::End()
  {
    return end_();
  }

  ResultCode ApiAdapter::VoiceLoad(const char *voice_name)
  {
    return voice_load_(voice_name);
  }

  ResultCode ApiAdapter::VoiceClear()
  {
    return voice_clear_();
  }

  ResultCode ApiAdapter::SetParam(IntPtr p_param)
  {
    return set_param_(p_param);
  }

  ResultCode ApiAdapter::GetParam(IntPtr p_param, uint32_t *size)
  {
    return get_param_(p_param, size);
  }

  ResultCode ApiAdapter::LangLoad(const char *dir_lang)
  {
    return lang_load_(dir_lang);
  }

  ResultCode ApiAdapter::TextToKana(int32_t *job_id, TJobParam *param, const char *text)
  {
    return text_to_kana_(job_id, param, text);
  }

  ResultCode ApiAdapter::CloseKana(int32_t job_id, int32_t use_event)
  {
    return close_kana_(job_id, use_event);
  }

  ResultCode ApiAdapter::GetKana(int32_t job_id,
                                 char *text_buf,
                                 uint32_t len_buf,
                                 uint32_t *size,
                                 uint32_t *pos)
  {
    return get_kana_(job_id, text_buf, len_buf, size, pos);
  }

  ResultCode ApiAdapter::TextToSpeech(int32_t *job_id, TJobParam *param, const char *text)
  {
    return text_to_speech_(job_id, param, text);
  }

  ResultCode ApiAdapter::CloseSpeech(int32_t job_id, int32_t use_event)
  {
    return close_speech_(job_id, use_event);
  }

  ResultCode ApiAdapter::GetData(int32_t job_id, int16_t *raw_buf, uint32_t len_buf, uint32_t *size)
  {
    return get_data_(job_id, raw_buf, len_buf, size);
  }

} // namespace ebyroid
