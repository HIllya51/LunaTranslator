#include "GXP.h"
/**
 *  jichi 5/11/2014: Hook to the beginning of a function
 *
 *  Executable description shows "AVGEngineV2"
 *
 *  Cached wrong text can also be found in GetGlyphOutlineW.
 *
 *  4/27/2015 old logic:
 *  1. find the following location
 *     00A78144   66:833C70 00     CMP WORD PTR DS:[EAX+ESI*2],0x0
 *     i.e. 0x66833C7000
 *     There are several matches, the first one is used.
 *  2. find the first push operation after it
 *  3. find the function call after push, and hook to it
 *     The text is in the arg1, which is character by character
 *
 *  But in the new game since ウルスラグ� there the function call is not immediately after 0x66833C7000 any more.
 *  My own way to find the function to hook is as follows:
 *  1. find the following location
 *     00A78144   66:833C70 00     CMP WORD PTR DS:[EAX+ESI*2],0x0
 *     i.e. 0x66833C7000
 *     There are several matches, the first one is used.
 *  2. Use Ollydbg to debug step by step until the first function call is encountered
 *     Then, the text character is directly on the stack
 *
 *  Here's an example of Demonion II (reladdr = 0x18c540):
 *  The text is displayed character by character.
 *  sub_58C540 proc near
 *  arg_0 = dword ptr  8 // LPCSTR with 1 character
 *
 *  0138C540  /$ 55             PUSH EBP
 *  0138C541  |. 8BEC           MOV EBP,ESP
 *  0138C543  |. 83E4 F8        AND ESP,0xFFFFFFF8
 *  0138C546  |. 8B43 0C        MOV EAX,DWORD PTR DS:[EBX+0xC]
 *  0138C549  |. 83EC 08        SUB ESP,0x8
 *  0138C54C  |. 56             PUSH ESI
 *  0138C54D  |. 57             PUSH EDI
 *  0138C54E  |. 85C0           TEST EAX,EAX
 *  0138C550  |. 75 04          JNZ SHORT demonion.0138C556
 *  0138C552  |. 33F6           XOR ESI,ESI
 *  0138C554  |. EB 18          JMP SHORT demonion.0138C56E
 *  0138C556  |> 8B4B 14        MOV ECX,DWORD PTR DS:[EBX+0x14]
 *  0138C559  |. 2BC8           SUB ECX,EAX
 *  0138C55B  |. B8 93244992    MOV EAX,0x92492493
 *  0138C560  |. F7E9           IMUL ECX
 *  0138C562  |. 03D1           ADD EDX,ECX
 *  0138C564  |. C1FA 04        SAR EDX,0x4
 *  0138C567  |. 8BF2           MOV ESI,EDX
 *  0138C569  |. C1EE 1F        SHR ESI,0x1F
 *  0138C56C  |. 03F2           ADD ESI,EDX
 *  0138C56E  |> 8B7B 10        MOV EDI,DWORD PTR DS:[EBX+0x10]
 *  0138C571  |. 8BCF           MOV ECX,EDI
 *  0138C573  |. 2B4B 0C        SUB ECX,DWORD PTR DS:[EBX+0xC]
 *  0138C576  |. B8 93244992    MOV EAX,0x92492493
 *  0138C57B  |. F7E9           IMUL ECX
 *  0138C57D  |. 03D1           ADD EDX,ECX
 *  0138C57F  |. C1FA 04        SAR EDX,0x4
 *  0138C582  |. 8BC2           MOV EAX,EDX
 *  0138C584  |. C1E8 1F        SHR EAX,0x1F
 *  0138C587  |. 03C2           ADD EAX,EDX
 *  0138C589  |. 3BC6           CMP EAX,ESI
 *  0138C58B  |. 73 2F          JNB SHORT demonion.0138C5BC
 *  0138C58D  |. C64424 08 00   MOV BYTE PTR SS:[ESP+0x8],0x0
 *  0138C592  |. 8B4C24 08      MOV ECX,DWORD PTR SS:[ESP+0x8]
 *  0138C596  |. 8B5424 08      MOV EDX,DWORD PTR SS:[ESP+0x8]
 *  0138C59A  |. 51             PUSH ECX
 *  0138C59B  |. 8B4D 08        MOV ECX,DWORD PTR SS:[EBP+0x8]
 *  0138C59E  |. 52             PUSH EDX
 *  0138C59F  |. B8 01000000    MOV EAX,0x1
 *  0138C5A4  |. 8BD7           MOV EDX,EDI
 *  0138C5A6  |. E8 F50E0000    CALL demonion.0138D4A0
 *  0138C5AB  |. 83C4 08        ADD ESP,0x8
 *  0138C5AE  |. 83C7 1C        ADD EDI,0x1C
 *  0138C5B1  |. 897B 10        MOV DWORD PTR DS:[EBX+0x10],EDI
 *  0138C5B4  |. 5F             POP EDI
 *  0138C5B5  |. 5E             POP ESI
 *  0138C5B6  |. 8BE5           MOV ESP,EBP
 *  0138C5B8  |. 5D             POP EBP
 *  0138C5B9  |. C2 0400        RETN 0x4
 *  0138C5BC  |> 397B 0C        CMP DWORD PTR DS:[EBX+0xC],EDI
 *  0138C5BF  |. 76 05          JBE SHORT demonion.0138C5C6
 *  0138C5C1  |. E8 1B060D00    CALL demonion.0145CBE1
 *  0138C5C6  |> 8B03           MOV EAX,DWORD PTR DS:[EBX]
 *  0138C5C8  |. 57             PUSH EDI                                 ; /Arg4
 *  0138C5C9  |. 50             PUSH EAX                                 ; |Arg3
 *  0138C5CA  |. 8B45 08        MOV EAX,DWORD PTR SS:[EBP+0x8]           ; |
 *  0138C5CD  |. 50             PUSH EAX                                 ; |Arg2
 *  0138C5CE  |. 8D4C24 14      LEA ECX,DWORD PTR SS:[ESP+0x14]          ; |
 *  0138C5D2  |. 51             PUSH ECX                                 ; |Arg1
 *  0138C5D3  |. 8BC3           MOV EAX,EBX                              ; |
 *  0138C5D5  |. E8 D6010000    CALL demonion.0138C7B0                   ; \demonion.0138C7B0
 *  0138C5DA  |. 5F             POP EDI
 *  0138C5DB  |. 5E             POP ESI
 *  0138C5DC  |. 8BE5           MOV ESP,EBP
 *  0138C5DE  |. 5D             POP EBP
 *  0138C5DF  \. C2 0400        RETN 0x4
 *
 *  4/26/2015  ウルスラグ� *  base = 0xa30000, old hook addr = 0xbe6360
 *
 *  00A7813A   EB 02            JMP SHORT .00A7813E
 *  00A7813C   8BC7             MOV EAX,EDI
 *  00A7813E   8BB3 E4020000    MOV ESI,DWORD PTR DS:[EBX+0x2E4]
 *  00A78144   66:833C70 00     CMP WORD PTR DS:[EAX+ESI*2],0x0  ; jich: here's the first found segment
 *  00A78149   74 36            JE SHORT .00A78181
 *  00A7814B   837F 14 08       CMP DWORD PTR DS:[EDI+0x14],0x8
 *  00A7814F   72 08            JB SHORT .00A78159
 *  00A78151   8B07             MOV EAX,DWORD PTR DS:[EDI]
 *
 *  00A7883A   24 3C            AND AL,0x3C
 *  00A7883C   50               PUSH EAX
 *  00A7883D   C74424 4C 000000>MOV DWORD PTR SS:[ESP+0x4C],0x0
 *  00A78845   0F5B             ???                                      ; Unknown command
 *  00A78847   C9               LEAVE
 *  00A78848   F3:0F114424 44   MOVSS DWORD PTR SS:[ESP+0x44],XMM0
 *  00A7884E   F3:0F114C24 48   MOVSS DWORD PTR SS:[ESP+0x48],XMM1
 *  00A78854   E8 37040000      CALL .00A78C90  ; jichi: here's the target function to hook to, text char on the stack[0]
 *  00A78859   A1 888EDD00      MOV EAX,DWORD PTR DS:[0xDD8E88]
 *  00A7885E   A8 01            TEST AL,0x1
 *  00A78860   75 30            JNZ SHORT .00A78892
 *  00A78862   83C8 01          OR EAX,0x1
 *  00A78865   A3 888EDD00      MOV DWORD PTR DS:[0xDD8E88],EAX
 *
 *  Here's the new function call:
 *  00A78C8A   CC               INT3
 *  00A78C8B   CC               INT3
 *  00A78C8C   CC               INT3
 *  00A78C8D   CC               INT3
 *  00A78C8E   CC               INT3
 *  00A78C8F   CC               INT3
 *  00A78C90   55               PUSH EBP
 *  00A78C91   8BEC             MOV EBP,ESP
 *  00A78C93   56               PUSH ESI
 *  00A78C94   8BF1             MOV ESI,ECX
 *  00A78C96   57               PUSH EDI
 *  00A78C97   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  00A78C9A   8B4E 04          MOV ECX,DWORD PTR DS:[ESI+0x4]
 *  00A78C9D   3BF9             CMP EDI,ECX
 *  00A78C9F   73 76            JNB SHORT .00A78D17
 *  00A78CA1   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  00A78CA3   3BC7             CMP EAX,EDI
 *  00A78CA5   77 70            JA SHORT .00A78D17
 *  00A78CA7   2BF8             SUB EDI,EAX
 *  00A78CA9   B8 93244992      MOV EAX,0x92492493
 *  00A78CAE   F7EF             IMUL EDI
 *  00A78CB0   03D7             ADD EDX,EDI
 *  00A78CB2   C1FA 04          SAR EDX,0x4
 *  00A78CB5   8BFA             MOV EDI,EDX
 *  00A78CB7   C1EF 1F          SHR EDI,0x1F
 *  00A78CBA   03FA             ADD EDI,EDX
 *  00A78CBC   3B4E 08          CMP ECX,DWORD PTR DS:[ESI+0x8]
 *  00A78CBF   75 09            JNZ SHORT .00A78CCA
 *  00A78CC1   6A 01            PUSH 0x1
 *  00A78CC3   8BCE             MOV ECX,ESI
 *  00A78CC5   E8 36030000      CALL .00A79000
 *  00A78CCA   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
 *  00A78CCD   8D0CFD 00000000  LEA ECX,DWORD PTR DS:[EDI*8]
 *  00A78CD4   2BCF             SUB ECX,EDI
 *  00A78CD6   8B3E             MOV EDI,DWORD PTR DS:[ESI]
 *  00A78CD8   85D2             TEST EDX,EDX
 *  00A78CDA   74 7B            JE SHORT .00A78D57
 *  00A78CDC   66:8B048F        MOV AX,WORD PTR DS:[EDI+ECX*4]
 *  00A78CE0   66:8902          MOV WORD PTR DS:[EDX],AX
 *  00A78CE3   8B448F 04        MOV EAX,DWORD PTR DS:[EDI+ECX*4+0x4]
 *  00A78CE7   8942 04          MOV DWORD PTR DS:[EDX+0x4],EAX
 *  00A78CEA   8B448F 08        MOV EAX,DWORD PTR DS:[EDI+ECX*4+0x8]
 *  00A78CEE   8942 08          MOV DWORD PTR DS:[EDX+0x8],EAX
 *  00A78CF1   8B448F 0C        MOV EAX,DWORD PTR DS:[EDI+ECX*4+0xC]
 *  00A78CF5   8942 0C          MOV DWORD PTR DS:[EDX+0xC],EAX
 *  00A78CF8   C742 10 00000000 MOV DWORD PTR DS:[EDX+0x10],0x0
 *  00A78CFF   8B448F 14        MOV EAX,DWORD PTR DS:[EDI+ECX*4+0x14]
 *  00A78D03   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  00A78D06   8A448F 18        MOV AL,BYTE PTR DS:[EDI+ECX*4+0x18]
 *  00A78D0A   8842 18          MOV BYTE PTR DS:[EDX+0x18],AL
 *  00A78D0D   8346 04 1C       ADD DWORD PTR DS:[ESI+0x4],0x1C
 *  00A78D11   5F               POP EDI
 *  00A78D12   5E               POP ESI
 *  00A78D13   5D               POP EBP
 *  00A78D14   C2 0400          RETN 0x4
 *  00A78D17   3B4E 08          CMP ECX,DWORD PTR DS:[ESI+0x8]
 *  00A78D1A   75 09            JNZ SHORT .00A78D25
 *  00A78D1C   6A 01            PUSH 0x1
 *  00A78D1E   8BCE             MOV ECX,ESI
 *  00A78D20   E8 DB020000      CALL .00A79000
 *  00A78D25   8B4E 04          MOV ECX,DWORD PTR DS:[ESI+0x4]
 *  00A78D28   85C9             TEST ECX,ECX
 *  00A78D2A   74 2B            JE SHORT .00A78D57
 *  00A78D2C   66:8B07          MOV AX,WORD PTR DS:[EDI]
 *  00A78D2F   66:8901          MOV WORD PTR DS:[ECX],AX
 *  00A78D32   8B47 04          MOV EAX,DWORD PTR DS:[EDI+0x4]
 *  00A78D35   8941 04          MOV DWORD PTR DS:[ECX+0x4],EAX
 *  00A78D38   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
 *  00A78D3B   8941 08          MOV DWORD PTR DS:[ECX+0x8],EAX
 *  00A78D3E   8B47 0C          MOV EAX,DWORD PTR DS:[EDI+0xC]
 *  00A78D41   8941 0C          MOV DWORD PTR DS:[ECX+0xC],EAX
 *  00A78D44   C741 10 00000000 MOV DWORD PTR DS:[ECX+0x10],0x0
 *  00A78D4B   8B47 14          MOV EAX,DWORD PTR DS:[EDI+0x14]
 *  00A78D4E   8941 14          MOV DWORD PTR DS:[ECX+0x14],EAX
 *  00A78D51   8A47 18          MOV AL,BYTE PTR DS:[EDI+0x18]
 *  00A78D54   8841 18          MOV BYTE PTR DS:[ECX+0x18],AL
 *  00A78D57   8346 04 1C       ADD DWORD PTR DS:[ESI+0x4],0x1C
 *  00A78D5B   5F               POP EDI
 *  00A78D5C   5E               POP ESI
 *  00A78D5D   5D               POP EBP
 *  00A78D5E   C2 0400          RETN 0x4
 *  00A78D61   CC               INT3
 *  00A78D62   CC               INT3
 *  00A78D63   CC               INT3
 *  00A78D64   CC               INT3
 *  00A78D65   CC               INT3
 */
