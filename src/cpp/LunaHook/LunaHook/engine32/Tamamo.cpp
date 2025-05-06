#include "Tamamo.h"

/** jichi 8/23/2015 Tamamo
 *  Sample game: 閃光の騎士 ～カリスティアナイト～ Ver1.03
 *
 *  Debugging method: insert hw breakpoint to the text in memory
 *
 *  006107A6   76 08              JBE SHORT .006107B0
 *  006107A8   3BF8               CMP EDI,EAX
 *  006107AA   0F82 68030000      JB .00610B18
 *  006107B0   0FBA25 F88E7300 01 BT DWORD PTR DS:[0x738EF8],0x1
 *  006107B8   73 07              JNB SHORT .006107C1
 *  006107BA   F3:A4              REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI] ; jichi: accessed here
 *  006107BC   E9 17030000        JMP .00610AD8
 *  006107C1   81F9 80000000      CMP ECX,0x80
 *  006107C7   0F82 CE010000      JB .0061099B
 *  006107CD   8BC7               MOV EAX,EDI
 *  006107CF   33C6               XOR EAX,ESI
 *  006107D1   A9 0F000000        TEST EAX,0xF
 *  006107D6   75 0E              JNZ SHORT .006107E6
 *
 *  0012FD7C   0012FE1C
 *  0012FD80   00000059
 *  0012FD84   0051C298  RETURN to .0051C298 from .00610790
 *  0012FD88   0207E490	; jichi: target
 *  0012FD8C   0C0BE768	; jichi: source text
 *  0012FD90   00000059	; jichi: source size
 *  0012FD94   002A7C58
 *  0012FD98   0C1E7338
 *  0012FD9C   0012FE1C
 *  0012FDA0  /0012FDC0 ; jichi: split
 *  0012FDA4  |0056A83F  RETURN to .0056A83F from .0051C1C0
 *  0012FDA8  |0C1E733C
 *  0012FDAC  |00000000
 *  0012FDB0  |FFFFFFFF
 *  0012FDB4  |020EDAD0
 *  0012FDB8  |0220CC28
 *  0012FDBC  |020EDAD0
 *  0012FDC0  ]0012FE44
 *  0012FDC4  |0055EF84  RETURN to .0055EF84 from .0056A7B0
 *  0012FDC8  |0012FE1C
 *  0012FDCC  |ED1BC1C5
 *  0012FDD0  |020EDAD0
 *  0012FDD4  |002998A8
 *  0012FDD8  |020EDAD0
 *
 *  Hooked call:
 *  0051C283   5D               POP EBP
 *  0051C284   C2 0C00          RETN 0xC
 *  0051C287   8BD6             MOV EDX,ESI
 *  0051C289   85FF             TEST EDI,EDI
 *  0051C28B   74 0E            JE SHORT .0051C29B
 *  0051C28D   57               PUSH EDI
 *  0051C28E   8D040B           LEA EAX,DWORD PTR DS:[EBX+ECX]
 *  0051C291   50               PUSH EAX
 *  0051C292   52               PUSH EDX
 *  0051C293   E8 F8440F00      CALL .00610790    ; jichi: copy invoked here
 *  0051C298   83C4 0C          ADD ESP,0xC
 *  0051C29B   837E 14 10       CMP DWORD PTR DS:[ESI+0x14],0x10
 *  0051C29F   897E 10          MOV DWORD PTR DS:[ESI+0x10],EDI
 *  0051C2A2   72 0F            JB SHORT .0051C2B3
 *  0051C2A4   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  0051C2A6   C60438 00        MOV BYTE PTR DS:[EAX+EDI],0x0
 *  0051C2AA   8BC6             MOV EAX,ESI
 *  0051C2AC   5F               POP EDI
 *  0051C2AD   5E               POP ESI
 *  0051C2AE   5B               POP EBX
 *  0051C2AF   5D               POP EBP
 *  0051C2B0   C2 0C00          RETN 0xC
 *  0051C2B3   8BC6             MOV EAX,ESI
 *
 *  Sample text with new lines:
 *
 *  0C0BE748  70 00 69 00 2E 00 64 00 6C 00 6C 00 00 00 6C 00  p.i...d.l.l...l.
 *  0C0BE758  00 00 00 00 0F 00 00 00 8B 91 3F 66 00 00 00 88  .......拒?f...・
 *  0C0BE768  83 4E 83 8B 83 67 83 93 81 75 8E 84 82 C9 82 CD  クルトン「私には
 *  0C0BE778  95 90 91 95 82 AA 82 C2 82 A2 82 C4 82 A2 82 DC  武装がついていま
 *  0C0BE788  82 B9 82 F1 82 A9 82 E7 81 41 0D 0A 81 40 8D 55  せんから、..　攻
 *  0C0BE798  82 DF 82 C4 82 B1 82 E7 82 EA 82 BD 82 E7 82 D0  めてこられたらひ
 *  0C0BE7A8  82 C6 82 BD 82 DC 82 E8 82 E0 82 A0 82 E8 82 DC  とたまりもありま
 *  0C0BE7B8  82 B9 82 F1 81 76 3C 65 3E 00 3E 00 3E 00 00 00  せん」<e>.>.>...
 *  0C0BE7C8  9E 91 3F 66 99 82 00 88 83 53 83 8D 81 5B 83 93  梠?f凾.・Sローン
 *  0C0BE7D8  8C 5A 81 75 82 D6 82 D6 81 42 95 D4 82 B5 82 C4  兄「へへ。返して
 *  0C0BE7E8  82 D9 82 B5 82 AF 82 E8 82 E1 82 C2 82 A2 82 C4  ほしけりゃついて
 *  0C0BE7F8  82 AB 82 C8 81 42 83 49 83 8C 82 B3 82 DC 82 CC  きな。オレさまの
 *
 *  Sample game: 冒険者の町を作ろう!2 Ver1.01
 *
 *  0068028B   CC               INT3
 *  0068028C   CC               INT3
 *  0068028D   CC               INT3
 *  0068028E   CC               INT3
 *  0068028F   CC               INT3
 *  00680290   55               PUSH EBP
 *  00680291   8BEC             MOV EBP,ESP
 *  00680293   57               PUSH EDI
 *  00680294   56               PUSH ESI
 *  00680295   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
 *  00680298   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
 *  0068029B   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  0068029E   8BC1             MOV EAX,ECX
 *  006802A0   8BD1             MOV EDX,ECX
 *  006802A2   03C6             ADD EAX,ESI
 *  006802A4   3BFE             CMP EDI,ESI
 *  006802A6   76 08            JBE SHORT .006802B0
 *  006802A8   3BF8             CMP EDI,EAX
 *  006802AA   0F82 A4010000    JB .00680454
 *  006802B0   81F9 00010000    CMP ECX,0x100
 *  006802B6   72 1F            JB SHORT .006802D7
 *  006802B8   833D 64FB8C00 00 CMP DWORD PTR DS:[0x8CFB64],0x0
 *  006802BF   74 16            JE SHORT .006802D7
 *  006802C1   57               PUSH EDI
 *  006802C2   56               PUSH ESI
 *  006802C3   83E7 0F          AND EDI,0xF
 *  006802C6   83E6 0F          AND ESI,0xF
 *  006802C9   3BFE             CMP EDI,ESI
 *  006802CB   5E               POP ESI
 *  006802CC   5F               POP EDI
 *  006802CD   75 08            JNZ SHORT .006802D7
 *  006802CF   5E               POP ESI
 *  006802D0   5F               POP EDI
 *  006802D1   5D               POP EBP
 *  006802D2   E9 FC090100      JMP .00690CD3
 *  006802D7   F7C7 03000000    TEST EDI,0x3
 *  006802DD   75 15            JNZ SHORT .006802F4
 *  006802DF   C1E9 02          SHR ECX,0x2
 *  006802E2   83E2 03          AND EDX,0x3
 *  006802E5   83F9 08          CMP ECX,0x8
 *  006802E8   72 2A            JB SHORT .00680314
 *  006802EA   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]  jichi: here
 *  006802EC   FF2495 04046800  JMP DWORD PTR DS:[EDX*4+0x680404]
 *  006802F3   90               NOP
 *  006802F4   8BC7             MOV EAX,EDI
 *  006802F6   BA 03000000      MOV EDX,0x3
 *  006802FB   83E9 04          SUB ECX,0x4
 *  006802FE   72 0C            JB SHORT .0068030C
 *  00680300   83E0 03          AND EAX,0x3
 *  00680303   03C8             ADD ECX,EAX
 *  00680305   FF2485 18036800  JMP DWORD PTR DS:[EAX*4+0x680318]
 *  0068030C   FF248D 14046800  JMP DWORD PTR DS:[ECX*4+0x680414]
 *  00680313   90               NOP
 *  00680314   FF248D 98036800  JMP DWORD PTR DS:[ECX*4+0x680398]
 *  0068031B   90               NOP
 *  0068031C   2803             SUB BYTE PTR DS:[EBX],AL
 *  0068031E   68 00540368      PUSH 0x68035400
 *  00680323   0078 03          ADD BYTE PTR DS:[EAX+0x3],BH
 *  00680326   68 0023D18A      PUSH 0x8AD12300
 *  0068032B   06               PUSH ES
 *  0068032C   8807             MOV BYTE PTR DS:[EDI],AL
 *  0068032E   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  00680331   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
 *  00680334   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
 *
 *  0067FA4F   8BC6             MOV EAX,ESI
 *  0067FA51   EB 45            JMP SHORT .0067FA98
 *  0067FA53   397D 10          CMP DWORD PTR SS:[EBP+0x10],EDI
 *  0067FA56   74 16            JE SHORT .0067FA6E
 *  0067FA58   3975 0C          CMP DWORD PTR SS:[EBP+0xC],ESI
 *  0067FA5B   72 11            JB SHORT .0067FA6E
 *  0067FA5D   56               PUSH ESI
 *  0067FA5E   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
 *  0067FA61   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
 *  0067FA64   E8 27080000      CALL .00680290  ; jichi: copy invoked here
 *  0067FA69   83C4 0C          ADD ESP,0xC
 *  0067FA6C  ^EB C1            JMP SHORT .0067FA2F
 *  0067FA6E   FF75 0C          PUSH DWORD PTR SS:[EBP+0xC]
 *  0067FA71   57               PUSH EDI
 *  0067FA72   FF75 08          PUSH DWORD PTR SS:[EBP+0x8]
 *
 * 0012FC04   00000059
 * 0012FC08   00000000
 * 0012FC0C  /0012FC28
 * 0012FC10  |0067FA69  RETURN to .0067FA69 from .00680290
 * 0012FC14  |072CEF78  ; jichi: target text
 * 0012FC18  |07261840	; jichi: source text
 * 0012FC1C  |00000059	; jichi: source size
 * 0012FC20  |FFFFFFFE
 * 0012FC24  |00000000
 * 0012FC28  ]0012FC40  ; jichi: split
 * 0012FC2C  |00404E58  RETURN to .00404E58 from .0067FA1F
 * 0012FC30  |072CEF78	; jichi: target text
 * 0012FC34  |0000005F	; jichi: target capacity
 * 0012FC38  |07261840	; jichi: source text
 * 0012FC3C  |00000059	; jichi: source size
 * 0012FC40  ]0012FC58
 * 0012FC44  |00404E38  RETURN to .00404E38 from .00404E40
 * 0012FC48  |072CEF78
 * 0012FC4C  |0000005F
 * 0012FC50  |07261840
 * 0012FC54  |00000059
 * 0012FC58  ]0012FC78
 * 0012FC5C  |00404B06  RETURN to .00404B06 from .00404E20
 * 0012FC60  |072CEF78
 * 0012FC64  |0000005F
 * 0012FC68  |07261840
 * 0012FC6C  |00000059
 * 0012FC70  |00000000
 * 0012FC74  |0012FD30
 * 0012FC78  ]0012FC98
 * 0012FC7C  |004025FE  RETURN to .004025FE from .00404AE0
 * 0012FC80  |072CEF78
 * 0012FC84  |0000005F
 * 0012FC88  |07261840
 * 0012FC8C  |00000059
 * 0012FC90  |0012FD30
 * 0012FC94  |00000059
 * 0012FC98  ]0012FCB0
 * 0012FC9C  |0040254B  RETURN to .0040254B from .00402560
 * 0012FCA0  |074B6EA4
 * 0012FCA4  |00000000
 * 0012FCA8  |FFFFFFFF
 *
 * 07261840  83 4A 83 43 81 75 82 A0 82 C6 82 CD 82 B1 82 EA  カイ「あとはこれ
 * 07261850  82 C9 81 41 91 BA 92 B7 82 CC 83 54 83 43 83 93  に、村長のサイン
 * 07261860  82 C6 88 F3 8A D3 82 F0 81 63 81 63 82 C1 82 C6  と印鑑を……っと
 * 07261870  81 42 0D 0A 81 40 82 6E 82 6A 81 41 82 AB 82 E5  。..　ＯＫ、きょ
 * 07261880  82 A4 82 CC 83 66 83 58 83 4E 83 8F 81 5B 83 4E  うのデスクワーク
 * 07261890  8F 49 97 B9 81 76 3C 65 3E 00 81 76 3C 65 3E 00  終了」<e>.」<e>.
 * 072618A0  98 DD 95 48 00 40 00 88 83 4A 83 43 81 75 81 63  俤菱.@.・Jイ「…
 * 072618B0  81 63 82 A4 82 F1 81 41 82 BB 82 A4 82 B5 82 E6  …うん、そうしよ
 */
