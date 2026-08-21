
#include "pipehost.hpp"

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
    wchar_t *path = argv[4];
    HMODULE h = LoadLibrary(argv[3]);
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

        lunasp::PipeHost host(argv[1], argv[2]);
        if (!host.ok())
            return 0;
        while (true)
        {
            wchar_t fr[1024] = {0};
            if (!host.read(fr, 1024))
                break;
            wchar_t to[0x400] = {};
            ret = simpleTransSentM(key, fr, to, 0x28, 0x4);
            host.write(to, wcslen(to) * 2);
        }
    }
    return 0;
}