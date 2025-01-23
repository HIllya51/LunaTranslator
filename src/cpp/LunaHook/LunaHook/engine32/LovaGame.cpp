#include "LovaGame.h"

bool LovaGame::attach_function()
{
  return false;
#if 0 
        /** 7/19/2015: Game engine specific for http://lova.jp
 *
 *  No idea why hooking to this place will crash the game.
 *
 *  Debugging method:
 *  - Find text in UTF8/UTF16
 *    There is one UTF8 matched, and 2 UTF16
 *  - Use virtual machine to find where UTF8 is MODIFIED
 *    It is modified in msvcrt
 *  - Backtrack the stack to find where text is accessed in main module
 *
 *  Base addr = 05f0000
 *
 *  012FF246   C64418 08 00     MOV BYTE PTR DS:[EAX+EBX+0x8],0x0
 *  012FF24B   C740 04 01000000 MOV DWORD PTR DS:[EAX+0x4],0x1
 *  012FF252   8918             MOV DWORD PTR DS:[EAX],EBX
 *  012FF254   8BF0             MOV ESI,EAX
 *  012FF256   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  012FF259   53               PUSH EBX
 *  012FF25A   50               PUSH EAX
 *  012FF25B   8D4E 08          LEA ECX,DWORD PTR DS:[ESI+0x8]
 *  012FF25E   51               PUSH ECX
 *  012FF25F   E8 CEAE2A00      CALL .015AA132                           ; JMP to msvcr100.memcpy, copied here
 *  012FF264   8B07             MOV EAX,DWORD PTR DS:[EDI]
 *  012FF266   83E0 03          AND EAX,0x3
 *  012FF269   0BF0             OR ESI,EAX
 *  012FF26B   83C4 0C          ADD ESP,0xC
 *  012FF26E   8937             MOV DWORD PTR DS:[EDI],ESI
 *  012FF270   8B75 FC          MOV ESI,DWORD PTR SS:[EBP-0x4]
 */ 
 
  ULONG processStartAddress, processStopAddress;
  if (!FillRange(processName,&startAddress, &stopAddress)) { // need accurate stopAddress
    ConsoleOutput("LOVA: failed to get memory range");
    return false;
  }

  const BYTE bytes[] = {
    0xC6,0x44,0x18, 0x08, 0x00,           // 012FF246   C64418 08 00     MOV BYTE PTR DS:[EAX+EBX+0x8],0x0
    0xC7,0x40, 0x04, 0x01,0x00,0x00,0x00, // 012FF24B   C740 04 01000000 MOV DWORD PTR DS:[EAX+0x4],0x1
    0x89,0x18,                            // 012FF252   8918             MOV DWORD PTR DS:[EAX],EBX
    0x8B,0xF0,                            // 012FF254   8BF0             MOV ESI,EAX
    0x8B,0x45, 0x08,                      // 012FF256   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
    0x53,                                 // 012FF259   53               PUSH EBX
    0x50,                                 // 012FF25A   50               PUSH EAX
    0x8D,0x4E, 0x08,                      // 012FF25B   8D4E 08          LEA ECX,DWORD PTR DS:[ESI+0x8]
    0x51,                                 // 012FF25E   51               PUSH ECX
    0xE8 //CEAE2A00                       // 012FF25F   E8 CEAE2A00      CALL .015AA132                           ; JMP to msvcr100.memcpy, copied here
  };
  enum { addr_offset = sizeof(bytes) - 1 };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("LOVA: could not find instruction pattern");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  //hp.text_fun = SpecialGameHookLova;
  hp.offset=stackoffset(2); // source in arg2
  hp.type = USING_STRING|RELATIVE_SPLIT;
  ConsoleOutput("INSERT LOVA");
  return NewHook(hp, "LOVA");
#endif
}