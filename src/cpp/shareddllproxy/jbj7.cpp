
#define CODEPAGE_JA 932
#define CODEPAGE_GB 936

#define CODEPAGE_BIG5 950

int jbjwmain(int argc, wchar_t *argv[])
{
    HANDLE hPipe = CreateNamedPipe(argv[2], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT, PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);

    // system("chcp 932");
    HMODULE module = LoadLibraryW(argv[1]);
    typedef int (*_JC_Transfer_Unicode)(int, UINT, UINT, int, int, LPCWSTR, LPWSTR, int &, LPWSTR, int &);
    typedef int(__cdecl * _DJC_OpenAllUserDic_Unicode)(LPWSTR, int unknown);
    auto JC_Transfer_Unicode = (_JC_Transfer_Unicode)GetProcAddress(module, "JC_Transfer_Unicode");
    auto DJC_OpenAllUserDic_Unicode = (_DJC_OpenAllUserDic_Unicode)GetProcAddress(module, "DJC_OpenAllUserDic_Unicode");

    int USERDIC_PATH_SIZE = 0x204;
    int MAX_USERDIC_COUNT = 3;
    int USERDIC_BUFFER_SIZE = USERDIC_PATH_SIZE * MAX_USERDIC_COUNT; // 1548, sizeof(wchar_t)
    wchar_t cache[1548] = {0};
    int __i = 0;

    for (int i = 4; i < argc; i++)
    {
        wchar_t _[MAX_PATH];
        wcscpy(_, argv[i]);
        wcscat(_, L".DIC");
        if (PathFileExistsW(_))
        {
            wcscpy(cache + __i * USERDIC_PATH_SIZE, argv[i]);
            __i++;
        }
    }
    DJC_OpenAllUserDic_Unicode(cache, 0);
    wchar_t *fr = new wchar_t[3000];
    wchar_t *to = new wchar_t[3000];
    wchar_t *buf = new wchar_t[3000];

    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[3]));
    if (!ConnectNamedPipe(hPipe, NULL))
        return 0;
    unsigned char intcache[4];
    while (true)
    {
        memset(fr, 0, 3000 * sizeof(wchar_t));
        memset(to, 0, 3000 * sizeof(wchar_t));
        memset(buf, 0, 3000 * sizeof(wchar_t));
        int a = 3000;
        int b = 3000;
        UINT code;
        DWORD _;

        ReadFile(hPipe, &code, 4, &_, NULL);

        if (!ReadFile(hPipe, (unsigned char *)fr, 6000, &_, NULL))
            break;

        JC_Transfer_Unicode(0, CODEPAGE_JA, code, 1, 1, fr, to, a, buf, b);

        WriteFile(hPipe, (unsigned char *)to, 2 * wcslen(to), &_, NULL);
    }

    return 0;
}