namespace
{ // unnamed
  void TamamoFilter(TextBuffer *buffer, HookParam *)
  {
    LPSTR text = (LPSTR)buffer->buff;
    if (::memchr(text, '<', buffer->size))
      StringFilter(buffer, TEXTANDLEN("<e>"));
    StringFilter(buffer, TEXTANDLEN("\x0d\x0a\x81\x40")); // remove \n before space
    StringFilterBetween(buffer, TEXTANDLEN("<"), TEXTANDLEN(">"));
    StringFilterBetween(buffer, TEXTANDLEN("{"), TEXTANDLEN("}"));
  }
  void SpecialHookTamamo(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto text = (LPCSTR)context->stack[1]; // arg2
    auto size = context->stack[2];         // arg3
    if (0 < size && size < VNR_TEXT_CAPACITY && size == ::strlen(text) && !all_ascii(text))
    {

      //*len = argof(esp_base, 3 - 1);

      //*split = argof(8 - 1, esp_base); // use parent return address as split
      //*split = argof(7 - 1, esp_base); // use the address just before parent retaddr
      *split = context->stack[5];
      // if (hp.split)
      //   *split = *(DWORD *)(esp_base + hp.split);
      buffer->from(text, size);
    }
  }
} // unnamed namespace
bool InsertTamamoHook()
{
  ULONG addr = 0;
  { // for new games
    const BYTE bytes[] = {
        0x8b, 0xd6,       // 0051c287   8bd6             mov edx,esi
        0x85, 0xff,       // 0051c289   85ff             test edi,edi
        0x74, 0x0e,       // 0051c28b   74 0e            je short .0051c29b
        0x57,             // 0051c28d   57               push edi
        0x8d, 0x04, 0x0b, // 0051c28e   8d040b           lea eax,dword ptr ds:[ebx+ecx]
        0x50,             // 0051c291   50               push eax
        0x52,             // 0051c292   52               push edx
        0xe8              // f8440f00 // 0051c293   e8 f8440f00      call .00610790    ; jichi: copy invoked here
    };
    enum
    {
      addr_offset = sizeof(bytes) - 1
    };
    addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (addr)
    {
      addr += addr_offset;
      ConsoleOutput("Tamamo: pattern for new version found");
    }
  }
  if (!addr)
  { // for old games
    const BYTE bytes[] = {
        0x72, 0x11,       // 0067fa5b   72 11            jb short .0067fa6e
        0x56,             // 0067fa5d   56               push esi
        0xff, 0x75, 0x10, // 0067fa5e   ff75 10          push dword ptr ss:[ebp+0x10]
        0xff, 0x75, 0x08, // 0067fa61   ff75 08          push dword ptr ss:[ebp+0x8]
        0xe8              // 27080000  // 0067fa64   e8 27080000      call .00680290  ; jichi: copy invoked here
    };
    enum
    {
      addr_offset = sizeof(bytes) - 1
    };
    addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (addr)
    {
      addr += addr_offset;
      ConsoleOutput("Tamamo: pattern for old version found");
    }
  }
  if (!addr)
  {
    ConsoleOutput("Tamamo: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.text_fun = SpecialHookTamamo;
  hp.filter_fun = TamamoFilter;
  hp.type = USING_STRING | USING_SPLIT | NO_CONTEXT;
  ConsoleOutput("INSERT Tamamo");
  return NewHook(hp, "Tamamo");
}
namespace
{
  void Tamamogettext(TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->strA();

    s = re::sub(s, "\\{#(.*?)\\}");
    s = re::sub(s, "<(.*?)>");

    s = re::sub(s, "(.*)\x81u([\\s\\S]*?)\x81v(.*)", "\x81u$2\x81v"); // 「  」
    s = re::sub(s, "(.*)\x81i([\\s\\S]*?)\x81j(.*)", "\x81i$2\x81j"); // （  ）
    buffer->from(s);
  }
  void Tamamogetname(TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->strA();

    s = re::sub(s, "\\{#(.*?)\\}");
    s = re::sub(s, "<(.*?)>");
    if (s.find("\x81u") != s.npos && s.find("\x81v") != s.npos)
      s = re::sub(s, "(.*)\x81u([\\s\\S]*?)\x81v(.*)", "$1"); // 「  」
    else if (s.find("\x81i") != s.npos && s.find("\x81j") != s.npos)
      s = re::sub(s, "(.*)\x81i([\\s\\S]*?)\x81j(.*)", "$1"); // （  ）
    else
      return buffer->clear();
    buffer->from(s);
  }
  bool tamamo3()
  {
    // 閃光の騎士 ～カリスティアナイト～
    char face[] = "face_%s_%s.png";
    auto addr = MemDbg::findBytes(face, sizeof(face), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    bool ok = false;

    BYTE bytes[] = {0x68, XX4};
    memcpy(bytes + 1, &addr, 4);
    for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING;
      hp.filter_fun = Tamamogettext;
      ok |= NewHook(hp, "tamamo_text");
      hp.address = addr + 5;
      hp.offset = stackoffset(3);
      hp.filter_fun = Tamamogetname;
      ok |= NewHook(hp, "tamamo_name");
    }
    return ok;
  }
}
bool Tamamo::attach_function()
{
  bool aa = tamamo3();
  return InsertTamamoHook() || aa;
}