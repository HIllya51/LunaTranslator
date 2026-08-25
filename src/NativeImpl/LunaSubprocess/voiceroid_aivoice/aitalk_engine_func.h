// aitalk_engine.h
// C 接口声明，反编译自 aitalk_engine.dll (Amaneo AIVoice2 / AITalk6 引擎)
// 仅声明本程序用到的函数。全部为 x64 调用约定 (MSVC x64 只有一种调用约定，
// 函数指针直接用即可，无需显式 __fastcall)。
#pragma once
#include <cstdint>
#include <cstddef>

// ---- 返回码 ----
// 0 = 成功; 0xFFFFFFFF(-1) 一般性错误; 0xFFFFFD03(-813) obj 为空;
// 0xFFFFFC2D(-979) 未授权; 0xFFFFFC17(-1001) 未授权
// 1 = 被用户取消(回调返回)

// ---- TTS 回调事件 ----
// 来自反编译中的分发: BEGIN=0, BEGIN_SENTENCE=1, MARKER=2, BUFREQ=3, BUFDONE=4,
//                       ?=5, END_SENTENCE=6, END=7
enum AI_TTS_EVENT {
    AI_TTS_EVENT_BEGIN          = 0,
    AI_TTS_EVENT_BEGIN_SENTENCE = 1,
    AI_TTS_EVENT_MARKER        = 2,
    AI_TTS_EVENT_BUFREQ        = 3,   // 请求输出缓冲区(由宿主提供 PCM 缓冲)
    AI_TTS_EVENT_BUFDONE       = 4,   // 缓冲区已填满/已产生 PCM(宿主取走)
    AI_TTS_EVENT_END_SENTENCE  = 6,
    AI_TTS_EVENT_END           = 7,
};

// 引擎传给回调的事件头. handler 第 2 参数 ev 指向引擎栈上的局部:
//   ev+0x00 = int  事件码 (AI_TTS_EVENT_*)
//   ev+0x04 = int  保留
//   ev+0x08 = void* 指向 bufdesc (BUFREQ 时 = ev-0x20, 即 bufdesc 本体在 ev-0x20..ev-0x08)
// 反编译依据: BUFREQ sub_1800D1EF0 (传 &v10; v10@rbp-0x28=ev; v6..v9@rbp-0x48..-0x30=bufdesc);
//            BUFDONE sub_1800D1530 (传 &v4;  v4@rbp-0x48=ev;  v6[0..3]@rbp-0x38..-0x20).
struct TtsEvent {
    int32_t  code;       // +0  AI_TTS_EVENT_*
    int32_t  reserved;   // +4
    void*    data;       // +8  指向 bufdesc (BUFREQ 时等于 ev-0x20)
};

// BUFREQ/BUFDONE 的音频结构 (4 个 qword). BUFREQ 时此结构位于 ev-0x20,
// 用 ev+8 解引用或直接用 ev-0x20 访问等价 (二者指向同一地址).
//   BUFREQ: 宿主填 [0]=buf, [1]=size(字节,>=2), [2]=0, [3]=0.
//           ★ [2]/[3] 必须为 0 ★ —— sub_1800D1EF0 只校验 buf!=0 && size>=2,
//           把 [2]/[3] 原样存入 a1+0xD0/0xD8; 填非 0 则声码器会把它当指针解引用 → 段错误
//           (这就是旧版崩溃的根因; 可工作的 aitalk_tts.cpp 也填 0).
//   BUFDONE: 已填充 PCM 缓冲指针在 ev+0x10 (= v6[0]=a1+0xB8). 本引擎每帧写 1 个 int16
//           样本, 取 ((int16*)*(ev+0x10))[0] 即可 (v6[1] 即 a1+0xC8 实测为 0, 不作字节数用).
struct TtsAudioData {
    void*    buf;        // +0  int16 PCM 缓冲指针
    uint64_t size;       // +8  BUFREQ=容量(字节,>=2); BUFDONE 实测为 0 (不用)
    uint64_t field2;     // +16 BUFREQ 时必须为 0
    uint64_t field3;     // +24 BUFREQ 时必须为 0
};

// 回调函数原型。
//   反编译依据: TtsCallbackSink 的统一分发器只有三条指令:
//     mov rax,rcx          ; rax = sink
//     mov rcx,[rcx+0x10]   ; rcx = userdata   (第1参数)
//     call [rax+8]         ; 调 handler, rdx = 事件指针(第2参数)
//   故原型为 handler(userdata, event)
//   重要: 返回值会被引擎检查 (sub_1800D1530/D1EF0): 0=成功, 1=取消(用户),
//         其它=回调失败. 因此处理完后必须 return 0.
typedef int (*AITalkHandler)(void* userData, TtsEvent* event);

// ---- 库初始化 / 授权 / 终止 ----
// config 为 32 字节(4 个 qword), 全 0 即可(库内有默认值)
struct TTSConfig { uint64_t field[4]; };

typedef int    (*PFN_ai_ttsLibraryConfigInitialize)(TTSConfig* config);    // 清零 config
typedef int    (*PFN_ai_ttsLibraryInitialize)(TTSConfig* config);          // 可传 null(内部建默认)
typedef int    (*PFN_ai_ttsLibraryAuthenticate)(const char* licPath, const char* key1, const char* key2);
typedef int    (*PFN_ai_ttsLibraryUnauthenticate)();
typedef int    (*PFN_ai_ttsLibraryTerminate)();
typedef int    (*PFN_ai_ttsLogInitialize)(void* logHandle);                // 传 0 跳过
typedef int    (*PFN_ai_ttsLogSetLevel)(int level);

