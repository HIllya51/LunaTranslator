#include "littlecheese.h"

bool littlecheese::attach_function()
{
    // 黒と金の開かない鍵
    /*if ( a3 == 33088 )
        cmp     edx, 8140h*/
    const BYTE bytes81[] = {
        0x81, 0xFA, 0x40, 0x81, 0x00, 0x00, 0x75};
    auto addr = MemDbg::findBytes(bytes81, sizeof(bytes81), processStartAddress, processStopAddress);
    if (!addr)
        return false;
    const BYTE align[] = {0x83, 0xC4}; // add esp xxx
    addr = reverseFindBytes(align, sizeof(align), addr - 0x100, addr);
    if (!addr)
        return false;
    HookParam hp;
    hp.offset = regoffset(ecx);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    };
    if (*(DWORD *)(addr - 4) == 0x55575653)
    {
        hp.address = addr - 4;
        hp.type = USING_CHAR | CODEC_ANSI_BE;
    }
    else
    {
        hp.address = addr;
        hp.split = regoffset(edx);
        hp.type = USING_CHAR | CODEC_ANSI_BE | NO_CONTEXT | USING_SPLIT;
    }
    return NewHook(hp, "littlecheese");
}