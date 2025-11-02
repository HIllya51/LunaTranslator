#include "TamaokaSoft.h"
bool TamaokaSoft::attach_function()
{
    HookParam hp;
    hp.address = (DWORD)TextOutA;
    hp.offset = stackoffset(4);
    hp.split = stackoffset(4);
    hp.type = USING_STRING | USING_SPLIT;
    return NewHook(hp, "TamaokaSoft");
}