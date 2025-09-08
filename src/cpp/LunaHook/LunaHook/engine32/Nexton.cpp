#include "Nexton.h"
/**
 *  jichi 9/5/2013: NEXTON games with aInfo.db
 *  Sample games:
 *  - /HA-C@4D69E:InnocentBullet.exe (イノセントバレッ�)
 *  - /HA-C@40414C:ImoutoBancho.exe (妹番長)
 *
 *  See: http://ja.wikipedia.org/wiki/ネクストン
 *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2576241908
 *
 *  Old:
 *  md5 = 85ac031f2539e1827d9a1d9fbde4023d
 *  hcode = /HA-C@40414C:ImoutoBancho.exe
 *  - addr: 4211020 (0x40414c)
 *  - module: 1051997988 (0x3eb43724)
 *  - length_offset: 1
 *  - off: 4294967280 (0xfffffff0) = -0x10
 *  - split: 0
 *  - type: 68 (0x44)
 *
 *  New (11/7/2013):
 *  /HA-20:4@583DE:MN2.EXE (NEW)
 *  - addr: 361438 (0x583de)
 *  - module: 3436540819
 *  - length_offset: 1
 *  - off: 4294967260 (0xffffffdc) = -0x24
 *  - split: 4
 *  - type: 84 (0x54)
 */

bool InsertNextonHook()
{
#if 0
  // 0x8944241885c00f84
  const BYTE bytes[] = {
    //0xe8 //??,??,??,??,      00804147   e8 24d90100      call imoutoba.00821a70
    0x89,0x44,0x24, 0x18,   // 0080414c   894424 18        mov dword ptr ss:[esp+0x18],eax; hook here
    0x85,0xc0,              // 00804150   85c0             test eax,eax
    0x0f,0x84               // 00804152  ^0f84 c0feffff    je imoutoba.00804018
  };
  //enum { addr_offset = 0 };
  ULONG addr = processStartAddress; //- sizeof(bytes);
  do {
    addr += sizeof(bytes); // ++ so that each time return diff address
    ULONG range = min(processStopAddress - addr, MAX_REL_ADDR);
    addr = MemDbg::findBytes(bytes, sizeof(bytes), addr, addr + range);
    if (!addr) {
      ConsoleOutput("NEXTON: pattern not exist");
      return false;
    }

    //const BYTE hook_ins[] = {
    //  0x57,       // 00804144   57               push edi
    //  0x8b,0xc3,  // 00804145   8bc3             mov eax,ebx
    //  0xe8 //??,??,??,??,      00804147   e8 24d90100      call imoutoba.00821a70
    //};
  } while(0xe8c38b57 != *(DWORD *)(addr - 8));
#endif // 0
  const BYTE bytes[] = {
      0x57,                   // 0044d696   57               push edi
      0x8b, 0xc3,             // 0044d697   8bc3             mov eax,ebx
      0xe8, XX4,              // 0044d699   e8 6249fdff      call .00422000
      0x89, 0x44, 0x24, 0x18, // 0044d69e   894424 18        mov dword ptr ss:[esp+0x18],eax ; jichi: this is the ith hook point
      0x85, 0xc0,             // 0044d6a2   85c0             test eax,eax
      0x0f, 0x84              // c2feffff    // 0044d6a4  ^0f84 c2feffff    je .0044d56c
  };
  enum
  {
    addr_offset = 0x0044d69e - 0x0044d696
  }; // = 8
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("NEXTON: pattern not exist");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  // hp.type = CODEC_ANSI_BE; // 4

  // 魔王のくせに生イキ�っ �今度は性戦ぽ  // CheatEngine search for byte array: 8944241885C00F84
  // addr = 0x4583de; // wrong
  // addr = 0x5460ba;
  // addr = 0x5f3d8a;
  // addr = 0x768776;
  // addr = 0x7a5319;

  hp.offset = regoffset(edi);
  hp.split = stackoffset(1);
  hp.type = CODEC_ANSI_BE | USING_SPLIT; // 0x54

  // Indirect is needed for new games,
  // Such as: /HA-C*0@4583DE for 「魔王のくせに生イキ�っ���  //hp.type = CODEC_ANSI_BE|DATA_INDIRECT; // 12
  // hp.type = CODEC_UTF16;
  // GROWL_DWORD3(addr, -hp.offset, hp.type);

  ConsoleOutput("INSERT NEXTON");
  return NewHook(hp, "NEXTON");

  // ConsoleOutput("NEXTON: disable GDI hooks"); // There are no GDI functions hooked though
  //  // disable GetGlyphOutlineA
}

namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {
      /**
       *  Scenario caller:
       *  0047D555   8BCE             MOV ECX,ESI
       *  0047D557   FFD0             CALL EAX
       *  0047D559   8B4D 08          MOV ECX,DWORD PTR SS:[EBP+0x8]
       *  0047D55C   51               PUSH ECX
       *  0047D55D   8BCE             MOV ECX,ESI
       *  0047D55F   E8 ECFDFCFF      CALL .0044D350 ; jichi: scenario called here
       *  0047D564   A1 0C839800      MOV EAX,DWORD PTR DS:[0x98830C]
       *  0047D569   C746 38 00000000 MOV DWORD PTR DS:[ESI+0x38],0x0
       *  0047D570   8BB7 20040000    MOV ESI,DWORD PTR DS:[EDI+0x420]
       *  0047D576   8B50 14          MOV EDX,DWORD PTR DS:[EAX+0x14]
       *  0047D579   2B50 10          SUB EDX,DWORD PTR DS:[EAX+0x10]
       *  0047D57C   8D78 10          LEA EDI,DWORD PTR DS:[EAX+0x10]
       *  0047D57F   C1FA 02          SAR EDX,0x2
       *  0047D582   3BF2             CMP ESI,EDX
       *  0047D584   72 05            JB SHORT .0047D58B
       *  0047D586   E8 091C0300      CALL .004AF194
       *  0047D58B   8B07             MOV EAX,DWORD PTR DS:[EDI]
       *  0047D58D   8B34B0           MOV ESI,DWORD PTR DS:[EAX+ESI*4]
       *  0047D590   8B16             MOV EDX,DWORD PTR DS:[ESI]
       *  0047D592   8B42 04          MOV EAX,DWORD PTR DS:[EDX+0x4]
       *  0047D595   8BCE             MOV ECX,ESI
       *  0047D597   FFD0             CALL EAX
       *  0047D599   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
       *  0047D59C   51               PUSH ECX
       *  0047D59D   8BCE             MOV ECX,ESI
       *  0047D59F   E8 ACFDFCFF      CALL .0044D350  ; jichi: name called here
       *  0047D5A4   5F               POP EDI
       *  0047D5A5   5E               POP ESI
       *  0047D5A6   5B               POP EBX
       *  0047D5A7   8BE5             MOV ESP,EBP
       *  0047D5A9   5D               POP EBP
       *  0047D5AA   C2 0800          RETN 0x8
       *  0047D5AD   CC               INT3
       *  0047D5AE   CC               INT3
       *  0047D5AF   CC               INT3
       *
       *  History:
       *
       *  0047C054   50               PUSH EAX
       *  0047C055   8BCF             MOV ECX,EDI
       *  0047C057   E8 F412FDFF      CALL .0044D350  ; jichi: name history called here
       *  0047C05C   46               INC ESI
       *  0047C05D   3B7424 14        CMP ESI,DWORD PTR SS:[ESP+0x14]
       *  0047C061  ^0F82 EAFEFFFF    JB .0047BF51
       *  0047C067   8B4C24 20        MOV ECX,DWORD PTR SS:[ESP+0x20]
       *  0047C06B   3BF1             CMP ESI,ECX
       *  0047C06D   0F83 A7000000    JNB .0047C11A
       *  0047C073   EB 0B            JMP SHORT .0047C080
       *  0047C075   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
       *  0047C07C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
       *  0047C080   8B8B 483A0000    MOV ECX,DWORD PTR DS:[EBX+0x3A48]
       *  0047C086   2B8B 443A0000    SUB ECX,DWORD PTR DS:[EBX+0x3A44]
       *  0047C08C   C1F9 03          SAR ECX,0x3
       *  0047C08F   3BF1             CMP ESI,ECX
       *  0047C091   72 05            JB SHORT .0047C098
       *
       *  0045BFCF   53               PUSH EBX
       *  0045BFD0   53               PUSH EBX
       *  0045BFD1   E8 15670500      CALL .004B26EB  ; jichi: scenario history called here
       *  0045BFD6   8BC6             MOV EAX,ESI
       *  0045BFD8   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
       *  0045BFDB   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
       *  0045BFE2   59               POP ECX
       *  0045BFE3   5F               POP EDI
       *  0045BFE4   5E               POP ESI
       *  0045BFE5   5B               POP EBX
       *  0045BFE6   8BE5             MOV ESP,EBP
       *  0045BFE8   5D               POP EBP
       *  0045BFE9   C3               RETN
       *  0045BFEA   CC               INT3
       */
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        static std::string data_;
        auto text = (LPCSTR)s->stack[1]; // arg1
        if (!text || !*text)
          return;
        *role = Engine::OtherRole;
        auto retaddr = s->stack[0];
        BYTE ins = *(BYTE *)retaddr;
        if (ins == 0xa1) // 0047D564   A1 0C839800      MOV EAX,DWORD PTR DS:[0x98830C]
          *role = Engine::ScenarioRole;
        else if (ins == 0x5f) // 0047D5A4   5F               POP EDI
          *role = Engine::NameRole;

        buffer->from(text);
      }
    } // namespace Private

    /**
     *  Sample game: Innocent Bullet
     *
     *  Name/Scenario/History are translated in different callers.
     *
     *  0044D34D   CC               INT3
     *  0044D34E   CC               INT3
     *  0044D34F   CC               INT3
     *  0044D350   55               PUSH EBP
     *  0044D351   8BEC             MOV EBP,ESP
     *  0044D353   83E4 F8          AND ESP,0xFFFFFFF8
     *  0044D356   6A FF            PUSH -0x1
     *  0044D358   68 30B88800      PUSH .0088B830
     *  0044D35D   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
     *  0044D363   50               PUSH EAX
     *  0044D364   81EC B0000000    SUB ESP,0xB0
     *  0044D36A   A1 50569600      MOV EAX,DWORD PTR DS:[0x965650]
     *  0044D36F   33C4             XOR EAX,ESP
     *  0044D371   898424 A8000000  MOV DWORD PTR SS:[ESP+0xA8],EAX
     *  0044D378   53               PUSH EBX
     *  0044D379   56               PUSH ESI
     *  0044D37A   57               PUSH EDI
     *  0044D37B   A1 50569600      MOV EAX,DWORD PTR DS:[0x965650]
     *  0044D380   33C4             XOR EAX,ESP
     *  0044D382   50               PUSH EAX
     *  0044D383   8D8424 C0000000  LEA EAX,DWORD PTR SS:[ESP+0xC0]
     *  0044D38A   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
     *  0044D390   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
     *  0044D393   8BF1             MOV ESI,ECX
     *  0044D395   8B16             MOV EDX,DWORD PTR DS:[ESI]
     *  0044D397   894424 38        MOV DWORD PTR SS:[ESP+0x38],EAX
     *  0044D39B   8B42 04          MOV EAX,DWORD PTR DS:[EDX+0x4]
     *  0044D39E   897424 34        MOV DWORD PTR SS:[ESP+0x34],ESI
     *  0044D3A2   FFD0             CALL EAX
     *  0044D3A4   68 60244200      PUSH .00422460
     *  0044D3A9   B9 EC769800      MOV ECX,.009876EC
     *  0044D3AE   E8 FD41FDFF      CALL .004215B0
     *  0044D3B3   8B3D F4769800    MOV EDI,DWORD PTR DS:[0x9876F4]
     *  0044D3B9   8B47 30          MOV EAX,DWORD PTR DS:[EDI+0x30]
     *  0044D3BC   2B47 2C          SUB EAX,DWORD PTR DS:[EDI+0x2C]
     *  0044D3BF   8B5E 04          MOV EBX,DWORD PTR DS:[ESI+0x4]
     *  0044D3C2   83C7 20          ADD EDI,0x20
     *  0044D3C5   33C9             XOR ECX,ECX
     *  0044D3C7   83C4 04          ADD ESP,0x4
     *  0044D3CA   C1F8 02          SAR EAX,0x2
     *  0044D3CD   3BD9             CMP EBX,ECX
     *  0044D3CF   7C 24            JL SHORT .0044D3F5
     *  0044D3D1   3BC3             CMP EAX,EBX
     *  0044D3D3   7E 20            JLE SHORT .0044D3F5
     *  0044D3D5   8B57 10          MOV EDX,DWORD PTR DS:[EDI+0x10]
     *  0044D3D8   2B57 0C          SUB EDX,DWORD PTR DS:[EDI+0xC]
     *  0044D3DB   C1FA 02          SAR EDX,0x2
     *  0044D3DE   3BDA             CMP EBX,EDX
     *  0044D3E0   72 07            JB SHORT .0044D3E9
     *  0044D3E2   E8 AD1D0600      CALL .004AF194
     *  0044D3E7   33C9             XOR ECX,ECX
     *  0044D3E9   8B47 0C          MOV EAX,DWORD PTR DS:[EDI+0xC]
     *  0044D3EC   8B1498           MOV EDX,DWORD PTR DS:[EAX+EBX*4]
     *  0044D3EF   895424 1C        MOV DWORD PTR SS:[ESP+0x1C],EDX
     *  0044D3F3   EB 04            JMP SHORT .0044D3F9
     *  0044D3F5   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
     *  0044D3F9   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
     *  0044D3FD   D9EE             FLDZ
     *  0044D3FF   83C0 34          ADD EAX,0x34
     *  0044D402   D95C24 14        FSTP DWORD PTR SS:[ESP+0x14]
     *  0044D406   894424 4C        MOV DWORD PTR SS:[ESP+0x4C],EAX
     *  0044D40A   8B00             MOV EAX,DWORD PTR DS:[EAX]
     *  0044D40C   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  0044D410   DB4424 18        FILD DWORD PTR SS:[ESP+0x18]
     *  0044D414   85C0             TEST EAX,EAX
     *  0044D416   7D 06            JGE SHORT .0044D41E
     *  0044D418   D805 D05C9100    FADD DWORD PTR DS:[0x915CD0]
     *  0044D41E   894C24 3C        MOV DWORD PTR SS:[ESP+0x3C],ECX
     *  0044D422   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
     *  0044D426   894C24 2C        MOV DWORD PTR SS:[ESP+0x2C],ECX
     *  0044D42A   8D4C24 70        LEA ECX,DWORD PTR SS:[ESP+0x70]
     *  0044D42E   51               PUSH ECX
     *  0044D42F   C74424 70 60DC90>MOV DWORD PTR SS:[ESP+0x70],.0090DC60
     *  0044D437   E8 242B0000      CALL .0044FF60
     *  0044D43C   33FF             XOR EDI,EDI
     *  0044D43E   8D5424 6C        LEA EDX,DWORD PTR SS:[ESP+0x6C]
     *  0044D442   89BC24 C8000000  MOV DWORD PTR SS:[ESP+0xC8],EDI
     *  0044D449   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
     *  0044D44D   52               PUSH EDX
     *  0044D44E   E8 6D150000      CALL .0044E9C0
     *  0044D453   8B8424 80000000  MOV EAX,DWORD PTR SS:[ESP+0x80]
     *  0044D45A   8B4C24 7C        MOV ECX,DWORD PTR SS:[ESP+0x7C]
     *  0044D45E   894424 60        MOV DWORD PTR SS:[ESP+0x60],EAX
     *  0044D462   3BC8             CMP ECX,EAX
     *  0044D464   76 10            JBE SHORT .0044D476
     *  0044D466   E8 291D0600      CALL .004AF194
     *  0044D46B   8B8424 80000000  MOV EAX,DWORD PTR SS:[ESP+0x80]
     *  0044D472   8B4C24 7C        MOV ECX,DWORD PTR SS:[ESP+0x7C]
     *  0044D476   8B5424 70        MOV EDX,DWORD PTR SS:[ESP+0x70]
     *  0044D47A   895424 58        MOV DWORD PTR SS:[ESP+0x58],EDX
     *  0044D47E   897C24 38        MOV DWORD PTR SS:[ESP+0x38],EDI
     *  0044D482   8BD9             MOV EBX,ECX
     *  0044D484   3BC8             CMP ECX,EAX
     *  0044D486   76 05            JBE SHORT .0044D48D
     *  0044D488   E8 071D0600      CALL .004AF194
     *  0044D48D   8B7C24 70        MOV EDI,DWORD PTR SS:[ESP+0x70]
     *  0044D491   897C24 50        MOV DWORD PTR SS:[ESP+0x50],EDI
     *  0044D495   895C24 54        MOV DWORD PTR SS:[ESP+0x54],EBX
     *  0044D499   85FF             TEST EDI,EDI
     *  0044D49B   74 06            JE SHORT .0044D4A3
     *  0044D49D   3B7C24 58        CMP EDI,DWORD PTR SS:[ESP+0x58]
     *  0044D4A1   74 05            JE SHORT .0044D4A8
     *  0044D4A3   E8 EC1C0600      CALL .004AF194
     *  0044D4A8   3B5C24 60        CMP EBX,DWORD PTR SS:[ESP+0x60]
     *  0044D4AC   0F84 E4030000    JE .0044D896
     *  0044D4B2   85FF             TEST EDI,EDI
     *  0044D4B4   0F85 9C000000    JNZ .0044D556
     *  0044D4BA   E8 D51C0600      CALL .004AF194
     *  0044D4BF   33C0             XOR EAX,EAX
     *  0044D4C1   3B58 10          CMP EBX,DWORD PTR DS:[EAX+0x10]
     *  0044D4C4   72 05            JB SHORT .0044D4CB
     *  0044D4C6   E8 C91C0600      CALL .004AF194
     *  0044D4CB   8B0B             MOV ECX,DWORD PTR DS:[EBX]
     *  0044D4CD   8B01             MOV EAX,DWORD PTR DS:[ECX]
     *  0044D4CF   8B50 10          MOV EDX,DWORD PTR DS:[EAX+0x10]
     *  0044D4D2   FFD2             CALL EDX
     *  0044D4D4   85C0             TEST EAX,EAX
     *  0044D4D6   0F85 99030000    JNZ .0044D875
     *  0044D4DC   85FF             TEST EDI,EDI
     *  0044D4DE   75 7D            JNZ SHORT .0044D55D
     *  0044D4E0   E8 AF1C0600      CALL .004AF194
     *  0044D4E5   3B5F 10          CMP EBX,DWORD PTR DS:[EDI+0x10]
     *  0044D4E8   72 05            JB SHORT .0044D4EF
     *  0044D4EA   E8 A51C0600      CALL .004AF194
     *  0044D4EF   8B0B             MOV ECX,DWORD PTR DS:[EBX]
     *  0044D4F1   8B01             MOV EAX,DWORD PTR DS:[ECX]
     *  0044D4F3   8B50 08          MOV EDX,DWORD PTR DS:[EAX+0x8]
     *  0044D4F6   FFD2             CALL EDX
     *  0044D4F8   8BC8             MOV ECX,EAX
     *  0044D4FA   C78424 B4000000 >MOV DWORD PTR SS:[ESP+0xB4],0xF
     *  0044D505   C78424 B0000000 >MOV DWORD PTR SS:[ESP+0xB0],0x0
     *  0044D510   C68424 A0000000 >MOV BYTE PTR SS:[ESP+0xA0],0x0
     *  0044D518   8D79 01          LEA EDI,DWORD PTR DS:[ECX+0x1]
     *  0044D51B   EB 03            JMP SHORT .0044D520
     *  0044D51D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
     *  0044D520   8A11             MOV DL,BYTE PTR DS:[ECX]
     *  0044D522   41               INC ECX
     *  0044D523   84D2             TEST DL,DL
     *  0044D525  ^75 F9            JNZ SHORT .0044D520
     *  0044D527   2BCF             SUB ECX,EDI
     *  0044D529   51               PUSH ECX
     *  0044D52A   50               PUSH EAX
     *  0044D52B   8D8C24 A4000000  LEA ECX,DWORD PTR SS:[ESP+0xA4]
     *  0044D532   E8 D934FCFF      CALL .00410A10
     *  0044D537   C68424 C8000000 >MOV BYTE PTR SS:[ESP+0xC8],0x1
     *  0044D53F   83BC24 B4000000 >CMP DWORD PTR SS:[ESP+0xB4],0x10
     *  0044D547   72 18            JB SHORT .0044D561
     *  0044D549   8B8424 A0000000  MOV EAX,DWORD PTR SS:[ESP+0xA0]
     *  0044D550   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
     *  0044D554   EB 16            JMP SHORT .0044D56C
     *  0044D556   8B07             MOV EAX,DWORD PTR DS:[EDI]
     *  0044D558  ^E9 64FFFFFF      JMP .0044D4C1
     *  0044D55D   8B3F             MOV EDI,DWORD PTR DS:[EDI]
     *  0044D55F  ^EB 84            JMP SHORT .0044D4E5
     *  0044D561   8D8C24 A0000000  LEA ECX,DWORD PTR SS:[ESP+0xA0]
     *  0044D568   894C24 30        MOV DWORD PTR SS:[ESP+0x30],ECX
     *  0044D56C   8B7C24 30        MOV EDI,DWORD PTR SS:[ESP+0x30]
     *  0044D570   0FB617           MOVZX EDX,BYTE PTR DS:[EDI]
     *  0044D573   52               PUSH EDX
     *  0044D574   33DB             XOR EBX,EBX
     *  0044D576   E8 39420600      CALL .004B17B4
     *  0044D57B   83C4 04          ADD ESP,0x4
     *  0044D57E   85C0             TEST EAX,EAX
     *  0044D580   74 12            JE SHORT .0044D594
     *  0044D582   8BCF             MOV ECX,EDI
     *  0044D584   3859 01          CMP BYTE PTR DS:[ECX+0x1],BL
     *  0044D587   8D41 01          LEA EAX,DWORD PTR DS:[ECX+0x1]
     *  0044D58A   74 08            JE SHORT .0044D594
     *  0044D58C   0FB619           MOVZX EBX,BYTE PTR DS:[ECX]
     *  0044D58F   C1E3 08          SHL EBX,0x8
     *  0044D592   8BF8             MOV EDI,EAX
     *  0044D594   0FB63F           MOVZX EDI,BYTE PTR DS:[EDI]
     *  0044D597   03FB             ADD EDI,EBX
     *  0044D599   0F84 8E020000    JE .0044D82D
     *  0044D59F   D94424 28        FLD DWORD PTR SS:[ESP+0x28]
     *  0044D5A3   D946 0C          FLD DWORD PTR DS:[ESI+0xC]
     *  0044D5A6   DED9             FCOMPP
     *  0044D5A8   DFE0             FSTSW AX
     *  0044D5AA   F6C4 05          TEST AH,0x5
     *  0044D5AD   0F8B 7A020000    JPO .0044D82D
     *  0044D5B3   8B4424 30        MOV EAX,DWORD PTR SS:[ESP+0x30]
     *  0044D5B7   50               PUSH EAX
     *  0044D5B8   E8 0F420600      CALL .004B17CC
     *  0044D5BD   83C4 04          ADD ESP,0x4
     *  0044D5C0   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
     *  0044D5C4   83FF 20          CMP EDI,0x20
     *  0044D5C7   75 27            JNZ SHORT .0044D5F0
     *  0044D5C9   FF86 88000000    INC DWORD PTR DS:[ESI+0x88]
     *  0044D5CF   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
     *  0044D5D3   8B51 38          MOV EDX,DWORD PTR DS:[ECX+0x38]
     *  0044D5D6   DB41 38          FILD DWORD PTR DS:[ECX+0x38]
     *  0044D5D9   85D2             TEST EDX,EDX
     *  0044D5DB   7D 06            JGE SHORT .0044D5E3
     *  0044D5DD   D805 D05C9100    FADD DWORD PTR DS:[0x915CD0]
     *  0044D5E3   D84424 14        FADD DWORD PTR SS:[ESP+0x14]
     *  0044D5E7   D95C24 14        FSTP DWORD PTR SS:[ESP+0x14]
     *  0044D5EB  ^E9 7CFFFFFF      JMP .0044D56C
     *  0044D5F0   81FF 40810000    CMP EDI,0x8140
     *  0044D5F6   75 14            JNZ SHORT .0044D60C
     *  0044D5F8   FF86 88000000    INC DWORD PTR DS:[ESI+0x88]
     *  0044D5FE   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
     *  0044D602   8B48 3C          MOV ECX,DWORD PTR DS:[EAX+0x3C]
     *  0044D605   DB40 3C          FILD DWORD PTR DS:[EAX+0x3C]
     *  0044D608   85C9             TEST ECX,ECX
     *  0044D60A  ^EB CF            JMP SHORT .0044D5DB
     *  0044D60C   83FF 0A          CMP EDI,0xA
     *  0044D60F   75 6F            JNZ SHORT .0044D680
     *  0044D611   8B46 18          MOV EAX,DWORD PTR DS:[ESI+0x18]
     *  0044D614   83F8 03          CMP EAX,0x3
     *  0044D617   77 3D            JA SHORT .0044D656
     *  0044D619   FF2485 98DA4400  JMP DWORD PTR DS:[EAX*4+0x44DA98]
     *  0044D620   56               PUSH ESI
     *  0044D621   E8 3A080000      CALL .0044DE60
     *  0044D626   EB 2E            JMP SHORT .0044D656
     *  0044D628   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D62C   51               PUSH ECX
     *  0044D62D   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D630   56               PUSH ESI
     *  0044D631   E8 FA080000      CALL .0044DF30
     *  0044D636   EB 1E            JMP SHORT .0044D656
     *  0044D638   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D63C   51               PUSH ECX
     *  0044D63D   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D640   56               PUSH ESI
     *  0044D641   E8 CA090000      CALL .0044E010
     *  0044D646   EB 0E            JMP SHORT .0044D656
     *  0044D648   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D64C   51               PUSH ECX
     *  0044D64D   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D650   56               PUSH ESI
     *  0044D651   E8 9A0A0000      CALL .0044E0F0
     *  0044D656   8B5424 4C        MOV EDX,DWORD PTR SS:[ESP+0x4C]
     *  0044D65A   D9EE             FLDZ
     *  0044D65C   8B02             MOV EAX,DWORD PTR DS:[EDX]
     *  0044D65E   D95C24 14        FSTP DWORD PTR SS:[ESP+0x14]
     *  0044D662   D946 14          FLD DWORD PTR DS:[ESI+0x14]
     *  0044D665   DB02             FILD DWORD PTR DS:[EDX]
     *  0044D667   85C0             TEST EAX,EAX
     *  0044D669   7D 06            JGE SHORT .0044D671
     *  0044D66B   D805 D05C9100    FADD DWORD PTR DS:[0x915CD0]
     *  0044D671   DEC1             FADDP ST(1),ST
     *  0044D673   D84424 28        FADD DWORD PTR SS:[ESP+0x28]
     *  0044D677   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
     *  0044D67B  ^E9 ECFEFFFF      JMP .0044D56C
     *  0044D680   83FF 0D          CMP EDI,0xD
     *  0044D683  ^0F84 E3FEFFFF    JE .0044D56C
     *  0044D689   83FF 09          CMP EDI,0x9
     *  0044D68C  ^0F84 DAFEFFFF    JE .0044D56C
     *  0044D692   8B5C24 1C        MOV EBX,DWORD PTR SS:[ESP+0x1C]
     *  0044D696   57               PUSH EDI
     *  0044D697   8BC3             MOV EAX,EBX
     *  0044D699   E8 6249FDFF      CALL .00422000
     *  0044D69E   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX ; jichi: This is the ITH hook point
     *  0044D6A2   85C0             TEST EAX,EAX
     *  0044D6A4  ^0F84 C2FEFFFF    JE .0044D56C
     *  0044D6AA   57               PUSH EDI
     *  0044D6AB   8BC3             MOV EAX,EBX
     *  0044D6AD   E8 4E49FDFF      CALL .00422000
     *  0044D6B2   85C0             TEST EAX,EAX
     *  0044D6B4  ^0F84 B2FEFFFF    JE .0044D56C
     *  0044D6BA   83C0 10          ADD EAX,0x10
     *  0044D6BD   894424 40        MOV DWORD PTR SS:[ESP+0x40],EAX
     *  0044D6C1  ^0F84 A5FEFFFF    JE .0044D56C
     *  0044D6C7   57               PUSH EDI
     *  0044D6C8   8BC3             MOV EAX,EBX
     *  0044D6CA   E8 3149FDFF      CALL .00422000
     *  0044D6CF   85C0             TEST EAX,EAX
     *  0044D6D1   75 04            JNZ SHORT .0044D6D7
     *  0044D6D3   D9EE             FLDZ
     *  0044D6D5   EB 03            JMP SHORT .0044D6DA
     *  0044D6D7   D940 20          FLD DWORD PTR DS:[EAX+0x20]
     *  0044D6DA   D95C24 24        FSTP DWORD PTR SS:[ESP+0x24]
     *  0044D6DE   8D4C24 20        LEA ECX,DWORD PTR SS:[ESP+0x20]
     *  0044D6E2   D94424 24        FLD DWORD PTR SS:[ESP+0x24]
     *  0044D6E6   51               PUSH ECX
     *  0044D6E7   8D8E 04010000    LEA ECX,DWORD PTR DS:[ESI+0x104]
     *  0044D6ED   D95C24 24        FSTP DWORD PTR SS:[ESP+0x24]
     *  0044D6F1   E8 6A55FFFF      CALL .00442C60
     *  0044D6F6   D94424 24        FLD DWORD PTR SS:[ESP+0x24]
     *  0044D6FA   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D6FE   D9C0             FLD ST
     *  0044D700   DEC2             FADDP ST(2),ST
     *  0044D702   D946 10          FLD DWORD PTR DS:[ESI+0x10]
     *  0044D705   DEC2             FADDP ST(2),ST
     *  0044D707   D9C9             FXCH ST(1)
     *  0044D709   D95C24 48        FSTP DWORD PTR SS:[ESP+0x48]
     *  0044D70D   D94424 28        FLD DWORD PTR SS:[ESP+0x28]
     *  0044D711   D95C24 20        FSTP DWORD PTR SS:[ESP+0x20]
     *  0044D715   D94424 48        FLD DWORD PTR SS:[ESP+0x48]
     *  0044D719   D946 08          FLD DWORD PTR DS:[ESI+0x8]
     *  0044D71C   DED9             FCOMPP
     *  0044D71E   DFE0             FSTSW AX
     *  0044D720   F6C4 05          TEST AH,0x5
     *  0044D723   7A 47            JPE SHORT .0044D76C
     *  0044D725   51               PUSH ECX
     *  0044D726   8BC6             MOV EAX,ESI
     *  0044D728   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D72B   E8 D0060000      CALL .0044DE00
     *  0044D730   D94424 24        FLD DWORD PTR SS:[ESP+0x24]
     *  0044D734   D846 10          FADD DWORD PTR DS:[ESI+0x10]
     *  0044D737   8B5424 4C        MOV EDX,DWORD PTR SS:[ESP+0x4C]
     *  0044D73B   8B02             MOV EAX,DWORD PTR DS:[EDX]
     *  0044D73D   D95C24 48        FSTP DWORD PTR SS:[ESP+0x48]
     *  0044D741   D946 14          FLD DWORD PTR DS:[ESI+0x14]
     *  0044D744   DB02             FILD DWORD PTR DS:[EDX]
     *  0044D746   85C0             TEST EAX,EAX
     *  0044D748   7D 06            JGE SHORT .0044D750
     *  0044D74A   D805 D05C9100    FADD DWORD PTR DS:[0x915CD0]
     *  0044D750   DEC1             FADDP ST(1),ST
     *  0044D752   D84424 28        FADD DWORD PTR SS:[ESP+0x28]
     *  0044D756   D95C24 20        FSTP DWORD PTR SS:[ESP+0x20]
     *  0044D75A   D9EE             FLDZ
     *  0044D75C   D95C24 14        FSTP DWORD PTR SS:[ESP+0x14]
     *  0044D760   D94424 20        FLD DWORD PTR SS:[ESP+0x20]
     *  0044D764   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
     *  0044D768   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D76C   FF86 88000000    INC DWORD PTR DS:[ESI+0x88]
     *  0044D772   D95C24 64        FSTP DWORD PTR SS:[ESP+0x64]
     *  0044D776   D94424 28        FLD DWORD PTR SS:[ESP+0x28]
     *  0044D77A   8D7E 6C          LEA EDI,DWORD PTR DS:[ESI+0x6C]
     *  0044D77D   8D5C24 64        LEA EBX,DWORD PTR SS:[ESP+0x64]
     *  0044D781   D95C24 68        FSTP DWORD PTR SS:[ESP+0x68]
     *  0044D785   E8 B658FFFF      CALL .00443040
     *  0044D78A   D9E8             FLD1
     *  0044D78C   8B5C24 18        MOV EBX,DWORD PTR SS:[ESP+0x18]
     *  0044D790   83EC 0C          SUB ESP,0xC
     *  0044D793   D95C24 08        FSTP DWORD PTR SS:[ESP+0x8]
     *  0044D797   8D46 54          LEA EAX,DWORD PTR DS:[ESI+0x54]
     *  0044D79A   D94424 34        FLD DWORD PTR SS:[ESP+0x34]
     *  0044D79E   8B7424 4C        MOV ESI,DWORD PTR SS:[ESP+0x4C]
     *  0044D7A2   D95C24 04        FSTP DWORD PTR SS:[ESP+0x4]
     *  0044D7A6   D94424 20        FLD DWORD PTR SS:[ESP+0x20]
     *  0044D7AA   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D7AD   E8 1E040000      CALL .0044DBD0
     *  0044D7B2   8D5C24 2C        LEA EBX,DWORD PTR SS:[ESP+0x2C]
     *  0044D7B6   8D7C24 3C        LEA EDI,DWORD PTR SS:[ESP+0x3C]
     *  0044D7BA   E8 E1050000      CALL .0044DDA0
     *  0044D7BF   0FB74C24 3C      MOVZX ECX,WORD PTR SS:[ESP+0x3C]
     *  0044D7C4   8B7424 34        MOV ESI,DWORD PTR SS:[ESP+0x34]
     *  0044D7C8   8DBE A4000000    LEA EDI,DWORD PTR DS:[ESI+0xA4]
     *  0044D7CE   8D5C24 18        LEA EBX,DWORD PTR SS:[ESP+0x18]
     *  0044D7D2   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
     *  0044D7D6   E8 15C8FCFF      CALL .00419FF0
     *  0044D7DB   0FB74C24 2C      MOVZX ECX,WORD PTR SS:[ESP+0x2C]
     *  0044D7E0   B8 56555555      MOV EAX,0x55555556
     *  0044D7E5   F7E9             IMUL ECX
     *  0044D7E7   8BC2             MOV EAX,EDX
     *  0044D7E9   C1E8 1F          SHR EAX,0x1F
     *  0044D7EC   03C2             ADD EAX,EDX
     *  0044D7EE   8DBE 8C000000    LEA EDI,DWORD PTR DS:[ESI+0x8C]
     *  0044D7F4   8D5C24 18        LEA EBX,DWORD PTR SS:[ESP+0x18]
     *  0044D7F8   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  0044D7FC   E8 EFC7FCFF      CALL .00419FF0
     *  0044D801   8DBE D4000000    LEA EDI,DWORD PTR DS:[ESI+0xD4]
     *  0044D807   D94424 48        FLD DWORD PTR SS:[ESP+0x48]
     *  0044D80B   8D5C24 38        LEA EBX,DWORD PTR SS:[ESP+0x38]
     *  0044D80F   D95C24 14        FSTP DWORD PTR SS:[ESP+0x14]
     *  0044D813   D94424 20        FLD DWORD PTR SS:[ESP+0x20]
     *  0044D817   D95C24 28        FSTP DWORD PTR SS:[ESP+0x28]
     *  0044D81B   E8 D0C7FCFF      CALL .00419FF0
     *  0044D820   C74424 38 000000>MOV DWORD PTR SS:[ESP+0x38],0x0
     *  0044D828  ^E9 3FFDFFFF      JMP .0044D56C
     *  0044D82D   C68424 C8000000 >MOV BYTE PTR SS:[ESP+0xC8],0x0
     *  0044D835   83BC24 B4000000 >CMP DWORD PTR SS:[ESP+0xB4],0x10
     *  0044D83D   72 10            JB SHORT .0044D84F
     *  0044D83F   8B8C24 A0000000  MOV ECX,DWORD PTR SS:[ESP+0xA0]
     *  0044D846   51               PUSH ECX
     *  0044D847   E8 29130600      CALL .004AEB75
     *  0044D84C   83C4 04          ADD ESP,0x4
     *  0044D84F   8B7C24 50        MOV EDI,DWORD PTR SS:[ESP+0x50]
     *  0044D853   8B5C24 54        MOV EBX,DWORD PTR SS:[ESP+0x54]
     *  0044D857   C78424 B4000000 >MOV DWORD PTR SS:[ESP+0xB4],0xF
     *  0044D862   C78424 B0000000 >MOV DWORD PTR SS:[ESP+0xB0],0x0
     *  0044D86D   C68424 A0000000 >MOV BYTE PTR SS:[ESP+0xA0],0x0
     *  0044D875   85FF             TEST EDI,EDI
     *  0044D877   75 19            JNZ SHORT .0044D892
     *  0044D879   E8 16190600      CALL .004AF194
     *  0044D87E   33C0             XOR EAX,EAX
     *  0044D880   3B58 10          CMP EBX,DWORD PTR DS:[EAX+0x10]
     *  0044D883   72 05            JB SHORT .0044D88A
     *  0044D885   E8 0A190600      CALL .004AF194
     *  0044D88A   83C3 04          ADD EBX,0x4
     *  0044D88D  ^E9 03FCFFFF      JMP .0044D495
     *  0044D892   8B07             MOV EAX,DWORD PTR DS:[EDI]
     *  0044D894  ^EB EA            JMP SHORT .0044D880
     *  0044D896   66:8B5424 2C     MOV DX,WORD PTR SS:[ESP+0x2C]
     *  0044D89B   66:8996 84000000 MOV WORD PTR DS:[ESI+0x84],DX
     *  0044D8A2   8B4E 64          MOV ECX,DWORD PTR DS:[ESI+0x64]
     *  0044D8A5   2B4E 60          SUB ECX,DWORD PTR DS:[ESI+0x60]
     *  0044D8A8   B8 67666666      MOV EAX,0x66666667
     *  0044D8AD   F7E9             IMUL ECX
     *  0044D8AF   C1FA 03          SAR EDX,0x3
     *  0044D8B2   8BC2             MOV EAX,EDX
     *  0044D8B4   C1E8 1F          SHR EAX,0x1F
     *  0044D8B7   03C2             ADD EAX,EDX
     *  0044D8B9   74 0F            JE SHORT .0044D8CA
     *  0044D8BB   D94424 14        FLD DWORD PTR SS:[ESP+0x14]
     *  0044D8BF   51               PUSH ECX
     *  0044D8C0   8BC6             MOV EAX,ESI
     *  0044D8C2   D91C24           FSTP DWORD PTR SS:[ESP]
     *  0044D8C5   E8 36050000      CALL .0044DE00
     *  0044D8CA   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
     *  0044D8D0   33DB             XOR EBX,EBX
     *  0044D8D2   895C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EBX
     *  0044D8D6   895C24 2C        MOV DWORD PTR SS:[ESP+0x2C],EBX
     *  0044D8DA   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
     *  0044D8DE   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
     *  0044D8E2   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  0044D8E6   3986 98000000    CMP DWORD PTR DS:[ESI+0x98],EAX
     *  0044D8EC   76 05            JBE SHORT .0044D8F3
     *  0044D8EE   E8 A1180600      CALL .004AF194
     *  0044D8F3   8BBE 98000000    MOV EDI,DWORD PTR DS:[ESI+0x98]
     *  0044D8F9   8B8E 8C000000    MOV ECX,DWORD PTR DS:[ESI+0x8C]
     *  0044D8FF   894C24 58        MOV DWORD PTR SS:[ESP+0x58],ECX
     *  0044D903   3BBE 9C000000    CMP EDI,DWORD PTR DS:[ESI+0x9C]
     *  0044D909   76 05            JBE SHORT .0044D910
     *  0044D90B   E8 84180600      CALL .004AF194
     *  0044D910   8B86 8C000000    MOV EAX,DWORD PTR DS:[ESI+0x8C]
     *  0044D916   894424 40        MOV DWORD PTR SS:[ESP+0x40],EAX
     *  0044D91A   897C24 44        MOV DWORD PTR SS:[ESP+0x44],EDI
     *  0044D91E   895C24 34        MOV DWORD PTR SS:[ESP+0x34],EBX
     *  0044D922   3BC3             CMP EAX,EBX
     *  0044D924   74 06            JE SHORT .0044D92C
     *  0044D926   3B4424 58        CMP EAX,DWORD PTR SS:[ESP+0x58]
     *  0044D92A   74 05            JE SHORT .0044D931
     *  0044D92C   E8 63180600      CALL .004AF194
     *  0044D931   8B5424 44        MOV EDX,DWORD PTR SS:[ESP+0x44]
     *  0044D935   3B5424 18        CMP EDX,DWORD PTR SS:[ESP+0x18]
     *  0044D939   0F84 0D010000    JE .0044DA4C
     *  0044D93F   8B4424 34        MOV EAX,DWORD PTR SS:[ESP+0x34]
     *  0044D943   33DB             XOR EBX,EBX
     *  0044D945   8DBE EC000000    LEA EDI,DWORD PTR DS:[ESI+0xEC]
     *  0044D94B   894424 24        MOV DWORD PTR SS:[ESP+0x24],EAX
     *  0044D94F   8B4E 4C          MOV ECX,DWORD PTR DS:[ESI+0x4C]
     *  0044D952   2B4E 48          SUB ECX,DWORD PTR DS:[ESI+0x48]
     *  0044D955   B8 67666666      MOV EAX,0x66666667
     *  0044D95A   F7E9             IMUL ECX
     *  0044D95C   C1FA 03          SAR EDX,0x3
     *  0044D95F   8BCA             MOV ECX,EDX
     *  0044D961   C1E9 1F          SHR ECX,0x1F
     *  0044D964   03CA             ADD ECX,EDX
     *  0044D966   8B5424 20        MOV EDX,DWORD PTR SS:[ESP+0x20]
     *  0044D96A   8D0413           LEA EAX,DWORD PTR DS:[EBX+EDX]
     *  0044D96D   3BC1             CMP EAX,ECX
     *  0044D96F   72 05            JB SHORT .0044D976
     *  0044D971   E8 1E180600      CALL .004AF194
     *  0044D976   8B46 48          MOV EAX,DWORD PTR DS:[ESI+0x48]
     *  0044D979   034424 24        ADD EAX,DWORD PTR SS:[ESP+0x24]
     *  0044D97D   8D8C24 88000000  LEA ECX,DWORD PTR SS:[ESP+0x88]
     *  0044D984   D900             FLD DWORD PTR DS:[EAX]
     *  0044D986   51               PUSH ECX
     *  0044D987   D99C24 8C000000  FSTP DWORD PTR SS:[ESP+0x8C]
     *  0044D98E   D940 04          FLD DWORD PTR DS:[EAX+0x4]
     *  0044D991   D99C24 90000000  FSTP DWORD PTR SS:[ESP+0x90]
     *  0044D998   D940 08          FLD DWORD PTR DS:[EAX+0x8]
     *  0044D99B   D99C24 94000000  FSTP DWORD PTR SS:[ESP+0x94]
     *  0044D9A2   D940 0C          FLD DWORD PTR DS:[EAX+0xC]
     *  0044D9A5   D99C24 98000000  FSTP DWORD PTR SS:[ESP+0x98]
     *  0044D9AC   D940 10          FLD DWORD PTR DS:[EAX+0x10]
     *  0044D9AF   D99C24 9C000000  FSTP DWORD PTR SS:[ESP+0x9C]
     *  0044D9B6   E8 A50B0000      CALL .0044E560
     *  0044D9BB   834424 24 14     ADD DWORD PTR SS:[ESP+0x24],0x14
     *  0044D9C0   43               INC EBX
     *  0044D9C1   83FB 04          CMP EBX,0x4
     *  0044D9C4  ^7C 89            JL SHORT .0044D94F
     *  0044D9C6   8D5C24 2C        LEA EBX,DWORD PTR SS:[ESP+0x2C]
     *  0044D9CA   8D7C24 3C        LEA EDI,DWORD PTR SS:[ESP+0x3C]
     *  0044D9CE   E8 CD030000      CALL .0044DDA0
     *  0044D9D3   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
     *  0044D9D9   2B86 98000000    SUB EAX,DWORD PTR DS:[ESI+0x98]
     *  0044D9DF   8B5424 24        MOV EDX,DWORD PTR SS:[ESP+0x24]
     *  0044D9E3   BF 04000000      MOV EDI,0x4
     *  0044D9E8   017C24 20        ADD DWORD PTR SS:[ESP+0x20],EDI
     *  0044D9EC   C1F8 02          SAR EAX,0x2
     *  0044D9EF   895424 34        MOV DWORD PTR SS:[ESP+0x34],EDX
     *  0044D9F3   394424 1C        CMP DWORD PTR SS:[ESP+0x1C],EAX
     *  0044D9F7   72 05            JB SHORT .0044D9FE
     *  0044D9F9   E8 96170600      CALL .004AF194
     *  0044D9FE   8B8E B4000000    MOV ECX,DWORD PTR DS:[ESI+0xB4]
     *  0044DA04   2B8E B0000000    SUB ECX,DWORD PTR DS:[ESI+0xB0]
     *  0044DA0A   C1F9 02          SAR ECX,0x2
     *  0044DA0D   394C24 1C        CMP DWORD PTR SS:[ESP+0x1C],ECX
     *  0044DA11   72 05            JB SHORT .0044DA18
     *  0044DA13   E8 7C170600      CALL .004AF194
     *  0044DA18   8B4424 40        MOV EAX,DWORD PTR SS:[ESP+0x40]
     *  0044DA1C   FF4424 1C        INC DWORD PTR SS:[ESP+0x1C]
     *  0044DA20   85C0             TEST EAX,EAX
     *  0044DA22   75 24            JNZ SHORT .0044DA48
     *  0044DA24   E8 6B170600      CALL .004AF194
     *  0044DA29   33C0             XOR EAX,EAX
     *  0044DA2B   8B5424 44        MOV EDX,DWORD PTR SS:[ESP+0x44]
     *  0044DA2F   3B50 10          CMP EDX,DWORD PTR DS:[EAX+0x10]
     *  0044DA32   72 05            JB SHORT .0044DA39
     *  0044DA34   E8 5B170600      CALL .004AF194
     *  0044DA39   017C24 44        ADD DWORD PTR SS:[ESP+0x44],EDI
     *  0044DA3D   8B4424 40        MOV EAX,DWORD PTR SS:[ESP+0x40]
     *  0044DA41   33DB             XOR EBX,EBX
     *  0044DA43  ^E9 DAFEFFFF      JMP .0044D922
     *  0044DA48   8B00             MOV EAX,DWORD PTR DS:[EAX]
     *  0044DA4A  ^EB DF            JMP SHORT .0044DA2B
     *  0044DA4C   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
     *  0044DA52   2B86 98000000    SUB EAX,DWORD PTR DS:[ESI+0x98]
     *  0044DA58   8D4C24 6C        LEA ECX,DWORD PTR SS:[ESP+0x6C]
     *  0044DA5C   C1F8 02          SAR EAX,0x2
     *  0044DA5F   8946 38          MOV DWORD PTR DS:[ESI+0x38],EAX
     *  0044DA62   C78424 C8000000 >MOV DWORD PTR SS:[ESP+0xC8],-0x1
     *  0044DA6D   E8 CE0E0000      CALL .0044E940
     *  0044DA72   8B8C24 C0000000  MOV ECX,DWORD PTR SS:[ESP+0xC0]
     *  0044DA79   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  0044DA80   59               POP ECX
     *  0044DA81   5F               POP EDI
     *  0044DA82   5E               POP ESI
     *  0044DA83   5B               POP EBX
     *  0044DA84   8B8C24 A8000000  MOV ECX,DWORD PTR SS:[ESP+0xA8]
     *  0044DA8B   33CC             XOR ECX,ESP
     *  0044DA8D   E8 EE100600      CALL .004AEB80
     *  0044DA92   8BE5             MOV ESP,EBP
     *  0044DA94   5D               POP EBP
     *  0044DA95   C2 0400          RETN 0x4
     *  0044DA98   20D6             AND DH,DL
     *  0044DA9A   44               INC ESP
     *  0044DA9B   0028             ADD BYTE PTR DS:[EAX],CH
     *  0044DA9D   D6               SALC
     *  0044DA9E   44               INC ESP
     *  0044DA9F   0038             ADD BYTE PTR DS:[EAX],BH
     *  0044DAA1   D6               SALC
     *  0044DAA2   44               INC ESP
     *  0044DAA3   0048 D6          ADD BYTE PTR DS:[EAX-0x2A],CL
     *  0044DAA6   44               INC ESP
     *  0044DAA7   00CC             ADD AH,CL
     *  0044DAA9   CC               INT3
     *  0044DAAA   CC               INT3
     *  0044DAAB   CC               INT3
     *  0044DAAC   CC               INT3
     *  0044DAAD   CC               INT3
     *  0044DAAE   CC               INT3
     *  0044DAAF   CC               INT3
     */
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      const uint8_t bytes[] = {
          0x57,                   // 0044d696   57               push edi
          0x8b, 0xc3,             // 0044d697   8bc3             mov eax,ebx
          0xe8, XX4,              // 0044d699   e8 6249fdff      call .00422000
          0x89, 0x44, 0x24, 0x18, // 0044d69e   894424 18        mov dword ptr ss:[esp+0x18],eax ; jichi: this is the ith hook point
          0x85, 0xc0,             // 0044d6a2   85c0             test eax,eax
          0x0f, 0x84              // c2feffff    // 0044d6a4  ^0f84 c2feffff    je .0044d56c
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr); // range is around 50, use 80
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS | NO_CONTEXT;
      hp.offset = stackoffset(1);
      hp.text_fun = Private::hookBefore;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      return NewHook(hp, "EmbedNexton");
    }

  } // namespace ScenarioHook
} // unnamed namespace

