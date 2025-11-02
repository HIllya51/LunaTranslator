#include "RpgmXP.h"

bool InsertRpgmXPHook()
{

    /*
     * Sample games:
     * セントヘレナ(RJ137364)
     */
    HookParam hp;
    wcsncpy_s(hp.module, L"gdi32.dll", MAX_MODULE_SIZE - 1);
    strncpy_s(hp.function, "GetGlyphOutlineW", MAX_MODULE_SIZE - 1);
    hp.address = 0;
    hp.offset = stackoffset(2); // arg2
    hp.index = 0;
    hp.split = regoffset(esi);
    hp.split_index = 0;
    hp.type = CODEC_UTF16 | USING_SPLIT | MODULE_OFFSET | FUNCTION_OFFSET;
    ConsoleOutput(" INSERT RpgmXP");

    return NewHook(hp, "RpgmXP");
}

bool RpgmXP::attach_function()
{
    return InsertRpgmXPHook();
}