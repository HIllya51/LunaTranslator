#include "5pb.h"
#include "mages/mages.h"
/** jichi 12/2/2014 5pb
 *
 *  Sample game: [140924] CROSS�CHANNEL 〜FINAL COMPLETE� *  See: http://sakuradite.com/topic/528
 *
 *  Debugging method: insert breakpoint.
 *  The first matched function cannot extract prelude text.
 *  The second matched function can extract anything but contains garbage.
 *
 *  Function for scenario:
 *  0016d90e   cc               int3
 *  0016d90f   cc               int3
 *  0016d910   8b15 782b6e06    mov edx,dword ptr ds:[0x66e2b78]         ; .00b43bfe
 *  0016d916   8a0a             mov cl,byte ptr ds:[edx]	; jichi: hook here
 *  0016d918   33c0             xor eax,eax
 *  0016d91a   84c9             test cl,cl
 *  0016d91c   74 41            je short .0016d95f
 *  0016d91e   8bff             mov edi,edi
 *  0016d920   80f9 25          cmp cl,0x25
 *  0016d923   75 11            jnz short .0016d936
 *  0016d925   8a4a 01          mov cl,byte ptr ds:[edx+0x1]
 *  0016d928   42               inc edx
 *  0016d929   80f9 4e          cmp cl,0x4e
 *  0016d92c   74 05            je short .0016d933
 *  0016d92e   80f9 6e          cmp cl,0x6e
 *  0016d931   75 26            jnz short .0016d959
 *  0016d933   42               inc edx
 *  0016d934   eb 23            jmp short .0016d959
 *  0016d936   80f9 81          cmp cl,0x81
 *  0016d939   72 05            jb short .0016d940
 *  0016d93b   80f9 9f          cmp cl,0x9f
 *  0016d93e   76 0a            jbe short .0016d94a
 *  0016d940   80f9 e0          cmp cl,0xe0
 *  0016d943   72 0c            jb short .0016d951
 *  0016d945   80f9 fc          cmp cl,0xfc
 *  0016d948   77 07            ja short .0016d951
 *  0016d94a   b9 02000000      mov ecx,0x2
 *  0016d94f   eb 05            jmp short .0016d956
 *  0016d951   b9 01000000      mov ecx,0x1
 *  0016d956   40               inc eax
 *  0016d957   03d1             add edx,ecx
 *  0016d959   8a0a             mov cl,byte ptr ds:[edx]
 *  0016d95b   84c9             test cl,cl
 *  0016d95d  ^75 c1            jnz short .0016d920
 *  0016d95f   c3               retn
 *
 *  Function for everything:
 *  001e9a76   8bff             mov edi,edi
 *  001e9a78   55               push ebp
 *  001e9a79   8bec             mov ebp,esp
 *  001e9a7b   51               push ecx
 *  001e9a7c   8365 fc 00       and dword ptr ss:[ebp-0x4],0x0
 *  001e9a80   53               push ebx
 *  001e9a81   8b5d 10          mov ebx,dword ptr ss:[ebp+0x10]
 *  001e9a84   85db             test ebx,ebx
 *  001e9a86   75 07            jnz short .001e9a8f
 *  001e9a88   33c0             xor eax,eax
 *  001e9a8a   e9 9a000000      jmp .001e9b29
 *  001e9a8f   56               push esi
 *  001e9a90   83fb 04          cmp ebx,0x4
 *  001e9a93   72 75            jb short .001e9b0a
 *  001e9a95   8d73 fc          lea esi,dword ptr ds:[ebx-0x4]
 *  001e9a98   85f6             test esi,esi
 *  001e9a9a   74 6e            je short .001e9b0a
 *  001e9a9c   8b4d 0c          mov ecx,dword ptr ss:[ebp+0xc]
 *  001e9a9f   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
 *  001e9aa2   8a10             mov dl,byte ptr ds:[eax]
 *  001e9aa4   83c0 04          add eax,0x4
 *  001e9aa7   83c1 04          add ecx,0x4
 *  001e9aaa   84d2             test dl,dl
 *  001e9aac   74 52            je short .001e9b00
 *  001e9aae   3a51 fc          cmp dl,byte ptr ds:[ecx-0x4]
 *  001e9ab1   75 4d            jnz short .001e9b00
 *  001e9ab3   8a50 fd          mov dl,byte ptr ds:[eax-0x3]
 *  001e9ab6   84d2             test dl,dl
 *  001e9ab8   74 3c            je short .001e9af6
 *  001e9aba   3a51 fd          cmp dl,byte ptr ds:[ecx-0x3]
 *  001e9abd   75 37            jnz short .001e9af6
 *  001e9abf   8a50 fe          mov dl,byte ptr ds:[eax-0x2]
 *  001e9ac2   84d2             test dl,dl
 *  001e9ac4   74 26            je short .001e9aec
 *  001e9ac6   3a51 fe          cmp dl,byte ptr ds:[ecx-0x2]
 *  001e9ac9   75 21            jnz short .001e9aec
 *  001e9acb   8a50 ff          mov dl,byte ptr ds:[eax-0x1]
 *  001e9ace   84d2             test dl,dl
 *  001e9ad0   74 10            je short .001e9ae2
 *  001e9ad2   3a51 ff          cmp dl,byte ptr ds:[ecx-0x1]
 *  001e9ad5   75 0b            jnz short .001e9ae2
 *  001e9ad7   8345 fc 04       add dword ptr ss:[ebp-0x4],0x4
 *  001e9adb   3975 fc          cmp dword ptr ss:[ebp-0x4],esi
 *  001e9ade  ^72 c2            jb short .001e9aa2
 *  001e9ae0   eb 2e            jmp short .001e9b10
 *  001e9ae2   0fb640 ff        movzx eax,byte ptr ds:[eax-0x1]
 *  001e9ae6   0fb649 ff        movzx ecx,byte ptr ds:[ecx-0x1]
 *  001e9aea   eb 46            jmp short .001e9b32
 *  001e9aec   0fb640 fe        movzx eax,byte ptr ds:[eax-0x2]
 *  001e9af0   0fb649 fe        movzx ecx,byte ptr ds:[ecx-0x2]
 *  001e9af4   eb 3c            jmp short .001e9b32
 *  001e9af6   0fb640 fd        movzx eax,byte ptr ds:[eax-0x3]
 *  001e9afa   0fb649 fd        movzx ecx,byte ptr ds:[ecx-0x3]
 *  001e9afe   eb 32            jmp short .001e9b32
 *  001e9b00   0fb640 fc        movzx eax,byte ptr ds:[eax-0x4]
 *  001e9b04   0fb649 fc        movzx ecx,byte ptr ds:[ecx-0x4]
 *  001e9b08   eb 28            jmp short .001e9b32
 *  001e9b0a   8b4d 0c          mov ecx,dword ptr ss:[ebp+0xc]
 *  001e9b0d   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
 *  001e9b10   8b75 fc          mov esi,dword ptr ss:[ebp-0x4]
 *  001e9b13   eb 0d            jmp short .001e9b22
 *  001e9b15   8a10             mov dl,byte ptr ds:[eax]    ; jichi: here, word by word
 *  001e9b17   84d2             test dl,dl
 *  001e9b19   74 11            je short .001e9b2c
 *  001e9b1b   3a11             cmp dl,byte ptr ds:[ecx]
 *  001e9b1d   75 0d            jnz short .001e9b2c
 *  001e9b1f   40               inc eax
 *  001e9b20   46               inc esi
 *  001e9b21   41               inc ecx
 *  001e9b22   3bf3             cmp esi,ebx
 *  001e9b24  ^72 ef            jb short .001e9b15
 *  001e9b26   33c0             xor eax,eax
 *  001e9b28   5e               pop esi
 *  001e9b29   5b               pop ebx
 *  001e9b2a   c9               leave
 *  001e9b2b   c3               retn
 */