// ---- PathSet ----
typedef void*  (*PFN_ai_PathSet_new)();
typedef int    (*PFN_ai_PathSet_add)(void* pathSet, const char* key, const char* path);
typedef int    (*PFN_ai_PathSet_remove)(void* pathSet, const char* key);
typedef void   (*PFN_ai_PathSet_delete)(void* pathSet);

// ---- Talker ----
typedef void*  (*PFN_ai_Talker_new)();
typedef void*  (*PFN_ai_Talker_newEx)(void* config16);
typedef void   (*PFN_ai_Talker_delete)(void* talker);
typedef int    (*PFN_ai_Talker_setPathSet)(void* talker, void* pathSet);
typedef int    (*PFN_ai_Talker_setSink)(void* talker, const void* sink);
typedef int    (*PFN_ai_Talker_setDefaultConfig)(void* talker, void* config);
typedef void*  (*PFN_ai_Talker_getDefaultConfig)(void* talker);

// 字典加载
//   loadLangDic(talker, key, langDicPath, pkgType)   —— pkgType=1 (.aildic 是 tar 包)
//   loadVoiceDic(talker, key, aivdicPath, pkgType, voiceLicPath)
typedef int    (*PFN_ai_Talker_loadLangDic)(void* talker, const char* key, const char* langDicPath, unsigned int pkgType);
typedef int    (*PFN_ai_Talker_loadVoiceDic)(void* talker, const char* key, const char* aivdicPath, unsigned int pkgType, const char* voiceLicPath);
typedef int    (*PFN_ai_Talker_loadLangDicByKey)(void* talker, const char* key);
typedef int    (*PFN_ai_Talker_loadVoiceDicByKey)(void* talker);
typedef int    (*PFN_ai_Talker_unloadAllLangDic)(void* talker);
typedef int    (*PFN_ai_Talker_unloadAllVoiceDic)(void* talker);
typedef int    (*PFN_ai_Talker_selectLangDic)(void* talker, const char* key);
typedef int    (*PFN_ai_Talker_selectVoiceDic)(void* talker, const char* key);

// 语音信息
typedef int    (*PFN_ai_Talker_getVoiceFs)(void* talker);            // 采样率(Hz)
typedef const char* (*PFN_ai_Talker_getVoiceName)(void* talker);
typedef int    (*PFN_ai_Talker_getVoiceGender)(void* talker);

// 合成
//   talk(talker, text, encoding) —— encoding=文本编码(0=UTF-8, 1=Shift_JIS, 2=EUC-JP, 见说明)
typedef int    (*PFN_ai_Talker_talk)(void* talker, const char* text, unsigned int encoding);
// 两步合成 (编辑器实际使用的方式):
//   compileToImkana(talker, imkanaObj, text, encoding) -> 填充 IR
//   talkByImKana(talker, imkanaObj) -> 由 IR 合成音频
typedef void*  (*PFN_ai_TtsImKana_new)();
typedef void   (*PFN_ai_TtsImKana_delete)(void* imkana);
typedef int    (*PFN_ai_Talker_compileToImkana)(void* talker, void* imkana, const char* text, unsigned int encoding);
typedef int    (*PFN_ai_Talker_talkByImKana)(void* talker, void* imkana);
typedef int    (*PFN_ai_Talker_textAnalyze)(void* talker, void** outImKana, int mode, void* ctx);

// ---- TtsCallbackSink ----
//   new(handler, userData) -> sink 对象, 内部布局 [vtable, handler, userData]
typedef void*  (*PFN_ai_TtsCallbackSink_new)(AITalkHandler handler, void* userData);
typedef void   (*PFN_ai_TtsCallbackSink_delete)(void* sink);

// ---- TalkerConfig (可选, 调整音量/语速/音高) ----
typedef void*  (*PFN_ai_TalkerConfig_new)();
typedef int    (*PFN_ai_TalkerConfig_delete)(void*);
typedef int    (*PFN_ai_TalkerConfig_setVolume)(void* cfg, double v);        // 0.0~1.0
typedef int    (*PFN_ai_TalkerConfig_setRate)(void* cfg, double v);           // 0.5~2.0
typedef int    (*PFN_ai_TalkerConfig_setPitch)(void* cfg, double v);          // 0.5~2.0
typedef int    (*PFN_ai_TalkerConfig_setMasterVolume)(void* cfg, double v);   // 0.0~1.0
typedef int    (*PFN_ai_TalkerConfig_setStyleColor)(void* cfg, const char* styleKey); // UTF-8 风格名
typedef int    (*PFN_ai_TalkerConfig_setContext)(void* cfg, unsigned int ctx);        // 上下文索引(必须设, 否则未初始化)

// 风格信息
typedef int    (*PFN_ai_Talker_getStyleColorSize)(void* talker);              // 风格数量
typedef __int64 (*PFN_ai_Talker_getStyleColorLabel)(void* talker, unsigned int idx, wchar_t* buf, size_t bufSize);
