#include "GameMaker.h"

bool InsertGameMakerHook()
{

    /*
     * Sample games:
     *   VA-11 Hall A
     */
    const BYTE bytes[] = {
        0x85, 0xF6, // test esi,esi
        0x74, XX,   // je "VA-11 Hall A.exe"+D5014
        0x85, 0xC0, // test eax,eax
        0x74, XX,   // je "VA-11 Hall A.exe"+D5014
        0x50,       // push eax
        0x56        // push esi          << hook here
    };
    enum
    {
        addr_offset = sizeof(bytes) - 1
    };

    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
        ConsoleOutput("GameMaker: pattern not found");
        return false;
    }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING | NO_CONTEXT;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
        CharFilter(buffer, '#');
    };
    ConsoleOutput(" INSERT GameMaker");

    ConsoleOutput("GameMaker: use regex filter .+\\]");
    return NewHook(hp, "GameMaker");
}

bool GameMaker::attach_function()
{
    return InsertGameMakerHook();
}