bool Nexton::attach_function()
{
  bool embed = ScenarioHook::attach(processStartAddress, processStopAddress);
  return InsertNextonHook() || embed;
}

/** jichi 8/17/2014 Nexton1
 *  Sample games:
 *  - [Nomad][071026] 淫烙�巫女 Trial
 *
 *  Debug method: text are prefetched into memory. Add break point to it.
 *
 *  GetGlyphOutlineA is called, but no correct text.
 *
 *  There are so many good hooks. The shortest function was picked,as follows:
 *  0041974e   cc               int3
 *  0041974f   cc               int3
 *  00419750   56               push esi    ; jichi: hook here, text in arg1
 *  00419751   8b7424 08        mov esi,dword ptr ss:[esp+0x8]
 *  00419755   8bc6             mov eax,esi
 *  00419757   57               push edi
 *  00419758   8d78 01          lea edi,dword ptr ds:[eax+0x1]
 *  0041975b   eb 03            jmp short inrakutr.00419760
 *  0041975d   8d49 00          lea ecx,dword ptr ds:[ecx]
 *  00419760   8a10             mov dl,byte ptr ds:[eax] ; jichi: eax is the text
 *  00419762   83c0 01          add eax,0x1
 *  00419765   84d2             test dl,dl
 *  00419767  ^75 f7            jnz short inrakutr.00419760
 *  00419769   2bc7             sub eax,edi
 *  0041976b   50               push eax
 *  0041976c   56               push esi
 *  0041976d   83c1 04          add ecx,0x4
 *  00419770   e8 eb85feff      call inrakutr.00401d60
 *  00419775   5f               pop edi
 *  00419776   5e               pop esi
 *  00419777   c2 0400          retn 0x4
 *  0041977a   cc               int3
 *  0041977b   cc               int3
 *  0041977c   cc               int3
 *
 *  Runtime stack: this function takes two arguments. Text address is in arg1.
 *
 *  Other possible hooks are as follows:
 *  00460caf   53               push ebx
 *  00460cb0   c700 16000000    mov dword ptr ds:[eax],0x16
 *  00460cb6   e8 39feffff      call inrakutr.00460af4
 *  00460cbb   83c4 14          add esp,0x14
 *  00460cbe   385d fc          cmp byte ptr ss:[ebp-0x4],bl
 *  00460cc1   74 07            je short inrakutr.00460cca
 *  00460cc3   8b45 f8          mov eax,dword ptr ss:[ebp-0x8]
 *  00460cc6   8360 70 fd       and dword ptr ds:[eax+0x70],0xfffffffd
 *  00460cca   33c0             xor eax,eax
 *  00460ccc   eb 2c            jmp short inrakutr.00460cfa
 *  00460cce   0fb601           movzx eax,byte ptr ds:[ecx] ; jichi: here, ecx
 *  00460cd1   8b55 f4          mov edx,dword ptr ss:[ebp-0xc]
 *  00460cd4   f64410 1d 04     test byte ptr ds:[eax+edx+0x1d],0x4
 *  00460cd9   74 0e            je short inrakutr.00460ce9
 *  00460cdb   8d51 01          lea edx,dword ptr ds:[ecx+0x1]
 *  00460cde   381a             cmp byte ptr ds:[edx],bl
 *  00460ce0   74 07            je short inrakutr.00460ce9
 *  00460ce2   c1e0 08          shl eax,0x8
 *  00460ce5   8bf0             mov esi,eax
 *  00460ce7   8bca             mov ecx,edx
 *  00460ce9   0fb601           movzx eax,byte ptr ds:[ecx]
 *  00460cec   03c6             add eax,esi
 *  00460cee   385d fc          cmp byte ptr ss:[ebp-0x4],bl
 *  00460cf1   74 07            je short inrakutr.00460cfa
 *  00460cf3   8b4d f8          mov ecx,dword ptr ss:[ebp-0x8]
 *  00460cf6   8361 70 fd       and dword ptr ds:[ecx+0x70],0xfffffffd
 *  00460cfa   5e               pop esi
 *  00460cfb   5b               pop ebx
 *  00460cfc   c9               leave
 *  00460cfd   c3               retn
 *
 *  00460d41   74 05            je short inrakutr.00460d48
 *  00460d43   381e             cmp byte ptr ds:[esi],bl
 *  00460d45   74 01            je short inrakutr.00460d48
 *  00460d47   46               inc esi
 *  00460d48   8bc6             mov eax,esi
 *  00460d4a   5e               pop esi
 *  00460d4b   5b               pop ebx
 *  00460d4c   c3               retn
 *  00460d4d   56               push esi
 *  00460d4e   8b7424 08        mov esi,dword ptr ss:[esp+0x8]
 *  00460d52   0fb606           movzx eax,byte ptr ds:[esi] ; jichi: esi & ebp
 *  00460d55   50               push eax
 *  00460d56   e8 80fcffff      call inrakutr.004609db
 *  00460d5b   85c0             test eax,eax
 *  00460d5d   59               pop ecx
 *  00460d5e   74 0b            je short inrakutr.00460d6b
 *  00460d60   807e 01 00       cmp byte ptr ds:[esi+0x1],0x0
 *  00460d64   74 05            je short inrakutr.00460d6b
 *  00460d66   6a 02            push 0x2
 *  00460d68   58               pop eax
 *  00460d69   5e               pop esi
 *  00460d6a   c3               retn
 *
 *  00460d1d   53               push ebx
 *  00460d1e   53               push ebx
 *  00460d1f   53               push ebx
 *  00460d20   53               push ebx
 *  00460d21   53               push ebx
 *  00460d22   c700 16000000    mov dword ptr ds:[eax],0x16
 *  00460d28   e8 c7fdffff      call inrakutr.00460af4
 *  00460d2d   83c4 14          add esp,0x14
 *  00460d30   33c0             xor eax,eax
 *  00460d32   eb 16            jmp short inrakutr.00460d4a
 *  00460d34   0fb606           movzx eax,byte ptr ds:[esi] ; jichi: esi, ebp
 *  00460d37   50               push eax
 *  00460d38   e8 9efcffff      call inrakutr.004609db
 *  00460d3d   46               inc esi
 *  00460d3e   85c0             test eax,eax
 *  00460d40   59               pop ecx
 *  00460d41   74 05            je short inrakutr.00460d48
 *  00460d43   381e             cmp byte ptr ds:[esi],bl
 *  00460d45   74 01            je short inrakutr.00460d48
 *  00460d47   46               inc esi
 *
 *  0042c59f   cc               int3
 *  0042c5a0   56               push esi
 *  0042c5a1   8bf1             mov esi,ecx
 *  0042c5a3   8b86 cc650000    mov eax,dword ptr ds:[esi+0x65cc]
 *  0042c5a9   8b50 1c          mov edx,dword ptr ds:[eax+0x1c]
 *  0042c5ac   57               push edi
 *  0042c5ad   8b7c24 0c        mov edi,dword ptr ss:[esp+0xc]
 *  0042c5b1   8d8e cc650000    lea ecx,dword ptr ds:[esi+0x65cc]
 *  0042c5b7   57               push edi
 *  0042c5b8   ffd2             call edx
 *  0042c5ba   8bc7             mov eax,edi
 *  0042c5bc   8d50 01          lea edx,dword ptr ds:[eax+0x1]
 *  0042c5bf   90               nop
 *  0042c5c0   8a08             mov cl,byte ptr ds:[eax] ; jichi: here eax
 *  0042c5c2   83c0 01          add eax,0x1
 *  0042c5c5   84c9             test cl,cl
 *  0042c5c7  ^75 f7            jnz short inrakutr.0042c5c0
 *  0042c5c9   2bc2             sub eax,edx
 *  0042c5cb   50               push eax
 *  0042c5cc   57               push edi
 *  0042c5cd   8d8e 24660000    lea ecx,dword ptr ds:[esi+0x6624]
 *  0042c5d3   e8 8857fdff      call inrakutr.00401d60
 *  0042c5d8   8b86 b4660000    mov eax,dword ptr ds:[esi+0x66b4]
 *  0042c5de   85c0             test eax,eax
 *  0042c5e0   74 0d            je short inrakutr.0042c5ef
 *  0042c5e2   8b8e b8660000    mov ecx,dword ptr ds:[esi+0x66b8]
 *  0042c5e8   2bc8             sub ecx,eax
 *  0042c5ea   c1f9 02          sar ecx,0x2
 *  0042c5ed   75 05            jnz short inrakutr.0042c5f4
 *  0042c5ef   e8 24450300      call inrakutr.00460b18
 *  0042c5f4   8b96 b4660000    mov edx,dword ptr ds:[esi+0x66b4]
 *  0042c5fa   8b0a             mov ecx,dword ptr ds:[edx]
 *  0042c5fc   8b01             mov eax,dword ptr ds:[ecx]
 *  0042c5fe   8b50 30          mov edx,dword ptr ds:[eax+0x30]
 *  0042c601   ffd2             call edx
 *  0042c603   8b06             mov eax,dword ptr ds:[esi]
 *  0042c605   8b90 f8000000    mov edx,dword ptr ds:[eax+0xf8]
 *  0042c60b   6a 00            push 0x0
 *  0042c60d   68 c3164a00      push inrakutr.004a16c3
 *  0042c612   57               push edi
 *  0042c613   8bce             mov ecx,esi
 *  0042c615   ffd2             call edx
 *  0042c617   5f               pop edi
 *  0042c618   5e               pop esi
 *  0042c619   c2 0400          retn 0x4
 *  0042c61c   cc               int3
 *
 *  0041974e   cc               int3
 *  0041974f   cc               int3
 *  00419750   56               push esi
 *  00419751   8b7424 08        mov esi,dword ptr ss:[esp+0x8]
 *  00419755   8bc6             mov eax,esi
 *  00419757   57               push edi
 *  00419758   8d78 01          lea edi,dword ptr ds:[eax+0x1]
 *  0041975b   eb 03            jmp short inrakutr.00419760
 *  0041975d   8d49 00          lea ecx,dword ptr ds:[ecx]
 *  00419760   8a10             mov dl,byte ptr ds:[eax] ; jichi: eax
 *  00419762   83c0 01          add eax,0x1
 *  00419765   84d2             test dl,dl
 *  00419767  ^75 f7            jnz short inrakutr.00419760
 *  00419769   2bc7             sub eax,edi
 *  0041976b   50               push eax
 *  0041976c   56               push esi
 *  0041976d   83c1 04          add ecx,0x4
 *  00419770   e8 eb85feff      call inrakutr.00401d60
 *  00419775   5f               pop edi
 *  00419776   5e               pop esi
 *  00419777   c2 0400          retn 0x4
 *  0041977a   cc               int3
 *  0041977b   cc               int3
 *  0041977c   cc               int3
 *
 *  0042c731   57               push edi
 *  0042c732   ffd0             call eax
 *  0042c734   8bc7             mov eax,edi
 *  0042c736   8d50 01          lea edx,dword ptr ds:[eax+0x1]
 *  0042c739   8da424 00000000  lea esp,dword ptr ss:[esp]
 *  0042c740   8a08             mov cl,byte ptr ds:[eax] ; jichi: eax
 *  0042c742   83c0 01          add eax,0x1
 *  0042c745   84c9             test cl,cl
 *  0042c747  ^75 f7            jnz short inrakutr.0042c740
 *  0042c749   2bc2             sub eax,edx
 *  0042c74b   8bf8             mov edi,eax
 *  0042c74d   e8 fe1d0100      call inrakutr.0043e550
 *  0042c752   8b0d 187f4c00    mov ecx,dword ptr ds:[0x4c7f18]
 *  0042c758   8b11             mov edx,dword ptr ds:[ecx]
 *  0042c75a   8b42 70          mov eax,dword ptr ds:[edx+0x70]
 *  0042c75d   ffd0             call eax
 *  0042c75f   83c0 0a          add eax,0xa
 *  0042c762   0fafc7           imul eax,edi
 *  0042c765   5f               pop edi
 *  0042c766   8986 60660000    mov dword ptr ds:[esi+0x6660],eax
 */
