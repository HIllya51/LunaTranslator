std::optional<std::vector<byte>> _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume);
std::vector<std::wstring> _List(const wchar_t *token);
extern wchar_t SPCAT_VOICES_7[];
extern wchar_t SPCAT_VOICES_10[];
int neospeechlist(int argc, wchar_t *argv[])
{
    FILE *f = _wfopen(argv[1], L"wb");
    for (auto key : {SPCAT_VOICES_7, SPCAT_VOICES_10})
    {
        auto speechs = _List(key);
        for (int i = 0; i < speechs.size(); i++)
        {
            if (speechs[i].substr(0, 2) == L"VW")
            {
                fwrite(speechs[i].c_str(), 1, speechs[i].size() * 2, f);
                fwrite(L"\n", 1, 2, f);
                fwrite(key, 1, wcslen(key) * 2, f);
                fwrite(L"\n", 1, 2, f);
                auto idx = std::to_wstring(i);
                fwrite(idx.c_str(), 1, idx.size() * 2, f);
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
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        std::wstring content = text;
        int fsize;
        ZeroMemory(text, sizeof(text));
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        std::wstring hkey = text;
        int idx;
        if (!ReadFile(hPipe, &idx, 4, &_, NULL))
            break;
        ZeroMemory(text, sizeof(text));
        auto data = std::move(_Speak(content, hkey.c_str(), idx, speed, 100));
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