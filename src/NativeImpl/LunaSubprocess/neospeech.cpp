#include "../implsapi.hpp"
#include "pipehost.hpp"
int neospeechlist(int argc, wchar_t *argv[])
{
    FILE *f = _wfopen(argv[1], L"wb");
    auto speechs = SAPI::List();
    for (int i = 0; i < speechs.size(); i++)
    {
        if (speechs[i].second.substr(0, 2) == L"VW")
        {
            fwrite(speechs[i].first.c_str(), 1, speechs[i].first.size() * 2, f);
            fwrite(L"\n", 1, 2, f);
            fwrite(speechs[i].second.c_str(), 1, speechs[i].second.size() * 2, f);
            fwrite(L"\n", 1, 2, f);
        }
    }
    fclose(f);
    return 0;
}
int neospeech(int argc, wchar_t *argv[])
{
    lunasp::PipeHost host(argv[1], argv[2], argv[3]);
    if (!host.ok())
        return 0;
    wchar_t text[10000];
    while (true)
    {
        ZeroMemory(text, sizeof(text));
        int speed;
        if (!host.read(&speed, 4))
            break;
        int pitch;
        if (!host.read(&pitch, 4))
            break;
        if (!host.read(text, 10000 * 2))
            break;
        std::wstring content = text;
        int fsize;
        ZeroMemory(text, sizeof(text));
        if (!host.read(text, 10000 * 2))
            break;
        std::wstring hkey = text;
        ZeroMemory(text, sizeof(text));
        auto data = std::move(SAPI::Speak(content, hkey.c_str(), speed, pitch));
        if (data)
        {
            memcpy(host.mem(), data.value().data(), data.value().size());
            fsize = (int)data.value().size();
            host.write(&fsize, 4);
        }
        else
        {
            fsize = 0;
            host.write(&fsize, 4);
        }
    }
    return 0;
}