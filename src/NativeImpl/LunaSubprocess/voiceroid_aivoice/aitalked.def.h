#ifndef AITALKED_FUNC_H
#define AITALKED_FUNC_H

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

struct TJeitaParam
{
  char female_name[kMaxVoiceName];
  char male_name[kMaxVoiceName];
  int32_t pause_middle;
  int32_t pause_long;
  int32_t pause_sentence;
  char control[kControlLength];
};

struct TSpeakerParam
{
  char voiceName[kMaxVoiceName];
  float volume;
  float speed;
  float pitch;
  float range;
  int32_t pauseMiddle;
  int32_t pauseLong;
  int32_t pauseSentence;
};

struct TSpeakerParamEx:public TSpeakerParam
{
  char style_rate[kMaxVoiceName];
};
struct AITalk_TTtsParam
{
  uint32_t size; // default 308
  ProcTextBuf proc_text_buf;
  ProcRawBuf proc_raw_buf;
  ProcEventTTS proc_event_tts;
  uint32_t lenTextBufBytes;  // default 16384
  uint32_t lenRawBufBytes;   // default 176400
  float volume;                  // default 1
  int pauseBegin;                // default -1
  int pauseTerm;                 // default -1
  char voiceName[kMaxVoiceName]; // default empty
  TJeitaParam Jeita;
  uint32_t numSpeakers; // default 0
  int32_t __reserved__;
  TSpeakerParam Speaker[1]; // TSpeakerParam[] Speaker;
};
struct AITalk_TTtsParamEx
{
  uint32_t size;
  ProcTextBuf proc_text_buf;
  ProcRawBuf proc_raw_buf;
  ProcEventTTS proc_event_tts;
  uint32_t lenTextBufBytes;
  uint32_t lenRawBufBytes;
  float volume;
  int32_t pauseBegin;
  int32_t pauseTerm;
  ExtendFormat extend_format;
  char voice_name[kMaxVoiceName];
  TJeitaParam Jeita;
  uint32_t numSpeakers;
  int32_t __reserved__;
  TSpeakerParamEx Speaker[1];
};

struct TJobParam
{
  JobInOut mode_in_out;
  IntPtr user_data;
};

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

#endif // AITALKED_FUNC_H
