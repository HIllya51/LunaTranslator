#include "FVP.h"

namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {
      /**
       *  FIXME: Scenario/name/history text cannot be distinguished
       *
       *  Sample game: 紅い瞳に映るセカイ
       *
       *  Scenario:
       *
       *  0012FD44   0043CB56  RETURN to .0043CB56 from .00433610
       *  0012FD48   0B711390
       *  0012FD4C   024FE43C
       *  0012FD50   02541120
       *  0012FD54   024FEC50
       *  0012FD58   00000000
       *  0012FD5C   024FE43C
       *  0012FD60   0044598E  RETURN to .0044598E
       *  0012FD64   024FE53C
       *  0012FD68   00000001
       *  0012FD6C   024FE43C
       *
       *  EAX 0000000E
       *  ECX 01B99750
       *  EDX 0B711391
       *  EBX 01E7047C
       *  ESP 0012FD44
       *  EBP 01B99750
       *  ESI 0B711390
       *  EDI 024FE53C
       *  EIP 00433610 .00433610
       *
       *  ecx:
       *  01B99750  F4 D8 45 00 A8 D5 45 00 A0 2B 8E 0A 00 00 00 00  E.ｨﾕE.+・....
       *  01B99760  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  01B99770  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  01B99780  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  [ecx+8]
       *  0A8E2BA0  B0 51 A6 63 C0 83 4C 04 15 00 00 00 03 00 00 00  ｰQｦcﾀキ......
       *  0A8E2BB0  00 00 00 0C 02 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  0A8E2BC0  00 04 00 00 80 00 00 00 00 00 00 00 00 00 00 00  ..............
       *  0A8E2BD0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  0012FD44   0043CB56  RETURN to .0043CB56 from .00433610
       *  0012FD48   0B6CE660
       *  0012FD4C   024FE43C
       *  0012FD50   02541120
       *  0012FD54   024FEC50
       *  0012FD58   00000000
       *  0012FD5C   024FE43C
       *  0012FD60   0044598E  RETURN to .0044598E
       *  0012FD64   024FE53C
       *  0012FD68   00000001
       *  0012FD6C   024FE43C
       *  0012FD70   00597669  d3dx9_31.00597669
       *  0012FD74   00000000
       *  0012FD78   004454D2  RETURN to .004454D2
       *  0012FD7C   01E7047C
       *  0012FD80   0043F67F  RETURN to .0043F67F from .00445440
       *  0012FD84   76F32EB2  user32.PeekMessageA
       *  0012FD88   76F52B5A  user32.TranslateAcceleratorA
       *  0012FD8C   76F366E3  user32.IsIconic
       *
       *  0B6D9118  06 06 07 07 07 07 08 08 07 08 09 0A 0A 08 09 09  .....
       *  0B6D9128  37 5F 7C 3B E8 B7 02 00 D8 FF 61 02 30 8C 70 0B  7_|;霍.ﾘa0継
       *  0B6D9138  35 5E 75 31 EF B7 02 08 98 7C 58 02 20 2F B9 01  5^u1・・X /ｹ
       *  0B6D9148  0B 00 00 00 C0 D0 E0 F0 A8 9A C7 23 00 00 00 8D  ...ﾀﾐ瑩ｨ塢#...・
       *  0B6D9158  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D9168  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D9178  81 42 00 00 00 00 00 00 B2 9A C7 23 00 00 00 8D  。......ｲ塢#...・
       *
       *  0B6D9188  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D9198  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D91A8  81 42 00 00 00 00 00 00 B4 9A C7 23 00 00 00 80  。......ｴ塢#...
       *  0B6D91B8  14 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  0B6D91C8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0B6D91D8  00 00 00 00 00 00 00 00 BE 9A C7 23 00 00 00 80  ........ｾ塢#...
       *  0B6D91E8  1A 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  0B6D91F8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0B6D9208  00 00 00 00 00 00 00 00 C0 9A C7 23 00 00 00 80  ........ﾀ塢#...
       *  0B6D9218  20 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00   ...............
       *  0B6D9228  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0B6D9238  00 00 00 00 00 00 00 00 CA 9A C7 23 00 00 00 80  ........ﾊ塢#...
       *  0B6D9248  26 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  &...............
       *  0B6D9258  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0B6D9268  00 00 00 00 00 00 00 00 CC 9A C7 23 00 00 00 80  ........ﾌ塢#...
       *
       *  History:
       *
       *  0012FD44   0043CB56  RETURN to .0043CB56 from .00433610
       *  0012FD48   0B7113D8
       *  0012FD4C   024FE43C
       *  0012FD50   02541120
       *  0012FD54   024FEC50
       *  0012FD58   00000000
       *  0012FD5C   024FE43C
       *  0012FD60   0044598E  RETURN to .0044598E
       *  0012FD64   024FE5CC
       *  0012FD68   00000001
       *  0012FD6C   024FE43C
       *
       *  0B6D9118  06 06 07 07 07 07 08 08 07 08 09 0A 0A 08 09 09  .....
       *  0B6D9128  37 5F 7C 3B E8 B7 02 00 D8 FF 61 02 30 8C 70 0B  7_|;霍.ﾘa0継
       *  0B6D9138  35 5E 75 31 EF B7 02 08 98 7C 58 02 20 2F B9 01  5^u1・・X /ｹ
       *  0B6D9148  0B 00 00 00 C0 D0 E0 F0 A8 9A C7 23 00 00 00 8D  ...ﾀﾐ瑩ｨ塢#...・
       *  0B6D9158  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D9168  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D9178  81 42 00 00 00 00 00 00 B2 9A C7 23 00 00 00 8D  。......ｲ塢#...・
       *  0B6D9188  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D9198  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D91A8  81 42 00 00 00 00 00 00 B4 9A C7 23 00 00 00 8A  。......ｴ塢#...・
       *  0B6D91B8  01 00 40 81 BB 82 CC 82 79 83 5B 81 57 83 AA 82  .@⊇のＺゼ仝Μ・
       *  0B6D91C8  CF 82 E7 82 CF 82 E7 82 C6 82 AC 97 B3 82 EA 82  ﾏらぱらとぎ竜れ・
       *  0B6D91D8  E9 82 42 81 7E 00 00 00 BE 9A C7 23 00 00 00 8D  驍B×...ｾ塢#...・
       *  0B6D91E8  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D91F8  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D9208  81 42 00 00 00 00 00 00 C0 9A C7 23 00 00 00 8D  。......ﾀ塢#...・
       *
       *  0B6D9218  81 40 82 BB 82 CC 83 79 81 5B 83 57 82 AA 82 CF  　そのページがぱ
       *  0B6D9228  82 E7 82 CF 82 E7 82 C6 97 AC 82 B3 82 EA 82 E9  らぱらと流される
       *  0B6D9238  81 42 00 00 00 00 00 00 CA 9A C7 23 00 00 00 80  。......ﾊ塢#...
       *  0B6D9248  26 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  &...............
       *  0B6D9258  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0B6D9268  00 00 00 00 00 00 00 00 CC 9A C7 23 00 00 00 80  ........ﾌ塢#...
       *
       *  ecx:
       *  02536A88  F4 D8 45 00 A8 D5 45 00 80 39 2F 04 00 00 00 00  E.ｨﾕE.9/....
       *  02536A98  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  02536AA8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  02536AB8  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  [ecx+8]
       *  042F3980  B0 51 A6 63 A0 1A E2 09 15 00 00 00 03 00 00 00  ｰQｦc・......
       *  042F3990  00 00 00 0C 02 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  042F39A0  00 04 00 00 80 00 00 00 00 00 00 00 00 00 00 00  ..............
       *  042F39B0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  042F39C0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  EAX 0000000E
       *  ECX 02537740
       *  EDX 0B7113D9
       *  EBX 01E7047C
       *  ESP 0012FD44
       *  EBP 02537740
       *  ESI 0B7113D8
       *  EDI 024FE5CC
       *  EIP 00433610 .00433610
       *
       *  0012FD44   0043CB56  RETURN to .0043CB56 from .00433610
       *  0012FD48   0B6CEA20
       *  0012FD4C   024FE43C
       *  0012FD50   02541120
       *  0012FD54   024FEC50
       *  0012FD58   00000000
       *  0012FD5C   024FE43C
       *  0012FD60   0044598E  RETURN to .0044598E
       *  0012FD64   024FE5CC
       *  0012FD68   00000001
       *  0012FD6C   024FE43C
       *  0012FD70   005A44DE  d3dx9_31.005A44DE
       *  0012FD74   00000000
       *  0012FD78   004454D2  RETURN to .004454D2
       *  0012FD7C   01E7047C
       *  0012FD80   0043F67F  RETURN to .0043F67F from .00445440
       *  0012FD84   76F32EB2  user32.PeekMessageA
       *  0012FD88   76F52B5A  user32.TranslateAcceleratorA
       *  0012FD8C   76F366E3  user32.IsIconic
       *
       *  Config message:
       *
       *  0012FD44   0043CB56  RETURN to .0043CB56 from .00433610
       *  0012FD48   026A1180
       *  0012FD4C   02508B94
       *  0012FD50   02541120
       *  0012FD54   025093A8
       *  0012FD58   00000000
       *  0012FD5C   02508B94
       *  0012FD60   0044598E  RETURN to .0044598E
       *  0012FD64   02508BA4
       *  0012FD68   00000001
       *  0012FD6C   02508B94
       *  0012FD70   005AC45E  d3dx9_31.005AC45E
       *  0012FD74   00000000
       *  0012FD78   004454D2  RETURN to .004454D2
       *  0012FD7C   01E7047C
       *  0012FD80   0043F67F  RETURN to .0043F67F from .00445440
       *  0012FD84   76F32EB2  user32.PeekMessageA
       *  0012FD88   76F52B5A  user32.TranslateAcceleratorA
       *  0012FD8C   76F366E3  user32.IsIconic
       *
       *  EAX 0000001E
       *  ECX 0253A4F8
       *  EDX 026A1181
       *  EBX 01E7047C
       *  ESP 0012FD44
       *  EBP 0253A4F8
       *  ESI 026A1180
       *  EDI 02508BA4
       *  EIP 00433610 .00433610
       *
       *  ecx:
       *  0253A4F8  F4 D8 45 00 A8 D5 45 00 00 D4 2F 04 00 00 00 00  E.ｨﾕE..ﾔ/....
       *  0253A508  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0253A518  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *  0253A528  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  [ecx+8]
       *  042FD400  B0 51 A6 63 C0 18 E2 09 15 00 00 00 03 00 00 00  ｰQｦcﾀ・......
       *  042FD410  00 00 00 0C 02 00 00 00 00 00 00 00 00 00 00 00  ...............
       *  042FD420  00 02 00 00 20 00 00 00 00 00 00 00 00 00 00 00  ... ...........
       *  042FD430  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
       *
       *  026A1160  25 07 4F 11 08 00 10 FE 0C 0A 1D 0C 01 1A 05 04  %O....
       *  026A1170  04 01 00 00 0C 01 07 90 11 08 00 0F 7C 05 0E 1F  ...・.|
       *
       *  026A1180  83 81 83 62 83 5A 81 5B 83 57 91 AC 93 78 83 54  メッセージ速度サ
       *  026A1190  83 93 83 76 83 8B 83 65 83 4C 83 58 83 67 00 03  ンプルテキスト.
       *  026A11A0  7B 00 03 85 00 0F 7C 05 03 6F 00 06 54 11 08 00  {.・|o.T.
       *
       */
      // bool hookBefore(winhook::hook_context *s)
      // {
      //   static std::string data_; // persistent storage, which makes this function not thread-safe
      //   LPCSTR text = (LPCSTR)s->stack[1]; // arg1
      //   if (!text || !*text)
      //     return true;
      //   //auto role = Engine::OtherRole;
      //   //if (text[-2] == 0 && text[-3] == 0 && text[-4] == 0) // 234 should be zero for text on the heap?
      //   //  role = Engine::ScenarioRole;
      //   auto role = Engine::ScenarioRole;

      //   auto retaddr = s->stack[0]; // retaddr, there is only one retaddr anyway
      //   //auto split = s->ecx;
      //   //if (Engine::isAddressReadable(split))
      //   //  split = *(DWORD *)(split + 8);
      //   auto sig = Engine::hashThreadSignature(role, retaddr);
      //   data_ = EngineController::instance()->dispatchTextASTD(text, role, sig);
      //   s->stack[1] = (ULONG)data_.c_str(); // reset arg1
      //   return true;
      // }
    } // namespace Private

    /** jichi 7/28/2015
     *  Sample game: 紅い瞳に映るセカイ
     *  Text can also be extracted in both GetGlyphOutlineA and lstrlenA
     *  See also: http://capita.tistory.com/m/post/267
     *
     *  0043360E   CC               INT3
     *  0043360F   CC               INT3
     *  00433610   83EC 0C          SUB ESP,0xC
     *  00433613   55               PUSH EBP
     *  00433614   56               PUSH ESI
     *  00433615   57               PUSH EDI
     *  00433616   8BF9             MOV EDI,ECX
     *  00433618   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
     *  0043361C   8DB7 74050000    LEA ESI,DWORD PTR DS:[EDI+0x574]
     *  00433622   50               PUSH EAX
     *  00433623   8BCE             MOV ECX,ESI
     *  00433625   897C24 18        MOV DWORD PTR SS:[ESP+0x18],EDI
     *  00433629   C74424 10 010000>MOV DWORD PTR SS:[ESP+0x10],0x1
     *  00433631   E8 8AEFFFFF      CALL .004325C0
     *  00433636   8D8F 90050000    LEA ECX,DWORD PTR DS:[EDI+0x590]
     *  0043363C   51               PUSH ECX
     *  0043363D   8D8F B8050000    LEA ECX,DWORD PTR DS:[EDI+0x5B8]
     *  00433643   E8 E8EFFFFF      CALL .00432630
     *  00433648   8B6C24 1C        MOV EBP,DWORD PTR SS:[ESP+0x1C]
     *  0043364C   8A45 00          MOV AL,BYTE PTR SS:[EBP]
     *  0043364F   84C0             TEST AL,AL
     *  00433651   0F84 8C000000    JE .004336E3
     *  00433657   53               PUSH EBX
     *  00433658   EB 06            JMP SHORT .00433660
     *  0043365A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  00433660   66:0FB6D0        MOVZX DX,AL
     *  00433664   0FB7DA           MOVZX EBX,DX
     *  00433667   0FB7C3           MOVZX EAX,BX
     *  0043366A   50               PUSH EAX
     *  0043366B   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
     *  0043366F   45               INC EBP
     *  00433670   E8 DA4D0100      CALL .0044844F
     *  00433675   83C4 04          ADD ESP,0x4
     *  00433678   85C0             TEST EAX,EAX
     *  0043367A   74 13            JE SHORT .0043368F
     *  0043367C   66:0FB64D 00     MOVZX CX,BYTE PTR SS:[EBP]
     *  00433681   C1E3 08          SHL EBX,0x8
     *  00433684   66:0BD9          OR BX,CX
     *  00433687   0FB7DB           MOVZX EBX,BX
     *  0043368A   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
     *  0043368E   45               INC EBP
     *  0043368F   8B4E 0C          MOV ECX,DWORD PTR DS:[ESI+0xC]
     *  00433692   85C9             TEST ECX,ECX
     *  00433694   75 04            JNZ SHORT .0043369A
     *  00433696   33C0             XOR EAX,EAX
     *  00433698   EB 07            JMP SHORT .004336A1
     *  0043369A   8B46 14          MOV EAX,DWORD PTR DS:[ESI+0x14]
     *  0043369D   2BC1             SUB EAX,ECX
     *  0043369F   D1F8             SAR EAX,1
     *  004336A1   8B7E 10          MOV EDI,DWORD PTR DS:[ESI+0x10]
     *  004336A4   8BD7             MOV EDX,EDI
     *  004336A6   2BD1             SUB EDX,ECX
     *  004336A8   D1FA             SAR EDX,1
     *  004336AA   3BD0             CMP EDX,EAX
     *  004336AC   73 0B            JNB SHORT .004336B9
     *  004336AE   66:891F          MOV WORD PTR DS:[EDI],BX
     *  004336B1   83C7 02          ADD EDI,0x2
     *  004336B4   897E 10          MOV DWORD PTR DS:[ESI+0x10],EDI
     *  004336B7   EB 1E            JMP SHORT .004336D7
     *  004336B9   3BCF             CMP ECX,EDI
     *  004336BB   76 05            JBE SHORT .004336C2
     *  004336BD   E8 644A0100      CALL .00448126
     *  004336C2   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  004336C4   8D4C24 20        LEA ECX,DWORD PTR SS:[ESP+0x20]
     *  004336C8   51               PUSH ECX
     *  004336C9   57               PUSH EDI
     *  004336CA   50               PUSH EAX
     *  004336CB   8D5424 1C        LEA EDX,DWORD PTR SS:[ESP+0x1C]
     *  004336CF   52               PUSH EDX
     *  004336D0   8BCE             MOV ECX,ESI
     *  004336D2   E8 F9E8FFFF      CALL .00431FD0
     *  004336D7   8A45 00          MOV AL,BYTE PTR SS:[EBP]
     *  004336DA   84C0             TEST AL,AL
     *  004336DC  ^75 82            JNZ SHORT .00433660
     *  004336DE   8B7C24 18        MOV EDI,DWORD PTR SS:[ESP+0x18]
     *  004336E2   5B               POP EBX
     *  004336E3   8D4424 1C        LEA EAX,DWORD PTR SS:[ESP+0x1C]
     *  004336E7   50               PUSH EAX
     *  004336E8   8BCE             MOV ECX,ESI
     *  004336EA   C74424 20 7E0000>MOV DWORD PTR SS:[ESP+0x20],0x7E
     *  004336F2   E8 C9EEFFFF      CALL .004325C0
     *  004336F7   6A 01            PUSH 0x1
     *  004336F9   6A 00            PUSH 0x0
     *  004336FB   6A 00            PUSH 0x0
     *  004336FD   8BCF             MOV ECX,EDI
     *  004336FF   E8 5CF4FFFF      CALL .00432B60
     *  00433704   5F               POP EDI
     *  00433705   5E               POP ESI
     *  00433706   5D               POP EBP
     *  00433707   83C4 0C          ADD ESP,0xC
     *  0043370A   C2 0400          RETN 0x4
     *  0043370D   CC               INT3
     *  0043370E   CC               INT3
     *  0043370F   CC               INT3
     *
     *  Sample game: 星空のメモリア
     *  0042EAAD   CC               INT3
     *  0042EAAE   CC               INT3
     *  0042EAAF   CC               INT3
     *  0042EAB0   83EC 0C          SUB ESP,0xC
     *  0042EAB3   55               PUSH EBP
     *  0042EAB4   56               PUSH ESI
     *  0042EAB5   57               PUSH EDI
     *  0042EAB6   8BF9             MOV EDI,ECX
     *  0042EAB8   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
     *  0042EABC   8DB7 A4000000    LEA ESI,DWORD PTR DS:[EDI+0xA4]
     *  0042EAC2   50               PUSH EAX
     *  0042EAC3   8BCE             MOV ECX,ESI
     *  0042EAC5   897C24 18        MOV DWORD PTR SS:[ESP+0x18],EDI
     *  0042EAC9   C74424 10 010000>MOV DWORD PTR SS:[ESP+0x10],0x1
     *  0042EAD1   E8 5AF2FFFF      CALL .0042DD30
     *  0042EAD6   8D8F B8000000    LEA ECX,DWORD PTR DS:[EDI+0xB8]
     *  0042EADC   51               PUSH ECX
     *  0042EADD   8D8F E0000000    LEA ECX,DWORD PTR DS:[EDI+0xE0]
     *  0042EAE3   E8 B8F2FFFF      CALL .0042DDA0
     *  0042EAE8   8B6C24 1C        MOV EBP,DWORD PTR SS:[ESP+0x1C]
     *  0042EAEC   8A45 00          MOV AL,BYTE PTR SS:[EBP]
     *  0042EAEF   84C0             TEST AL,AL
     *  0042EAF1   0F84 96000000    JE .0042EB8D
     *  0042EAF7   53               PUSH EBX
     *  0042EAF8   EB 06            JMP SHORT .0042EB00
     *  0042EAFA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  0042EB00   66:0FB6D0        MOVZX DX,AL
     *  0042EB04   0FB7DA           MOVZX EBX,DX
     *  0042EB07   0FB7C3           MOVZX EAX,BX
     *  0042EB0A   50               PUSH EAX
     *  0042EB0B   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
     *  0042EB0F   83C5 01          ADD EBP,0x1
     *  0042EB12   E8 22430100      CALL .00442E39
     *  0042EB17   83C4 04          ADD ESP,0x4
     *  0042EB1A   85C0             TEST EAX,EAX
     *  0042EB1C   74 11            JE SHORT .0042EB2F
     *  0042EB1E   33C9             XOR ECX,ECX
     *  0042EB20   8AEB             MOV CH,BL
     *  0042EB22   83C5 01          ADD EBP,0x1
     *  0042EB25   8A4D FF          MOV CL,BYTE PTR SS:[EBP-0x1]
     *  0042EB28   0FB7D9           MOVZX EBX,CX
     *  0042EB2B   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
     *  0042EB2F   8B56 04          MOV EDX,DWORD PTR DS:[ESI+0x4]
     *  0042EB32   85D2             TEST EDX,EDX
     *  0042EB34   75 04            JNZ SHORT .0042EB3A
     *  0042EB36   33C9             XOR ECX,ECX
     *  0042EB38   EB 07            JMP SHORT .0042EB41
     *  0042EB3A   8B4E 08          MOV ECX,DWORD PTR DS:[ESI+0x8]
     *  0042EB3D   2BCA             SUB ECX,EDX
     *  0042EB3F   D1F9             SAR ECX,1
     *  0042EB41   85D2             TEST EDX,EDX
     *  0042EB43   74 19            JE SHORT .0042EB5E
     *  0042EB45   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
     *  0042EB48   2BC2             SUB EAX,EDX
     *  0042EB4A   D1F8             SAR EAX,1
     *  0042EB4C   3BC8             CMP ECX,EAX
     *  0042EB4E   73 0E            JNB SHORT .0042EB5E
     *  0042EB50   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
     *  0042EB53   66:8918          MOV WORD PTR DS:[EAX],BX
     *  0042EB56   83C0 02          ADD EAX,0x2
     *  0042EB59   8946 08          MOV DWORD PTR DS:[ESI+0x8],EAX
     *  0042EB5C   EB 23            JMP SHORT .0042EB81
     *  0042EB5E   8B7E 08          MOV EDI,DWORD PTR DS:[ESI+0x8]
     *  0042EB61   3BD7             CMP EDX,EDI
     *  0042EB63   76 05            JBE SHORT .0042EB6A
     *  0042EB65   E8 6E420100      CALL .00442DD8
     *  0042EB6A   8D5424 20        LEA EDX,DWORD PTR SS:[ESP+0x20]
     *  0042EB6E   52               PUSH EDX
     *  0042EB6F   57               PUSH EDI
     *  0042EB70   56               PUSH ESI
     *  0042EB71   8D4424 1C        LEA EAX,DWORD PTR SS:[ESP+0x1C]
     *  0042EB75   50               PUSH EAX
     *  0042EB76   8BCE             MOV ECX,ESI
     *  0042EB78   E8 83ECFFFF      CALL .0042D800
     *  0042EB7D   8B7C24 18        MOV EDI,DWORD PTR SS:[ESP+0x18]
     *  0042EB81   8A45 00          MOV AL,BYTE PTR SS:[EBP]
     *  0042EB84   84C0             TEST AL,AL
     *  0042EB86  ^0F85 74FFFFFF    JNZ .0042EB00
     *  0042EB8C   5B               POP EBX
     *  0042EB8D   8D4C24 1C        LEA ECX,DWORD PTR SS:[ESP+0x1C]
     *  0042EB91   51               PUSH ECX
     *  0042EB92   8BCE             MOV ECX,ESI
     *  0042EB94   C74424 20 7E0000>MOV DWORD PTR SS:[ESP+0x20],0x7E
     *  0042EB9C   E8 8FF1FFFF      CALL .0042DD30
     *  0042EBA1   6A 01            PUSH 0x1
     *  0042EBA3   6A 00            PUSH 0x0
     *  0042EBA5   6A 00            PUSH 0x0
     *  0042EBA7   8BCF             MOV ECX,EDI
     *  0042EBA9   E8 72F4FFFF      CALL .0042E020
     *  0042EBAE   5F               POP EDI
     *  0042EBAF   5E               POP ESI
     *  0042EBB0   5D               POP EBP
     *  0042EBB1   83C4 0C          ADD ESP,0xC
     *  0042EBB4   C2 0400          RETN 0x4
     *  0042EBB7   CC               INT3
     *  0042EBB8   CC               INT3
     *  0042EBB9   CC               INT3
     *  0042EBBA   CC               INT3
     *  0042EBBB   CC               INT3
     *  0042EBBC   CC               INT3
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x53,                              // 00433657   53               push ebx
          0xeb, 0x06,                        // 00433658   eb 06            jmp short .00433660
          0x8d, 0x9b, 0x00, 0x00, 0x00, 0x00 // 0043365a   8d9b 00000000    lea ebx,dword ptr ds:[ebx]
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;

      // 0042EAAD   CC               INT3
      // 0042EAAE   CC               INT3
      // 0042EAAF   CC               INT3
      // 0042EAB0   83EC 0C          SUB ESP,0xC
      // 0042EAB3   55               PUSH EBP
      // 0042EAB4   56               PUSH ESI
      //
      // 00433657 - 00433610 = 71, function not aligned
      addr = MemDbg::findEnclosingFunctionBeforeDword(0x550cec83, addr, MemDbg::MaximumFunctionSize, 1); // step = 1
      // addr = MemDbg::findEnclosingAlignedFunction(addr); // does not work
      // addr = MemDbg::findEnclosingFunctionAfterInt3(addr); // does not work as there is not enough int3
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.embed_hook_font = F_DrawTextA | F_GetGlyphOutlineA;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        buffer->from(re::sub(buffer->strA(), "\\[.+\\|(.+?)\\]", "$1"));
      };

      return NewHook(hp, "EmbedFVP");
    }
  } // namespace ScenarioHook
} // unnamed namespace

/** Public class */

