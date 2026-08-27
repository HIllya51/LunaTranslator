
#include "engines.h"
#include "aitalk-sdk/core.h"

struct AITalk_SDK_impl
{
#define AI_FNS(X)                                                                                                                                                                                \
    X(initialize, AITalkReturnCode (*)(), "AITalk_Core_initialize")                                                                                                                              \
    X(finalize, AITalkReturnCode (*)(), "AITalk_Core_finalize")                                                                                                                                  \
    X(authenticate, AITalkReturnCode (*)(), "AITalk_Core_authenticate")                                                                                                                          \
    X(isBusy, AITalkReturnCode (*)(AITalk_Core_Tts *), "AITalk_Core_Tts_isBusy")                                                                                                                 \
    X(EngineLicense_setPath, AITalkReturnCode (*)(const char *), "AITalk_Core_EngineLicense_setPath")                                                                                            \
    X(EngineLicense_setCode, AITalkReturnCode (*)(const char *), "AITalk_Core_EngineLicense_setCode")                                                                                            \
    X(EngineLicense_setValue, AITalkReturnCode (*)(AITalk_Core_EngineLicenseId, const char *), "AITalk_Core_EngineLicense_setValue")                                                             \
    X(Tts_new, AITalkReturnCode (*)(AITalk_Core_Tts **), "AITalk_Core_Tts_new")                                                                                                                  \
    X(Tts_delete, AITalkReturnCode (*)(AITalk_Core_Tts *), "AITalk_Core_Tts_delete")                                                                                                             \
    X(Tts_putKeyValue, AITalkReturnCode (*)(AITalk_Core_Tts *, AITalk_Core_TtsId, const char *, AITalkMixedType), "AITalk_Core_Tts_putKeyValue")                                                 \
    X(Tts_hasKey, AITalkReturnCode (*)(AITalk_Core_Tts * ptr, const AITalk_Core_TtsId id, const char *key), "AITalk_Core_Tts_hasKey")                                                            \
    X(Tts_deleteKey, AITalkReturnCode (*)(AITalk_Core_Tts *, AITalk_Core_TtsId, const char *), "AITalk_Core_Tts_deleteKey")                                                                      \
    X(Tts_selectDefaultKey, AITalkReturnCode (*)(AITalk_Core_Tts *, AITalk_Core_TtsId, const char *), "AITalk_Core_Tts_selectDefaultKey")                                                        \
    X(Tts_run, AITalkReturnCode (*)(AITalk_Core_Tts *, const char *, AITalk_Core_TtsOutCallback, void *), "AITalk_Core_Tts_run")                                                                 \
    X(Tts_generateAIKanaContainer, AITalkReturnCode (*)(AITalk_Core_Tts *, AITalk_Core_AIKanaContainer **, const char *, AITalk_TextEncodingsId), "AITalk_Core_Tts_generateAIKanaContainer")     \
    X(AIKanaContainer_getAIKana, AITalkReturnCode (*)(AITalk_Core_AIKanaContainer *, const char **, size_t *const), "AITalk_Core_AIKanaContainer_getAIKana")                                     \
    X(AIKanaContainer_delete, AITalkReturnCode (*)(AITalk_Core_AIKanaContainer *), "AITalk_Core_AIKanaContainer_delete")                                                                         \
    X(CallbackSelector_new, AITalkReturnCode (*)(AITalk_Core_CallbackSelector **), "AITalk_Core_CallbackSelector_new")                                                                           \
    X(CallbackSelector_delete, AITalkReturnCode (*)(AITalk_Core_CallbackSelector *), "AITalk_Core_CallbackSelector_delete")                                                                      \
    X(CallbackSelector_putValue, AITalkReturnCode (*)(AITalk_Core_CallbackSelector *, AITalk_Core_CallbackSelector_CallbackId, void *), "AITalk_Core_CallbackSelector_putValue")                 \
    X(CallbackSelector_select, AITalkReturnCode (*)(AITalk_Core_CallbackSelector *, void *, AITalk_Core_TtsOutEventId, void *), "AITalk_Core_CallbackSelector_select")                           \
    X(TtsParameter_new, AITalkReturnCode (*)(AITalk_Core_TtsParameter **), "AITalk_Core_TtsParameter_new")                                                                                       \
    X(TtsParameter_putKeyValue, AITalkReturnCode (*)(AITalk_Core_TtsParameter *, const AITalk_Core_TtsParameterId, const char *, const AITalkMixedType), "AITalk_Core_TtsParameter_putKeyValue") \
    X(TtsParameter_delete, AITalkReturnCode (*)(AITalk_Core_TtsParameter *), "AITalk_Core_TtsParameter_delete")                                                                                  \
    X(PresetSet_new, AITalkReturnCode (*)(AITalk_Core_PresetSet **), "AITalk_Core_PresetSet_new")                                                                                                \
    X(PresetSet_delete, AITalkReturnCode (*)(AITalk_Core_PresetSet *), "AITalk_Core_PresetSet_delete")                                                                                           \
    X(PresetSet_set, AITalkReturnCode (*)(AITalk_Core_PresetSet *, AITalkPresetSetId, AITalkMixedType), "AITalk_Core_PresetSet_set")
    DECLARE_API_STRUCT
#undef AI_FNS

