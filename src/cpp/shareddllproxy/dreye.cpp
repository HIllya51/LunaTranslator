extern "C"
{
    typedef int(__stdcall *MTInitCJ)(int);
    typedef int(__stdcall *TranTextFlowCJ)(char *src, char *dest, int, int);
}

int dreyewmain(int argc, wchar_t *argv[])
{
    SetCurrentDirectory(argv[1]);
    HMODULE h = LoadLibrary(argv[2]);
    /*wchar_t* apiinit = argv[3];
    wchar_t* apitrans = argv[4];*/
    if (h)
    {

        MTInitCJ _MTInitCJ;
        TranTextFlowCJ _TranTextFlowCJ;
        if (_wtoi(argv[3]) == 3 || _wtoi(argv[3]) == 10)
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitCJ");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowCJ"); // WStrToStr(apitrans, 936).c_str());
        }
        else
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitEC");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowEC"); // WStrToStr(apitrans, 936).c_str());
        }

        _MTInitCJ(_wtoi(argv[3]));

        HANDLE hPipe = CreateNamedPipe(argv[4], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

        SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[5]));
        if (!ConnectNamedPipe(hPipe, NULL))
            return 0;
        while (true)
        {
            char src[4096] = {0};
            char buffer[3000] = {0};
            DWORD _;
            if (!ReadFile(hPipe, src, 4096, &_, NULL))
                break;

            _TranTextFlowCJ(src, buffer, 3000, _wtoi(argv[3]));
            // MessageBoxW(0, StringToWideString(src,932).c_str(),L"", 0);
            StringToWideString(src, 932);
            WriteFile(hPipe, buffer, strlen(buffer), &_, NULL);
        }
    }
    return 0;
}