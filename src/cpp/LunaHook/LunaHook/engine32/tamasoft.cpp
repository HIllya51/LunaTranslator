#include "TamaSoft.h"
namespace
{
    DECLARE_FUNCTION(fuck, EXPAND_BRACKETS(const char *));
}
bool TamaSoft::attach_function()
{
    BYTE bytes2[] = {
        0x8a, 0x45, 0x00,
        0xc7, XX, XX, XX, XX4,
        0x84, 0xc0,
        0x0f, 0x84, XX4,
        0x3c, 0x81,
        0x72, 0x04,
        0x3c, 0x9f,
        0x76, 0x10,
        0x3c, 0xe0,
        0x0f, 0x82, XX4,
        0x3c, 0xfc,
        0x0f, 0x87, XX4};
    BYTE bytes[] = {
        0x8a, 0x4d, 0x00,
        0x84, 0xc9,
        0x0f, 0x84, XX4,
        0x80, 0xf9, 0x81,
        0x72, 0x05,
        0x80, 0xf9, 0x9f,
        0x76, 0x12,
        0x80, 0xf9, 0xe0,
        0x0f, 0x82, XX4,
        0x80, 0xf9, 0xfc,
        0x0f, 0x87, XX4};
    bool succ = true;
    HookParam hp;
    hp.offset = regoffset(ebp);
    hp.type = USING_STRING | NO_CONTEXT;
    hp.address = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    { fuck(buffer->strA().c_str()); };
    succ &= NewHook(hp, "TamaSoft");
    hp.address = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
    succ &= NewHook(hp, "TamaSoft");
    hp.address = (uintptr_t)fuck;
    hp.offset = GETARG(1);
    hp.filter_fun = nullptr;
    succ &= NewHook(hp, "TamaSoft");
    return succ;
}