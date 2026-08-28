#include "../implsapi.hpp"

DECLARE_API bool SAPI_Speak(const wchar_t *Content, LPCWSTR voiceid, int rate, int volume, int pitch, void (*cb)(byte *, size_t))
{
    if (auto &&_ = SAPI::Speak(Content, voiceid, rate, pitch, volume))
    {
        cb(_.value().data(), _.value().size());
        return true;
    }
    return false;
}

DECLARE_API void SAPI_List(void (*cb)(const wchar_t *, const wchar_t *))
{
    auto _list = SAPI::List();
    for (auto &&[id, name] : _list)
        cb(id.c_str(), name.c_str());
}