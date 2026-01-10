#include "Leaf.h"

/** jichi 12/25/2014: Leaf/AQUAPLUS
 *  Sample game: [141224] [AQUAPLUS] WHITE ALBUM2 ミニアフタースト�リー
 *  Debug method: hardware break found text
 *  The text address is fixed.
 *  There are three matched functions.
 *  It can find both character name and scenario.
 *
 *  The scenario text contains "\n" or "\k".
 *
 *  0045145C   CC               INT3
 *  0045145D   CC               INT3
 *  0045145E   CC               INT3
 *  0045145F   CC               INT3
 *  00451460   D9EE             FLDZ
 *  00451462   56               PUSH ESI
 *  00451463   8B7424 08        MOV ESI,DWORD PTR SS:[ESP+0x8]
 *  00451467   D95E 0C          FSTP DWORD PTR DS:[ESI+0xC]
 *  0045146A   57               PUSH EDI
 *  0045146B   8BF9             MOV EDI,ECX
 *  0045146D   8B97 B0A00000    MOV EDX,DWORD PTR DS:[EDI+0xA0B0]
 *  00451473   33C0             XOR EAX,EAX
 *  00451475   3BD0             CMP EDX,EAX
 *  00451477   C706 05000000    MOV DWORD PTR DS:[ESI],0x5
 *  0045147D   C746 04 03000000 MOV DWORD PTR DS:[ESI+0x4],0x3
 *  00451484   8946 10          MOV DWORD PTR DS:[ESI+0x10],EAX
 *  00451487   8946 08          MOV DWORD PTR DS:[ESI+0x8],EAX
 *  0045148A   7F 0D            JG SHORT .00451499
 *  0045148C   8987 B0A00000    MOV DWORD PTR DS:[EDI+0xA0B0],EAX
 *  00451492   5F               POP EDI
 *  00451493   8BC6             MOV EAX,ESI
 *  00451495   5E               POP ESI
 *  00451496   C2 0400          RETN 0x4
 *  00451499   8D0492           LEA EAX,DWORD PTR DS:[EDX+EDX*4]
 *  0045149C   53               PUSH EBX
 *  0045149D   8B9C87 B08C0000  MOV EBX,DWORD PTR DS:[EDI+EAX*4+0x8CB0]
 *  004514A4   8D0487           LEA EAX,DWORD PTR DS:[EDI+EAX*4]
 *  004514A7   55               PUSH EBP
 *  004514A8   8D6B FF          LEA EBP,DWORD PTR DS:[EBX-0x1]
 *  004514AB   B9 04000000      MOV ECX,0x4
 *  004514B0   3BE9             CMP EBP,ECX
 *  004514B2   0F87 10020000    JA .004516C8
 *  004514B8   FF24AD E8164500  JMP DWORD PTR DS:[EBP*4+0x4516E8]
 *  004514BF   8B80 C08C0000    MOV EAX,DWORD PTR DS:[EAX+0x8CC0]
 *  004514C5   8D0480           LEA EAX,DWORD PTR DS:[EAX+EAX*4]
 *  004514C8   03C0             ADD EAX,EAX
 *  004514CA   0FBE9400 6416BC0>MOVSX EDX,BYTE PTR DS:[EAX+EAX+0xBC1664]
 *  004514D2   03C0             ADD EAX,EAX
 *  004514D4   8D5A FF          LEA EBX,DWORD PTR DS:[EDX-0x1]
 *  004514D7   3BD9             CMP EBX,ECX
 *  004514D9   0F87 B9000000    JA .00451598
 *  004514DF   FF249D FC164500  JMP DWORD PTR DS:[EBX*4+0x4516FC]
 *  004514E6   0FB688 6516BC00  MOVZX ECX,BYTE PTR DS:[EAX+0xBC1665]
 *  004514ED   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  004514F3   5D               POP EBP
 *  004514F4   5B               POP EBX
 *  004514F5   5F               POP EDI
 *  004514F6   894E 10          MOV DWORD PTR DS:[ESI+0x10],ECX
 *  004514F9   8BC6             MOV EAX,ESI
 *  004514FB   5E               POP ESI
 *  004514FC   C2 0400          RETN 0x4
 *  004514FF   0FBF90 6616BC00  MOVSX EDX,WORD PTR DS:[EAX+0xBC1666]
 *  00451506   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  0045150C   5D               POP EBP
 *  0045150D   5B               POP EBX
 *  0045150E   5F               POP EDI
 *  0045150F   8956 10          MOV DWORD PTR DS:[ESI+0x10],EDX
 *  00451512   8BC6             MOV EAX,ESI
 *  00451514   5E               POP ESI
 *  00451515   C2 0400          RETN 0x4
 *  00451518   8B80 6816BC00    MOV EAX,DWORD PTR DS:[EAX+0xBC1668]
 *  0045151E   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  00451524   5D               POP EBP
 *  00451525   5B               POP EBX
 *  00451526   8946 10          MOV DWORD PTR DS:[ESI+0x10],EAX
 *  00451529   5F               POP EDI
 *  0045152A   8BC6             MOV EAX,ESI
 *  0045152C   5E               POP ESI
 *  0045152D   C2 0400          RETN 0x4
 *  00451530   D980 6C16BC00    FLD DWORD PTR DS:[EAX+0xBC166C]
 *  00451536   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  0045153C   5D               POP EBP
 *  0045153D   D95E 0C          FSTP DWORD PTR DS:[ESI+0xC]
 *  00451540   5B               POP EBX
 *  00451541   5F               POP EDI
 *  00451542   894E 04          MOV DWORD PTR DS:[ESI+0x4],ECX
 *  00451545   8BC6             MOV EAX,ESI
 *  00451547   5E               POP ESI
 *  00451548   C2 0400          RETN 0x4
 *  0045154B   8B80 7016BC00    MOV EAX,DWORD PTR DS:[EAX+0xBC1670]
 *  00451551   8D58 01          LEA EBX,DWORD PTR DS:[EAX+0x1]
 *  00451554   8A10             MOV DL,BYTE PTR DS:[EAX]
 *  00451556   40               INC EAX
 *  00451557   84D2             TEST DL,DL
 *  00451559  ^75 F9            JNZ SHORT .00451554
 *  0045155B   2BC3             SUB EAX,EBX
 *  0045155D   8D58 01          LEA EBX,DWORD PTR DS:[EAX+0x1]
 *  00451560   53               PUSH EBX
 *  00451561   6A 00            PUSH 0x0
 *  00451563   53               PUSH EBX
 *  00451564   6A 00            PUSH 0x0
 *  00451566   FF15 74104A00    CALL DWORD PTR DS:[0x4A1074]             ; kernel32.GetProcessHeap
 *  0045156C   50               PUSH EAX
 *  0045156D   FF15 B4104A00    CALL DWORD PTR DS:[0x4A10B4]             ; ntdll.RtlAllocateHeap
 *  00451573   50               PUSH EAX
 *  00451574   E8 373F0200      CALL .004754B0
 *  00451579   8B8F B0A00000    MOV ECX,DWORD PTR DS:[EDI+0xA0B0]
 *  0045157F   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  00451582   8B8C8F C08C0000  MOV ECX,DWORD PTR DS:[EDI+ECX*4+0x8CC0]
 *  00451589   8D1489           LEA EDX,DWORD PTR DS:[ECX+ECX*4]
 *  0045158C   8B0C95 7016BC00  MOV ECX,DWORD PTR DS:[EDX*4+0xBC1670]
 *  00451593   E9 0C010000      JMP .004516A4
 *  00451598   52               PUSH EDX
 *  00451599   68 A8644A00      PUSH .004A64A8
 *  0045159E   E9 2B010000      JMP .004516CE
 *  004515A3   8D9492 2D230000  LEA EDX,DWORD PTR DS:[EDX+EDX*4+0x232D]
 *  004515AA   8B1C97           MOV EBX,DWORD PTR DS:[EDI+EDX*4]
 *  004515AD   85DB             TEST EBX,EBX
 *  004515AF   0F8C 23010000    JL .004516D8
 *  004515B5   8B80 C08C0000    MOV EAX,DWORD PTR DS:[EAX+0x8CC0]
 *  004515BB   99               CDQ
 *  004515BC   BD 1A000000      MOV EBP,0x1A
 *  004515C1   F7FD             IDIV EBP
 *  004515C3   C1E2 04          SHL EDX,0x4
 *  004515C6   03D3             ADD EDX,EBX
 *  004515C8   85C0             TEST EAX,EAX
 *  004515CA   74 1C            JE SHORT .004515E8
 *  004515CC   D98497 34A70000  FLD DWORD PTR DS:[EDI+EDX*4+0xA734]
 *  004515D3   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  004515D9   5D               POP EBP
 *  004515DA   D95E 0C          FSTP DWORD PTR DS:[ESI+0xC]
 *  004515DD   5B               POP EBX
 *  004515DE   5F               POP EDI
 *  004515DF   894E 04          MOV DWORD PTR DS:[ESI+0x4],ECX
 *  004515E2   8BC6             MOV EAX,ESI
 *  004515E4   5E               POP ESI
 *  004515E5   C2 0400          RETN 0x4
 *  004515E8   8B8497 B4A00000  MOV EAX,DWORD PTR DS:[EDI+EDX*4+0xA0B4]
 *  004515EF   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  004515F5   5D               POP EBP
 *  004515F6   5B               POP EBX
 *  004515F7   8946 10          MOV DWORD PTR DS:[ESI+0x10],EAX
 *  004515FA   5F               POP EDI
 *  004515FB   8BC6             MOV EAX,ESI
 *  004515FD   5E               POP ESI
 *  004515FE   C2 0400          RETN 0x4
 *  00451601   8B88 C08C0000    MOV ECX,DWORD PTR DS:[EAX+0x8CC0]
 *  00451607   D980 BC8C0000    FLD DWORD PTR DS:[EAX+0x8CBC]
 *  0045160D   894E 10          MOV DWORD PTR DS:[ESI+0x10],ECX
 *  00451610   D95E 0C          FSTP DWORD PTR DS:[ESI+0xC]
 *  00451613   8B88 B88C0000    MOV ECX,DWORD PTR DS:[EAX+0x8CB8]
 *  00451619   894E 08          MOV DWORD PTR DS:[ESI+0x8],ECX
 *  0045161C   8D9492 2D230000  LEA EDX,DWORD PTR DS:[EDX+EDX*4+0x232D]
 *  00451623   8B0C97           MOV ECX,DWORD PTR DS:[EDI+EDX*4]
 *  00451626   894E 04          MOV DWORD PTR DS:[ESI+0x4],ECX
 *  00451629   33C9             XOR ECX,ECX
 *  0045162B   8988 B08C0000    MOV DWORD PTR DS:[EAX+0x8CB0],ECX
 *  00451631   8988 B48C0000    MOV DWORD PTR DS:[EAX+0x8CB4],ECX
 *  00451637   8988 B88C0000    MOV DWORD PTR DS:[EAX+0x8CB8],ECX
 *  0045163D   5D               POP EBP
 *  0045163E   8988 BC8C0000    MOV DWORD PTR DS:[EAX+0x8CBC],ECX
 *  00451644   8988 C08C0000    MOV DWORD PTR DS:[EAX+0x8CC0],ECX
 *  0045164A   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  00451650   5B               POP EBX
 *  00451651   5F               POP EDI
 *  00451652   8BC6             MOV EAX,ESI
 *  00451654   5E               POP ESI
 *  00451655   C2 0400          RETN 0x4
 *  00451658   8B90 C08C0000    MOV EDX,DWORD PTR DS:[EAX+0x8CC0]
 *  0045165E   8B8497 14080000  MOV EAX,DWORD PTR DS:[EDI+EDX*4+0x814]  ; jichi: text in eax
 *  00451665   8D58 01          LEA EBX,DWORD PTR DS:[EAX+0x1]  ; jichi: hook here would crash
 *  00451668   8A10             MOV DL,BYTE PTR DS:[EAX]        ; jichi: text accessed here in eax
 *  0045166A   40               INC EAX
 *  0045166B   84D2             TEST DL,DL
 *  0045166D  ^75 F9            JNZ SHORT .00451668
 *  0045166F   2BC3             SUB EAX,EBX     ; jichi: hook here, text in ebx-1
 *  00451671   8D58 01          LEA EBX,DWORD PTR DS:[EAX+0X1]
 *  00451674   53               PUSH EBX
 *  00451675   6A 00            PUSH 0x0
 *  00451677   53               PUSH EBX
 *  00451678   6A 00            PUSH 0x0
 *  0045167A   FF15 74104A00    CALL DWORD PTR DS:[0x4A1074]             ; kernel32.GetProcessHeap
 *  00451680   50               PUSH EAX
 *  00451681   FF15 B4104A00    CALL DWORD PTR DS:[0x4A10B4]             ; ntdll.RtlAllocateHeap
 *  00451687   50               PUSH EAX
 *  00451688   E8 233E0200      CALL .004754B0
 *  0045168D   8B8F B0A00000    MOV ECX,DWORD PTR DS:[EDI+0xA0B0]
 *  00451693   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  00451696   8B948F C08C0000  MOV EDX,DWORD PTR DS:[EDI+ECX*4+0x8CC0]
 *  0045169D   8B8C97 14080000  MOV ECX,DWORD PTR DS:[EDI+EDX*4+0x814]  ; jichi: text in ecx
 *  004516A4   53               PUSH EBX
 *  004516A5   51               PUSH ECX
 *  004516A6   50               PUSH EAX
 *  004516A7   8946 08          MOV DWORD PTR DS:[ESI+0x8],EAX
 *  004516AA   E8 31410200      CALL .004757E0
 *  004516AF   83C4 18          ADD ESP,0x18
 *  004516B2   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  004516B8   5D               POP EBP
 *  004516B9   5B               POP EBX
 *  004516BA   5F               POP EDI
 *  004516BB   C746 04 05000000 MOV DWORD PTR DS:[ESI+0x4],0x5
 *  004516C2   8BC6             MOV EAX,ESI
 *  004516C4   5E               POP ESI
 *  004516C5   C2 0400          RETN 0x4
 *  004516C8   53               PUSH EBX
 *  004516C9   68 8C644A00      PUSH .004A648C
 *  004516CE   6A 00            PUSH 0x0
 *  004516D0   E8 6BABFFFF      CALL .0044C240
 *  004516D5   83C4 0C          ADD ESP,0xC
 *  004516D8   FF8F B0A00000    DEC DWORD PTR DS:[EDI+0xA0B0]
 *  004516DE   5D               POP EBP
 *  004516DF   5B               POP EBX
 *  004516E0   5F               POP EDI
 *  004516E1   8BC6             MOV EAX,ESI
 *  004516E3   5E               POP ESI
 *  004516E4   C2 0400          RETN 0x4
 *  004516E7   90               NOP
 *  004516E8   BF 144500A3      MOV EDI,0xA3004514
 *  004516ED   15 45005816      ADC EAX,0x16580045
 *  004516F2   45               INC EBP
 *  004516F3   00C8             ADD AL,CL
 *  004516F5   16               PUSH SS
 *  004516F6   45               INC EBP
 *  004516F7   0001             ADD BYTE PTR DS:[ECX],AL
 *  004516F9   16               PUSH SS
 *  004516FA   45               INC EBP
 *  004516FB   00E6             ADD DH,AH
 *  004516FD   14 45            ADC AL,0x45
 *  004516FF   00FF             ADD BH,BH
 *  00451701   14 45            ADC AL,0x45
 *  00451703   0018             ADD BYTE PTR DS:[EAX],BL
 *  00451705   15 45003015      ADC EAX,0x15300045
 *  0045170A   45               INC EBP
 *  0045170B   004B 15          ADD BYTE PTR DS:[EBX+0x15],CL
 *  0045170E   45               INC EBP
 *  0045170F   0083 7C240800    ADD BYTE PTR DS:[EBX+0x8247C],AL
 *  00451715   56               PUSH ESI
 *  00451716   8BF1             MOV ESI,ECX
 *  00451718   74 29            JE SHORT .00451743
 *  0045171A   8B86 B0A00000    MOV EAX,DWORD PTR DS:[ESI+0xA0B0]
 *  00451720   3D FF000000      CMP EAX,0xFF
 *  00451725   7C 15            JL SHORT .0045173C
 *  00451727   68 74644A00      PUSH .004A6474
 *  0045172C   6A 00            PUSH 0x0
 *  0045172E   E8 0DABFFFF      CALL .0044C240
 *  00451733   83C4 08          ADD ESP,0x8
 *  00451736   33C0             XOR EAX,EAX
 *  00451738   5E               POP ESI
 *  00451739   C2 0800          RETN 0x8
 *  0045173C   40               INC EAX
 *  0045173D   8986 B0A00000    MOV DWORD PTR DS:[ESI+0xA0B0],EAX
 *  00451743   8B86 B0A00000    MOV EAX,DWORD PTR DS:[ESI+0xA0B0]
 *  00451749   8D0C80           LEA ECX,DWORD PTR DS:[EAX+EAX*4]
 *  0045174C   8D0C8E           LEA ECX,DWORD PTR DS:[ESI+ECX*4]
 *  0045174F   57               PUSH EDI
 *  00451750   8BB9 B08C0000    MOV EDI,DWORD PTR DS:[ECX+0x8CB0]
 *  00451756   8BD7             MOV EDX,EDI
 *  00451758   83EA 01          SUB EDX,0x1
 *  0045175B   74 70            JE SHORT .004517CD
 *  0045175D   83EA 01          SUB EDX,0x1
 *  00451760   74 1A            JE SHORT .0045177C
 *  00451762   57               PUSH EDI
 *  00451763   68 CC644A00      PUSH .004A64CC
 *  00451768   6A 00            PUSH 0x0
 *  0045176A   E8 D1AAFFFF      CALL .0044C240
 *  0045176F   83C4 0C          ADD ESP,0xC
 *  00451772   5F               POP EDI
 *  00451773   B8 01000000      MOV EAX,0x1
 *  00451778   5E               POP ESI
 *  00451779   C2 0800          RETN 0x8
 *  0045177C   8D9480 2D230000  LEA EDX,DWORD PTR DS:[EAX+EAX*4+0x232D]
 *  00451783   8B3C96           MOV EDI,DWORD PTR DS:[ESI+EDX*4]
 *  00451786   85FF             TEST EDI,EDI
 *  00451788   0F8C C8000000    JL .00451856
 *  0045178E   8B81 C08C0000    MOV EAX,DWORD PTR DS:[ECX+0x8CC0]
 *  00451794   99               CDQ
 *  00451795   B9 1A000000      MOV ECX,0x1A
 *  0045179A   F7F9             IDIV ECX
 *  0045179C   C1E2 04          SHL EDX,0x4
 *  0045179F   03D7             ADD EDX,EDI
 *  004517A1   85C0             TEST EAX,EAX
 *  004517A3   74 13            JE SHORT .004517B8
 *  004517A5   DB4424 0C        FILD DWORD PTR SS:[ESP+0xC]
 *  004517A9   5F               POP EDI
 *  004517AA   8D41 E7          LEA EAX,DWORD PTR DS:[ECX-0x19]
 *  004517AD   D99C96 34A70000  FSTP DWORD PTR DS:[ESI+EDX*4+0xA734]
 *  004517B4   5E               POP ESI
 *  004517B5   C2 0800          RETN 0x8
 *  004517B8   8B4424 0C        MOV EAX,DWORD PTR SS:[ESP+0xC]
 *  004517BC   898496 B4A00000  MOV DWORD PTR DS:[ESI+EDX*4+0xA0B4],EAX
 *  004517C3   5F               POP EDI
 *  004517C4   B8 01000000      MOV EAX,0x1
 *  004517C9   5E               POP ESI
 *  004517CA   C2 0800          RETN 0x8
 *  004517CD   8B89 C08C0000    MOV ECX,DWORD PTR DS:[ECX+0x8CC0]
 *  004517D3   8D0489           LEA EAX,DWORD PTR DS:[ECX+ECX*4]
 *  004517D6   03C0             ADD EAX,EAX
 *  004517D8   0FBE9400 6416BC0>MOVSX EDX,BYTE PTR DS:[EAX+EAX+0xBC1664]
 *  004517E0   03C0             ADD EAX,EAX
 *  004517E2   8D7A FF          LEA EDI,DWORD PTR DS:[EDX-0x1]
 *  004517E5   83FF 04          CMP EDI,0x4
 *  004517E8   77 41            JA SHORT .0045182B
 *  004517EA   FF24BD 60184500  JMP DWORD PTR DS:[EDI*4+0x451860]
 *  004517F1   8A4C24 0C        MOV CL,BYTE PTR SS:[ESP+0xC]
 *  004517F5   8888 6516BC00    MOV BYTE PTR DS:[EAX+0xBC1665],CL
 *  004517FB   EB 3E            JMP SHORT .0045183B
 *  004517FD   66:8B5424 0C     MOV DX,WORD PTR SS:[ESP+0xC]
 *  00451802   66:8990 6616BC00 MOV WORD PTR DS:[EAX+0xBC1666],DX
 *  00451809   EB 30            JMP SHORT .0045183B
 *  0045180B   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  0045180F   8988 6816BC00    MOV DWORD PTR DS:[EAX+0xBC1668],ECX
 *  00451815   EB 24            JMP SHORT .0045183B
 *  00451817   DB4424 0C        FILD DWORD PTR SS:[ESP+0xC]
 *  0045181B   D998 6C16BC00    FSTP DWORD PTR DS:[EAX+0xBC166C]
 *  00451821   EB 18            JMP SHORT .0045183B
 *  00451823   51               PUSH ECX
 *  00451824   68 BC644A00      PUSH .004A64BC
 *  00451829   EB 06            JMP SHORT .00451831
 *  0045182B   52               PUSH EDX
 *  0045182C   68 A8644A00      PUSH .004A64A8
 *  00451831   6A 00            PUSH 0x0
 *  00451833   E8 08AAFFFF      CALL .0044C240
 *  00451838   83C4 0C          ADD ESP,0xC
 *  0045183B   8B86 B0A00000    MOV EAX,DWORD PTR DS:[ESI+0xA0B0]
 *  00451841   8D1480           LEA EDX,DWORD PTR DS:[EAX+EAX*4]
 *  00451844   8B8496 C08C0000  MOV EAX,DWORD PTR DS:[ESI+EDX*4+0x8CC0]
 *  0045184B   6A 00            PUSH 0x0
 *  0045184D   50               PUSH EAX
 *  0045184E   E8 FDF0FFFF      CALL .00450950
 *  00451853   83C4 08          ADD ESP,0x8
 *  00451856   5F               POP EDI
 *  00451857   B8 01000000      MOV EAX,0x1
 *  0045185C   5E               POP ESI
 *  0045185D   C2 0800          RETN 0x8
 *  00451860   F1               INT1
 *  00451861   17               POP SS                                   ; Modification of segment register
 *  00451862   45               INC EBP
 *  00451863   00FD             ADD CH,BH
 *  00451865   17               POP SS                                   ; Modification of segment register
 *  00451866   45               INC EBP
 *  00451867   000B             ADD BYTE PTR DS:[EBX],CL
 *  00451869   1845 00          SBB BYTE PTR SS:[EBP],AL
 *  0045186C   17               POP SS                                   ; Modification of segment register
 *  0045186D   1845 00          SBB BYTE PTR SS:[EBP],AL
 *  00451870   2318             AND EBX,DWORD PTR DS:[EAX]
 *  00451872   45               INC EBP
 *  00451873   00CC             ADD AH,CL
 *  00451875   CC               INT3
 *  00451876   CC               INT3
 *  00451877   CC               INT3
 *  00451878   CC               INT3
 *  00451879   CC               INT3
 *  0045187A   CC               INT3
 *  0045187B   CC               INT3
 *  0045187C   CC               INT3
 *  0045187D   CC               INT3
 *
 *  EAX 00000038
 *  ECX 00000004 ; jichi: fixed
 *  EDX 00000000 ; jichi: fixed
 *  EBX 00321221
 *  ESP 0012FD98
 *  EBP 00000002
 *  ESI 0012FDC4
 *  EDI 079047E0
 *  EIP 00451671 .00451671
 */
