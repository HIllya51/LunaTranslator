#include "Suika2.h"

bool Suika2_msvcrt()
{
    auto msvcrt = GetModuleHandle(L"msvcrt.dll");
    if (msvcrt == 0)
        return 0;
    auto _strdup = GetProcAddress(msvcrt, "_strdup");
    if (_strdup == 0)
        return 0;
    HookParam hp;
    hp.address = (uintptr_t)_strdup;
    hp.type = USING_STRING | CODEC_UTF8;
    hp.offset = regoffset(rcx);
    return NewHook(hp, "Suika2_msvcrt");
}
bool Suika2::attach_function()
{
    auto _1 = Suika2_msvcrt();
    return _1;
}