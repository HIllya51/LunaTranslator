std::optional<std::vector<byte>> _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume);

std::vector<std::wstring> _List(const wchar_t *token);
int neospeechlist(int argc, wchar_t *argv[])
{
    FILE *f = _wfopen(argv[1], L"wb");
    for (auto key : {L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices", L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices"})
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
    auto hkey = argv[4];
    auto idx = std::stoi(argv[5]);

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    auto handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, 1024 * 1024 * 10, argv[3]);

    auto mapview = (char *)MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, 1024 * 1024 * 10);
    memset(mapview, 0, 1024 * 1024 * 10);

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (ConnectNamedPipe(hPipe, NULL) != NULL)
    {
        DWORD len = 0;
    }
    int II = 0;
    while (true)
    {
        wchar_t text[10000];
        II += 1;
        DWORD _;
        int speed;
        if (!ReadFile(hPipe, (unsigned char *)&speed, 4, &_, NULL))
            break;
        if (!ReadFile(hPipe, (unsigned char *)text, 10000 * 2, &_, NULL))
            break;
        std::wstring content = text;
        int fsize;
        auto data = std::move(_Speak(content, hkey, idx, speed, 100));
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