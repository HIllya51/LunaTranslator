#ifndef AITalk_SDK_H
#define AITalk_SDK_H

#include "api_settings.h"
#include "abstract.hpp"
#include "aitalk_engine_func.h"

struct aitalk_engine : public Abstracttts
{
    aitalk_engine(const Settings &settings);
    virtual std::vector<int16_t> Speech(float _rate, float _pitch, const std::string &text) override;
    virtual ~aitalk_engine() override;
    virtual void setvoice(Settings &settings) override;

private:
    // ---------------- 函数指针表 ----------------
    struct Api
    {
        HMODULE dll = nullptr;
#define X(name) PFN_##name name = nullptr;
        X(ai_ttsLibraryConfigInitialize)
        X(ai_ttsLibraryInitialize)
        X(ai_ttsLibraryAuthenticate)
        X(ai_ttsLibraryUnauthenticate)
        X(ai_ttsLibraryTerminate)
        X(ai_ttsLogInitialize)
        X(ai_ttsLogSetLevel)
        X(ai_PathSet_new)
        X(ai_PathSet_add)
        X(ai_PathSet_delete)
        X(ai_Talker_new)
        X(ai_Talker_newEx)
        X(ai_Talker_delete)
        X(ai_Talker_setPathSet)
        X(ai_Talker_setSink)
        X(ai_Talker_setDefaultConfig)
        X(ai_Talker_getDefaultConfig)
        X(ai_Talker_loadLangDic)
        X(ai_Talker_loadVoiceDic)
        X(ai_Talker_unloadAllLangDic)
        X(ai_Talker_unloadAllVoiceDic)
        X(ai_Talker_selectLangDic)
        X(ai_Talker_selectVoiceDic)
        X(ai_Talker_getVoiceFs)
        X(ai_Talker_getVoiceName)
        X(ai_Talker_talk)
        X(ai_TtsImKana_new)
        X(ai_TtsImKana_delete)
        X(ai_Talker_compileToImkana)
        X(ai_Talker_talkByImKana)
        X(ai_TtsCallbackSink_new)
        X(ai_TtsCallbackSink_delete)
        X(ai_TalkerConfig_new)
        X(ai_TalkerConfig_delete)
        X(ai_TalkerConfig_setVolume)
        X(ai_TalkerConfig_setRate)
        X(ai_TalkerConfig_setPitch)
        X(ai_TalkerConfig_setMasterVolume)
        X(ai_TalkerConfig_setStyleColor)
        X(ai_TalkerConfig_setContext)
        X(ai_Talker_getStyleColorSize)
        X(ai_Talker_getStyleColorLabel)
#undef X

        bool load(const std::string &path)
        {
            dll = LoadLibraryA(path.c_str());
            if (!dll)
            {
                fprintf(stderr, "LoadLibrary 失败: %s (err=%lu)\n", path.c_str(), GetLastError());
                return false;
            }
#define X(name)                                    \
    name = (PFN_##name)GetProcAddress(dll, #name); \
    if (!name)                                     \
    {                                              \
        fprintf(stderr, "缺少导出: %s\n", #name);  \
        return false;                              \
    }
            X(ai_ttsLibraryConfigInitialize)
            X(ai_ttsLibraryInitialize)
            X(ai_ttsLibraryAuthenticate)
            X(ai_ttsLibraryUnauthenticate)
            X(ai_ttsLibraryTerminate)
            X(ai_ttsLogInitialize)
            X(ai_ttsLogSetLevel)
            X(ai_PathSet_new)
            X(ai_PathSet_add)
            X(ai_PathSet_delete)
            X(ai_Talker_new)
            X(ai_Talker_newEx)
            X(ai_Talker_delete)
            X(ai_Talker_setPathSet)
            X(ai_Talker_setSink)
            X(ai_Talker_setDefaultConfig)
            X(ai_Talker_getDefaultConfig)
            X(ai_Talker_loadLangDic)
            X(ai_Talker_loadVoiceDic)
            X(ai_Talker_unloadAllLangDic)
            X(ai_Talker_unloadAllVoiceDic)
            X(ai_Talker_selectLangDic)
            X(ai_Talker_selectVoiceDic)
            X(ai_Talker_getVoiceFs)
            X(ai_Talker_getVoiceName)
            X(ai_Talker_talk)
            X(ai_TtsImKana_new)
            X(ai_TtsImKana_delete)
            X(ai_Talker_compileToImkana)
            X(ai_Talker_talkByImKana)
            X(ai_TtsCallbackSink_new)
            X(ai_TtsCallbackSink_delete)
            X(ai_TalkerConfig_new)
            X(ai_TalkerConfig_delete)
            X(ai_TalkerConfig_setVolume)
            X(ai_TalkerConfig_setRate)
            X(ai_TalkerConfig_setPitch)
            X(ai_TalkerConfig_setMasterVolume)
            X(ai_TalkerConfig_setStyleColor)
            X(ai_TalkerConfig_setContext)
            X(ai_Talker_getStyleColorSize)
            X(ai_Talker_getStyleColorLabel)
#undef X
            return true;
        }
    };
    Api api;
    void *talker;
    bool hasloadvoice = false;
    std::string lastlang;
};
#endif