bool FVP::attach_function()
{
  ULONG startAddress, stopAddress;

  if (!ScenarioHook::attach(processStartAddress, processStopAddress))
    return false;
  // HijackManager::instance()->attachFunction((ULONG)::GetGlyphOutlineA); // for new game: 紅い瞳に映るセカイ
  // HijackManager::instance()->attachFunction((ULONG)::DrawTextA); // for old game: 星空のメモリア
  // HijackManager::instance()->attachFunction((ULONG)::CreateFontA);
  return true;
}

/**
 *  Get rid of ruby. Examples:
 *  [まぶた|瞼]を閉じた。
 */
// QString FVPEngine::rubyCreate(const QString &rb, const QString &rt)
//{
//   static QString fmt = "[%2|%1]";
//   return fmt.arg(rb, rt);
// }
//
//// Remove furigana in scenario thread.
// QString FVPEngine::rubyRemove(const QString &text)
//{
//   if (!text.contains('|'))
//     return text;
//   static QRegExp rx("\\[.+\\|(.+)\\]");
//   if (!rx.isMinimal())
//     rx.setMinimal(true);
//   return QString(text).replace(rx, "\\1");
// }

// std::wstring FVPEngine::rubyRemove(const std::wstring& text)
// {
//     if (text.find(L'|') == std::wstring::npos)
//         return text;
//     static std::wregex rx(L"\\[.+\\|(.+?)\\]");
//     return re::sub(text, rx, L"$1");
// }

// EOF