namespace
{ // unnamed

  // Characters to ignore: [%0-9A-Z]
  bool Insert5pbHook1()
  {
    const BYTE bytes[] = {
        0xcc,            // 0016d90e   cc               int3
        0xcc,            // 0016d90f   cc               int3
        0x8b, 0x15, XX4, // 0016d910   8b15 782b6e06    mov edx,dword ptr ds:[0x66e2b78]         ; .00b43bfe
        0x8a, 0x0a,      // 0016d916   8a0a             mov cl,byte ptr ds:[edx]	; jichi: hook here
        0x33, 0xc0,      // 0016d918   33c0             xor eax,eax
        0x84, 0xc9       // 0016d91a   84c9             test cl,cl
    };
    enum
    {
      addr_offset = 0x0016d916 - 0x0016d90e
    };

    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    // GROWL_DWORD3(addr+addr_offset, processStartAddress,processStopAddress);
    if (!addr)
    {
      return false;
    }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING;
    return NewHook(hp, "5pb1");
  }

  // Characters to ignore: [%@A-z]
  inline bool _5pb2garbage_ch(char c)
  {
    return c == '%' || c == '@' || c >= 'A' && c <= 'z';
  }

  // 001e9b15   8a10             mov dl,byte ptr ds:[eax]    ; jichi: here, word by word
  void SpecialHook5pb2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static DWORD lasttext;
    DWORD text = context->eax;
    if (lasttext == text)
      return;
    BYTE c = *(BYTE *)text;
    if (!c)
      return;
    BYTE size = ::LeadByteTable[c]; // 1, 2, or 3
    if (size == 1 && _5pb2garbage_ch(*(LPCSTR)text))
      return;
    lasttext = text;
    buffer->from(text, size);
  }

  bool Insert5pbHook2()
  {
    const BYTE bytes[] = {
        0x8a, 0x10, // 001e9b15   8a10             mov dl,byte ptr ds:[eax]    ; jichi: here, word by word
        0x84, 0xd2, // 001e9b17   84d2             test dl,dl
        0x74, 0x11  // 001e9b19   74 11            je short .001e9b2c
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    // GROWL_DWORD3(addr, processStartAddress,processStopAddress);
    if (!addr)
    {
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | NO_CONTEXT;
    hp.text_fun = SpecialHook5pb2;
    return NewHook(hp, "5pb2");
  }

  /** jichi 2/2/2015: New 5pb hook
   *  Sample game: Hyperdimension.Neptunia.ReBirth1
   *
   *  Debugging method: hardware breakpoint and find function in msvc110
   *  Then, backtrack the function stack to find proper function.
   *
   *  Hooked function: 558BEC56FF750C8BF1FF75088D460850
   *
   *  0025A12E   CC               INT3
   *  0025A12F   CC               INT3
   *  0025A130   55               PUSH EBP
   *  0025A131   8BEC             MOV EBP,ESP
   *  0025A133   56               PUSH ESI
   *  0025A134   FF75 0C          PUSH DWORD PTR SS:[EBP+0xC]
   *  0025A137   8BF1             MOV ESI,ECX
   *  0025A139   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
   *  0025A13C   8D46 08          LEA EAX,DWORD PTR DS:[ESI+0x8]
   *  0025A13F   50               PUSH EAX
   *  0025A140   E8 DB100100      CALL .0026B220
   *  0025A145   8B8E 988D0000    MOV ECX,DWORD PTR DS:[ESI+0x8D98]
   *  0025A14B   8988 80020000    MOV DWORD PTR DS:[EAX+0x280],ECX
   *  0025A151   8B8E A08D0000    MOV ECX,DWORD PTR DS:[ESI+0x8DA0]
   *  0025A157   8988 88020000    MOV DWORD PTR DS:[EAX+0x288],ECX
   *  0025A15D   8B8E A88D0000    MOV ECX,DWORD PTR DS:[ESI+0x8DA8]
   *  0025A163   8988 90020000    MOV DWORD PTR DS:[EAX+0x290],ECX
   *  0025A169   8B8E B08D0000    MOV ECX,DWORD PTR DS:[ESI+0x8DB0]
   *  0025A16F   8988 98020000    MOV DWORD PTR DS:[EAX+0x298],ECX
   *  0025A175   83C4 0C          ADD ESP,0xC
   *  0025A178   8D8E 188B0000    LEA ECX,DWORD PTR DS:[ESI+0x8B18]
   *  0025A17E   E8 DDD8FEFF      CALL .00247A60
   *  0025A183   5E               POP ESI
   *  0025A184   5D               POP EBP
   *  0025A185   C2 0800          RETN 0x8
   *  0025A188   CC               INT3
   *  0025A189   CC               INT3
   *
   *  Runtime stack, text in arg1, and name in arg2:
   *
   *  0015F93C   00252330  RETURN to .00252330 from .0025A130
   *  0015F940   181D0D4C  ASCII "That's my line! I won't let any of you
   *  take the title of True Goddess!"
   *  0015F944   0B8B4D20  ASCII "  White Heart  "
   *  0015F948   0B8B5528
   *  0015F94C   0B8B5524
   *  0015F950  /0015F980
   *  0015F954  |0026000F  RETURN to .0026000F from .002521D0
   *
   *
   *  Another candidate funciton for backup usage.
   *  Previous text in arg1.
   *  Current text in arg2.
   *  Current name in arg3.
   *
   *  0026B21C   CC               INT3
   *  0026B21D   CC               INT3
   *  0026B21E   CC               INT3
   *  0026B21F   CC               INT3
   *  0026B220   55               PUSH EBP
   *  0026B221   8BEC             MOV EBP,ESP
   *  0026B223   81EC A0020000    SUB ESP,0x2A0
   *  0026B229   BA A0020000      MOV EDX,0x2A0
   *  0026B22E   53               PUSH EBX
   *  0026B22F   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
   *  0026B232   56               PUSH ESI
   *  0026B233   57               PUSH EDI
   *  0026B234   8D041A           LEA EAX,DWORD PTR DS:[EDX+EBX]
   *  0026B237   B9 A8000000      MOV ECX,0xA8
   *  0026B23C   8BF3             MOV ESI,EBX
   *  0026B23E   8DBD 60FDFFFF    LEA EDI,DWORD PTR SS:[EBP-0x2A0]
   *  0026B244   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
   *  0026B246   B9 A8000000      MOV ECX,0xA8
   *  0026B24B   8BF0             MOV ESI,EAX
   *  0026B24D   8BFB             MOV EDI,EBX
   *  0026B24F   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
   *  0026B251   81C2 A0020000    ADD EDX,0x2A0
   *  0026B257   B9 A8000000      MOV ECX,0xA8
   *  0026B25C   8DB5 60FDFFFF    LEA ESI,DWORD PTR SS:[EBP-0x2A0]
   *  0026B262   8BF8             MOV EDI,EAX
   *  0026B264   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
   *  0026B266   81FA 40830000    CMP EDX,0x8340
   *  0026B26C  ^7C C6            JL SHORT .0026B234
   *  0026B26E   8BCB             MOV ECX,EBX
   *  0026B270   E8 EBC7FDFF      CALL .00247A60
   *  0026B275   FF75 0C          PUSH DWORD PTR SS:[EBP+0xC]
   *  0026B278   8B35 D8525000    MOV ESI,DWORD PTR DS:[0x5052D8]          ; msvcr110.sprintf
   *  0026B27E   68 805C5000      PUSH .00505C80                           ; ASCII "%s"
   *  0026B283   53               PUSH EBX
   *  0026B284   FFD6             CALL ESI
   *  0026B286   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
   *  0026B289   8D83 00020000    LEA EAX,DWORD PTR DS:[EBX+0x200]
   *  0026B28F   68 805C5000      PUSH .00505C80                           ; ASCII "%s"
   *  0026B294   50               PUSH EAX
   *  0026B295   FFD6             CALL ESI
   *  0026B297   83C4 18          ADD ESP,0x18
   *  0026B29A   8BC3             MOV EAX,EBX
   *  0026B29C   5F               POP EDI
   *  0026B29D   5E               POP ESI
   *  0026B29E   5B               POP EBX
   *  0026B29F   8BE5             MOV ESP,EBP
   *  0026B2A1   5D               POP EBP
   *  0026B2A2   C3               RETN
   *  0026B2A3   CC               INT3
   *  0026B2A4   CC               INT3
   *  0026B2A5   CC               INT3
   *  0026B2A6   CC               INT3
   */
  void SpecialHook5pb3(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    int index = 0;
    // Text in arg1, name in arg2
    if (LPCSTR text = (LPCSTR)context->stack[index + 1])
      if (*text)
      {
        if (index) // trim spaces in character name
          while (*text == ' ')
            text++;
        size_t sz = ::strlen(text);
        if (index)
          while (sz && text[sz - 1] == ' ')
            sz--;
        *split = FIXED_SPLIT_VALUE << index;
        buffer->from(text, sz);
      }
  }
  bool Insert5pbHook3()
  {
    const BYTE bytes[] = {
        // function starts
        0x55,             // 0025A130   55               PUSH EBP
        0x8b, 0xec,       // 0025A131   8BEC             MOV EBP,ESP
        0x56,             // 0025A133   56               PUSH ESI
        0xff, 0x75, 0x0c, // 0025A134   FF75 0C          PUSH DWORD PTR SS:[EBP+0xC]
        0x8b, 0xf1,       // 0025A137   8BF1             MOV ESI,ECX
        0xff, 0x75, 0x08, // 0025A139   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
        0x8d, 0x46, 0x08, // 0025A13C   8D46 08          LEA EAX,DWORD PTR DS:[ESI+0x8]
        0x50,             // 0025A13F   50               PUSH EAX
        0xe8              // 0025A140   E8 DB100100      CALL .0026B220
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    // GROWL_DWORD3(addr, processStartAddress,processStopAddress);
    if (!addr)
    {
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | NO_CONTEXT;
    hp.text_fun = SpecialHook5pb3;
    hp.filter_fun = NewLineCharToSpaceA; // replace '\n' by ' '
    return NewHook(hp, "5pb3");
  }
} // unnamed namespace
namespace
{
  // https://store.steampowered.com/app/589530/Hakuoki_Kyoto_Winds/
  bool hook4name()
  {
    const BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0x51,
        0x53,
        0x8b, 0x5d, 0x08,
        0x85, 0xdb,
        0x0f, 0x84, XX4,
        0x8b, 0x4d, 0x0c,
        0x8d, 0x53, XX,
        0x56,
        0x57,
        0x83, 0xcf, 0xff,
        0x33, 0xf6,
        0x8d, 0x49, 0x00,
        0x3b, 0x4a, 0xf8,
        0x74, XX,
        0x85, 0xff,
        0x79, XX};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8;
    hp.offset = stackoffset(3);
    return NewHook(hp, "5pb4");
  }
  bool hook4text()
  {
    const BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0xb8, 0x14, 0x10, 0x00, 0x00,
        0xe8, XX4,
        0xa1, XX4,
        0x33, 0xc5,
        0x89, 0x45, 0xfc,
        0x56,
        0x8b, 0x75, 0x08,
        0x8d, 0x85, XX4,
        0x57,
        0x68, 0xff, 0x0f, 0x00, 0x00,
        0x6a, 0x00,
        0x50,
        0x8b, 0xf9,
        0xc6, 0x85, XX4, 0x00,
        0xe8, XX4};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8;
    hp.offset = stackoffset(1);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      StringCharReplacer(buffer, TEXTANDLEN("#n"), ' ');
      StringFilter(buffer, TEXTANDLEN("#I"));
    };
    return NewHook(hp, "5pb4");
  }
  bool hook4()
  {
    return hook4name() && hook4text();
  }
}
bool Insert5pbHook()
{
  bool ok = Insert5pbHook1();
  ok = Insert5pbHook2() || ok;
  ok = Insert5pbHook3() || ok;
  return ok || hook4();
}
bool Insert5pbHookex()
{
  // 祝姬
  const BYTE bytes[] = {
      0x0F, 0xB6, 0xC2, 0x35, 0xC5, 0x9D, 0x1C, 0x81};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  const BYTE start[] = {
      0x55, 0x8b, 0xec, 0x83, 0xe4};
  addr = reverseFindBytes(start, sizeof(start), addr - 0x40, addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(ecx);
  hp.type = CODEC_UTF16;

  return NewHook(hp, "5pb");
}

bool InsertStuffScriptHook()
{
  // BOOL GetTextExtentPoint32(
  //   _In_   HDC hdc,
  //   _In_   LPCTSTR lpString,
  //   _In_   int c,
  //   _Out_  LPSIZE lpSize
  // );
  HookParam hp;
  hp.address = (DWORD)::GetTextExtentPoint32A;
  hp.offset = stackoffset(2); // arg2 lpString
  hp.split = regoffset(esp);
  hp.type = USING_STRING | USING_SPLIT;
  return NewHook(hp, "StuffScriptEngine");
  // RegisterEngine(ENGINE_STUFFSCRIPT);
}
void StuffScript2Filter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);

  if (text[0] == '-')
  {
    StringFilter(buffer, TEXTANDLEN("-/-"));
    StringFilterBetween(buffer, TEXTANDLEN("-"), TEXTANDLEN("-"));
  }
  StringCharReplacer(buffer, TEXTANDLEN("_n_r"), '\n');
  StringCharReplacer(buffer, TEXTANDLEN("_r"), ' ');
  StringFilter(buffer, TEXTANDLEN("\\n"));
  StringFilter(buffer, TEXTANDLEN("_n"));
}
bool InsertStuffScript2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/r41537
   * https://vndb.org/r41539
   */
  const BYTE bytes[] = {
      0x0F, XX, XX4,    // jne tokyobabel.exe+3D4E8
      0xB9, XX4,        // mov ecx,tokyobabel.exe+54EAC
      0x8D, 0x85, XX4,  // lea eax,[ebp+tokyobabel.exe+59B968]
      0x8A, 0x10,       // mov dl,[eax]                         <-- hook here
      0x3A, 0x11,       // cmp dl,[ecx]
      0x75, 0x1A,       // jne tokyobabel.exe+3D1D7
      0x84, 0xD2,       // test dl,dl
      0x74, 0x12,       // je tokyobabel.exe+3D1D3
      0x8A, 0x50, 0x01, // mov dl,[eax+01]
      0x3A, 0x51, 0x01, // cmp dl,[ecx+01]
      0x75, 0x0E,       // jne tokyobabel.exe+3D1D7
      0x83, 0xC0, 0x02, // add eax,02
      0x83, 0xC1, 0x02, // add ecx,02
      0x84, 0xD2,       // test dl,dl
      0x75, 0xE4,       // jne Agreement.exe+4F538
      0x33, 0xC0,       // xor eax,eax
      0xEB, 0x05,       // jmp Agreement.exe+4F55D
      0x1B, 0xC0,       // sbb eax,eax
      0x83, 0xD8, 0xFF, // sbb eax,-01
      XX2,              // cmp eax,edi
      0x0F, 0x84, XX4   // je tokyobabel.exe+3D4E8
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 0x11;
  hp.offset = regoffset(eax);
  hp.index = 0;
  hp.type = USING_STRING | NO_CONTEXT;
  hp.filter_fun = StuffScript2Filter;
  return NewHook(hp, "StuffScript2");
}
void StuffScript3Filter(TextBuffer *buffer, HookParam *)
{

  StringFilterBetween(buffer, TEXTANDLEN("/\x81\x79"), TEXTANDLEN("\x81\x7A")); // remove hidden name
  StringFilterBetween(buffer, TEXTANDLEN("["), TEXTANDLEN("]"));                // garbage

  // ruby
  CharFilter(buffer, '<');
  StringFilterBetween(buffer, TEXTANDLEN(","), TEXTANDLEN(">"));

  StringFilter(buffer, TEXTANDLEN("_r\x81\x40"));
  StringFilter(buffer, TEXTANDLEN("_r"));
}
bool InsertStuffScript3Hook()
{
  /*
   * Sample games:
   * https://vndb.org/v3111
   */
  const BYTE bytes[] = {
      0xCC,                  // int 3
      0x81, 0xEC, XX4,       // sub esp,00000140          <-- hook here
      0xA1, XX4,             // mov eax,[EVOLIMIT.exe+8C1F0]
      0x33, 0xC4,            // xor eax,esp
      0x89, 0x84, 0x24, XX4, // mov [esp+0000013C],eax
      0x53,                  // push ebx
      0x55,                  // push ebp
      0x8B, 0xAC, 0x24, XX4, // mov ebp,[esp+0000014C]
      0x8B, 0x45, 0x2C       // mov eax,[ebp+2C]
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = regoffset(ecx);
  hp.type = USING_STRING | NO_CONTEXT;
  hp.filter_fun = StuffScript3Filter;
  return NewHook(hp, "StuffScript3");
}
namespace
{
  bool hook1()
  {
    // https://vndb.org/v445
    // Bullet Butlers

    char sss[] = "%s%s%s";
    auto aSSS = MemDbg::findBytes(sss, sizeof(sss), processStartAddress, processStopAddress);
    if (!aSSS)
      return false;
    auto pushasss = MemDbg::find_leaorpush_addr_all(aSSS, processStartAddress, processStopAddress);
    if (pushasss.size() != 3)
      return false;
    if (pushasss[1] - pushasss[0] > 0x40)
      return false;
    const BYTE bytes[] = {
        0x8a, 0x11,
        0x88, 0x14, 0x08,
        0x41,
        0x84, 0xd2,
        0x75, 0xf6};
    ULONG addr = reverseFindBytes(bytes, sizeof(bytes), pushasss[0] - 0x400, pushasss[0]);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x180);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING; // 主界面可以内嵌，但开启内嵌后，打开history会直接闪退，放弃。
    hp.filter_fun = StuffScript3Filter;
    return NewHook(hp, "StuffScript4");
  }
}
bool StuffScript_attach_function()
{
  auto _ = hook1() || InsertStuffScriptHook();
  _ |= InsertStuffScript2Hook();
  _ |= InsertStuffScript3Hook();
  return _;
}
bool _5pb::attach_function()
{
  bool b1 = Insert5pbHook();
  bool b2 = Insert5pbHookex();
  bool b3 = hookmages::MAGES();
  bool sf = StuffScript_attach_function();
  return b1 || b2 || b3 || sf;
}

