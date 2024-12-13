#include "littlecheese.h"

bool littlecheese::attach_function()
{
    // 黒と金の開かない鍵
    /*if ( a3 == 33088 )
        cmp     edx, 8140h*/
    const BYTE bytes81[] = {
        0x81, 0xFA, 0x40, 0x81, 0x00, 0x00, 0x75};
    auto addr = MemDbg::findBytes(bytes81, sizeof(bytes81), processStartAddress, processStopAddress);
    if (addr == 0)
        return false;
    const BYTE align[] = {0x83, 0xC4}; // add esp xxx
    addr = reverseFindBytes(align, sizeof(align), addr - 0x100, addr);
    if (addr == 0)
        return false;
    if (*(DWORD *)(addr - 4) == 0x55575653)
    {
        HookParam hp;
        hp.address = addr - 4;
        hp.offset = regoffset(ecx);
        hp.type = USING_CHAR | CODEC_ANSI_BE;
        return NewHook(hp, "littlecheese");
    }
    else
    {
        HookParam hp;
        hp.address = addr;
        hp.offset = regoffset(ecx);
        hp.split = regoffset(edx);
        hp.type = USING_CHAR | CODEC_ANSI_BE | NO_CONTEXT | USING_SPLIT;
        return NewHook(hp, "littlecheese");
    }
}