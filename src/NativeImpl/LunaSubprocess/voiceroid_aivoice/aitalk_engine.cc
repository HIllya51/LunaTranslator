#include "aitalk_engine.h"

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
void aitalk_engine::setvoice(Settings &settings)
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
}
aitalk_engine::aitalk_engine(const Settings &settings)
{
    if (!api.load(settings.dllpath))
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
}

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
aitalk_engine::~aitalk_engine()
{
    api.ai_Talker_delete(talker);
    api.ai_ttsLibraryTerminate();
}
std::vector<int16_t> aitalk_engine::Speech(float _rate, float _pitch, const std::string &text)
{
    void *cfg = api.ai_TalkerConfig_new();
    int nStyle = api.ai_Talker_getStyleColorSize(talker);
    if (nStyle > 0)
    {
        wchar_t wbuf[256] = {};
        api.ai_Talker_getStyleColorLabel(talker, 0, wbuf, 256);
        std::string styleKey = WideStringToString(wbuf);
        api.ai_TalkerConfig_setStyleColor(cfg, styleKey.c_str());
    }
    api.ai_TalkerConfig_setContext(cfg, 0); // context 必须显式设, 否则是垃圾值
    api.ai_TalkerConfig_setMasterVolume(cfg, 2.0);
    api.ai_TalkerConfig_setVolume(cfg, 2.0);
    api.ai_TalkerConfig_setRate(cfg, _rate);
    api.ai_TalkerConfig_setPitch(cfg, _pitch);
    int r = api.ai_Talker_setDefaultConfig(talker, cfg);

    api.ai_TalkerConfig_delete(cfg);
    SynthState state;
    state.event.Create(NULL, FALSE, FALSE, NULL);
    void *sink = api.ai_TtsCallbackSink_new(&CALLBACK_TTS_HANDLER, &state);
    if (!sink)
        throw std::runtime_error("ai_TtsCallbackSink_new");
    r = api.ai_Talker_setSink(talker, sink);
    void *imkana = api.ai_TtsImKana_new();
    unsigned int encoding = 1; // 0=UTF-8 1=Shift_JIS 2=EUC-JP (若日文乱码改 1)
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
    return state.pcm;
}
