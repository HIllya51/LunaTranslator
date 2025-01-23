
extern "C"
{
    typedef DWORD(__stdcall *StartSession)(wchar_t *path, void *bufferStart, void *bufferStop, const wchar_t *app);
    typedef DWORD(__stdcall *OpenEngine)(int key);
    typedef DWORD(__stdcall *SimpleTransSentM)(int key, const wchar_t *fr, wchar_t *t, int, int);
    typedef DWORD(__stdcall *SetBasicDictPathW)(int key, const wchar_t *fr);
}

int kingsoftwmain(int argc, wchar_t *argv[])
{
    //_setmode(_fileno(stdout), _O_U16TEXT);
    // wchar_t path[] = L"C:\\dataH\\��ɽ����.2009.רҵ��\\FastAIT09_Setup.25269.4101\\GTS\\JapaneseSChinese\\DCT";
    wchar_t *path = argv[2];
    HMODULE h = LoadLibrary(argv[1]);
    enum
    {
        key = 0x4f4
    };
    if (h)
    {
        StartSession startSession = (StartSession)::GetProcAddress(h, "StartSession");
        OpenEngine openEngine = (OpenEngine)::GetProcAddress(h, "OpenEngine");
        SimpleTransSentM simpleTransSentM = (SimpleTransSentM)::GetProcAddress(h, "SimpleTransSentM");
        SetBasicDictPathW setBasicDictPathW = (SetBasicDictPathW)::GetProcAddress(h, "SetBasicDictPathW");

        enum
        {
            bufferSize = key
        };
        char buffer[bufferSize];
        int ret = startSession(path, buffer, buffer + bufferSize, L"DCT");

        ret = openEngine(key);
        ret = setBasicDictPathW(key, path);

        HANDLE hPipe = CreateNamedPipe(argv[3], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

        SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[4]));
        ConnectNamedPipe(hPipe, NULL);
        while (true)
        {
            wchar_t fr[1024] = {0};
            DWORD _;
            if (!ReadFile(hPipe, fr, 1024, &_, NULL))
                break;
            wchar_t to[0x400] = {};
            ret = simpleTransSentM(key, fr, to, 0x28, 0x4);
            WriteFile(hPipe, to, wcslen(to) * 2, &_, NULL);
        }
    }
    return 0;
}