#include "engines.h"
#include "aitalk_engine.def.h"

static const char *errMeaning(int code)
{
    if (code == 0)
        return "OK";
    if (code == 1)
        return "canceled";
    if (code == -813)
        return "obj null";
    if (code == -979)
        return "unauthenticated";
    if (code == -1001)
        return "not authenticated";
    return "error";
}

struct aitalk_engine_impl
{
#define AI_FNS(X)                                                                                                                \
    X(ai_ttsLibraryConfigInitialize, int (*)(TTSConfig *), "ai_ttsLibraryConfigInitialize")                                      \
    X(ai_ttsLibraryInitialize, int (*)(TTSConfig *), "ai_ttsLibraryInitialize")                                                  \
    X(ai_ttsLibraryAuthenticate, int (*)(const char *, const char *, const char *), "ai_ttsLibraryAuthenticate")                 \
    X(ai_ttsLibraryUnauthenticate, int (*)(), "ai_ttsLibraryUnauthenticate")                                                     \
    X(ai_ttsLibraryTerminate, int (*)(), "ai_ttsLibraryTerminate")                                                               \
    X(ai_ttsLogInitialize, int (*)(void *), "ai_ttsLogInitialize")                                                               \
    X(ai_ttsLogSetLevel, int (*)(int), "ai_ttsLogSetLevel")                                                                      \
    X(ai_PathSet_new, void *(*)(), "ai_PathSet_new")                                                                             \
    X(ai_PathSet_add, int (*)(void *, const char *, const char *), "ai_PathSet_add")                                             \
    X(ai_PathSet_delete, void (*)(void *), "ai_PathSet_delete")                                                                  \
    X(ai_Talker_new, void *(*)(), "ai_Talker_new")                                                                               \
    X(ai_Talker_newEx, void *(*)(void *), "ai_Talker_newEx")                                                                     \
    X(ai_Talker_delete, void (*)(void *), "ai_Talker_delete")                                                                    \
    X(ai_Talker_setPathSet, int (*)(void *, void *), "ai_Talker_setPathSet")                                                     \
    X(ai_Talker_setSink, int (*)(void *, const void *), "ai_Talker_setSink")                                                     \
    X(ai_Talker_setDefaultConfig, int (*)(void *, void *), "ai_Talker_setDefaultConfig")                                         \
    X(ai_Talker_getDefaultConfig, void *(*)(void *), "ai_Talker_getDefaultConfig")                                               \
    X(ai_Talker_loadLangDic, int (*)(void *, const char *, const char *, unsigned int), "ai_Talker_loadLangDic")                 \
    X(ai_Talker_loadVoiceDic, int (*)(void *, const char *, const char *, unsigned int, const char *), "ai_Talker_loadVoiceDic") \
    X(ai_Talker_unloadAllLangDic, int (*)(void *), "ai_Talker_unloadAllLangDic")                                                 \
    X(ai_Talker_unloadAllVoiceDic, int (*)(void *), "ai_Talker_unloadAllVoiceDic")                                               \
    X(ai_Talker_selectLangDic, int (*)(void *, const char *), "ai_Talker_selectLangDic")                                         \
    X(ai_Talker_selectVoiceDic, int (*)(void *, const char *), "ai_Talker_selectVoiceDic")                                       \
    X(ai_Talker_getVoiceFs, int (*)(void *), "ai_Talker_getVoiceFs")                                                             \
    X(ai_Talker_getVoiceName, const char *(*)(void *), "ai_Talker_getVoiceName")                                                 \
    X(ai_Talker_talk, int (*)(void *, const char *, unsigned int), "ai_Talker_talk")                                             \
    X(ai_TtsImKana_new, void *(*)(), "ai_TtsImKana_new")                                                                         \
    X(ai_TtsImKana_delete, void (*)(void *), "ai_TtsImKana_delete")                                                              \
    X(ai_Talker_compileToImkana, int (*)(void *, void *, const char *, unsigned int), "ai_Talker_compileToImkana")               \
    X(ai_Talker_talkByImKana, int (*)(void *, void *), "ai_Talker_talkByImKana")                                                 \
    X(ai_TtsCallbackSink_new, void *(*)(AITalkHandler, void *), "ai_TtsCallbackSink_new")                                        \
    X(ai_TtsCallbackSink_delete, void (*)(void *), "ai_TtsCallbackSink_delete")                                                  \
    X(ai_TalkerConfig_new, void *(*)(), "ai_TalkerConfig_new")                                                                   \
    X(ai_TalkerConfig_delete, int (*)(void *), "ai_TalkerConfig_delete")                                                         \
    X(ai_TalkerConfig_setVolume, int (*)(void *, double), "ai_TalkerConfig_setVolume")                                           \
    X(ai_TalkerConfig_setRate, int (*)(void *, double), "ai_TalkerConfig_setRate")                                               \
    X(ai_TalkerConfig_setPitch, int (*)(void *, double), "ai_TalkerConfig_setPitch")                                             \
    X(ai_TalkerConfig_setMasterVolume, int (*)(void *, double), "ai_TalkerConfig_setMasterVolume")                               \
    X(ai_TalkerConfig_setStyleColor, int (*)(void *, const char *), "ai_TalkerConfig_setStyleColor")                             \
    X(ai_TalkerConfig_setContext, int (*)(void *, unsigned int), "ai_TalkerConfig_setContext")                                   \
    X(ai_Talker_getStyleColorSize, int (*)(void *), "ai_Talker_getStyleColorSize")                                               \
    X(ai_Talker_getStyleColorLabel, __int64 (*)(void *, unsigned int, wchar_t *, size_t), "ai_Talker_getStyleColorLabel")
    DECLARE_API_STRUCT
#undef AI_FNS
    Api api;
    void *talker = nullptr;
    bool hasloadvoice = false;
    std::string lastlang;
    void *cfg = nullptr;