bool InsertNexton1Hook()
{
  const BYTE bytes[] = {
      0x56,                   // 00419750   56               push esi    ; jichi: hook here, text in arg1
      0x8b, 0x74, 0x24, 0x08, // 00419751   8b7424 08        mov esi,dword ptr ss:[esp+0x8]
      0x8b, 0xc6,             // 00419755   8bc6             mov eax,esi
      0x57,                   // 00419757   57               push edi
      0x8d, 0x78, 0x01,       // 00419758   8d78 01          lea edi,dword ptr ds:[eax+0x1]
      0xeb, 0x03,             // 0041975b   eb 03            jmp short inrakutr.00419760
      0x8d, 0x49, 0x00,       // 0041975d   8d49 00          lea ecx,dword ptr ds:[ecx]
      0x8a, 0x10,             // 00419760   8a10             mov dl,byte ptr ds:[eax] ; jichi: eax is the text
      0x83, 0xc0, 0x01,       // 00419762   83c0 01          add eax,0x1
      0x84, 0xd2,             // 00419765   84d2             test dl,dl
      0x75, 0xf7,             // 00419767  ^75 f7            jnz short inrakutr.00419760
      0x2b, 0xc7,             // 00419769   2bc7             sub eax,edi
      0x50,                   // 0041976b   50               push eax
      0x56,                   // 0041976c   56               push esi
      0x83, 0xc1, 0x04        // 0041976d   83c1 04          add ecx,0x4
                              // 0xe8, XX4,           // 00419770   e8 eb85feff      call inrakutr.00401d60
                              // 0x5f,                // 00419775   5f               pop edi
                              // 0x5e,                // 00419776   5e               pop esi
                              // 0xc2, 0x04,0x00      // 00419777   c2 0400          retn 0x4
  };
  enum
  {
    addr_offset = 0
  }; // distance to the beginning of the function
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL_DWORD(addr); // supposed to be 0x4010e0
  if (!addr)
  {
    return false;
  }
  // GROWL_DWORD(addr);

  HookParam hp;
  hp.address = addr + addr_offset;
  // hp.length_offset = 1;
  hp.offset = stackoffset(1); // [esp+4] == arg0
  hp.type = USING_STRING;
  return NewHook(hp, "NEXTON1");
}
namespace
{
  // 真・恋姫†無双～乙女繚乱☆三国志演義～
  bool h2()
  {
    const BYTE bytes[] = {
        0x8b, 0xf8,
        0x0f, 0xb6, 0x3f,
        0x03, 0xfb,
        0x0f, 0x84, XX4,
        0x83, 0xff, 0x0a,
        0x0f, 0x84, XX4,
        0x83, 0xff, 0x20,
        0xd9, 0x44, 0x24, XX,
        0x0f, 0x84, XX4,
        0x81, 0xff, 0x40, 0x81, 0x00, 0x00};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0xd0);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.split = stackoffset(4);
    hp.type = USING_STRING | EMBED_ABLE | USING_SPLIT | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA; // 中文显示不正常，不过英文可以。
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      s = re::sub(s, R"(\n(?!\x81\x40))");
      buffer->from(s);
    };
    return NewHook(hp, "NEXTON2");
  }
}

bool Nexton1::attach_function()
{

  return h2() | InsertNexton1Hook();
}