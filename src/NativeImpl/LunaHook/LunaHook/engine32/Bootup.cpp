#include "Bootup.h"

/**
 *  jichi 5/22/2015: Insert Bootup hook
 *  Sample games:
 *  - [090709] [PIL] 仏蘭西少女
 *  - [110318] [Daisy2] 三国恋戦� *  - [110329] [PIL/SLASH] 神学校
 *  - [150527] [Daisy2] 絶対階級学� *
 *  Properties
 *  - There is Bootup.dat existing in the game folder.
 *  - lstrlenW can find text repeating once
 *  - GetCharABCWidthsW and TextOutW can find cached text that missing characters
 *    GetCharABCWidthsA and TextOutA for old games.
 *  - There is only one TextOut (W for new and A for old).
 *
 *  Logic:
 *  + GDI hook
 *    - Hook to the caller of TextOut
 *  + Lstr hook
 *    - Find last (second) caller of the first GetCharABCWidths after int3
 *    - Find the lstrlen function in this caller, and hook to it
 *
 *  Full text is in arg1, shifted one by one.
 *  Character to paint is also in arg3
 *
 *  All Bootup games are slightly different
 *  - 三国恋戦�仏蘭西少女: text in both lstrlenA and caller of TextOutA
 *    But I didn't find correct lstrlenA to hook. BootupLstrA find nothing for 仏蘭西少女 and name for 三国恋戦�
 *  - 神学校: text in both lstrlenW and TextOutW, but lstrlenW has repetition
 *    Caller of TextOutW the same as that of TextOutA
 *  - 絶対階級学� text in both lstrlenW and TextOutW. But TextOutW's name has repetition
 *    Caller of TextOutW different 神学校
 *
 *  Here's the beginning of caller of TextOutW in 絶対階級学�
 *  00B61ADD   CC               INT3
 *  00B61ADE   CC               INT3
 *  00B61ADF   CC               INT3
 *  00B61AE0   55               PUSH EBP
 *  00B61AE1   8BEC             MOV EBP,ESP
 *  00B61AE3   81EC 98000000    SUB ESP,0x98
 *  00B61AE9   53               PUSH EBX
 *  00B61AEA   56               PUSH ESI
 *  00B61AEB   57               PUSH EDI
 *  00B61AEC   8BF2             MOV ESI,EDX
 *  00B61AEE   8BF9             MOV EDI,ECX
 *  00B61AF0   8975 D8          MOV DWORD PTR SS:[EBP-0x28],ESI
 *  00B61AF3   897D E0          MOV DWORD PTR SS:[EBP-0x20],EDI
 *  00B61AF6   E8 A5FEFFFF      CALL .00B619A0
 *  00B61AFB   8BD8             MOV EBX,EAX
 *  00B61AFD   895D CC          MOV DWORD PTR SS:[EBP-0x34],EBX
 *  00B61B00   66:833B 00       CMP WORD PTR DS:[EBX],0x0
 *  00B61B04   0F85 0B020000    JNZ .00B61D15
 *  00B61B0A   B8 00010000      MOV EAX,0x100
 *  00B61B0F   66:8933          MOV WORD PTR DS:[EBX],SI
 *  00B61B12   66:3BF0          CMP SI,AX
 *  00B61B15   72 26            JB SHORT .00B61B3D
 *  00B61B17   8B47 3C          MOV EAX,DWORD PTR DS:[EDI+0x3C]
 *  00B61B1A   85C0             TEST EAX,EAX
 *  00B61B1C   74 1F            JE SHORT .00B61B3D
 *  00B61B1E   8B57 44          MOV EDX,DWORD PTR DS:[EDI+0x44]
 *  00B61B21   85D2             TEST EDX,EDX
 *  00B61B23   7E 18            JLE SHORT .00B61B3D
 *  00B61B25   33C9             XOR ECX,ECX
 *  00B61B27   85D2             TEST EDX,EDX
 *  00B61B29   7E 12            JLE SHORT .00B61B3D
 *  00B61B2B   8B47 40          MOV EAX,DWORD PTR DS:[EDI+0x40]
 *  00B61B2E   8BFF             MOV EDI,EDI
 *  00B61B30   66:3930          CMP WORD PTR DS:[EAX],SI
 *  00B61B33   74 6F            JE SHORT .00B61BA4
 *  00B61B35   41               INC ECX
 *  00B61B36   83C0 02          ADD EAX,0x2
 *  00B61B39   3BCA             CMP ECX,EDX
 *  00B61B3B  ^7C F3            JL SHORT .00B61B30
 *  00B61B3D   33C0             XOR EAX,EAX
 *  00B61B3F   66:8945 9E       MOV WORD PTR SS:[EBP-0x62],AX
 *  00B61B43   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00B61B46   0FAF47 1C        IMUL EAX,DWORD PTR DS:[EDI+0x1C]
 *  00B61B4A   0FAF47 1C        IMUL EAX,DWORD PTR DS:[EDI+0x1C]
 *  00B61B4E   0FAF47 18        IMUL EAX,DWORD PTR DS:[EDI+0x18]
 *  00B61B52   50               PUSH EAX
 *  00B61B53   6A 00            PUSH 0x0
 *  00B61B55   FF77 14          PUSH DWORD PTR DS:[EDI+0x14]
 *  00B61B58   66:8975 9C       MOV WORD PTR SS:[EBP-0x64],SI
 *  00B61B5C   E8 2FC20200      CALL .00B8DD90
 *  00B61B61   83C4 0C          ADD ESP,0xC
 *  00B61B64   8D45 9C          LEA EAX,DWORD PTR SS:[EBP-0x64]
 *  00B61B67   6A 01            PUSH 0x1
 *  00B61B69   50               PUSH EAX
 *  00B61B6A   6A 00            PUSH 0x0
 *  00B61B6C   6A 00            PUSH 0x0
 *  00B61B6E   FF77 10          PUSH DWORD PTR DS:[EDI+0x10]
 *  00B61B71   FF15 8820BB00    CALL DWORD PTR DS:[0xBB2088]             ; gdi32.TextOutW
 *  00B61B77   8B47 1C          MOV EAX,DWORD PTR DS:[EDI+0x1C]
 *  00B61B7A   8B57 14          MOV EDX,DWORD PTR DS:[EDI+0x14]
 *  00B61B7D   8B7F 04          MOV EDI,DWORD PTR DS:[EDI+0x4]
 *  00B61B80   8B73 0C          MOV ESI,DWORD PTR DS:[EBX+0xC]
 *  00B61B83   0FAFF8           IMUL EDI,EAX
 *  00B61B86   48               DEC EAX
 *  00B61B87   8975 C4          MOV DWORD PTR SS:[EBP-0x3C],ESI
 *  00B61B8A   897D C8          MOV DWORD PTR SS:[EBP-0x38],EDI
 *
 *  TextOutW's caller for 神学校
 *  0113183E   CC               INT3
 *  0113183F   CC               INT3
 *  01131840   55               PUSH EBP
 *  01131841   8BEC             MOV EBP,ESP
 *  01131843   83EC 74          SUB ESP,0x74
 *  01131846   53               PUSH EBX
 *  01131847   56               PUSH ESI
 *  01131848   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  0113184B   57               PUSH EDI
 *  0113184C   8B7D 0C          MOV EDI,DWORD PTR SS:[EBP+0xC]
 *  0113184F   8BCF             MOV ECX,EDI
 *  01131851   8BD6             MOV EDX,ESI
 *  01131853   E8 A8FEFFFF      CALL .01131700
 *  01131858   8BD8             MOV EBX,EAX
 *  0113185A   66:833B 00       CMP WORD PTR DS:[EBX],0x0
 *  0113185E   895D 90          MOV DWORD PTR SS:[EBP-0x70],EBX
 *  01131861   0F85 700F0000    JNZ .011327D7
 *  01131867   B8 00010000      MOV EAX,0x100
 *  0113186C   66:893B          MOV WORD PTR DS:[EBX],DI
 *  0113186F   66:3BF8          CMP DI,AX
 *  01131872   72 2E            JB SHORT .011318A2
 *  01131874   8B56 3C          MOV EDX,DWORD PTR DS:[ESI+0x3C]
 *  01131877   85D2             TEST EDX,EDX
 *  01131879   74 27            JE SHORT .011318A2
 *  0113187B   8B46 44          MOV EAX,DWORD PTR DS:[ESI+0x44]
 *  0113187E   85C0             TEST EAX,EAX
 *  01131880   7E 20            JLE SHORT .011318A2
 *  01131882   33FF             XOR EDI,EDI
 *  01131884   85C0             TEST EAX,EAX
 *  01131886   7E 1A            JLE SHORT .011318A2
 *  01131888   8B46 40          MOV EAX,DWORD PTR DS:[ESI+0x40]
 *  0113188B   EB 03            JMP SHORT .01131890
 *  0113188D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  01131890   66:8B4D 0C       MOV CX,WORD PTR SS:[EBP+0xC]
 *  01131894   66:3908          CMP WORD PTR DS:[EAX],CX
 *  01131897   74 74            JE SHORT .0113190D
 *  01131899   47               INC EDI
 *  0113189A   83C0 02          ADD EAX,0x2
 *  0113189D   3B7E 44          CMP EDI,DWORD PTR DS:[ESI+0x44]
 *  011318A0  ^7C EE            JL SHORT .01131890
 *  011318A2   66:8B45 0C       MOV AX,WORD PTR SS:[EBP+0xC]
 *  011318A6   66:8945 8C       MOV WORD PTR SS:[EBP-0x74],AX
 *  011318AA   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  011318AD   0FAFC0           IMUL EAX,EAX
 *  011318B0   0FAF46 18        IMUL EAX,DWORD PTR DS:[ESI+0x18]
 *  011318B4   0FAF46 04        IMUL EAX,DWORD PTR DS:[ESI+0x4]
 *  011318B8   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  011318BB   33C9             XOR ECX,ECX
 *  011318BD   50               PUSH EAX
 *  011318BE   51               PUSH ECX
 *  011318BF   52               PUSH EDX
 *  011318C0   66:894D 8E       MOV WORD PTR SS:[EBP-0x72],CX
 *  011318C4   E8 87060200      CALL .01151F50
 *  011318C9   8B4E 10          MOV ECX,DWORD PTR DS:[ESI+0x10]
 *  011318CC   83C4 0C          ADD ESP,0xC
 *  011318CF   6A 01            PUSH 0x1
 *  011318D1   8D45 8C          LEA EAX,DWORD PTR SS:[EBP-0x74]
 *  011318D4   50               PUSH EAX
 *  011318D5   6A 00            PUSH 0x0
 *  011318D7   6A 00            PUSH 0x0
 *  011318D9   51               PUSH ECX
 *  011318DA   FF15 38101701    CALL DWORD PTR DS:[0x1171038]            ; gdi32.TextOutW
 *  011318E0   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  011318E3   8B46 04          MOV EAX,DWORD PTR DS:[ESI+0x4]
 *  011318E6   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  011318E9   0FAFC1           IMUL EAX,ECX
 *  011318EC   8B7B 0C          MOV EDI,DWORD PTR DS:[EBX+0xC]
 */
