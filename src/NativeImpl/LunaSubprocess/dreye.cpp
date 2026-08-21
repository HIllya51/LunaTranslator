#include "pipehost.hpp"

extern "C"
{
    typedef int(__stdcall *MTInitCJ)(int);
    typedef int(__stdcall *TranTextFlowCJ)(char *src, char *dest, int, int);
}

int dreyewmain(int argc, wchar_t *argv[])
{
    SetCurrentDirectory(argv[3]);
    HMODULE h = LoadLibrary(argv[4]);
    /*wchar_t* apiinit = argv[3];
    wchar_t* apitrans = argv[4];*/
    if (h)
    {

        MTInitCJ _MTInitCJ;
        TranTextFlowCJ _TranTextFlowCJ;
        if (_wtoi(argv[5]) == 3 || _wtoi(argv[5]) == 10)
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitCJ");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowCJ"); // WStrToStr(apitrans, 936).c_str());
        }
        else
        {
            _MTInitCJ = (MTInitCJ)GetProcAddress(h, "MTInitEC");                   // WStrToStr(apiinit, 936).c_str());
            _TranTextFlowCJ = (TranTextFlowCJ)GetProcAddress(h, "TranTextFlowEC"); // WStrToStr(apitrans, 936).c_str());
        }

        if (!_MTInitCJ || !_TranTextFlowCJ)
            return 0;

        _MTInitCJ(_wtoi(argv[5]));

        lunasp::PipeHost host(argv[1], argv[2]);
        if (!host.ok())
            return 0;
        while (true)
        {
            char src[4096] = {0};
            char buffer[3000] = {0};
            if (!host.read(src, sizeof(src) - 1))
                break;

            _TranTextFlowCJ(src, buffer, 3000, _wtoi(argv[5]));
            host.write(buffer, strlen(buffer));
        }
    }
    return 0;
}