
#include "api_settings.h"

#define DLL_DECL(m, sig, exp) \
    using pfn_##m = sig;      \
    pfn_##m m = nullptr;
#define DLL_RESOLVE(m, sig, exp)                      \
    m = (pfn_##m)GetProcAddress(dll, exp);            \
    if (!m)                                           \
    {                                                 \
        fprintf(stderr, "missing export: %s\n", exp); \
        ok = false;                                   \
    }
#define DECLARE_API_STRUCT                                                                 \
    struct Api                                                                             \
    {                                                                                      \
        HMODULE dll = nullptr;                                                             \
        AI_FNS(DLL_DECL)                                                                   \
        bool load(const char *path)                                                        \
        {                                                                                  \
            dll = LoadLibraryA(path);                                                      \
            if (!dll)                                                                      \
            {                                                                              \
                fprintf(stderr, "LoadLibrary 失败: %s (err=%lu)\n", path, GetLastError()); \
                return false;                                                              \
            }                                                                              \
            bool ok = true;                                                                \
            AI_FNS(DLL_RESOLVE)                                                            \
            return ok;                                                                     \
        }                                                                                  \
    };

struct Abstracttts
{
    virtual std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text) = 0;
    virtual ~Abstracttts() = default;
    virtual void SetVoice(Settings &settings) = 0;
};

Abstracttts *create_aitalked(const Settings &settings);
#ifdef _WIN64
Abstracttts *create_AITalk_SDK(const Settings &settings);
Abstracttts *create_aitalk_engine(const Settings &settings);
#endif

inline Abstracttts *createruntime(const Settings &settings)
{
    switch (settings.apitype)
    {
    case APITYPE::aitalked:
        return create_aitalked(settings);
#ifdef _WIN64
    case APITYPE::AITalk_SDK:
        return create_AITalk_SDK(settings);
    case APITYPE::aitalk_engine:
        return create_aitalk_engine(settings);
#endif
    }
    return nullptr;
}