namespace
{ // unnamed

  bool InsertBootupGDIHook()
  {
    bool widechar = true;
    ULONG addr = MemDbg::findCallerAddressAfterInt3((ULONG)TextOutW, processStartAddress, processStopAddress);
    if (!addr)
    {
      addr = MemDbg::findCallerAddressAfterInt3((ULONG)TextOutA, processStartAddress, processStopAddress);
      widechar = false;
    }
    if (!addr)
    {
      ConsoleOutput("BootupGDI: failed to find TextOut");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.type = USING_SPLIT | NO_CONTEXT | USING_CHAR;   // use NO_CONTEXT to get rid of floating reladdr
    hp.type |= widechar ? CODEC_UTF16 : CODEC_ANSI_BE; // use context as split is sufficient, but will produce floating split

    hp.offset = stackoffset(2); // arg2, character in arg2, could be modified by hook
    if (widechar)
      hp.split = regoffset(edx);
    else
      hp.split = stackoffset(1);
    hp.text_fun =
        [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      DWORD arg2 = context->stack[2];
      if ((arg2 & 0xffff0000))
      { // if arg2 high bits are there, this is new Bootup game
        hp->type |= DATA_INDIRECT;
        hp->offset = stackoffset(3);
        hp->split = regoffset(ebx);
      }
      hp->text_fun = nullptr;
    };

    ConsoleOutput("INSERT BootupGDI");

    ConsoleOutput("BootupGDI: disable GDI hooks");

    return NewHook(hp, widechar ? "BootupW" : "BootupA");
  }
  bool InsertBootupLstrHook() // for character name
  {
    bool widechar = true;
    ULONG addr = MemDbg::findLastCallerAddressAfterInt3((ULONG)GetCharABCWidthsW, processStartAddress, processStopAddress);
    if (!addr)
    {
      // Do not hook to lstrlenA, which causes text extraction to stop
      // addr = MemDbg::findLastCallerAddressAfterInt3((ULONG)GetCharABCWidthsA, processStartAddress, processStopAddress);
      // widechar = false;
    }
    if (!addr)
    {
      ConsoleOutput("BootupLstr: failed to find GetCharABCWidths");
      return false;
    }
    // GROWL_DWORD2(addr, processStartAddress);
    // enum { range = 0x200 }; // 0x012A2CCB  - 0x12A2CB0 = 0x1b
    addr = MemDbg::findCallAddress(widechar ? (ULONG)::lstrlenW : (ULONG)::lstrlenA,
                                   processStartAddress, processStopAddress,
                                   addr - processStartAddress); //, range); // no range
    if (!addr)
    {
      ConsoleOutput("BootupLstr: failed to find lstrlen");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.type = widechar ? (USING_STRING | CODEC_UTF16) : USING_STRING; // use context as split is sufficient, but will produce floating split
    // hp.type = CODEC_UTF16|NO_CONTEXT|USING_SPLIT; // use text address as split
    // hp.split = 0;

    ConsoleOutput("INSERT BootupLstr");

    return NewHook(hp, widechar ? "BootupLstrW" : "BootupLstrA");
  }
} // unnamed namespace
bool InsertBootupHook()
{
  bool ret = InsertBootupGDIHook();
  InsertBootupLstrHook();
  return ret;
}

bool Bootup::attach_function()
{

  return InsertBootupHook();
}