    aitalk_engine_impl(const Settings &settings);
    ~aitalk_engine_impl();
    void SetVoice(Settings &settings);
    std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text);
};

static constexpr size_t BUFFER_SAMPLES = 8192;
struct SynthState
{
    alignas(64) int16_t buf[BUFFER_SAMPLES];
    std::vector<int16_t> pcm;
    CEvent event;
};
static int CALLBACK_TTS_HANDLER(void *userData, TtsEvent *event)
{
    SynthState *st = (SynthState *)userData;
    if (!event)
        return 0;
    char *ev = (char *)event;
    int code = event->code;      // ev+0
    void *dataPtr = event->data; // ev+8 (指向 bufdesc)
    switch (code)
    {
    case AI_TTS_EVENT_BUFREQ:
    {
        *(void **)(ev - 0x20) = st->buf;
        *(uint64_t *)(ev - 0x18) = sizeof(st->buf); // 字节, >=2
        *(uint64_t *)(ev - 0x10) = 0;               // f2 = 0  (★ 勿填非 0)
        *(uint64_t *)(ev - 0x08) = 0;               // f3 = 0
        break;
    }
    case AI_TTS_EVENT_BUFDONE:
    {
        void *bp = *(void **)(ev + 0x10);
        if (bp)
        {
            st->pcm.push_back(((int16_t *)bp)[0]);
        }
        break;
    }
    case AI_TTS_EVENT_END:
        st->event.Set();
        break;
    default:
        break; // BEGIN / BEGIN_SENTENCE / END_SENTENCE / MARKER: 不处理
    }
    return 0;
}

aitalk_engine_impl::aitalk_engine_impl(const Settings &settings)
{
    if (!api.load(settings.dllpath.c_str()))
        throw std::runtime_error("load dll failed");
    TTSConfig config{};
    int r = api.ai_ttsLibraryConfigInitialize(&config);
    static uint32_t logCfg[2] = {3, 0};
    config.field[1] = (uint64_t)(uintptr_t)&logCfg;
    r = api.ai_ttsLibraryInitialize(&config);
    if (r != 0)
        throw std::runtime_error(errMeaning(r));
    if (api.ai_ttsLogSetLevel)
        api.ai_ttsLogSetLevel(2);
    r = api.ai_ttsLibraryAuthenticate(settings.license_path.c_str(), settings.seed.c_str(), settings.product.c_str());
    if (r != 0)
        throw std::runtime_error(errMeaning(r));
    talker = api.ai_Talker_new();
    if (!talker)
        throw std::runtime_error("ai_Talker_new");

    cfg = api.ai_TalkerConfig_new();
    api.ai_TalkerConfig_setContext(cfg, 0);
    api.ai_TalkerConfig_setMasterVolume(cfg, 2.0);
    api.ai_TalkerConfig_setVolume(cfg, 2.0);
}

