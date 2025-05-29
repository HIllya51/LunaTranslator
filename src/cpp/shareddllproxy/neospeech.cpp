#include "../implsapi.hpp"
int neospeechlist(int argc, wchar_t *argv[])
{
    FILE *f = _wfopen(argv[1], L"wb");
    for (auto key : {10, 7})
    {
        auto speechs = SAPI::List(key);
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
    }
    fclose(f);
    return 0;
}
int neospeech(int argc, wchar_t *argv[])
{

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 16, argv[3]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 16);
    memset(mapview, 0, 1024 * 1024 * 16);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;
    wchar_t text[10000];
    DWORD _;
    while (true)
    {
        ZeroMemory(text, sizeof(text));
        int speed;
        if (!ReadFile(hPipe, (unsigned char *)&speed, 4, &_, NULL))
            break;
        int pitch;
        if (!ReadFile(hPipe, (unsigned char *)&pitch, 4, &_, NULL))
            break;
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        std::wstring content = text;
        int fsize;
        ZeroMemory(text, sizeof(text));
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        std::wstring hkey = text;
        ZeroMemory(text, sizeof(text));
        auto data = std::move(SAPI::Speak(content, hkey.c_str(), speed, pitch));
        if (data)
        {
            memcpy(mapview, data.value().data(), data.value().size());
            fsize = data.value().size();
            WriteFile(hPipe, &fsize, 4, &_, NULL);
        }
        else
        {
            fsize = 0;
            WriteFile(hPipe, &fsize, 4, &_, NULL);
        }
    }
    return 0;
}