    Api api;
    AITalk_Core_Tts *tts = nullptr;
    AITalk_Core_CallbackSelector *selector = nullptr;
    AITalk_Core_PresetSet *preset = nullptr;
    AITalk_Core_TtsParameter *param = nullptr;

    AITalk_SDK_impl(const Settings &settings);
    ~AITalk_SDK_impl();
    void SetVoice(Settings &settings);
    std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text);

    template <typename T>
    inline AITalkMixedType createdata(T value)
    {
        AITalkMixedType v;
        using U = std::decay_t<T>;
        if constexpr (std::is_same_v<U, float>)
            v.floating = value;
        else if constexpr (std::is_same_v<U, AITalk_TextEncodingsIdEnum>)
            v.int32 = value;
        else if constexpr (std::is_same_v<U, AITalk_Core_TtsParameter_ContextIdEnum>)
            v.int32 = value;
        else if constexpr (std::is_same_v<U, AITalk_TypeOfInputIdEnum>)
            v.int32 = value;
        else if constexpr (std::is_same_v<U, const char *>)
            v.str = value;
        else if constexpr (std::is_same_v<U, AITalk_Core_PresetSet *>)
            v.any = value;
        else if constexpr (std::is_same_v<U, AITalk_Core_TtsParameter *>)
            v.any = value;
        else
            static_assert(false, "unknow type");
        return v;
    }
    template <typename T>
    AITalkReturnCode putKV(AITalk_Core_TtsId id, const char *key, T path, bool existremove = false)
    {
        if (AITalkReturnCode_Ok == api.Tts_hasKey(tts, id, key))
        {
            if (!existremove)
                return AITalkReturnCode_Ok;
            auto r = api.Tts_deleteKey(tts, id, key);
            if (r != AITalkReturnCode_Ok)
                return r;
        }
        return api.Tts_putKeyValue(tts, id, key, createdata(path));
    };
    AITalkReturnCode select(AITalk_Core_TtsId id, const char *key)
    {
        return api.Tts_selectDefaultKey(tts, id, key);
    };
    template <typename T>
    bool loadAndSelect(AITalk_Core_TtsId id, const char *key, T path, bool existremove = false)
    {
        return putKV(id, key, path, existremove) == AITalkReturnCode_Ok && select(id, key) == AITalkReturnCode_Ok;
    };
};
struct Ctx
{
    AITalk_SDK_impl *pimpl;
    std::vector<int16_t> pcm;
    CEvent event;
};

// PCM scratch buffer handed to the engine on every Bufreq event. Reused across
// Bufreq/Bufdone pairs (after Bufdone the engine never touches it again).
static constexpr size_t AUDIO_BUF_BYTES = 0x20000; // 128 KiB -> 65536 int16 samples/block
static char g_audio_buf[AUDIO_BUF_BYTES];
// Marker scratch buffer (we ignore marker data, but the engine wants a buffer
// pointer in Bufreq rather than NULL).
static char g_marker_buf[0x10000];

// Bufreq: the engine asks for a buffer to fill. We hand out g_audio_buf and a
// marker scratch buffer (its contents are ignored).
extern "C" AITalkReturnCode bufreq_cb(void *user_data, char **audio_buffer,
                                      size_t *audio_buffer_size,
                                      char **marker_buffer, size_t *marker_buffer_size)
{
    (void)user_data;
    *audio_buffer = g_audio_buf;
    *audio_buffer_size = AUDIO_BUF_BYTES;
    *marker_buffer = g_marker_buf;
    *marker_buffer_size = sizeof(g_marker_buf);
    // NOTE: TtsOutCallback-family callbacks must report success with
    // AITalkReturnCode_CallbackSuccess (2000), NOT AITalkReturnCode_Ok (0).
    // Returning 0 is treated as a callback error -> UserCallbackError (-12).
    return AITalkReturnCode_CallbackSuccess;
}

// Bufdone: the engine has filled audio_buffer (audio_buffer_size bytes).
// Copy the int16 samples out into our vector.
extern "C" AITalkReturnCode bufdone_cb(void *user_data, char *audio_buffer,
                                       size_t audio_buffer_size,
                                       char *marker_buffer, size_t marker_buffer_size)
{
    Ctx *c = (Ctx *)user_data;
    (void)marker_buffer;
    (void)marker_buffer_size;
    const size_t max_samples = 6'000'000; // ~125 s @ 48 kHz
    size_t n = audio_buffer_size / sizeof(int16_t);
    if (c->pcm.size() + n > max_samples)
    {
        if (c->pcm.size() >= max_samples)
            return AITalkReturnCode_CallbackSuccess;
        n = max_samples - c->pcm.size();
    }
    const int16_t *s = (const int16_t *)audio_buffer;
    c->pcm.insert(c->pcm.end(), s, s + n);
    return AITalkReturnCode_CallbackSuccess;
}

