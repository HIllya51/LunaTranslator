#include "CisLugI.h"

bool CisLugI::attach_function()
{
    // int __cdecl common_tcsncpy_s<char>(_BYTE *a1, int a2, int a3, int a4)
    //  errno_t __cdecl strncpy_s(char *Destination, rsize_t SizeInBytes, const char *Source, rsize_t MaxCount)
    //  {
    //  return common_tcsncpy_s<char>(Destination, SizeInBytes, (int)Source, MaxCount);
    //  }
    BYTE sig[] = {
        0x8b,
        0xff,
        0x55,
        0x8b,
        0xec,
        0x51,
        0x8b,
        XX,
        0x14,
        0x8b,
        XX,
        0x08,
        0x56,
        0x85,
        XX,
        0x75,
        XX,
        0x85,
        XX,
        0x75,
        XX,
        0x39,
        XX,
        0x0c,
        0x75,
        XX,
        0x33,
        0xc0,
        0xeb,
        XX,
        0x85,
        XX,
        0x74,
        XX,
        0x8b,
        XX,
        0x0c,
        0x85,
        XX,
        0x74,
        XX,
        0x85,
        XX,
        0x75,
        XX,

    };
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
        return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING;
    hp.offset = stackoffset(3);

    return NewHook(hp, "CisLugI");
}