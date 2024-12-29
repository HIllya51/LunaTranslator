
std::optional<std::vector<byte>> _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume);
std::vector<std::wstring> _List(const wchar_t *token);
extern wchar_t SPCAT_VOICES_7[];
extern wchar_t SPCAT_VOICES_10[];
namespace SAPI
{

    std::vector<std::wstring> List(int version)
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
    std::optional<std::vector<byte>> Speak(std::wstring &Content, int version, int voiceid, int rate, int volume)
    {
        const wchar_t *_;
        switch (version)
        {
        case 7:
            _ = SPCAT_VOICES_7;
            break;
        case 10:
            _ = SPCAT_VOICES_10;
            break;
            return {};
        }
        return _Speak(Content, _, voiceid, rate, volume);
    }
};

DECLARE_API bool SAPI_Speak(const wchar_t *Content, int version, int voiceid, int rate, int volume, void (*cb)(byte *, size_t))
{
    auto _c = std::wstring(Content);
    if (auto _ = std::move(SAPI::Speak(_c, version, voiceid, rate, volume)))
    {
        cb(_.value().data(), _.value().size());
        return true;
    }
    return false;
}

DECLARE_API void SAPI_List(int version, void (*cb)(const wchar_t *))
{
    auto _list = SAPI::List(version);
    for (auto _ : _list)
        cb(_.c_str());
}