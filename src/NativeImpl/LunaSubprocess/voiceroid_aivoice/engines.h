
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

#ifndef _WIN64
struct aitalked_impl;
struct aitalked : public Abstracttts
{
    aitalked(const Settings &settings);
    virtual std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text) override;
    virtual ~aitalked() override;
    virtual void SetVoice(Settings &settings) override;

private:
    aitalked_impl *pimpl;
};

#else
struct AITalk_SDK_impl;
struct AITalk_SDK : public Abstracttts
{
    AITalk_SDK(const Settings &settings);
    virtual std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text) override;
    virtual ~AITalk_SDK() override;
    virtual void SetVoice(Settings &settings) override;

private:
    AITalk_SDK_impl *pimpl;
};

struct aitalk_engine_impl;
struct aitalk_engine : public Abstracttts
{
    aitalk_engine(const Settings &settings);
    virtual std::vector<int16_t> Speek(float _rate, float _pitch, const std::string &text) override;
    virtual ~aitalk_engine() override;
    virtual void SetVoice(Settings &settings) override;

private:
    aitalk_engine_impl *pimpl;
};
#endif

inline Abstracttts *createruntime(const Settings &settings)
{
#ifndef _WIN64
    return new aitalked(settings);
#else
    if (std::filesystem::exists(std::filesystem::path(settings.dllpath).parent_path() / "AITalk_SDK.dll"))
        return new AITalk_SDK(settings);
    return new aitalk_engine(settings);
#endif
}