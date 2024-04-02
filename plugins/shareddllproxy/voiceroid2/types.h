#pragma once
#define MAX_VOICENAME 80
#define MAX_JEITACONTROL 12
struct TConfig
{
    unsigned int hzVoiceDB;
    char *dirVoiceDBS;
    unsigned int msecTimeout;
    char *pathLicense;
    char *codeAuthSeed;
    unsigned int __reserved__;
};
typedef int (*ProcTextBuf)(int, int, void *);
typedef int (*ProcRawBuf)(int, int, int, unsigned long long, void *);
typedef int (*ProcEventTts)(int, int, int, unsigned long long, char *, void *);
struct TJeitaParam
{
    char femaleName[MAX_VOICENAME];
    char maleName[MAX_VOICENAME];
    int pauseMiddle;
    int pauseLong;
    int pauseSentence;
    char control[MAX_JEITACONTROL];
};
struct TSpeakerParam
{
    char voiceName[MAX_VOICENAME];
    float volume;
    float speed;
    float pitch;
    float range;
    int pauseMiddle;
    int pauseLong;
    int pauseSentence;
    char styleRate[MAX_VOICENAME];
};
struct TTtsParam
{
    unsigned int size;
    ProcTextBuf procTextBuf;
    ProcRawBuf procRawBuf;
    ProcEventTts procEventTts;
    unsigned int lenTextBufBytes;
    unsigned int lenRawBufBytes;
    float volume;
    int pauseBegin;
    int pauseTerm;
    int extendFormat;
    char voiceName[MAX_VOICENAME];
    TJeitaParam jeita;
    unsigned int numSpeakers;
    int __reserved__;
    TSpeakerParam speaker[1];
};
struct TJobParam
{
    unsigned int modeInOut;
    void *userData;
};
enum Result
{
    Success = 0,
    InternalError = -1,
    Unsupported = -2,
    InvalidArgument = -3,
    WaitTimeout = -4,
    NotInitialized = -10,
    AlreadyInitialized = 10,
    NotLoaded = -11,
    AlreadyLoaded = 11,
    Insufficient = -20,
    PartiallyRegistered = 21,
    LicenseAbsent = -100,
    LicenseExpired = -101,
    LicenseRejected = -102,
    TooManyJobs = -201,
    InvalidJobId = -202,
    JobBusy = -203,
    NoMoreData = 204,
    OutOfMemory = -206,
    FileNotFound = -1001,
    PathNotFound = -1002,
    ReadFault = -1003,
    CountLimit = -1004,
    UserDictionaryLocked = -1011,
    UserDictionaryNoEntry = -1012
};
typedef Result(__stdcall *AITalkAPI_Init)(TConfig *);
typedef Result(__stdcall *AITalkAPI_LangClear)();
typedef Result(__stdcall *AITalkAPI_LangLoad)(char *);
typedef Result(__stdcall *AITalkAPI_VoiceLoad)(char *);
typedef Result(__stdcall *AITalkAPI_SetParam)(TTtsParam *);
typedef Result(__stdcall *AITalkAPI_GetParam)(TTtsParam *, int *);
typedef Result(__stdcall *AITalkAPI_GetKana)(int, char *, int, int *, int *);
typedef Result(__stdcall *AITalkAPI_TextToKana)(int *, TJobParam *, char *);

char *UnicodeToShift_jis(const wchar_t *unicode);