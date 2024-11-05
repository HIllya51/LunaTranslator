#ifndef API_ADAPTER_H
#define API_ADAPTER_H

// forward-declaration to avoid including Windows.h in header
#ifndef _WINDEF_
struct HINSTANCE__;
typedef HINSTANCE__ *HINSTANCE;
#endif

namespace ebyroid
{

  static constexpr int32_t kMaxVoiceName = 80;

  static constexpr int32_t kControlLength = 12;

  static constexpr int32_t kConfigRawbufSize = 0x158880;

  static constexpr int32_t kLenSeedValue = 0;

  enum EventReasonCode : uint32_t
  {
    TEXTBUF_FULL = 0x00000065,
    TEXTBUF_FLUSH = 0x00000066,
    TEXTBUF_CLOSE = 0x00000067,
    RAWBUF_FULL = 0x000000C9,
    RAWBUF_FLUSH = 0x000000CA,
    RAWBUF_CLOSE = 0x000000CB,
    PH_LABEL = 0x0000012D,
    BOOKMARK = 0x0000012E,
    AUTOBOOKMARK = 0x0000012F
  };

  enum ExtendFormat : uint32_t
  {
    NONE = 0,
    JEITA_RUBY = 1,
    AUTO_BOOKMARK = 16,
    BOTH = JEITA_RUBY | AUTO_BOOKMARK
  };

  enum JobInOut : uint32_t
  {
    IOMODE_PLAIN_TO_WAVE = 11,
    IOMODE_AIKANA_TO_WAVE = 12,
    IOMODE_JEITA_TO_WAVE = 13,
    IOMODE_PLAIN_TO_AIKANA = 21,
    IOMODE_AIKANA_TO_JEITA = 32
  };

  enum ResultCode : int32_t
  {
    ERR_USERDIC_NOENTRY = -1012,
    ERR_USERDIC_LOCKED = -1011,
    ERR_COUNT_LIMIT = -1004,
    ERR_READ_FAULT = -1003,
    ERR_PATH_NOT_FOUND = -1002,
    ERR_FILE_NOT_FOUND = -1001,
    ERR_OUT_OF_MEMORY = -206,
    ERR_JOB_BUSY = -203,
    ERR_INVALID_JOBID = -202,
    ERR_TOO_MANY_JOBS = -201,
    ERR_LICENSE_REJECTED = -102,
    ERR_LICENSE_EXPIRED = -101,
    ERR_LICENSE_ABSENT = -100,
    ERR_INSUFFICIENT = -20,
    ERR_NOT_LOADED = -11,
    ERR_NOT_INITIALIZED = -10,
    ERR_WAIT_TIMEOUT = -4,
    ERR_INVALID_ARGUMENT = -3,
    ERR_UNSUPPORTED = -2,
    ERR_INTERNAL_ERROR = -1,
    ERR_SUCCESS = 0,
    ERR_ALREADY_INITIALIZED = 10,
    ERR_ALREADY_LOADED = 11,
    ERR_PARTIALLY_REGISTERED = 21,
    ERR_NOMORE_DATA = 204
  };

  enum StatusCode : int32_t
  {
    STAT_WRONG_STATE = -1,
    STAT_INPROGRESS = 10,
    STAT_STILL_RUNNING = 11,
    STAT_DONE = 12
  };

  typedef void *IntPtr;
  typedef int(__stdcall *ProcTextBuf)(EventReasonCode reason_code, int32_t job_id, IntPtr user_data);
  typedef int(__stdcall *ProcRawBuf)(EventReasonCode reason_code,
                                     int32_t job_id,
                                     uint64_t tick,
                                     IntPtr user_data);
  typedef int(__stdcall *ProcEventTTS)(EventReasonCode reason_code,
                                       int32_t job_id,
                                       uint64_t tick,
                                       const char *name,
                                       IntPtr user_data);

#pragma pack(push, 1)
  struct AITalk_TTtsParam
  {
    // C#: public const int MAX_VOICENAME_ = 80;
    enum
    {
      MAX_VOICENAME_ = 80
    }; // 80 is used in AITalkMarshal.cs

    struct TJeitaParam
    {
      char femaleName[MAX_VOICENAME_]; // default: ""
      char maleName[MAX_VOICENAME_];   // default ""
      int pauseMiddle;                 // default 0
      int pauseLong;                   // default 0
      int pauseSentence;               // default 0
      char control[12];                // default ""  the length is used in AITalkMarshal.cs
    };

    struct TSpeakerParam
    {
      char voiceName[MAX_VOICENAME_];
      float volume;
      float speed;
      float pitch;
      float range;
      int pauseMiddle;
      int pauseLong;
      int pauseSentence;
    };
    unsigned int size; // default 308
    ProcTextBuf proc_text_buf;
    ProcRawBuf proc_raw_buf;
    ProcEventTTS proc_event_tts;
    unsigned int lenTextBufBytes;   // default 16384
    unsigned int lenRawBufBytes;    // default 176400
    float volume;                   // default 1
    int pauseBegin;                 // default -1
    int pauseTerm;                  // default -1
    char voiceName[MAX_VOICENAME_]; // default empty
    TJeitaParam Jeita;
    unsigned int numSpeakers; // default 0
    int __reserved__;
    TSpeakerParam Speaker[1]; // TSpeakerParam[] Speaker;

