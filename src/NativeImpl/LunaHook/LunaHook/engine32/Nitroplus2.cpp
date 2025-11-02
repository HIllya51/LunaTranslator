#include "Nitroplus2.h"

/**
 *  Jazzinghen 23/05/2020: Add TokyoNecro hook
 *
 *  [Nitroplus] 東京Necro 1.01 - Text boxes hook
 *
 *  Hook code: HS-14*8@B5420:TokyoNecro.exe
 *
 *  Debug method:
 *  Found memory location where the text was written, then used hardware break on write.
 *  After that found the function that writes the text in, found that the memory pointed
 *  contains more than just the text. Followed the call stack "upwards" until a function
 *  that handles only the text copy is found.
 *
 *  Disassembled code:
 *  TokyoNecro.exe+B5420 - 55                - push ebp                  ; place to hook
 *  TokyoNecro.exe+B5421 - 8B EC             - mov ebp,esp
 *  TokyoNecro.exe+B5423 - 6A FF             - push -01
 *  TokyoNecro.exe+B5425 - 68 E8613000       - push TokyoNecro.exe+1961E8
 *  TokyoNecro.exe+B542A - 64 A1 00000000    - mov eax,fs:[00000000]
 *  TokyoNecro.exe+B5430 - 50                - push eax
 *  TokyoNecro.exe+B5431 - 64 89 25 00000000 - mov fs:[00000000],esp
 *  TokyoNecro.exe+B5438 - 83 EC 1C          - sub esp,1C
 *  TokyoNecro.exe+B543B - 8B 55 08          - mov edx,[ebp+08]
 *  TokyoNecro.exe+B543E - 53                - push ebx
 *  TokyoNecro.exe+B543F - 56                - push esi
 *  TokyoNecro.exe+B5440 - 8B C2             - mov eax,edx
 *  TokyoNecro.exe+B5442 - 57                - push edi
 *  TokyoNecro.exe+B5443 - 8B D9             - mov ebx,ecx
 *  TokyoNecro.exe+B5445 - C7 45 EC 0F000000 - mov [ebp-14],0000000F
 *  TokyoNecro.exe+B544C - C7 45 E8 00000000 - mov [ebp-18],00000000
 *  TokyoNecro.exe+B5453 - C6 45 D8 00       - mov byte ptr [ebp-28],00
 *  TokyoNecro.exe+B5457 - 8D 70 01          - lea esi,[eax+01]
 *  TokyoNecro.exe+B545A - 8D 9B 00000000    - lea ebx,[ebx+00000000]
 *  TokyoNecro.exe+B5460 - 8A 08             - mov cl,[eax]
 *  TokyoNecro.exe+B5462 - 40                - inc eax
 *  TokyoNecro.exe+B5463 - 84 C9             - test cl,cl
 *  TokyoNecro.exe+B5465 - 75 F9             - jne TokyoNecro.exe+B5460
 *  TokyoNecro.exe+B5467 - 2B C6             - sub eax,esi
 *  TokyoNecro.exe+B5469 - 52                - push edx
 *  TokyoNecro.exe+B546A - 8B F8             - mov edi,eax                ▷ Search
 *  TokyoNecro.exe+B546C - 8D 75 D8          - lea esi,[ebp-28]           |
 *  TokyoNecro.exe+B546F - E8 6CE1F4FF       - call TokyoNecro.exe+35E0   ▷
 *
 *  Notes:
 *
 *  There's more data above due to the fact that the start of the function is very
 *  common and it was hooking a wrong function.
 *
 *  The text is contained into the memory location at [esp+04] when hooking the
 *  code at TokyoNecro.exe+B5420
 *
 *  If the game is hooked right at the main menu it will also catch the real time clock
 *  rendered there.
 */

namespace
{

  const BYTE funcSig[] = {0x55, 0x8b, 0xec};

