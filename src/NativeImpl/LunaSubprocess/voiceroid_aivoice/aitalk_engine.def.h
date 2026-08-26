
#pragma once

enum AI_TTS_EVENT {
    AI_TTS_EVENT_BEGIN          = 0,
    AI_TTS_EVENT_BEGIN_SENTENCE = 1,
    AI_TTS_EVENT_MARKER        = 2,
    AI_TTS_EVENT_BUFREQ        = 3,   // 请求输出缓冲区(由宿主提供 PCM 缓冲)
    AI_TTS_EVENT_BUFDONE       = 4,   // 缓冲区已填满/已产生 PCM(宿主取走)
    AI_TTS_EVENT_END_SENTENCE  = 6,
    AI_TTS_EVENT_END           = 7,
};

struct TtsEvent {
    int32_t  code;       // +0  AI_TTS_EVENT_*
    int32_t  reserved;   // +4
    void*    data;       // +8  指向 bufdesc (BUFREQ 时等于 ev-0x20)
};

struct TtsAudioData {
    void*    buf;        // +0  int16 PCM 缓冲指针
    uint64_t size;       // +8  BUFREQ=容量(字节,>=2); BUFDONE 实测为 0 (不用)
    uint64_t field2;     // +16 BUFREQ 时必须为 0
    uint64_t field3;     // +24 BUFREQ 时必须为 0
};

typedef int (*AITalkHandler)(void* userData, TtsEvent* event);

// config 为 32 字节(4 个 qword), 全 0 即可(库内有默认值)
struct TTSConfig { uint64_t field[4]; };
