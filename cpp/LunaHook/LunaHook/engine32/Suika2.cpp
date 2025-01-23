#include "Suika2.h"
// 灰翼のロードピス
bool Suika2_msvcrt()
{
    auto msvcrt = GetModuleHandle(L"msvcrt.dll");
    if (msvcrt == 0)
        return 0;
    auto _strdup = GetProcAddress(msvcrt, "_strdup");
    if (_strdup == 0)
        return 0;
    HookParam hp;
    hp.address = (DWORD)_strdup;
    hp.type = USING_STRING | CODEC_UTF8;
    hp.offset = stackoffset(1);
    return NewHook(hp, "Suika2_msvcrt");
}
bool Suika2_06x()
{
    char _s[] = R"(\#{%06x}%s\#{%06x}%s)";
    auto a06xS06xS = MemDbg::findBytes(_s, sizeof(_s), processStartAddress, processStopAddress);
    if (a06xS06xS == 0)
        return 0;
    auto movoff = MemDbg::findBytes(&a06xS06xS, 4, processStartAddress, processStopAddress);
    if (movoff == 0)
        return 0;
    BYTE funcstart[] = {
        0x55, 0x57, 0x56};
    auto func = reverseFindBytes(funcstart, sizeof(funcstart), movoff - 0x200, movoff);
    if (func == 0)
        return 0;
    HookParam hp;
    hp.address = func;
    hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
    hp.offset = stackoffset(2);
    return NewHook(hp, "Suika2_06x");
}
bool Suika2::attach_function()
{
    auto _1 = Suika2_msvcrt();
    auto _2 = Suika2_06x();
    return _1 || _2;
}