namespace
{
  std::string save;
  int role;
}
static void SpecialHookLeaf(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD text = context->ebx - 1; // = ebx -1
  save = std::string((LPSTR)text, ::strlen((LPCSTR)text));
  *split = FIXED_SPLIT_VALUE; // only caller's address use as split
  buffer->from(save);
}
// Remove both \n and \k
static void LeafFilter(TextBuffer *buffer, HookParam *)
{
  LPSTR text = (LPSTR)buffer->buff;
  if (::memchr(text, '\\', buffer->size))
  {
    StringFilter(buffer, TEXTANDLEN("\\n"));
    StringFilter(buffer, TEXTANDLEN("\\k"));
  }
}
namespace
{
  void hook2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    strReplace(save, "\\k");
    save = re::sub(save, "<R(.+?)\\|.+>", "$1");
    buffer->from(save);
  }
  void hook2a(hook_context *s, TextBuffer buffer)
  {
    s->ecx = (DWORD)allocateString(buffer.viewA());
  }
}
bool InsertLeafHook()
{
  const BYTE bytes[] = {
      0x8b, 0x90, XX4,       // 00451658   8b90 c08c0000    mov edx,dword ptr ds:[eax+0x8cc0]
      0x8b, 0x84, 0x97, XX4, // 0045165e   8b8497 14080000  mov eax,dword ptr ds:[edi+edx*4+0x814]
      // The above is needed as there are other matches
      0x8d, 0x58, 0x01, // 00451665   8d58 01          lea ebx,dword ptr ds:[eax+0x1] ; jichi: hook here would crash because of jump
      0x8a, 0x10,       // 00451668   8a10             mov dl,byte ptr ds:[eax]    ; jichi: text accessed here in eax
      0x40,             // 0045166a   40               inc eax
      0x84, 0xd2,       // 0045166b   84d2             test dl,dl
      0x75, 0xf9,       // 0045166d  ^75 f9            jnz short .00451668
      0x2b, 0xc3,       // 0045166f   2bc3             sub eax,ebx     ; jichi: hook here, text in ebx-1
      0x8d, 0x58, 0x01  // 00451671   8d58 01           lea ebx,dword ptr ds:[eax+0x1]
                        // 0x53,               // 00451674   53               push ebx
                        // 0x6a, 0x00,         // 00451675   6a 00            push 0x0
                        // 0x53,               // 00451677   53               push ebx
                        // 0x6a, 0x00,         // 00451678   6a 00            push 0x0
                        // 0xff,0x15           // 0045167a   ff15 74104a00    call dword ptr ds:[0x4a1074]             ; kernel32.getprocessheap
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  enum
  {
    addr_offset = 0x0045166f - 0x00451658
  };
  // GROWL_DWORD(addr);
  if (!addr)
  {
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  // hp.offset=regoffset(eax);
  hp.type = USING_STRING | USING_SPLIT; // use top of the stack as split
  hp.text_fun = SpecialHookLeaf;
  hp.filter_fun = LeafFilter; // remove two characters
  auto succ = NewHook(hp, "Leaf");

  // ConsoleOutput("Leaf: disable GDI hooks");
  //  0045165E   8B8497 14080000  MOV EAX,DWORD PTR DS:[EDI+EDX*4+0x814]  ; jichi: text in eax, hook1 hook after here to replace eax
  //  0045169D   8B8C97 14080000  MOV ECX,DWORD PTR DS:[EDI+EDX*4+0x814]  ; jichi: text in ecx, hook2 hook after here to replace ecx
  const uint8_t bytes1[] = {0x8b, 0x84, 0x97, 0x14, 0x08, 0x00, 0x00},
                bytes2[] = {0x8b, 0x8c, 0x97, 0x14, 0x08, 0x00, 0x00};

  ULONG addr1 = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress),
        addr2 = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr1 || !addr2)
    return true;
  HookParam hp1;
  // 这个会卡死，无解
  //  hp.address=addr1+7;
  //  hp.hook_before=Private::hook1;
  //  hp.embed_fun=Private::hookafterbf;
  //  hp.type=EMBED_ABLE;
  // NewHook(hp,"EmbedLeaf");
  hp1.address = addr2 + 7;
  hp1.text_fun = hook2;
  hp1.embed_fun = hook2a;
  hp1.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
  hp1.lineSeparator = L"\\n";
  succ |= NewHook(hp1, "EmbedLeaf");
  return succ;
}
bool activehook()
{

  /*
   * Sample games:
   * https://vndb.org/v2477
   */
  const BYTE bytes[] = {
      0x56,             // push esi                   << hook here
      0xE8, XX4,        // call HEARTWORK.EXE+134F0
      0x83, 0xC4, 0x38, // add esp,38
      0x5F,             // pop edi
      0x5D,             // pop ebp
      0x5B,             // pop ebx
      0xE8, XX4         // call HEARTWORK.EXE+1AF80
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(ecx);
  hp.type = USING_STRING;
  return NewHook(hp, "active");
}
void AquaplusFilter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);

  CharReplacer(buffer, '^', '\"');
  StringCharReplacer(buffer, TEXTANDLEN("\\n"), ' ');
  StringFilter(buffer, TEXTANDLEN("\\k"));
  StringFilter(buffer, TEXTANDLEN("\\p"));
  if (cpp_strnstr(text, "<R", buffer->size))
  { // ex. <R華奢|きゃしゃ>
    StringFilter(buffer, TEXTANDLEN("<R"));
    StringFilterBetween(buffer, TEXTANDLEN("|"), TEXTANDLEN(">"));
  }
  StringFilter(buffer, "<c", 3); // remove "<c" followed by 1 char
  CharFilter(buffer, '>');
}