    size_t TotalSize() const
    {
      return sizeof(*this) + numSpeakers * sizeof(TSpeakerParam);
    }
  };
  struct TTtsParam
  {
    uint32_t size;
    ProcTextBuf proc_text_buf;
    ProcRawBuf proc_raw_buf;
    ProcEventTTS proc_event_tts;
    uint32_t len_text_buf_bytes;
    uint32_t len_raw_buf_bytes;
    float volume;
    int32_t pause_begin;
    int32_t pause_term;
    ExtendFormat extend_format;
    char voice_name[kMaxVoiceName];
    struct TJeitaParam
    {
      char female_name[kMaxVoiceName];
      char male_name[kMaxVoiceName];
      int32_t pause_middle;
      int32_t pause_long;
      int32_t pause_sentence;
      char control[kControlLength];
    };
    TJeitaParam jeita;
    uint32_t num_speakers;
    int32_t __reserved__;
    struct TSpeakerParam
    {
      char voice_name[kMaxVoiceName];
      float volume;
      float speed;
      float pitch;
      float range;
      int32_t pause_middle;
      int32_t pause_long;
      int32_t pause_sentence;
      char style_rate[kMaxVoiceName];
    };
    TSpeakerParam speaker[1];
  };
#pragma pack(pop)

#pragma pack(push, 1)
  struct TJobParam
  {
    JobInOut mode_in_out;
    IntPtr user_data;
  };
#pragma pack(pop)

#pragma pack(push, 1)
  struct TConfig
  {
    uint32_t hz_voice_db;
    const char *dir_voice_dbs;
    uint32_t msec_timeout;
    const char *path_license;
    const char *code_auth_seed;
    uint32_t len_auth_seed;
  };
#pragma pack(pop)

  class ApiAdapter
  {
  public:
    ApiAdapter(const ApiAdapter &) = delete;
    ApiAdapter(ApiAdapter &&) = delete;
    ~ApiAdapter();

    static ApiAdapter *Create(const char *);

    ResultCode Init(TConfig *config);
    ResultCode End();
    ResultCode SetParam(IntPtr p_param);
    ResultCode GetParam(IntPtr p_param, uint32_t *size);
    ResultCode LangLoad(const char *dir_lang);
    ResultCode VoiceLoad(const char *voice_name);
    ResultCode VoiceClear();
    ResultCode TextToKana(int32_t *job_id, TJobParam *param, const char *text);
    ResultCode CloseKana(int32_t job_id, int32_t use_event = 0);
    ResultCode GetKana(int32_t job_id,
                       char *text_buf,
                       uint32_t len_buf,
                       uint32_t *size,
                       uint32_t *pos);
    ResultCode TextToSpeech(int32_t *job_id, TJobParam *param, const char *text);
    ResultCode CloseSpeech(int32_t job_id, int32_t use_event = 0);
    ResultCode GetData(int32_t job_id, int16_t *raw_buf, uint32_t len_buf, uint32_t *size);

  private:
    ApiAdapter(HINSTANCE dll_instance) : dll_instance_(dll_instance) {}

    typedef ResultCode(__stdcall *ApiInit)(TConfig *);
    typedef ResultCode(__stdcall *ApiEnd)(void);
    typedef ResultCode(__stdcall *ApiSetParam)(IntPtr);
    typedef ResultCode(__stdcall *ApiGetParam)(IntPtr, uint32_t *);
    typedef ResultCode(__stdcall *ApiLangLoad)(const char *);
    typedef ResultCode(__stdcall *ApiVoiceLoad)(const char *);
    typedef ResultCode(__stdcall *ApiVoiceClear)(void);
    typedef ResultCode(__stdcall *ApiTextToKana)(int32_t *, TJobParam *, const char *);
    typedef ResultCode(__stdcall *ApiCloseKana)(int32_t, int32_t);
    typedef ResultCode(__stdcall *ApiGetKana)(int32_t, char *, uint32_t, uint32_t *, uint32_t *);
    typedef ResultCode(__stdcall *ApiTextToSpeech)(int32_t *, TJobParam *, const char *);
    typedef ResultCode(__stdcall *ApiCloseSpeech)(int32_t, int32_t);
    typedef ResultCode(__stdcall *ApiGetData)(int32_t, int16_t *, uint32_t, uint32_t *);

    HINSTANCE dll_instance_ = nullptr;

    ApiInit init_;
    ApiEnd end_;
    ApiVoiceLoad voice_load_;
    ApiVoiceClear voice_clear_;
    ApiSetParam set_param_;
    ApiGetParam get_param_;
    ApiLangLoad lang_load_;
    ApiTextToKana text_to_kana_;
    ApiCloseKana close_kana_;
    ApiGetKana get_kana_;
    ApiTextToSpeech text_to_speech_;
    ApiCloseSpeech close_speech_;
    ApiGetData get_data_;
  };

} // namespace ebyroid

#endif // API_ADAPTER_H