  bool TextHook()
  {

    const BYTE bytecodes[] = {
        0x8B, 0xF8,                   // 8B F8             - mov edi,eax
        0x8D, 0x75, 0xD8,             // 8D 75 D8          - lea esi,[ebp-28]
        0xE8, 0x6C, 0xE1, 0xF4, 0xFF, // E8 6CE1F4FF       - call TokyoNecro.exe+35E0
    };
    ULONG addr = MemDbg::findBytes(bytecodes, sizeof(bytecodes), processStartAddress, processStopAddress);
    if (!addr)
    {
      ConsoleOutput("TokyoNecro: pattern not found");
      return false;
    }

    // Look for the start of the function
    const ULONG function_start = MemDbg::findEnclosingAlignedFunction(addr);
    if (memcmp((void *)function_start, funcSig, sizeof(funcSig)) != 0)
    {
      ConsoleOutput("TokyoNecro: function start not found");
      return false;
    }

    HookParam hp;
    hp.address = function_start;
    // The memory address is held at [ebp+08] at TokyoNecro.exe+B543B, meaning that at
    // the start of the function it's right above the stack pointer. Since there's no
    // way to do an operation on the value of a register BEFORE dereferencing (e.g.
    // (void*)(esp+4) instead of ((void*)esp)+4) we have to go up the stack instead of
    // using the data in the registers
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    ConsoleOutput("INSERT TokyoNecroText");
    return NewHook(hp, "TokyoNecroText");
  }

  /**
   * [Nitroplus] 東京Necro 1.01 - Database/Encyclopedia hook
   *
   * Hook code: HS4*@B5380:tokyonecro.exe
   *
   * TokyoNecro.exe+B5380 - 55                - push ebp                  ; Location to hook
   * TokyoNecro.exe+B5381 - 8B EC             - mov ebp,esp
   * TokyoNecro.exe+B5383 - 6A FF             - push -01
   * TokyoNecro.exe+B5385 - 68 E8618E00       - push TokyoNecro.exe+1961E8
   * TokyoNecro.exe+B538A - 64 A1 00000000    - mov eax,fs:[00000000]
   * TokyoNecro.exe+B5390 - 50                - push eax
   * TokyoNecro.exe+B5391 - 64 89 25 00000000 - mov fs:[00000000],esp
   * TokyoNecro.exe+B5398 - 83 EC 1C          - sub esp,1C
   * TokyoNecro.exe+B539B - 8B 55 08          - mov edx,[ebp+08]
   * TokyoNecro.exe+B539E - 53                - push ebx
   * TokyoNecro.exe+B539F - 56                - push esi
   * TokyoNecro.exe+B53A0 - 8B C2             - mov eax,edx
   * TokyoNecro.exe+B53A2 - 57                - push edi
   * TokyoNecro.exe+B53A3 - 8B D9             - mov ebx,ecx
   * TokyoNecro.exe+B53A5 - C7 45 EC 0F000000 - mov [ebp-14],0000000F
   * TokyoNecro.exe+B53AC - C7 45 E8 00000000 - mov [ebp-18],00000000
   * TokyoNecro.exe+B53B3 - C6 45 D8 00       - mov byte ptr [ebp-28],00
   * TokyoNecro.exe+B53B7 - 8D 70 01          - lea esi,[eax+01]
   * TokyoNecro.exe+B53BA - 8D 9B 00000000    - lea ebx,[ebx+00000000]
   * TokyoNecro.exe+B53C0 - 8A 08             - mov cl,[eax]
   * TokyoNecro.exe+B53C2 - 40                - inc eax
   * TokyoNecro.exe+B53C3 - 84 C9             - test cl,cl
   * TokyoNecro.exe+B53C5 - 75 F9             - jne TokyoNecro.exe+B53C0
   * TokyoNecro.exe+B53C7 - 2B C6             - sub eax,esi
   * TokyoNecro.exe+B53C9 - 52                - push edx
   * TokyoNecro.exe+B53CA - 8B F8             - mov edi,eax               ▷ Search
   * TokyoNecro.exe+B53CC - 8D 75 D8          - lea esi,[ebp-28]          |
   * TokyoNecro.exe+B53CF - E8 0CE2F4FF       - call TokyoNecro.exe+35E0  ▷
   *
   *
   */