bool InsertAquaplus1Hook()
{

  /*
   * Sample games:
   * https://vndb.org/r20439
   */
  const BYTE bytes[] = {
      0xCC,                   // int 3
      0x53,                   // push ebx             << hook here
      0x8B, 0x5C, 0x24, 0x0C, // mov ebx,[esp+0C]
      0x55,                   // push ebp
      0x8B, 0x6C, 0x24, 0x0C, // mov ebp,[esp+0C]
      0x56,                   // push esi
      0x57,                   // push edi
      0x8B, 0x7D, 0x24,       // mov edi,[ebp+24]
      0x85, 0xFF              // test edi,edi
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  hp.filter_fun = AquaplusFilter;
  return NewHook(hp, "Aquaplus1");
}

bool InsertAquaplus2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/r108249
   */
  const BYTE bytes[] = {
      0xC6, 0x04, 0x30, 0x00, // mov byte ptr [eax+esi],00           << hook here
      0x8B, 0xF2,             // mov esi,edx
      0x8A, 0x02,             // mov al,[edx]
      0x42,                   // inc edx
      0x84, 0xC0,             // test al,al
      0x75, 0xF9              // jne "WHITE ALBUM Memories like Falling Snow.exe"+85253
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(ebx);
  hp.index = 0;
  hp.split = regoffset(esp);
  hp.split_index = 0;
  hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT | CODEC_UTF8;
  hp.filter_fun = AquaplusFilter;
  return NewHook(hp, "Aquaplus2");
}
bool InsertAquaplus3Hook()
{
  /*
   * Sample games:
   * Dungeon Travelers 2: The Royal Library & the Monster Seal
   */
  const BYTE bytes[] = {
      0xCC,                  // int 3
      0x80, 0x3D, XX4, 0x00, // cmp byte ptr [DT2_en.exe+3052EC],00    << hook here
      0x75, 0x67,            // jne DT2_en.exe+89DC0
      0x56,                  // push esi
      0xBA, XX4              // mov edx,DT2_en.exe+3051E0
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 1;
  hp.offset = regoffset(eax);
  hp.type = CODEC_UTF8 | USING_STRING | NO_CONTEXT;
  hp.filter_fun = NewLineCharToSpaceA;
  return NewHook(hp, "Aquaplus3");
}
bool InsertAquaplusHooks()
{
  return InsertAquaplus1Hook() || InsertAquaplus2Hook() || InsertAquaplus3Hook();
}

namespace
{
  bool kizuato()
  {
    const BYTE bytes[] = {
        // 痕　～きずあと～　
        0x3c, 0xa0,
        0x0f, 0x82, XX4,
        0x3c, 0xe0,
        0x0f, 0x83};
    const BYTE bytes2[] = {
        // 雫　～しずく～　
        0x80, 0xf9, 0xa0,
        0x0f, 0x82, XX4,
        0x80, 0xf9, 0xe0,
        0x0f, 0x83};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE subespbegin[] = {0x81, 0xEC, XX, 0x01, 0x00, 0x00};
    addr = reverseFindBytes(subespbegin, sizeof(subespbegin), addr - 0x500, addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | NO_CONTEXT;

    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      if (context->stack[16] == -1)
        return;
      auto current = std::string((char *)context->stack[13]);
      auto spls = re::split(current, R"((\\k|\\s))");
      current = spls[context->stack[16]];
      static std::string last;
      if (last == current)
        return;
      last = current;

      strReplace(current, "\\n");
      strReplace(current, "\\k");
      strReplace(current, "\\s");
      current = re::sub(current, R"(<R(.*?)\|(.*?)>)", "$1");
      current = re::sub(current, R"(<[A-Za-z]\d*(.*?)>)", "$1");
      buffer->from(current);
    };
    return NewHook(hp, "kizuato");
  }
}
namespace
{
  // WHITE ALBUM2 Special Contents
  /*
  int __cdecl sub_40DE00(char *Source, int a2)
  {
    int v2; // eax
    int v3; // edx
    _DWORD *v4; // esi
    unsigned __int8 *v5; // edi
    unsigned __int8 *v6; // ebx
    double v7; // st7
    float v9; // [esp+0h] [ebp-14h]
    float v10; // [esp+4h] [ebp-10h]

    sub_4033B0(Source, 0);
    v2 = sub_405100();
    sub_4050E0(v2 - 1);
    v4 = (_DWORD *)(4 * v3 + 4961380);
    v5 = (unsigned __int8 *)(4 * v3 + 4961381);
    v6 = (unsigned __int8 *)(4 * v3 + 4961382);
    if ( dword_4CFC84 )
      sub_44B0A0(
        452,
        0,
        Source,
        28,
        40,
        15,
        0,
        14,
        32,
        40,
        1,
        BYTE2(dword_4BB464[v3]),
        BYTE1(dword_4BB464[v3]),
        (unsigned __int8)dword_4BB464[v3],
        BYTE2(dword_4BB490),
        BYTE1(dword_4BB490),
        (unsigned __int8)dword_4BB490,
        1);
    else
      sub_44B0A0(
        452,
        0,
        Source,
        28,
        28,
        4,
        0,
        14,
        32,
        40,
        1,
        BYTE2(dword_4BB464[v3]),
        BYTE1(dword_4BB464[v3]),
        (unsigned __int8)dword_4BB464[v3],
        BYTE2(dword_4BB490),
        BYTE1(dword_4BB490),
        (unsigned __int8)dword_4BB490,
        1);
    sub_44B490(1091, 0, 4183, 1);
    if ( dword_4D00E4 )
      sub_44B110(dword_4D00F0 + 1, *v6, *v5, (unsigned __int8)*v4, -1, -1, -1);
    sub_44B540(1091, 2);
    if ( dword_4CFC84 )
    {
      v10 = 26.0;
      v7 = 75.0;
    }
    else
    {
      v10 = 536.0;
      v7 = 274.0;
    }
    v9 = v7;
    sub_44B730(1091, v9, v10);
    sub_44B7F0(1091, 640.0, 624.0);
    sub_44B940(1091, 2);
    dword_4CFC64 = (unsigned int)(dword_4CFC64 - 1) <= 1;
    dword_4CFC78 = a2;
    dword_4CFC74 = 0;
    dword_4CFC7C = 0;
    dword_4CFC98 = 0;
    sub_44B4E0(1091, 0);
    return sub_44B4F0(1091, dword_4CFC7C);
  }
  */
  bool wa2special()
  {
    BYTE sig[] = {
        0x6A, 0x01, 0x6A, 0x28, 0x6A, 0x20, 0x6A, 0x0E, 0x6A, 0x00, 0x6A, 0x0F, 0x6A, 0x28, 0x6A, 0x1C
        // .text:0040DE70                 push    1
        // .text:0040DE72                 push    28h ; '('
        // .text:0040DE74                 push    20h ; ' '
        // .text:0040DE76                 push    0Eh
        // .text:0040DE78                 push    0
        // .text:0040DE7A                 push    0Fh
        // .text:0040DE7C                 push    28h ; '('
        // .text:0040DE7E                 push    1Ch
    };
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_DYNA_SJIS | EMBED_AFTER_NEW;
    hp.lineSeparator = L"\\n";
    hp.filter_fun = AquaplusFilter;
    return NewHook(hp, "wa2special");
  }
}
namespace
{
  bool toheartpse()
  {
    /*
  int __cdecl sub_414C00(int a1, int a2, int a3, int a4, int a5, int a6, int a7)
{
  int result; // eax

  result = 0;
  if ( !a2 && dword_45B310 && (a5 == 33116 || a5 == 33951) && dword_44D3D8 + dword_45A2F4 == a3 && dword_44D3DC == a4 )
  {
    sub_414770(a1, 0, a3 - 1, a4 - 1, a5, -1, a7);
    sub_414770(a1, 0, a3 - 2, a4 - 1, a5, a6, -1);
    result = 1;
  }
  dword_45B310 = 0;
  if ( a5 == 33116 || a5 == 33951 )
  {
    dword_45B310 = 1;
    dword_44D3D8 = a3;
    dword_44D3DC = a4;
  }
  if ( !result )
    return sub_414770(a1, a2, a3 - 1, a4 - 1, a5, a6, a7);
  return result;
}
    */

    BYTE sig[] = {
        0x8b, 0x7c, 0x24, 0x24,
        0x85, 0xc9,
        0x75, XX,
        0x8b, 0x0d, XX4,
        0x85, 0xc9,
        0x74, XX,
        0x81, 0xff, 0x5c, 0x81, 0x00, 0x00,
        0x74, XX,
        0x81, 0xff, 0x9f, 0x84, 0x00, 0x00,
        0x75, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(5);
    hp.type = USING_CHAR | CODEC_ANSI_BE;
    return NewHook(hp, "toheartpse");
  }
}
namespace
{
  //[000128][Leaf] Filsnown ～光と刻～ Windows版（猪名川でいこう!!付属）
  bool filsnown()
  {
    BYTE sig[] = {
        0x8b, 0x45, 0x14,
        0x3d, 0x40, 0x81, 0x00, 0x00,
        0x0f, 0x84, XX4,
        0x83, 0xf8, 0x20,
        0x0f, 0x86, XX4,
        0x3d, 0xd0, 0x00, 0x00, 0x00,
        0x73, XX,
        0xC7, 0x45, XX, 0x01, 0x00, 0x00, 0x00,
        0x8b, 0x04, 0x85, XX4,
        0x89, 0x45, XX,
        0xeb, XX,
        0x3d, 0x40, 0x81, 0x00, 0x00,
        0x72, XX,
        0x3d, 0xa0, 0x83, 0x00, 0x00,
        0x73, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(4);
    hp.type = USING_CHAR | CODEC_ANSI_BE;
    return NewHook(hp, "filsnown");
  }
}
namespace
{
  bool veryveryold()
  {
    static bool iskizuato = wcscmp(processName_lower, L"kizuato.exe") == 0;
    static bool issizuku = wcscmp(processName_lower, L"sizuku.exe") == 0;
    static bool isthfont = wcscmp(processName_lower, L"lvns3.exe") == 0;
    if (!issizuku && !iskizuato && !isthfont)
      return false;
    if (0)
    {
      // https://github.com/catmirrors/xlvns
      // 这里面有，不过不太对，需要校对。
      HookParam hp;
      hp.address = iskizuato ? 0x40B3AE : 0x4095BE;
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        hp->text_fun = nullptr;
        auto _ = (char *)context->esi;
        ConsoleOutput("%p", _);
        auto f = fopen("./1.bin", "wb");
        fwrite(_, 1, 72 * 0x1000, f);
        fclose(f);
      };
      return NewHook(hp, "kizuato");
    }
    BYTE sig[] = {
        0xe8, XX4,
        0xa3, XX4,
        0x83, 0xc0, 0x28,
        0x83, 0xc4, 0x08,
        0x4f,
        0xa3, XX4,
        0x8d, 0x90, 0x00, 0x04, 0x00, 0x00,
        0x0f, 0xbf, 0xc7};
    BYTE sig2[] = {
        0xe8, XX4,
        0x83, 0xc4, 0x04,
        0xa3, 0xf0, 0xba, 0x41, 0x00,
        0x0f, 0xbf, 0xce,
        0xc1, 0xe1, 0x03,
        0x83, 0xc0, 0x28,
        0x0f, 0xbf, 0x75, 0x0c,
        0x8d, 0x14, 0xc9,
        0xa3, XX4,
        0x05, 0x00, 0x04, 0x00, 0x00,
        0x01, 0x55, 0xf4,
        0x33, 0xd2};
    BYTE sig3[] = {
        0xe8, XX4,
        0x83, 0xc4, 0x04,
        0xa3, XX, XX, XX, 0x00,
        0x0f, 0xbf, 0xcb,
        0xc1, 0xe1, 0x03,
        0x83, 0xc0, 0x28,
        0x0f, 0xbf, 0xde,
        0x8d, 0x14, 0xc9,
        0xa3, XX4,
        0x05, 0x00, 0x04, 0x00, 0x00,
        0x01, 0x55, 0xfc,
        0x0f, 0xbf, 0xcf,
        0xa3, XX4,
        0x89, 0x5d, 0xf4,
        0x33, 0xd2};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      addr = MemDbg::findBytes(sig2, sizeof(sig2), processStartAddress, processStopAddress);
    if (!addr)
      addr = MemDbg::findBytes(sig3, sizeof(sig3), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr, 0x100, true);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_UTF16;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      WORD ch = context->stack[3];
      static auto charset = StringToWideString(LoadResData(iskizuato ? L"kizfont" : (issizuku ? L"sizfont" : L"thfont"), L"CHARSET"));
      buffer->from_t(charset[ch]);
    };
    return NewHook(hp, iskizuato ? "kizuato" : (issizuku ? "sizuku" : "toheart"));
  }
}
bool Leaf::attach_function()
{
  return InsertLeafHook() || activehook() || InsertAquaplusHooks() || kizuato() || wa2special() || toheartpse() || filsnown() || veryveryold();
}