// Top-level TtsOutCallback: forward EVERY event to the CallbackSelector. For
// events with no registered typed callback (Begin, BeginSentence, AIKana,
// Marker, EndSentence, End, ...) the selector itself returns CallbackSuccess
// (2000) — the engine's expected "acknowledged" signal — so we must not
// short-circuit those to AITalkReturnCode_Ok (0).
extern "C" AITalkReturnCode tts_out_cb(void *user_data, AITalk_Core_TtsOutEventId event_id, void *data)
{
    Ctx *c = (Ctx *)user_data;
    AITalkReturnCode r = c->pimpl->api.CallbackSelector_select(c->pimpl->selector, user_data, event_id, data);
    if (event_id == AITalk_Core_TtsOutEventId_End)
        c->event.Set();
    return r;
}

AITalk_SDK_impl::AITalk_SDK_impl(const Settings &settings)
{
    if (!api.load(settings.dllpath.c_str()))
        throw std::runtime_error{"load dll failed"};
    api.initialize();
    api.EngineLicense_setPath(settings.license_path.c_str());
    api.EngineLicense_setCode(settings.seed.c_str());
    api.EngineLicense_setValue(3, settings.product.c_str());
    AITalkReturnCode a = api.authenticate();
    if (a != AITalkReturnCode_Ok)
        throw std::runtime_error("authenticate");
    api.Tts_new(&tts);
    if (a != AITalkReturnCode_Ok)
        throw std::runtime_error("Tts_new");
    api.CallbackSelector_new(&selector);
    api.CallbackSelector_putValue(selector, AITalk_Core_CallbackSelector_CallbackId_Bufreq, (void *)bufreq_cb);
    api.CallbackSelector_putValue(selector, AITalk_Core_CallbackSelector_CallbackId_Bufdone, (void *)bufdone_cb);
    api.TtsParameter_new(&param);
    api.PresetSet_new(&preset);
    putKV(AITalk_Core_TtsId_InputEncoding, NULL, AITalk_TextEncodingsId_Utf8);
    api.TtsParameter_putKeyValue(param, AITalk_Core_TtsParameterId_MasterVolume, NULL, createdata(5.0f));
    api.TtsParameter_putKeyValue(param, AITalk_Core_TtsParameterId_Volume, NULL, createdata(5.0f));
}

AITalk_SDK_impl::~AITalk_SDK_impl()
{
    if (selector)
        api.CallbackSelector_delete(selector);
    if (tts)
        api.Tts_delete(tts);
    if (preset)
        api.PresetSet_delete(preset);
    if (param)
        api.TtsParameter_delete(param);
    api.finalize();
}

std::vector<int16_t> AITalk_SDK_impl::Speek(float _rate, float _pitch, const std::string &text)
{
    api.TtsParameter_putKeyValue(param, AITalk_Core_TtsParameterId_Rate, NULL, createdata(_rate));
    api.TtsParameter_putKeyValue(param, AITalk_Core_TtsParameterId_Pitch, NULL, createdata(_pitch));
    loadAndSelect(AITalk_Core_TtsId_TtsParameter, "key", param, true);
    api.PresetSet_set(preset, AITalkPresetSetId_TtsParameter, createdata(param));
    loadAndSelect(AITalk_Core_TtsId_PresetSet, "key", preset, true);

    Ctx ctx;
    ctx.pimpl = this;
    ctx.event.Create(NULL, FALSE, FALSE, NULL);
    api.Tts_run(tts, text.c_str(), tts_out_cb, &ctx);
    WaitForSingleObject(ctx.event, INFINITE);
    return std::move(ctx.pcm);
}

void AITalk_SDK_impl::SetVoice(Settings &settings)
{
    if (!loadAndSelect(AITalk_Core_TtsId_LanguageDictionary, settings.language.c_str(), (std::filesystem::path(settings.language_dir) / (settings.language + ".aildic")).string().c_str()))
        throw std::runtime_error("AITalk_Core_TtsId_LanguageDictionary");
    if (putKV(AITalk_Core_TtsId_VoiceDictionaryLicense, settings.voice_name.c_str(), (std::filesystem::path(settings.voice_dir) / "voice.lic").string().c_str()) != AITalkReturnCode_Ok)
        throw std::runtime_error("AITalk_Core_TtsId_VoiceDictionaryLicense");
    if (!loadAndSelect(AITalk_Core_TtsId_VoiceDictionary, settings.voice_name.c_str(), (std::filesystem::path(settings.voice_dir) / (settings.voice_name + ".aivdic")).string().c_str()))
        throw std::runtime_error("AITalk_Core_TtsId_VoiceDictionary");
}

AITalk_SDK::AITalk_SDK(const Settings &settings)
{
    pimpl = new AITalk_SDK_impl(settings);
}
AITalk_SDK::~AITalk_SDK()
{
    if (pimpl)
        delete pimpl;
}
std::vector<int16_t> AITalk_SDK::Speek(float _rate, float _pitch, const std::string &text)
{
    return pimpl->Speek(_rate, _pitch, text);
}
void AITalk_SDK::SetVoice(Settings &settings)
{
    pimpl->SetVoice(settings);
}