  bool DatabaseHook()
  {
    const BYTE bytecodes[] = {
        0x8B, 0xF8,                   // 8B F8             - mov edi,eax
        0x8D, 0x75, 0xD8,             // 8D 75 D8          - lea esi,[ebp-28]
        0xE8, 0x0C, 0xE2, 0xF4, 0xFF, // E8 6CE1F4FF       - call TokyoNecro.exe+35E0
    };
    ULONG addr = MemDbg::findBytes(bytecodes, sizeof(bytecodes), processStartAddress, processStopAddress);
    if (!addr)
    {
      ConsoleOutput("TokyoNecro: pattern not found");
      return false;
    }

    // Look for the start of the function
    const ULONG function_start = MemDbg::findEnclosingAlignedFunction(addr);
    if (memcmp((void *)function_start, funcSig, sizeof(funcSig)) != 0)
    {
      ConsoleOutput("TokyoNecro: function start not found");
      return false;
    }

    HookParam hp;
    hp.address = function_start;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    return NewHook(hp, "TokyoNecroDatabase");
    ConsoleOutput("INSERT TokyoNecroDatabase");
  }

  bool InsertTokyoNecroHook()
  {
    DatabaseHook();
    return TextHook();
  }
} // namespace TokyoNecro

bool InsertNitroPlusHook()
{
  // 機神咆吼デモンベイン
  // みにくいモジカの子
  BYTE bytes[] = {
      0x55,
      0x8b, 0xec,
      0xff, 0x75, 0x10,
      0xff, 0x75, 0x0c,
      0xe8, XX, XX, 0xff, 0xff};
  BYTE bytes2[] = {
      0x55,
      0x8b, 0xec,
      0xff, 0x75, 0x0c,
      0xe8, XX, XX, 0xff, 0xff};
  auto addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  auto addr2 = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  ConsoleOutput("NitroPlus %p", addr1);
  ConsoleOutput("NitroPlus %p", addr2);
  if (addr1 == 0 && addr2 == 0)
    return false;
  auto succ = false;
  if (addr1)
  {
    HookParam hp;
    hp.address = addr1;
    hp.offset = stackoffset(2);
    hp.type = CODEC_UTF16;
    succ |= NewHook(hp, "NitroPlus");
  }
  if (addr2)
  {
    HookParam hp;
    hp.address = addr2;
    hp.offset = stackoffset(2);
    hp.type = CODEC_UTF16;
    succ |= NewHook(hp, "NitroPlus");
  }

  return succ;
}
namespace
{ // unnamed
  namespace ScenarioHook
  {