void KaleidoFilter(TextBuffer *buffer, HookParam *)
{
  // Unofficial eng TL with garbage newline spaces
  StringFilter(buffer, TEXTANDLEN(" \\n "));
  StringFilter(buffer, TEXTANDLEN(" \\n"));
  StringFilter(buffer, TEXTANDLEN("\\n"));
  StringCharReplacer(buffer, TEXTANDLEN("\xEF\xBC\x9F"), '?');
  auto s = buffer->strA();
  s = re::sub(s, "#[0-9a-f]{6};(.*?)%r", "$1");
  s = re::sub(s, "%t\\d+;");
  buffer->from(s);
}

bool InsertKaleidoHook()
{

  /*
   * Sample games:
   * https://vndb.org/v29889
   */
  const BYTE bytes[] = {
      0xFF, 0x75, 0xD4,      // push [ebp-2C]
      0xE8, XX4,             // call 5toubun.exe+1DD0
      0x83, 0xC4, 0x0C,      // add esp,0C
      0x8A, 0xC3,            // mov al,bl
      0x8B, 0x4D, 0xF4,      // mov ecx,[ebp-0C]
      0x64, 0x89, 0x0D, XX4, // mov fs:[00000000],ecx
      0x59                   // pop ecx          << hook here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 1
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(esi);
  hp.index = 0;
  hp.split = stackoffset(3);
  hp.split_index = 0;
  hp.type = USING_STRING | USING_SPLIT | CODEC_UTF8;
  hp.filter_fun = KaleidoFilter;
  return NewHook(hp, "Kaleido");
}
namespace
{ // ANONYMOUS;CODE 官中
  bool __1()
  {
    BYTE bytes[] = {
        0x8d, 0x45, 0xf4, 0x64, 0xA3, 0x00, 0x00, 0x00, 0x00, 0x8b, 0xf1, 0x8a, 0x46, 0x2c, 0x8b, 0x55, 0x08, 0x84, 0xc0, 0x74, 0x04, 0x32, 0xc0};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | CODEC_UTF8 | EMBED_ABLE | EMBED_AFTER_NEW;
    hp.lineSeparator = L"\\n";
    return NewHook(hp, "5bp");
  }
  bool __()
  {
    BYTE sig1[] = {
        0x81, 0xFE, 0xF0, 0x00, 0x00, 0x00};
    BYTE sig2[] = {
        0x81, 0xFE, 0xF8, 0x00, 0x00, 0x00};
    BYTE sig3[] = {
        0x81, 0xFE, 0xFC, 0x00, 0x00, 0x00};
    BYTE sig4[] = {
        0x81, 0xFE, 0xFE, 0x00, 0x00, 0x00};
    BYTE sig5[] = {
        0x81, 0xFE, 0x80, 0x00, 0x00, 0x00};
    BYTE sig6[] = {
        0x81, 0xFE, 0xE0, 0x00, 0x00, 0x00};
    std::unordered_map<uintptr_t, int> addr_hit;
    for (auto sigsz : std::vector<std::pair<BYTE *, int>>{{sig1, sizeof(sig1)}, {sig2, sizeof(sig2)}, {sig3, sizeof(sig3)}, {sig4, sizeof(sig4)}, {sig5, sizeof(sig5)}, {sig6, sizeof(sig6)}})
    {
      for (auto addr : Util::SearchMemory(sigsz.first, sigsz.second, PAGE_EXECUTE, processStartAddress, processStopAddress))
      {
        addr = MemDbg::findEnclosingAlignedFunction(addr);
        if (!addr)
          continue;
        if (!addr_hit.count(addr))
        {
          addr_hit[addr] = 1;
        }
        else
          addr_hit[addr] += 1;
      }
    }
    DWORD addr = 0;
    int m = 0;
    for (auto _ : addr_hit)
    {
      if (_.second > m)
      {
        m = _.second;
        addr = _.first;
      }
    }
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | CODEC_UTF8;
    hp.filter_fun = KaleidoFilter;
    return NewHook(hp, "5bp");
  }
} // namespace name
namespace
{
  bool __2()
  {
    // レヱル・ロマネスク origin 多国語版
    // https://vndb.org/r119877
    // char __thiscall sub_426B70(float *this, int a2, int a3, int a4, int a5, char a6, char a7)
    BYTE bytes[] = {
        0x0f, 0xb7, 0x04, 0x72,
        0x46,
        0x89, 0x85, XX4,
        0x0f, 0xb7, 0xc0,
        0x83, 0xc0, 0xf6,
        0x83, 0xf8, 0x52,
        0x0f, 0x87};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.split = stackoffset(2);
    hp.type = USING_SPLIT | USING_STRING | FULL_STRING | CODEC_UTF16 | EMBED_ABLE | EMBED_AFTER_NEW; // 中文显示不出来
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      // そうして、[おひとよ,2]御一夜――\n眼下に広がるこの町も、僕を間違いなく救ってくれた。
      // 「行政に関しての最大の変化は、市長です。\n現在の市長には[ひない,1]雛衣・ポーレットが就任しています」
      // 「なるほど。それゆえ、御一夜は衰退し、\n\x%lエアクラ;#00ffc040;エアクラ%l;#;工場の誘致話が持ち上がったわけか？」
      // 「ナビ。お前も\x%lエアクラ;#00ffc040;エアクラ%l;#;の仲間だったな。\n気を悪くしたか？」
      auto xx = buffer->strW();
      xx = re::sub(xx, L"\\[(.*?),\\d\\]", L"$1");
      xx = re::sub(xx, L"\\\\x%l(.*?);(.*?);(.*?);#;", L"$1");
      buffer->from(xx);
    };
    hp.lineSeparator = L"\\n";
    return NewHook(hp, "5bp");
  }

}

bool _5pb_2::attach_function()
{
  bool ___1 = __1() || __();
  ___1 |= __2();
  return InsertKaleidoHook() || ___1;
}