aitalk_engine_impl::~aitalk_engine_impl()
{
    if (cfg)
        api.ai_TalkerConfig_delete(talker);
    if (talker)
        api.ai_Talker_delete(talker);
    api.ai_ttsLibraryTerminate();
}

void aitalk_engine_impl::SetVoice(Settings &settings)
{
    int r;
    if (settings.language_dir != lastlang)
    {
        lastlang = settings.language_dir;
        api.ai_Talker_unloadAllLangDic(talker);
        r = api.ai_Talker_loadLangDic(talker, settings.seed.c_str(), (std::filesystem::path(settings.language_dir) / (settings.language + ".aildic")).string().c_str(), 1);
        if (r != 0)
            throw std::runtime_error(errMeaning(r));
        r = api.ai_Talker_selectLangDic(talker, settings.seed.c_str());
    }
    if (hasloadvoice)
        api.ai_Talker_unloadAllVoiceDic(talker);
    hasloadvoice = true;

    r = api.ai_Talker_loadVoiceDic(talker, settings.seed.c_str(), (std::filesystem::path(settings.voice_dir) / (settings.voice_name + ".aivdic")).string().c_str(), 1, (std::filesystem::path(settings.voice_dir) / ("voice.lic")).string().c_str());
    if (r != 0)
        throw std::runtime_error(errMeaning(r));
    r = api.ai_Talker_selectVoiceDic(talker, settings.seed.c_str());
    int fs = api.ai_Talker_getVoiceFs(talker);
    settings.frequency = fs > 0 ? fs : settings.frequency;

    int nStyle = api.ai_Talker_getStyleColorSize(talker);
    if (nStyle > 0)
    {
        wchar_t wbuf[256] = {};
        api.ai_Talker_getStyleColorLabel(talker, 0, wbuf, 256);
        std::string styleKey = WideStringToString(wbuf);
        api.ai_TalkerConfig_setStyleColor(cfg, styleKey.c_str());
    }
}

std::vector<int16_t> aitalk_engine_impl::Speek(float _rate, float _pitch, const std::string &text)
{
    api.ai_TalkerConfig_setRate(cfg, _rate);
    api.ai_TalkerConfig_setPitch(cfg, _pitch);
    api.ai_Talker_setDefaultConfig(talker, cfg);

    SynthState state;
    state.event.Create(NULL, FALSE, FALSE, NULL);
    void *sink = api.ai_TtsCallbackSink_new(&CALLBACK_TTS_HANDLER, &state);
    if (!sink)
        throw std::runtime_error("ai_TtsCallbackSink_new");
    int r = api.ai_Talker_setSink(talker, sink);
    void *imkana = api.ai_TtsImKana_new();
    unsigned int encoding = 0; // 0=UTF-8 1=Shift_JIS 2=EUC-JP (若日文乱码改 1)
    r = api.ai_Talker_compileToImkana(talker, imkana, text.c_str(), encoding);
    if (r != 0)
        throw std::runtime_error(errMeaning(r));
    r = api.ai_Talker_talkByImKana(talker, imkana);
    if (r != 0)
        throw std::runtime_error(errMeaning(r));
    if (imkana)
        api.ai_TtsImKana_delete(imkana);
    WaitForSingleObject(state.event, INFINITE);
    api.ai_TtsCallbackSink_delete(sink);
    return std::move(state.pcm);
}

aitalk_engine::aitalk_engine(const Settings &settings)
{
    pimpl = new aitalk_engine_impl(settings);
}

aitalk_engine::~aitalk_engine()
{
    if (pimpl)
        delete pimpl;
}

void aitalk_engine::SetVoice(Settings &settings)
{
    pimpl->SetVoice(settings);
}

std::vector<int16_t> aitalk_engine::Speek(float _rate, float _pitch, const std::string &text)
{
    return pimpl->Speek(_rate, _pitch, text);
}
