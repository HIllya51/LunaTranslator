#include "../implsapi.hpp"

DECLARE_API bool SAPI_Speak(const wchar_t *Content, LPCWSTR voiceid, int rate, int volume, int pitch, void (*cb)(byte *, size_t))
{
    auto _c = std::wstring(Content);
    if (auto _ = std::move(SAPI::Speak(_c, voiceid, rate, pitch, volume)))
    {
        cb(_.value().data(), _.value().size());
        return true;
    }
    return false;
}

DECLARE_API void SAPI_List(int version, void (*cb)(const wchar_t *, const wchar_t *))
{
    auto _list = SAPI::List(version);
    for (auto &&[id, name] : _list)
        cb(id.c_str(), name.c_str());
}