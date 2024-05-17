
#include "define.h"
#include "cinterface.h"
bool _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume, int *length, char **buffer);

std::vector<std::wstring> _List(const wchar_t *token);

namespace SAPI
{
    bool Speak(std::wstring &Content, int version, int voiceid, int rate, int volume, int *length, char **buffer);
    std::vector<std::wstring> List(int version);
    constexpr wchar_t SPCAT_VOICES_7[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices";
    constexpr wchar_t SPCAT_VOICES_10[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices";
};

bool SAPI::Speak(std::wstring &Content, int version, int voiceid, int rate, int volume, int *length, char **buffer)
{
    if (version == 7)
    {
        return _Speak(Content, SPCAT_VOICES_7, voiceid, rate, volume, length, buffer);
    }
    else if (version == 10)
    {
        return _Speak(Content, SPCAT_VOICES_10, voiceid, rate, volume, length, buffer);
    }
    else
    {
        return false;
    }
}
std::vector<std::wstring> SAPI::List(int version)
{
    if (version == 7)
    {
        return _List(SPCAT_VOICES_7);
    }
    else if (version == 10)
    {
        return _List(SPCAT_VOICES_10);
    }
    else
    {
        return {};
    }
}

DECLARE bool SAPI_Speak(const wchar_t *Content, int version, int voiceid, int rate, int volume, int *length, char **buffer)
{
    auto _c = std::wstring(Content);
    return SAPI::Speak(_c, version, voiceid, rate, volume, length, buffer);
}

wchar_t **SAPI_List(int version, size_t *num)
{
    auto _list = SAPI::List(version);
    *num = _list.size();
    return vecwstr2c(_list);
}