    /**
     *  Sample game: 凍京NECRO 体験版
     *  Debug step:
     *  1. find the text location that does not change
     *  2. Use Ollydbg to find where the text is modified
     *  3. Backtrack the stack to find proper caller.
     *
     *   Issues: It cannot extract character name.
     *
     *  File pattern: *.npk for new "Nitroplus" (p is lower case)
     *  btw, *.npa for old "Nitroplus"
     *
     *  00CF0E6A   CC               INT3
     *  00CF0E6B   CC               INT3
     *  00CF0E6C   CC               INT3
     *  00CF0E6D   CC               INT3
     *  00CF0E6E   CC               INT3
     *  00CF0E6F   CC               INT3
     *  00CF0E70   55               PUSH EBP	; jichi: text in arg1
     *  00CF0E71   8BEC             MOV EBP,ESP
     *  00CF0E73   6A FF            PUSH -0x1
     *  00CF0E75   68 184BDC00      PUSH .00DC4B18
     *  00CF0E7A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
     *  00CF0E80   50               PUSH EAX
     *  00CF0E81   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
     *  00CF0E88   83EC 1C          SUB ESP,0x1C
     *  00CF0E8B   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
     *  00CF0E8E   53               PUSH EBX
     *  00CF0E8F   56               PUSH ESI
     *  00CF0E90   8BC2             MOV EAX,EDX
     *  00CF0E92   57               PUSH EDI
     *  00CF0E93   8BD9             MOV EBX,ECX
     *  00CF0E95   C745 EC 0F000000 MOV DWORD PTR SS:[EBP-0x14],0xF
     *  00CF0E9C   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
     *  00CF0EA3   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
     *  00CF0EA7   8D70 01          LEA ESI,DWORD PTR DS:[EAX+0x1]
     *  00CF0EAA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  00CF0EB0   8A08             MOV CL,BYTE PTR DS:[EAX]
     *  00CF0EB2   40               INC EAX
     *  00CF0EB3   84C9             TEST CL,CL
     *  00CF0EB5  ^75 F9            JNZ SHORT .00CF0EB0
     *  00CF0EB7   2BC6             SUB EAX,ESI
     *  00CF0EB9   52               PUSH EDX
     *  00CF0EBA   8BF8             MOV EDI,EAX
     *  00CF0EBC   8D75 D8          LEA ESI,DWORD PTR SS:[EBP-0x28]
     *  00CF0EBF   E8 0C0DF5FF      CALL .00C41BD0
     *  00CF0EC4   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0	; jichi: pattern start
     *  00CF0ECB   8B8B 84030000    MOV ECX,DWORD PTR DS:[EBX+0x384]
     *  00CF0ED1   8B01             MOV EAX,DWORD PTR DS:[ECX]
     *  00CF0ED3   8B40 60          MOV EAX,DWORD PTR DS:[EAX+0x60]
     *  00CF0ED6   8BD6             MOV EDX,ESI
     *  00CF0ED8   52               PUSH EDX
     *  00CF0ED9   FFD0             CALL EAX   ;jichi: called here  .00CAEF00
     *  00CF0EDB   837D EC 10       CMP DWORD PTR SS:[EBP-0x14],0x10
     *  00CF0EDF   5F               POP EDI
     *  00CF0EE0   5E               POP ESI
     *  00CF0EE1   5B               POP EBX
     *  00CF0EE2   72 0C            JB SHORT .00CF0EF0
     *  00CF0EE4   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
     *  00CF0EE7   51               PUSH ECX
     *  00CF0EE8   E8 ED060B00      CALL .00DA15DA
     *  00CF0EED   83C4 04          ADD ESP,0x4
     *  00CF0EF0   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
     *  00CF0EF3   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  00CF0EFA   8BE5             MOV ESP,EBP
     *  00CF0EFC   5D               POP EBP
     *  00CF0EFD   C2 0400          RETN 0x4
     *  00CF0F00   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
     *  00CF0F06   8B01             MOV EAX,DWORD PTR DS:[ECX]
     *  00CF0F08   8B50 64          MOV EDX,DWORD PTR DS:[EAX+0x64]
     *  00CF0F0B   FFE2             JMP EDX
     *  00CF0F0D   CC               INT3
     *  00CF0F0E   CC               INT3
     *  00CF0F0F   CC               INT3
     *  00CF0F10   55               PUSH EBP
     *  00CF0F11   8BEC             MOV EBP,ESP
     *  00CF0F13   83EC 10          SUB ESP,0x10
     *  00CF0F16   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
     *  00CF0F1C   8B01             MOV EAX,DWORD PTR DS:[ECX]
     *  00CF0F1E   8B80 A0000000    MOV EAX,DWORD PTR DS:[EAX+0xA0]
     *  00CF0F24   8D55 F0          LEA EDX,DWORD PTR SS:[EBP-0x10]
     *  00CF0F27   52               PUSH EDX
     *  00CF0F28   FFD0             CALL EAX
     *  00CF0F2A   8D4D F8          LEA ECX,DWORD PTR SS:[EBP-0x8]
     *  00CF0F2D   FF15 7482DC00    CALL DWORD PTR DS:[0xDC8274]                                                          ; _1nput1_.1007E880
     *  00CF0F33   66:0F6E45 F0     MOVD MM0,DWORD PTR SS:[EBP-0x10]
     *  00CF0F38   66:0F6E4D F4     MOVD MM1,DWORD PTR SS:[EBP-0xC]
     *  00CF0F3D   8B0D E046E000    MOV ECX,DWORD PTR DS:[0xE046E0]
     *  00CF0F43   0F5B             ???                                                                                   ; Unknown command
     *  00CF0F45   C0F3 0F          SAL BL,0xF
     *  00CF0F48   1145 F8          ADC DWORD PTR SS:[EBP-0x8],EAX
     *  00CF0F4B   0F5B             ???                                                                                   ; Unknown command
     *  00CF0F4D   C9               LEAVE
     *  00CF0F4E   F3:0F114D FC     MOVSS DWORD PTR SS:[EBP-0x4],XMM1
     *  00CF0F53   8B41 54          MOV EAX,DWORD PTR DS:[ECX+0x54]
     *  00CF0F56   F3:0F1180 500100>MOVSS DWORD PTR DS:[EAX+0x150],XMM0
     *  00CF0F5E   F3:0F1045 FC     MOVSS XMM0,DWORD PTR SS:[EBP-0x4]
     *  00CF0F63   F3:0F1180 540100>MOVSS DWORD PTR DS:[EAX+0x154],XMM0
     *  00CF0F6B   0F57C0           XORPS XMM0,XMM0
     *  00CF0F6E   F3:0F1180 580100>MOVSS DWORD PTR DS:[EAX+0x158],XMM0
     *  00CF0F76   F3:0F1180 5C0100>MOVSS DWORD PTR DS:[EAX+0x15C],XMM0
     *  00CF0F7E   8BE5             MOV ESP,EBP
     *  00CF0F80   5D               POP EBP
     *  00CF0F81   C3               RETN
     *  00CF0F82   CC               INT3
     *  00CF0F83   CC               INT3
     *  00CF0F84   CC               INT3
     *  00CF0F85   CC               INT3
     *  00CF0F86   CC               INT3
     *  00CF0F87   CC               INT3
     *  00CF0F88   CC               INT3
     *  00CF0F89   CC               INT3
     *  00CF0F8A   CC               INT3
     *  00CF0F8B   CC               INT3
     *  00CF0F8C   CC               INT3
     *
     *  If the function does not work, here's the common function that performing strcpy
     *  00DA8E8A   CC               INT3
     *  00DA8E8B   CC               INT3
     *  00DA8E8C   CC               INT3
     *  00DA8E8D   CC               INT3
     *  00DA8E8E   CC               INT3
     *  00DA8E8F   CC               INT3
     *  00DA8E90   55               PUSH EBP
     *  00DA8E91   8BEC             MOV EBP,ESP
     *  00DA8E93   57               PUSH EDI
     *  00DA8E94   56               PUSH ESI
     *  00DA8E95   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
     *  00DA8E98   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
     *  00DA8E9B   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
     *  00DA8E9E   8BC1             MOV EAX,ECX
     *  00DA8EA0   8BD1             MOV EDX,ECX
     *  00DA8EA2   03C6             ADD EAX,ESI
     *  00DA8EA4   3BFE             CMP EDI,ESI
     *  00DA8EA6   76 08            JBE SHORT .00DA8EB0
     *  00DA8EA8   3BF8             CMP EDI,EAX
     *  00DA8EAA   0F82 A0010000    JB .00DA9050
     *  00DA8EB0   81F9 80000000    CMP ECX,0x80
     *  00DA8EB6   72 1C            JB SHORT .00DA8ED4
     *  00DA8EB8   833D D470E000 00 CMP DWORD PTR DS:[0xE070D4],0x0
     *  00DA8EBF   74 13            JE SHORT .00DA8ED4
     *  00DA8EC1   57               PUSH EDI
     *  00DA8EC2   56               PUSH ESI
     *  00DA8EC3   83E7 0F          AND EDI,0xF
     *  00DA8EC6   83E6 0F          AND ESI,0xF
     *  00DA8EC9   3BFE             CMP EDI,ESI
     *  00DA8ECB   5E               POP ESI
     *  00DA8ECC   5F               POP EDI
     *  00DA8ECD   75 05            JNZ SHORT .00DA8ED4
     *  00DA8ECF  ^E9 0E9FFFFF      JMP .00DA2DE2
     *  00DA8ED4   F7C7 03000000    TEST EDI,0x3
     *  00DA8EDA   75 14            JNZ SHORT .00DA8EF0
     *  00DA8EDC   C1E9 02          SHR ECX,0x2
     *  00DA8EDF   83E2 03          AND EDX,0x3
     *  00DA8EE2   83F9 08          CMP ECX,0x8
     *  00DA8EE5   72 29            JB SHORT .00DA8F10
     *  00DA8EE7   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]	; jichi: modified here
     *  00DA8EE9   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
     *  00DA8EF0   8BC7             MOV EAX,EDI
     *  00DA8EF2   BA 03000000      MOV EDX,0x3
     *  00DA8EF7   83E9 04          SUB ECX,0x4
     *  00DA8EFA   72 0C            JB SHORT .00DA8F08
     *  00DA8EFC   83E0 03          AND EAX,0x3
     *  00DA8EFF   03C8             ADD ECX,EAX
     *  00DA8F01   FF2485 148FDA00  JMP DWORD PTR DS:[EAX*4+0xDA8F14]
     *  00DA8F08   FF248D 1090DA00  JMP DWORD PTR DS:[ECX*4+0xDA9010]
     *  00DA8F0F   90               NOP
     *  00DA8F10   FF248D 948FDA00  JMP DWORD PTR DS:[ECX*4+0xDA8F94]
     *  00DA8F17   90               NOP
     *  00DA8F18   24 8F            AND AL,0x8F
     *  00DA8F1A   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8F1C   50               PUSH EAX
     *  00DA8F1D   8F               ???                                                                                   ; Unknown command
     *  00DA8F1E   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8F20  ^74 8F            JE SHORT .00DA8EB1
     *  00DA8F22   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8F24   23D1             AND EDX,ECX
     *  00DA8F26   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  00DA8F28   8807             MOV BYTE PTR DS:[EDI],AL
     *  00DA8F2A   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
     *  00DA8F2D   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
     *  00DA8F30   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  00DA8F33   C1E9 02          SHR ECX,0x2
     *  00DA8F36   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
     *  00DA8F39   83C6 03          ADD ESI,0x3
     *  00DA8F3C   83C7 03          ADD EDI,0x3
     *  00DA8F3F   83F9 08          CMP ECX,0x8
     *  00DA8F42  ^72 CC            JB SHORT .00DA8F10
     *  00DA8F44   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  00DA8F46   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
     *  00DA8F4D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
     *  00DA8F50   23D1             AND EDX,ECX
     *  00DA8F52   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  00DA8F54   8807             MOV BYTE PTR DS:[EDI],AL
     *  00DA8F56   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
     *  00DA8F59   C1E9 02          SHR ECX,0x2
     *  00DA8F5C   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
     *  00DA8F5F   83C6 02          ADD ESI,0x2
     *  00DA8F62   83C7 02          ADD EDI,0x2
     *  00DA8F65   83F9 08          CMP ECX,0x8
     *  00DA8F68  ^72 A6            JB SHORT .00DA8F10
     *  00DA8F6A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  00DA8F6C   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
     *  00DA8F73   90               NOP
     *  00DA8F74   23D1             AND EDX,ECX
     *  00DA8F76   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  00DA8F78   8807             MOV BYTE PTR DS:[EDI],AL
     *  00DA8F7A   83C6 01          ADD ESI,0x1
     *  00DA8F7D   C1E9 02          SHR ECX,0x2
     *  00DA8F80   83C7 01          ADD EDI,0x1
     *  00DA8F83   83F9 08          CMP ECX,0x8
     *  00DA8F86  ^72 88            JB SHORT .00DA8F10
     *  00DA8F88   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
     *  00DA8F8A   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
     *  00DA8F91   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
     *  00DA8F94   F7               ???                                                                                   ; Unknown command
     *  00DA8F95   8F               ???                                                                                   ; Unknown command
     *  00DA8F96   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8F98   E4 8F            IN AL,0x8F                                                                            ; I/O command
     *  00DA8F9A   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8F9C   DC8F DA00D48F    FMUL QWORD PTR DS:[EDI+0x8FD400DA]
     *  00DA8FA2   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8FA4   CC               INT3
     *  00DA8FA5   8F               ???                                                                                   ; Unknown command
     *  00DA8FA6   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8FA8   C48F DA00BC8F    LES ECX,FWORD PTR DS:[EDI+0x8FBC00DA]                                                 ; Modification of segment register
     *  00DA8FAE   DA00             FIADD DWORD PTR DS:[EAX]
     *  00DA8FB0   B4 8F            MOV AH,0x8F
     *
     */
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      const uint8_t bytes[] = {
          0xc7, 0x45, 0xfc, 0x00, 0x00, 0x00, 0x00, // 00cf0ec4   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0	; jichi: pattern start
          0x8b, 0x8b, 0x84, 0x03, 0x00, 0x00,       // 00cf0ecb   8b8b 84030000    mov ecx,dword ptr ds:[ebx+0x384]
          0x8b, 0x01,                               // 00cf0ed1   8b01             mov eax,dword ptr ds:[ecx]
          0x8b, 0x40, 0x60,                         // 00cf0ed3   8b40 60          mov eax,dword ptr ds:[eax+0x60]
          0x8b, 0xd6,                               // 00cf0ed6   8bd6             mov edx,esi
          0x52,                                     // 00cf0ed8   52               push edx
          0xff, 0xd0                                // 00cf0ed9   ffd0             call eax   ;jichi: called here  .00caef00
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.filter_fun = all_ascii_Filter;
      return NewHook(hp, "EmbedNitroplus");
    }

  } // namespace ScenarioHook
} // unnamed namespace