static bool InsertGXP1Hook()
{
  union
  {
    DWORD i;
    DWORD *id;
    BYTE *ib;
  };
  for (i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
  {
    // jichi example:
    // 00A78144   66:833C70 00     CMP WORD PTR DS:[EAX+ESI*2],0x0

    // find cmp word ptr [esi*2+eax],0
    if (*id != 0x703c8366)
      continue;
    i += 4;
    if (*ib != 0)
      continue;
    i++;
    DWORD j = i + 0x200;
    j = j < (processStopAddress - 8) ? j : (processStopAddress - 8);

    DWORD flag = false;
    while (i < j)
    {
      DWORD k = disasm(ib);
      if (k == 0)
        break;
      if (k == 1 && (*ib & 0xf8) == 0x50)
      { // push reg
        flag = true;
        break;
      }
      i += k;
    }
    if (flag)
      while (i < j)
      {
        if (*ib == 0xe8)
        { // jichi: find first long call after the push operation
          i++;
          DWORD addr = *id + i + 4;
          if (addr > processStartAddress && addr < processStopAddress)
          {
            HookParam hp;
            hp.address = addr;
            // hp.type = CODEC_UTF16|DATA_INDIRECT;
            hp.type = USING_STRING | CODEC_UTF16 | DATA_INDIRECT | NO_CONTEXT | FIXING_SPLIT; // jichi 4/25/2015: Fixing split
            hp.offset = stackoffset(1);

            // GROWL_DWORD3(hp.address, processStartAddress, hp.address - processStartAddress);

            // DWORD call = Util::FindCallAndEntryAbs(hp.address, processStopAddress - processStartAddress, processStartAddress, 0xec81); // zero
            // DWORD call = Util::FindCallAndEntryAbs(hp.address, processStopAddress - processStartAddress, processStartAddress, 0xec83); // zero
            // DWORD call = Util::FindCallAndEntryAbs(hp.address, processStopAddress - processStartAddress, processStartAddress, 0xec8b55); // zero
            // GROWL_DWORD3(call, processStartAddress, call - processStartAddress);

            ConsoleOutput("INSERT GXP");

            // jichi 5/13/2015: Disable hooking to GetGlyphOutlineW
            // FIXME: GetGlyphOutlineW can extract name, but GXP cannot
            ConsoleOutput("GXP: disable GDI hooks");

            return NewHook(hp, "GXP");
          }
        }
        i++;
      }
  }
  // ConsoleOutput("Unknown GXP engine.");
  ConsoleOutput("GXP: failed");
  return false;
}

static bool InsertGXP2Hook()
{
  // pattern = 0x0f5bc9f30f11442444f30f114c2448e8
  const BYTE bytes[] = {
      0x0f, 0x5b,                         // 00A78845   0F5B             ???                                      ; Unknown command
      0xc9,                               // 00A78847   C9               LEAVE
      0xf3, 0x0f, 0x11, 0x44, 0x24, 0x44, // 00A78848   F3:0F114424 44   MOVSS DWORD PTR SS:[ESP+0x44],XMM0
      0xf3, 0x0f, 0x11, 0x4c, 0x24, 0x48, // 00A7884E   F3:0F114C24 48   MOVSS DWORD PTR SS:[ESP+0x48],XMM1
      0xe8                                // 37040000                 // 00A78854   E8 37040000      CALL .00A78C90  ; jichi: here's the target function to hook to, text char on the stack[0]
  };
  enum
  {
    addr_offset = sizeof(bytes) - 1
  }; // 0x00a78854 - 0x00a78845
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("GXP2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.type = CODEC_UTF16 | NO_CONTEXT | DATA_INDIRECT | FIXING_SPLIT | USING_STRING;
  ConsoleOutput("INSERT GXP2");

  ConsoleOutput("GXP: disable GDI hooks");

  return NewHook(hp, "GXP2");
}

bool InsertGXPHook()
{
  // GXP1 and GXP2 are harmless to each other
  bool ok = InsertGXP1Hook();
  ok = InsertGXP2Hook() || ok;
  return ok;
}
namespace
{ // unnamed

  ULONG moduleBaseAddress_; // saved only for debugging purposes

  bool isBadText(std::wstring_view text)
  {
    return text[0] <= 127 || text[text.size() - 1] <= 127 // skip ascii text
           || ::wcschr(text.data(), 0xff3f);                        // Skip system text containing: ＿
  }

  namespace ScenarioHook1
  { // for old GXP1
    namespace Private
    {
      TextUnionW *arg_,
          argValue_;
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {

        static std::wstring text_; // persistent storage, which makes this function not thread-safe

        auto arg = (TextUnionW *)(s->stack[0] + 4); // arg1 + 0x4
        if (!arg->isValid())
          return;

        auto text = arg->view();
        if (isBadText(text))
          return;
        buffer->from(text);
      }
      void hook2a(hook_context *s, TextBuffer buffer)
      {
        auto arg = (TextUnionW *)(s->stack[0] + 4); // arg1 + 0x4
        arg_ = arg;
        argValue_ = *arg;

        arg->setText(buffer.viewW());
        // if (arg->size)
        //   hashes_.insert(Engine::hashWCharArray(arg->text, arg->size));
        //  return true;
      }
      void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (arg_)
        {
          *arg_ = argValue_;
          arg_ = nullptr;
        }
      }
    } // namespace Private

    /**
     *  Sample game: 塔の下のエクセルキトゥス体験版
     *  Executable description shows "AVGEngineV2"
     *
     *  Debugging method: Find the fixed text address, and check when it is being modified
     *
     *  Scenario caller, text in the struct of arg1 + 0x4.
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0xeb, 0x02,             // 01313bb6   eb 02            jmp short trial.01313bba
          0x8b, 0xc5,             // 01313bb8   8bc5             mov eax,ebp
          0x8b, 0x54, 0x24, 0x18, // 01313bba   8b5424 18        mov edx,dword ptr ss:[esp+0x18]
          0x8d, 0x0c, 0x51,       // 01313bbe   8d0c51           lea ecx,dword ptr ds:[ecx+edx*2]
          0x8d, 0x1c, 0x3f        // 01313bc1   8d1c3f           lea ebx,dword ptr ds:[edi+edi]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return addr;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return addr;
      // return winhook::hook_before(addr, Private::hookBefore);

      int count = 0;
      auto fun = [&count](ULONG addr) -> bool
      {
        auto retaddr = addr + 5;

        if (*(DWORD *)retaddr != 0x0c244c8a)
          return true;
        if (*(BYTE *)retaddr == 0x4f ||
            (*(DWORD *)retaddr & 0x00ff00ff) == 0x0024008b) // skip truncated texts
          return true;
        HookParam hp;
        hp.address = addr;
        hp.text_fun = Private::hookBefore;
        hp.embed_fun = Private::hook2a;
        hp.type = EMBED_ABLE | CODEC_UTF16 | USING_STRING | NO_CONTEXT;
        hp.lineSeparator = L"%r";
        hp.embed_hook_font = F_GetGlyphOutlineW;
        bool succ = NewHook(hp, "EmbedGXP");
        hp.address = addr + 5;
        hp.text_fun = Private::hookAfter;
        succ |= NewHook(hp, "EmbedGXP");
        count += 1;
        return succ; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
      return count;
    }
  } // namespace ScenarioHook1

  namespace ScenarioHook2
  { // for new GXP2
    namespace Private
    {
      TextUnionW *arg_,
          argValue_;
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        static std::wstring text_;            // persistent storage, which makes this function not thread-safe
        auto arg = (TextUnionW *)s->stack[0]; // arg1
        if (!arg->isValid())
          return;

        auto text = arg->view();
        if (isBadText(text))
          return;
        buffer->from(text);
      }
      void hook2a(hook_context *s, TextBuffer buffer)
      {
        auto arg = (TextUnionW *)s->stack[0]; // arg1 + 0x4
        arg_ = arg;
        argValue_ = *arg;

        arg->setText(buffer.viewW());
      }

      void hookAfter(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        if (arg_)
        {
          *arg_ = argValue_;
          arg_ = nullptr;
        }
      }
    } // namespace Private

    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x8d, 0x04, 0x3f, // 08159fd  |. 8d043f         lea eax,dword ptr ds:[edi+edi]	; jichi: edi *= 2 for wchar_t
          0x50,             // 0815a00  |. 50             push eax	; jichi: size
          0x8d, 0x04, 0x4b, // 0815a01  |. 8d044b         lea eax,dword ptr ds:[ebx+ecx*2]
          0x50,             // 0815a04  |. 50             push eax	; jichi: source text
          0x52              // 0815a05  |. 52             push edx	; jichi: target text
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return addr;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return addr;
      // return winhook::hook_before(addr, Private::hookBefore);

      int count = 0;
      auto fun = [&count](ULONG addr) -> bool
      {
        auto retaddr = addr + 5;
        if (*(WORD *)retaddr != 0x458a)
          return true;
        if (*(BYTE *)retaddr == 0xa1)
          return true;
        HookParam hp;
        hp.address = addr;
        hp.text_fun = Private::hookBefore;
        hp.embed_fun = Private::hook2a;
        hp.type = EMBED_ABLE | CODEC_UTF16 | USING_STRING | NO_CONTEXT;
        hp.lineSeparator = L"%r";
        hp.embed_hook_font = F_GetGlyphOutlineW;
        bool succ = NewHook(hp, "EmbedGXP2");
        hp.address = addr + 5;
        hp.text_fun = Private::hookAfter;
        succ |= NewHook(hp, "EmbedGXP2");
        count += 1;
        return succ; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
      return count;
    }
  } // namespace ScenarioHook2
  /*
  namespace PopupHook1 { // only for old GXP1 engine
  namespace Private {
    bool hookBefore(winhook::hook_context *s)
    {
      static std::wstring text_; // persistent storage, which makes this function not thread-safe
      auto arg = (TextUnionW *)(s->ecx + 0x1ec); // [ecx + 0x1ec]
      if (!arg->isValid())
        return true;
      auto text = arg->getText();
      if (isBadText(text))
        return true;
      auto retaddr = s->stack[0];
      auto reladdr = retaddr - moduleBaseAddress_;
      enum { role = Engine::OtherRole };
      std::wstring oldText = std::wstring(text),
              newText = EngineController::instance()->dispatchTextWSTD(oldText, role, reladdr);
      if (newText == oldText)
        return true;
      text_ = newText;
      arg->setText(text_);
      return true;
    }
  } // Private
   bool attach(ULONG startAddress, ULONG stopAddress)
  {
    const uint8_t bytes[] = {
      0x8b,0x86, 0xec,0x01,0x00,0x00, // 001092a9   8b86 ec010000    mov eax,dword ptr ds:[esi+0x1ec] ; jichi: text in eax
      0xeb, 0x06,                     // 001092af   eb 06            jmp short trial.001092b7
      0x8d,0x86, 0xec,0x01,0x00,0x00, // 001092b1   8d86 ec010000    lea eax,dword ptr ds:[esi+0x1ec]
      0x0f,0xb7,0x14,0x78,            // 001092b7   0fb71478         movzx edx,word ptr ds:[eax+edi*2]
      0x52                            // 001092bb   52               push edx
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    return winhook::hook_before(addr, Private::hookBefore);
    // Function called at runtime
    //int count = 0;
    //auto fun = [&count](ULONG addr) -> bool {
    //  auto before = std::bind(Private::hookBefore, addr + 5, std::placeholders::_1);
    //  count += winhook::hook_both(addr, before, Private::hookAfter);
    //  return true; // replace all functions
    //};
    //MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
    //DOUT("call number =" << count);
    //return count;
  }
  } // namespace PopupHook1

  namespace OtherHook { // for all GXP engines
  namespace Private {
    bool hookBefore(winhook::hook_context *s)
    {
      static std::wstring text_;
      auto text = (LPCWSTR)s->stack[3]; // arg3
      if (!text || !*text)
        return true;
      auto retaddr = s->stack[0];
      auto reladdr = retaddr - moduleBaseAddress_;
      enum { role = Engine::OtherRole };
      std::wstring oldText = std::wstring(text),
              newText = EngineController::instance()->dispatchTextWSTD(oldText, role, reladdr);
      if (newText.empty() || oldText == newText)
        return true;
      strReplace(newText, L"%r", L"\n");
      //newText.replace("%r", "\n");
      text_ = newText;
      s->stack[3] = (ULONG)text_.c_str();
      return true;
    }
  } // Private
   bool attach(ULONG startAddress, ULONG stopAddress)
  {
    const uint8_t bytes[] = {
      0x99,           // 014d45ae   99               cdq
      0x2b,0xc2,      // 014d45af   2bc2             sub eax,edx
      0xd1,0xf8,      // 014d45b1   d1f8             sar eax,1
      0x03 //,0xf0,   // 014d45b3   03f0             add esi,eax
    };
    int count = 0;
    auto fun = [&count](ULONG addr) -> bool {
      count +=
          (addr = MemDbg::findEnclosingAlignedFunction(addr))
          && winhook::hook_before(addr, Private::hookBefore);
      return true;
    };
    MemDbg::iterFindBytes(fun, bytes, sizeof(bytes), startAddress, stopAddress);
    DOUT("call number =" << count);
    return count;
  }
  } // namespace OtherHook
  */

  bool attach()
  {
    ULONG startAddress = processStartAddress, stopAddress = processStopAddress;

    moduleBaseAddress_ = startAddress; // used to calculate reladdr for debug purposes
    if (ScenarioHook2::attach(startAddress, stopAddress))
    {
    }
    else if (ScenarioHook1::attach(startAddress, stopAddress))
    {

      //  (PopupHook1::attach(startAddress, stopAddress));
    }
    else
      return false;
    // (OtherHook::attach(startAddress, stopAddress))

    return true;
  }

} // unnamed namespace
bool GXP::attach_function()
{
  auto _ = InsertGXPHook();
  return attach() || _;
}