namespace
{
  bool sayanouta()
  {
    // 沙耶の唄 The Best 10対応DL版
    char tolang[] = "string too long";
    auto tolangaddr = MemDbg::findBytes(tolang, sizeof(tolang), processStartAddress, processStopAddress);
    auto lower = processStartAddress;
    auto succ = false;
    while (true)
    {
      auto addrX = MemDbg::findPushAddress(tolangaddr, lower, processStopAddress);
      if (addrX == 0)
        break;
      lower = addrX + 0x100;

      const uint8_t bytes[] = {
          0x55, 0x8b, 0xec,
          0x53, 0x8b, 0x5d, 0x08,
          0x56, 0x8b, 0xf1,
          0x85, 0xdb,
          0x74, XX,
          0x8b, 0x4e, 0x14,
          0x83, 0xf9, 0x10,
          0x72, 0x04,
          0x8b, 0x06,
          0xeb, 0x02};

      ULONG addr = reverseFindBytes(bytes, sizeof(bytes), addrX - 0x200, addrX);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto refaddr = context->retaddr - (DWORD)GetModuleHandle(0);
        if (refaddr < 0xb0000 || refaddr > 0xb1000)
          return;
        buffer->from(context->stack[1], context->stack[2]);
      };
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        std::string result = buffer->strA();
        result = re::sub(result, "#\\{(.*?)\\}(.*?)#", "$2");
        strReplace(result, u8"　\n");
        strReplace(result, u8"\n");
        buffer->from(result);
      };
      succ |= NewHook(hp, "sayanouta");
    }
    return succ;
  }
}
bool Nitroplus2::attach_function()
{
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  bool b = InsertNitroPlusHook();
  bool b2 = (Util::SearchResourceString(L"TOKYONECRO")) && InsertTokyoNecroHook();
  b2 |= sayanouta();
  return b || b2 || embed;
}