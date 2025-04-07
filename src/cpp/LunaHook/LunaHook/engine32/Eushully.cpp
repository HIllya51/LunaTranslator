#include "Eushully.h"

/** jichi 6/1/2014 Eushully
 *  Insert to the last GetTextExtentPoint32A
 *
 *  ATCode:
 *  http://capita.tistory.com/m/post/255
 *
 *  Binary:
 *  {AGE.EXE!0x000113C3(89 C2 C1 E2 04 29 C2 E8 BD 25 20 00 52 89 D1 59), AGE.EXE!0x00012A47(E8 40 0F 20 00 90 90 90 90), AGE.EXE!0x0001DF07(55 8B EC 83 EC 08 56 EB 07 E8 32 5A 1F 00 EB F0), AGE.EXE!0x002137CE(90 90 90 90 90 C2 04 00 53 8B 1A 83 FB 6E 74 14 81 FB 96 01 00 00 74 1B 83 FB 6F 74 25 83 FB 72 74 27 EB 2C 8B 5A 10 89 1F 83 C7 04 B8 05 00 00 00 EB 1F 8B 5A 10 89 1F 83 C7 04 B8 07 00 00 00 EB 10 B8 03 00 00 00 EB 09 B8 01 00 00 00 EB 02 31 C0 5B C3 60 89 E5 83 EC 18 E8 7E 01 00 00 8B 55 F8 83 3A 00 75 31 8B 45 FC 8B 4C 30 E8 89 CA C1 E2 04 29 CA 8D 0C D6 8B 1C 08 51 8B 4C 08 FC 8B 7D F4 89 DA E8 7E FF FF FF 85 C0 74 0A 83 F8 01 74 09 8D 14 82 EB ED 89 EC 61 C3 C7 07 00 00 00 00 8B 75 F4 8B 7D F0 52 8B 06 85 C0 74 17 8D 04 81 8A 10 80 FA FF 74 08 F6 D2 88 17 40 47 EB F1 83 C6 04 EB E3 8B 55 F0 52 8B 02 E8 2F FF FF FF 8B 12 39 D0 74 C1 8B 55 F8 C7 02 01 00 00 00 8B 4D E4 8B 45 FC 8D 04 08 8B 55 F8 89 42 04 58 89 42 08 89 5A 0C 8B 45 FC 8B 4C 08 FC 8B 45 F4 8B 00 89 42 10 8D 04 81 89 42 14 8B 72 0C 8B 7D EC B9 08 00 00 00 F3 A5 8B 5D E8 8B 7A 14 8B 75 F0 31 C9 52 8A 06 84 C0 74 0F F6 D0 8A 14 39 88 14 19 88 04 39 41 46 EB EB 5A 8B 04 39 89 04 19 31 C0 F7 D0 89 04 39 83 C1 04 89 4A 18 8B 7A 0C 8B 42 10 31 C9 BB 6E 00 00 00 89 1F 89 4F 04 89 4F 08 C7 47 0C 02 00 00 00 83 C3 04 89 5F 14 89 4F 18 89 4F 1C 89 EC 61 C3 60 89 E5 83 EC 18 E8 59 00 00 00 8B 5D F8 83 3B 01 75 2E 31 C9 89 0B 8B 7B 0C 8B 75 EC 8D 49 08 F3 A5 8B 7B 14 8B 75 E8 8B 4B 18 F3 A4 8B 43 04 8B 53 08 89 10 8D 7B 04 31 C0 B9 40 01 00 00 F3 AB 89 EC 61 C3 8B 8C D6 A8 D7 05 00 8B 01 3D 96 01 00 00 74 07 83 F8 6E 74 02 EB 07 E8 7A FE FF FF 8B 01 C3 60 C7 45 FC A8 D7 05 00 EB 03 58 EB 05 E8 F8 FF FF FF 2D BD 39 21 00 03 80 D4 02 00 00 B9 00 01 00 00 8D 80 00 40 01 00 89 45 F8 8D 04 01 89 45 F4 8D 04 01 89 45 F0 8D 04 01 89 45 EC 8D 04 01 89 45 E8 61 C3)}
 *
 *  #1 other text AGE.EXE!0x000113C3(89 C2 C1 E2 04 29 C2 E8 BD 25 20 00 52 89 D1 59)
 *  #2 scenario AGE.EXE!0x00012A47(E8 40 0F 20 00 90 90 90 90)
 *
 *  0041130B   8B96 9CA30A00    MOV EDX,DWORD PTR DS:[ESI+0xAA39C]
 *  00411311   81A6 CCA90A00 FF>AND DWORD PTR DS:[ESI+0xAA9CC],0xF7FFFFF>
 *  0041131B   33C0             XOR EAX,EAX
 *  0041131D   50               PUSH EAX
 *  0041131E   8986 1C160000    MOV DWORD PTR DS:[ESI+0x161C],EAX
 *  00411324   8986 78EB0500    MOV DWORD PTR DS:[ESI+0x5EB78],EAX
 *  0041132A   8B42 0C          MOV EAX,DWORD PTR DS:[EDX+0xC]
 *  0041132D   68 F4536100      PUSH .006153F4                           ; ASCII "message:ReadTextSkip"
 *  00411332   8D8E 9CA30A00    LEA ECX,DWORD PTR DS:[ESI+0xAA39C]
 *  00411338   FFD0             CALL EAX
 *  0041133A   8B96 9CA30A00    MOV EDX,DWORD PTR DS:[ESI+0xAA39C]
 *  00411340   8B42 04          MOV EAX,DWORD PTR DS:[EDX+0x4]
 *  00411343   68 4C606100      PUSH .0061604C                           ; ASCII "set:CancelMesSkipOnClick"
 *  00411348   8D8E 9CA30A00    LEA ECX,DWORD PTR DS:[ESI+0xAA39C]
 *  0041134E   FFD0             CALL EAX
 *  00411350   83F8 02          CMP EAX,0x2
 *  00411353   75 1A            JNZ SHORT .0041136F
 *  00411355   68 34606100      PUSH .00616034                           ; ASCII "CALLBACK_SETTING.BIN"
 *  0041135A   8BCE             MOV ECX,ESI
 *  0041135C   E8 7FFBFFFF      CALL .00410EE0
 *  00411361   5F               POP EDI
 *  00411362   5E               POP ESI
 *  00411363   5B               POP EBX
 *  00411364   C3               RETN
 *  00411365   C786 18770700 01>MOV DWORD PTR DS:[ESI+0x77718],0x1
 *  0041136F   83BE 6C780700 00 CMP DWORD PTR DS:[ESI+0x7786C],0x0
 *  00411376   75 45            JNZ SHORT .004113BD
 *  00411378   F603 40          TEST BYTE PTR DS:[EBX],0x40
 *  0041137B   75 40            JNZ SHORT .004113BD
 *  0041137D   81A6 CCA90A00 FF>AND DWORD PTR DS:[ESI+0xAA9CC],0xF7FFFFF>
 *  00411387   33DB             XOR EBX,EBX
 *  00411389   8DBE B0780700    LEA EDI,DWORD PTR DS:[ESI+0x778B0]
 *  0041138F   90               NOP
 *  00411390   8B07             MOV EAX,DWORD PTR DS:[EDI]
 *  00411392   85C0             TEST EAX,EAX
 *  00411394   74 1E            JE SHORT .004113B4
 *  00411396   8B8F E4D5F8FF    MOV ECX,DWORD PTR DS:[EDI+0xFFF8D5E4]
 *  0041139C   8B57 0C          MOV EDX,DWORD PTR DS:[EDI+0xC]
 *  0041139F   51               PUSH ECX
 *  004113A0   52               PUSH EDX
 *  004113A1   50               PUSH EAX
 *  004113A2   53               PUSH EBX
 *  004113A3   8D8E 04480100    LEA ECX,DWORD PTR DS:[ESI+0x14804]
 *  004113A9   E8 42840900      CALL .004A97F0
 *  004113AE   C707 00000000    MOV DWORD PTR DS:[EDI],0x0
 *  004113B4   43               INC EBX
 *  004113B5   83C7 04          ADD EDI,0x4
 *  004113B8   83FB 03          CMP EBX,0x3
 *  004113BB  ^7C D3            JL SHORT .00411390
 *  004113BD   8B86 90D70500    MOV EAX,DWORD PTR DS:[ESI+0x5D790]
 *  004113C3   8BC8             MOV ECX,EAX         ; jichi: #1 hook here
 *  004113C5   C1E1 04          SHL ECX,0x4
 *  004113C8   2BC8             SUB ECX,EAX
 *  004113CA   8B94CE A8D70500  MOV EDX,DWORD PTR DS:[ESI+ECX*8+0x5D7A8]
 *  004113D1   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  004113D3   85C0             TEST EAX,EAX
 *  //004113C3   89C2             MOV EDX,EAX
 *  //004113C5   C1E2 04          SHL EDX,0x4
 *  //004113C8   29C2             SUB EDX,EAX
 *  //004113CA   E8 BD252000      CALL .0061398C
 *  //004113CF   52               PUSH EDX
 *  //004113D0   89D1             MOV ECX,EDX
 *  //004113D2   59               POP ECX
 *  004113D5   78 35            JS SHORT .0041140C
 *  004113D7   3D 00040000      CMP EAX,0x400
 *  004113DC   7D 2E            JGE SHORT .0041140C
 *  004113DE   8B8486 244F0A00  MOV EAX,DWORD PTR DS:[ESI+EAX*4+0xA4F24]
 *  004113E5   8BCE             MOV ECX,ESI
 *  004113E7   FFD0             CALL EAX
 *  004113E9   8B86 90D70500    MOV EAX,DWORD PTR DS:[ESI+0x5D790]
 *  004113EF   8BC8             MOV ECX,EAX
 *  004113F1   C1E1 04          SHL ECX,0x4
 *  004113F4   2BC8             SUB ECX,EAX
 *  004113F6   8B94CE 04D80500  MOV EDX,DWORD PTR DS:[ESI+ECX*8+0x5D804]
 *  004113FD   8D04CE           LEA EAX,DWORD PTR DS:[ESI+ECX*8]
 *  00411400   03D2             ADD EDX,EDX
 *  00411402   03D2             ADD EDX,EDX
 *  00411404   0190 A8D70500    ADD DWORD PTR DS:[EAX+0x5D7A8],EDX
 *  0041140A   EB 07            JMP SHORT .00411413
 *  0041140C   8BCE             MOV ECX,ESI
 *  0041140E   E8 7D6C0000      CALL .00418090
 *  00411413   8B86 9CA30A00    MOV EAX,DWORD PTR DS:[ESI+0xAA39C]
 *  00411419   8B50 04          MOV EDX,DWORD PTR DS:[EAX+0x4]
 *  0041141C   8D8E 9CA30A00    LEA ECX,DWORD PTR DS:[ESI+0xAA39C]
 *  00411422   68 4C606100      PUSH .0061604C                           ; ASCII "set:CancelMesSkipOnClick"
 *  00411427   FFD2             CALL EDX
 *  00411429   85C0             TEST EAX,EAX
 *  0041142B  ^0F85 30FFFFFF    JNZ .00411361
 *  00411431   3986 D8C90000    CMP DWORD PTR DS:[ESI+0xC9D8],EAX
 *  00411437  ^0F84 24FFFFFF    JE .00411361
 *  0041143D   8B86 D0A90A00    MOV EAX,DWORD PTR DS:[ESI+0xAA9D0]
 *  00411443   A8 10            TEST AL,0x10
 *  00411445   0F84 84000000    JE .004114CF
 *  0041144B   83E0 EF          AND EAX,0xFFFFFFEF
 *  0041144E   83BE 10770700 00 CMP DWORD PTR DS:[ESI+0x77710],0x0
 *  00411455   8986 D0A90A00    MOV DWORD PTR DS:[ESI+0xAA9D0],EAX
 *  0041145B  ^0F85 00FFFFFF    JNZ .00411361
 *  00411461   8B86 ECC90000    MOV EAX,DWORD PTR DS:[ESI+0xC9EC]
 *  00411467   8DBE 3C550000    LEA EDI,DWORD PTR DS:[ESI+0x553C]
 *  0041146D   85C0             TEST EAX,EAX
 *  0041146F  ^0F88 ECFEFFFF    JS .00411361
 *  00411475   3987 08040000    CMP DWORD PTR DS:[EDI+0x408],EAX
 *  0041147B  ^0F8E E0FEFFFF    JLE .00411361
 *  00411481   8BCE             MOV ECX,ESI
 *  00411483   E8 A86AFFFF      CALL .00407F30
 *  00411488   6A 00            PUSH 0x0
 *  0041148A   8BCE             MOV ECX,ESI
 *  0041148C   E8 EF3CFFFF      CALL .00405180
 *  00411491   8B86 90D70500    MOV EAX,DWORD PTR DS:[ESI+0x5D790]
 *  00411497   8BC8             MOV ECX,EAX
 *  00411499   C1E1 04          SHL ECX,0x4
 *  0041149C   2BC8             SUB ECX,EAX
 *  0041149E   8D34CE           LEA ESI,DWORD PTR DS:[ESI+ECX*8]
 *  004114A1   8BCF             MOV ECX,EDI
 *  004114A3   E8 0839FFFF      CALL .00404DB0
 *  004114A8   8B96 A4D70500    MOV EDX,DWORD PTR DS:[ESI+0x5D7A4]
 *  004114AE   8D0482           LEA EAX,DWORD PTR DS:[EDX+EAX*4]
 *  004114B1   8986 A8D70500    MOV DWORD PTR DS:[ESI+0x5D7A8],EAX
 *  004114B7   C787 B0740000 FF>MOV DWORD PTR DS:[EDI+0x74B0],-0x1
 *
 *  00412953   53               PUSH EBX
 *  00412954   FF15 B8406100    CALL DWORD PTR DS:[0x6140B8]             ; kernel32.Sleep
 *  0041295A   53               PUSH EBX
 *  0041295B   53               PUSH EBX
 *  0041295C   53               PUSH EBX
 *  0041295D   53               PUSH EBX
 *  0041295E   8D8D 34F8FFFF    LEA ECX,DWORD PTR SS:[EBP-0x7CC]
 *  00412964   51               PUSH ECX
 *  00412965   FF15 AC436100    CALL DWORD PTR DS:[0x6143AC]             ; user32.PeekMessageA
 *  0041296B   85C0             TEST EAX,EAX
 *  0041296D  ^0F85 5DF3FFFF    JNZ .00411CD0
 *  00412973  ^E9 D8F3FFFF      JMP .00411D50
 *  00412978   A9 00000020      TEST EAX,0x20000000
 *  0041297D   74 0C            JE SHORT .0041298B
 *  0041297F   8BCE             MOV ECX,ESI
 *  00412981   E8 3A63FFFF      CALL .00408CC0
 *  00412986  ^E9 C5F3FFFF      JMP .00411D50
 *  0041298B   85C0             TEST EAX,EAX
 *  0041298D   79 14            JNS SHORT .004129A3
 *  0041298F   8BCE             MOV ECX,ESI
 *  00412991   E8 AAEBFFFF      CALL .00411540
 *  00412996   6A 02            PUSH 0x2
 *  00412998   FF15 B8406100    CALL DWORD PTR DS:[0x6140B8]             ; kernel32.Sleep
 *  0041299E  ^E9 ADF3FFFF      JMP .00411D50
 *  004129A3   A8 01            TEST AL,0x1
 *  004129A5   74 25            JE SHORT .004129CC
 *  004129A7   8D8E D08D0600    LEA ECX,DWORD PTR DS:[ESI+0x68DD0]
 *  004129AD   E8 CEF30300      CALL .00451D80
 *  004129B2   8985 ACF8FFFF    MOV DWORD PTR SS:[EBP-0x754],EAX
 *  004129B8   3BC3             CMP EAX,EBX
 *  004129BA  ^0F8C 90F3FFFF    JL .00411D50
 *  004129C0   83A6 CCA90A00 FE AND DWORD PTR DS:[ESI+0xAA9CC],0xFFFFFFF>
 *  004129C7  ^E9 84F3FFFF      JMP .00411D50
 *  004129CC   A8 20            TEST AL,0x20
 *  004129CE   74 3C            JE SHORT .00412A0C
 *  004129D0   8D8E 5C8E0600    LEA ECX,DWORD PTR DS:[ESI+0x68E5C]
 *  004129D6   E8 A5F30300      CALL .00451D80
 *  004129DB   8985 ACF8FFFF    MOV DWORD PTR SS:[EBP-0x754],EAX
 *  004129E1   3BC3             CMP EAX,EBX
 *  004129E3  ^0F8C 67F3FFFF    JL .00411D50
 *  004129E9   83A6 CCA90A00 DF AND DWORD PTR DS:[ESI+0xAA9CC],0xFFFFFFD>
 *  004129F0   8D8E 5C8E0600    LEA ECX,DWORD PTR DS:[ESI+0x68E5C]
 *  004129F6   E8 45EE0300      CALL .00451840
 *  004129FB   50               PUSH EAX
 *  004129FC   8D8E 5C8E0600    LEA ECX,DWORD PTR DS:[ESI+0x68E5C]
 *  00412A02   E8 39F30300      CALL .00451D40
 *  00412A07  ^E9 44F3FFFF      JMP .00411D50
 *  00412A0C   A9 00000010      TEST EAX,0x10000000
 *  00412A11   74 14            JE SHORT .00412A27
 *  00412A13   8BCE             MOV ECX,ESI
 *  00412A15   E8 A664FFFF      CALL .00408EC0
 *  00412A1A   6A 02            PUSH 0x2
 *  00412A1C   FF15 B8406100    CALL DWORD PTR DS:[0x6140B8]             ; kernel32.Sleep
 *  00412A22  ^E9 29F3FFFF      JMP .00411D50
 *  00412A27   A9 00008000      TEST EAX,0x800000
 *  00412A2C   74 0C            JE SHORT .00412A3A
 *  00412A2E   8BCE             MOV ECX,ESI
 *  00412A30   E8 6B66FFFF      CALL .004090A0
 *  00412A35  ^E9 16F3FFFF      JMP .00411D50
 *  00412A3A   8B86 90D70500    MOV EAX,DWORD PTR DS:[ESI+0x5D790]
 *  00412A40   8BD0             MOV EDX,EAX
 *  00412A42   C1E2 04          SHL EDX,0x4
 *  00412A45   2BD0             SUB EDX,EAX
 *  00412A47   8B84D6 A8D70500  MOV EAX,DWORD PTR DS:[ESI+EDX*8+0x5D7A8]    ; jichi: #2 hook here
 *  //00412A47   E8 400F2000      CALL .0061398C
 *  00412A4E   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  00412A50   3BC3             CMP EAX,EBX
 *  00412A52   7C 37            JL SHORT .00412A8B
 *  00412A54   3D 00040000      CMP EAX,0x400
 *  00412A59   7D 30            JGE SHORT .00412A8B
 *  00412A5B   8BCE             MOV ECX,ESI
 *  00412A5D   8B9486 244F0A00  MOV EDX,DWORD PTR DS:[ESI+EAX*4+0xA4F24]
 *  00412A64   FFD2             CALL EDX
 *  00412A66   8B86 90D70500    MOV EAX,DWORD PTR DS:[ESI+0x5D790]
 *  00412A6C   8BC8             MOV ECX,EAX
 *  00412A6E   C1E1 04          SHL ECX,0x4
 *  00412A71   2BC8             SUB ECX,EAX
 *  00412A73   8D04CE           LEA EAX,DWORD PTR DS:[ESI+ECX*8]
 *  00412A76   8B90 04D80500    MOV EDX,DWORD PTR DS:[EAX+0x5D804]
 *  00412A7C   03D2             ADD EDX,EDX
 *  00412A7E   03D2             ADD EDX,EDX
 *  00412A80   0190 A8D70500    ADD DWORD PTR DS:[EAX+0x5D7A8],EDX
 *  00412A86  ^E9 C5F2FFFF      JMP .00411D50
 *  00412A8B   8BCE             MOV ECX,ESI
 *  00412A8D   E8 FE550000      CALL .00418090
 *  00412A92  ^E9 B9F2FFFF      JMP .00411D50
 *  00412A97   C785 A4F8FFFF 01>MOV DWORD PTR SS:[EBP-0x75C],0x1
 *  00412AA1   C745 FC FFFFFFFF MOV DWORD PTR SS:[EBP-0x4],-0x1
 *  00412AA8   B8 E02D4100      MOV EAX,.00412DE0
 *  00412AAD   C3               RETN
 *  00412AAE   8B85 14F8FFFF    MOV EAX,DWORD PTR SS:[EBP-0x7EC]
 *  00412AB4   50               PUSH EAX
 *  00412AB5   8B8D 10F8FFFF    MOV ECX,DWORD PTR SS:[EBP-0x7F0]
 *
 *  Patched code:
 *
 *  0041DF07   55               PUSH EBP
 *  0041DF08   8BEC             MOV EBP,ESP
 *  0041DF0A   83EC 08          SUB ESP,0x8
 *  0041DF0D   56               PUSH ESI
 *  0041DF0E   EB 07            JMP SHORT .0041DF17
 *  0041DF10   E8 325A1F00      CALL .00613947
 *  0041DF15  ^EB F0            JMP SHORT .0041DF07
 *
 *  006137CE   90               NOP
 *  006137CF   90               NOP
 *  006137D0   90               NOP
 *  006137D1   90               NOP
 *  006137D2   90               NOP
 *  006137D3   C2 0400          RETN 0x4
 *  006137D6   53               PUSH EBX
 *  006137D7   8B1A             MOV EBX,DWORD PTR DS:[EDX]
 *  006137D9   83FB 6E          CMP EBX,0x6E
 *  006137DC   74 14            JE SHORT .006137F2
 *  006137DE   81FB 96010000    CMP EBX,0x196
 *  006137E4   74 1B            JE SHORT .00613801
 *  006137E6   83FB 6F          CMP EBX,0x6F
 *  006137E9   74 25            JE SHORT .00613810
 *  006137EB   83FB 72          CMP EBX,0x72
 *  006137EE   74 27            JE SHORT .00613817
 *  006137F0   EB 2C            JMP SHORT .0061381E
 *  006137F2   8B5A 10          MOV EBX,DWORD PTR DS:[EDX+0x10]
 *  006137F5   891F             MOV DWORD PTR DS:[EDI],EBX
 *  006137F7   83C7 04          ADD EDI,0x4
 *  006137FA   B8 05000000      MOV EAX,0x5
 *  006137FF   EB 1F            JMP SHORT .00613820
 *  00613801   8B5A 10          MOV EBX,DWORD PTR DS:[EDX+0x10]
 *  00613804   891F             MOV DWORD PTR DS:[EDI],EBX
 *  00613806   83C7 04          ADD EDI,0x4
 *  00613809   B8 07000000      MOV EAX,0x7
 *  0061380E   EB 10            JMP SHORT .00613820
 *  00613810   B8 03000000      MOV EAX,0x3
 *  00613815   EB 09            JMP SHORT .00613820
 *  00613817   B8 01000000      MOV EAX,0x1
 *  0061381C   EB 02            JMP SHORT .00613820
 *  0061381E   31C0             XOR EAX,EAX
 *  00613820   5B               POP EBX
 *  00613821   C3               RETN
 *  00613822   60               PUSHAD      ; jichi: the translate function for hookpoint #2
 *  00613823   89E5             MOV EBP,ESP
 *  00613825   83EC 18          SUB ESP,0x18    ; reserve 18 local variables
 *  00613828   E8 7E010000      CALL .006139AB
 *  0061382D   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  00613830   833A 00          CMP DWORD PTR DS:[EDX],0x0
 *  00613833   75 31            JNZ SHORT .00613866
 *  00613835   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  00613838   8B4C30 E8        MOV ECX,DWORD PTR DS:[EAX+ESI-0x18]
 *  0061383C   89CA             MOV EDX,ECX
 *  0061383E   C1E2 04          SHL EDX,0x4
 *  00613841   29CA             SUB EDX,ECX
 *  00613843   8D0CD6           LEA ECX,DWORD PTR DS:[ESI+EDX*8]
 *  00613846   8B1C08           MOV EBX,DWORD PTR DS:[EAX+ECX]
 *  00613849   51               PUSH ECX
 *  0061384A   8B4C08 FC        MOV ECX,DWORD PTR DS:[EAX+ECX-0x4]
 *  0061384E   8B7D F4          MOV EDI,DWORD PTR SS:[EBP-0xC]
 *  00613851   89DA             MOV EDX,EBX
 *  00613853   E8 7EFFFFFF      CALL .006137D6
 *  00613858   85C0             TEST EAX,EAX
 *  0061385A   74 0A            JE SHORT .00613866
 *  0061385C   83F8 01          CMP EAX,0x1
 *  0061385F   74 09            JE SHORT .0061386A
 *  00613861   8D1482           LEA EDX,DWORD PTR DS:[EDX+EAX*4]
 *  00613864  ^EB ED            JMP SHORT .00613853
 *  00613866   89EC             MOV ESP,EBP
 *  00613868   61               POPAD
 *  00613869   C3               RETN
 *  0061386A   C707 00000000    MOV DWORD PTR DS:[EDI],0x0
 *  00613870   8B75 F4          MOV ESI,DWORD PTR SS:[EBP-0xC]
 *  00613873   8B7D F0          MOV EDI,DWORD PTR SS:[EBP-0x10]
 *  00613876   52               PUSH EDX
 *  00613877   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  00613879   85C0             TEST EAX,EAX
 *  0061387B   74 17            JE SHORT .00613894
 *  0061387D   8D0481           LEA EAX,DWORD PTR DS:[ECX+EAX*4]
 *  00613880   8A10             MOV DL,BYTE PTR DS:[EAX]
 *  00613882   80FA FF          CMP DL,0xFF
 *  00613885   74 08            JE SHORT .0061388F
 *  00613887   F6D2             NOT DL
 *  00613889   8817             MOV BYTE PTR DS:[EDI],DL
 *  0061388B   40               INC EAX
 *  0061388C   47               INC EDI
 *  0061388D  ^EB F1            JMP SHORT .00613880
 *  0061388F   83C6 04          ADD ESI,0x4
 *  00613892  ^EB E3            JMP SHORT .00613877
 *  00613894   8B55 F0          MOV EDX,DWORD PTR SS:[EBP-0x10]
 *  00613897   52               PUSH EDX
 *  00613898   8B02             MOV EAX,DWORD PTR DS:[EDX]
 *  0061389A   E8 2FFFFFFF      CALL .006137CE
 *  0061389F   8B12             MOV EDX,DWORD PTR DS:[EDX]
 *  006138A1   39D0             CMP EAX,EDX
 *  006138A3  ^74 C1            JE SHORT .00613866
 *  006138A5   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  006138A8   C702 01000000    MOV DWORD PTR DS:[EDX],0x1
 *  006138AE   8B4D E4          MOV ECX,DWORD PTR SS:[EBP-0x1C]
 *  006138B1   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  006138B4   8D0408           LEA EAX,DWORD PTR DS:[EAX+ECX]
 *  006138B7   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  006138BA   8942 04          MOV DWORD PTR DS:[EDX+0x4],EAX
 *  006138BD   58               POP EAX
 *  006138BE   8942 08          MOV DWORD PTR DS:[EDX+0x8],EAX
 *  006138C1   895A 0C          MOV DWORD PTR DS:[EDX+0xC],EBX
 *  006138C4   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  006138C7   8B4C08 FC        MOV ECX,DWORD PTR DS:[EAX+ECX-0x4]
 *  006138CB   8B45 F4          MOV EAX,DWORD PTR SS:[EBP-0xC]
 *  006138CE   8B00             MOV EAX,DWORD PTR DS:[EAX]
 *  006138D0   8942 10          MOV DWORD PTR DS:[EDX+0x10],EAX
 *  006138D3   8D0481           LEA EAX,DWORD PTR DS:[ECX+EAX*4]
 *  006138D6   8942 14          MOV DWORD PTR DS:[EDX+0x14],EAX
 *  006138D9   8B72 0C          MOV ESI,DWORD PTR DS:[EDX+0xC]
 *  006138DC   8B7D EC          MOV EDI,DWORD PTR SS:[EBP-0x14]
 *  006138DF   B9 08000000      MOV ECX,0x8
 *  006138E4   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
 *  006138E6   8B5D E8          MOV EBX,DWORD PTR SS:[EBP-0x18]
 *  006138E9   8B7A 14          MOV EDI,DWORD PTR DS:[EDX+0x14]
 *  006138EC   8B75 F0          MOV ESI,DWORD PTR SS:[EBP-0x10]
 *  006138EF   31C9             XOR ECX,ECX
 *  006138F1   52               PUSH EDX
 *  006138F2   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  006138F4   84C0             TEST AL,AL
 *  006138F6   74 0F            JE SHORT .00613907
 *  006138F8   F6D0             NOT AL
 *  006138FA   8A1439           MOV DL,BYTE PTR DS:[ECX+EDI]
 *  006138FD   881419           MOV BYTE PTR DS:[ECX+EBX],DL
 *  00613900   880439           MOV BYTE PTR DS:[ECX+EDI],AL
 *  00613903   41               INC ECX
 *  00613904   46               INC ESI
 *  00613905  ^EB EB            JMP SHORT .006138F2
 *  00613907   5A               POP EDX
 *  00613908   8B0439           MOV EAX,DWORD PTR DS:[ECX+EDI]
 *  0061390B   890419           MOV DWORD PTR DS:[ECX+EBX],EAX
 *  0061390E   31C0             XOR EAX,EAX
 *  00613910   F7D0             NOT EAX
 *  00613912   890439           MOV DWORD PTR DS:[ECX+EDI],EAX
 *  00613915   83C1 04          ADD ECX,0x4
 *  00613918   894A 18          MOV DWORD PTR DS:[EDX+0x18],ECX
 *  0061391B   8B7A 0C          MOV EDI,DWORD PTR DS:[EDX+0xC]
 *  0061391E   8B42 10          MOV EAX,DWORD PTR DS:[EDX+0x10]
 *  00613921   31C9             XOR ECX,ECX
 *  00613923   BB 6E000000      MOV EBX,0x6E
 *  00613928   891F             MOV DWORD PTR DS:[EDI],EBX
 *  0061392A   894F 04          MOV DWORD PTR DS:[EDI+0x4],ECX
 *  0061392D   894F 08          MOV DWORD PTR DS:[EDI+0x8],ECX
 *  00613930   C747 0C 02000000 MOV DWORD PTR DS:[EDI+0xC],0x2
 *  00613937   83C3 04          ADD EBX,0x4
 *  0061393A   895F 14          MOV DWORD PTR DS:[EDI+0x14],EBX
 *  0061393D   894F 18          MOV DWORD PTR DS:[EDI+0x18],ECX
 *  00613940   894F 1C          MOV DWORD PTR DS:[EDI+0x1C],ECX
 *  00613943   89EC             MOV ESP,EBP
 *  00613945   61               POPAD
 *  00613946   C3               RETN
 *  00613947   60               PUSHAD
 *  00613948   89E5             MOV EBP,ESP
 *  0061394A   83EC 18          SUB ESP,0x18
 *  0061394D   E8 59000000      CALL .006139AB
 *  00613952   8B5D F8          MOV EBX,DWORD PTR SS:[EBP-0x8]
 *  00613955   833B 01          CMP DWORD PTR DS:[EBX],0x1
 *  00613958   75 2E            JNZ SHORT .00613988
 *  0061395A   31C9             XOR ECX,ECX
 *  0061395C   890B             MOV DWORD PTR DS:[EBX],ECX
 *  0061395E   8B7B 0C          MOV EDI,DWORD PTR DS:[EBX+0xC]
 *  00613961   8B75 EC          MOV ESI,DWORD PTR SS:[EBP-0x14]
 *  00613964   8D49 08          LEA ECX,DWORD PTR DS:[ECX+0x8]
 *  00613967   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS>
 *  00613969   8B7B 14          MOV EDI,DWORD PTR DS:[EBX+0x14]
 *  0061396C   8B75 E8          MOV ESI,DWORD PTR SS:[EBP-0x18]
 *  0061396F   8B4B 18          MOV ECX,DWORD PTR DS:[EBX+0x18]
 *  00613972   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[>
 *  00613974   8B43 04          MOV EAX,DWORD PTR DS:[EBX+0x4]
 *  00613977   8B53 08          MOV EDX,DWORD PTR DS:[EBX+0x8]
 *  0061397A   8910             MOV DWORD PTR DS:[EAX],EDX
 *  0061397C   8D7B 04          LEA EDI,DWORD PTR DS:[EBX+0x4]
 *  0061397F   31C0             XOR EAX,EAX
 *  00613981   B9 40010000      MOV ECX,0x140
 *  00613986   F3:AB            REP STOS DWORD PTR ES:[EDI]
 *  00613988   89EC             MOV ESP,EBP
 *  0061398A   61               POPAD
 *  0061398B   C3               RETN
 *  0061398C   8B8CD6 A8D70500  MOV ECX,DWORD PTR DS:[ESI+EDX*8+0x5D7A8]    ; jichi: #2 hook jumped here, execute the original instruction first
 *  00613993   8B01             MOV EAX,DWORD PTR DS:[ECX]                  ; get dword split in ecx
 *  00613995   3D 96010000      CMP EAX,0x196
 *  0061399A   74 07            JE SHORT .006139A3                          ; translate if split is 0x196 or 0x6e
 *  0061399C   83F8 6E          CMP EAX,0x6E
 *  0061399F   74 02            JE SHORT .006139A3
 *  006139A1   EB 07            JMP SHORT .006139AA
 *  006139A3   E8 7AFEFFFF      CALL .00613822
 *  006139A8   8B01             MOV EAX,DWORD PTR DS:[ECX]
 *  006139AA   C3               RETN
 *  006139AB   60               PUSHAD
 *  006139AC   C745 FC A8D70500 MOV DWORD PTR SS:[EBP-0x4],0x5D7A8
 *  006139B3   EB 03            JMP SHORT .006139B8
 *  006139B5   58               POP EAX
 *  006139B6   EB 05            JMP SHORT .006139BD
 *  006139B8   E8 F8FFFFFF      CALL .006139B5
 *  006139BD   2D BD392100      SUB EAX,0x2139BD
 *  006139C2   0380 D4020000    ADD EAX,DWORD PTR DS:[EAX+0x2D4]
 *  006139C8   B9 00010000      MOV ECX,0x100
 *  006139CD   8D80 00400100    LEA EAX,DWORD PTR DS:[EAX+0x14000]
 *  006139D3   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  006139D6   8D0401           LEA EAX,DWORD PTR DS:[ECX+EAX]
 *  006139D9   8945 F4          MOV DWORD PTR SS:[EBP-0xC],EAX
 *  006139DC   8D0401           LEA EAX,DWORD PTR DS:[ECX+EAX]
 *  006139DF   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
 *  006139E2   8D0401           LEA EAX,DWORD PTR DS:[ECX+EAX]
 *  006139E5   8945 EC          MOV DWORD PTR SS:[EBP-0x14],EAX
 *  006139E8   8D0401           LEA EAX,DWORD PTR DS:[ECX+EAX]
 *  006139EB   8945 E8          MOV DWORD PTR SS:[EBP-0x18],EAX
 *  006139EE   61               POPAD
 *  006139EF   C3               RETN
 *  006139F0   0000             ADD BYTE PTR DS:[EAX],AL
 *  006139F2   0000             ADD BYTE PTR DS:[EAX],AL
 *  006139F4   0000             ADD BYTE PTR DS:[EAX],AL
 */
bool InsertEushullyHook()
{
  /*
  ULONG addr = MemDbg::findLastCallerAddressAfterInt3((DWORD)::GetTextExtentPoint32A, processStartAddress, processStopAddress);
  //GROWL_DWORD(addr);
  if (!addr) {
    ConsoleOutput("Eushully: failed");
    return false;
  }
  */
  ULONG lastCaller = 0,
        lastCall = 0;
  auto fun = [&lastCaller, &lastCall](ULONG caller, ULONG call) -> bool
  {
    lastCaller = caller;
    lastCall = call;
    return true; // find last caller && call
  };
  MemDbg::iterCallerAddressAfterInt3(fun, (ULONG)::GetTextExtentPoint32A, processStartAddress, processStopAddress);
  if (!lastCaller)
    return false;

  // OtherHook
  ULONG thisCaller = 0,
        thisCall = 0,
        prevCall = 0;
  auto fun2 = [&thisCaller, &thisCall, &prevCall](ULONG caller, ULONG call) -> bool
  {
    if (call - prevCall == 133)
    { // 0x0046e1f8 - 0x0046e173 = 133
      thisCaller = caller;
      thisCall = call;
      return false; // stop iteration
    }
    prevCall = call;
    return true; // continue iteration
  };
  MemDbg::iterCallerAddressAfterInt3(fun2, (ULONG)::GetGlyphOutlineA, processStartAddress, processStopAddress);
  // BOOL GetTextExtentPoint32(
  //   _In_   HDC hdc,
  //   _In_   LPCTSTR lpString,
  //   _In_   int c,
  //   _Out_  LPSIZE lpSize
  // );
  enum stack
  { // current stack
    // retaddr = 0 // esp[0] is the return address since this is the beginning of the function
    arg1_hdc = 4 * 1 // 0x4
    ,
    arg2_lpString = 4 * 2 // 0x8
    ,
    arg3_lc = 4 * 3 // 0xc
    ,
    arg4_lpSize = 4 * 4 // 0x10
  };
  {
    enum : DWORD
    {
      sig = 0x550010c2
    };
    enum
    {
      fun_offset = 3
    };
    for (auto addr = lastCaller; addr < lastCall; addr++)
      if (*(DWORD *)addr == sig)
      {
        lastCaller = addr + fun_offset;
        break;
      }
  }
  HookParam hp;
  hp.address = lastCaller;
  hp.type = USING_STRING | FIXING_SPLIT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS; // merging all threads
  hp.offset = arg2_lpString;                                                              // arg2 = 0x4 * 2
  hp.embed_hook_font = F_MultiByteToWideChar | F_GetTextExtentPoint32A | F_GetGlyphOutlineA | F_CreateFontA;
  ConsoleOutput("INSERT Eushully");
  bool succ = NewHook(hp, "ARCGameEngine");
  if (thisCaller)
  {
    hp.address = thisCall;
    hp.offset = stackoffset(6);
    succ |= NewHook(hp, "ARCGameEngine_other");
  }
  return succ;
}
namespace
{
  //(18禁ゲーム)[200529][エウシュリー] 天冥のコンキスタ DL版
  bool TENMEI()
  {
    BYTE sig[] = {
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x0f, 0x00, 0x00, 0x00,
        0xc6, 0x45, XX, 0x00,
        0xc6, 0x45, XX, 0x01,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
        0xc7, 0x45, XX, 0x0f, 0x00, 0x00, 0x00,
        0xc6, 0x45, XX, 0x00,
        0xc6, 0x45, XX, 0x03};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | USING_SPLIT | NO_CONTEXT; // 必须NO_CONTEXT否则被注音的字会被分开
    hp.offset = stackoffset(5);
    hp.split = stackoffset(1); // name 80000000 各种所有text 0
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      StringFilter(buffer, TEXTANDLEN("\xf0\x40"));
      CharFilter(buffer, '\n');
    };
    return NewHook(hp, "TENMEI");
  }
}
namespace
{
  bool pchooks()
  {
    HookParam hp;
    hp.address = (DWORD)GetStringTypeExW;
    hp.offset = stackoffset(3);
    hp.type = USING_STRING | CODEC_UTF16;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // 破折号和省略号会变成乱码
      for (auto i = 0; i < buffer->size / 2; i++)
      {
        auto wc = (wchar_t *)buffer->buff;
        if (wc[i] == 0xe001)
          wc[i] = 0x2014;
        else if (wc[i] == 0xe003)
          wc[i] = 0x2014;
        else if (wc[i] == 0xe000)
          wc[i] = 0x2026;
      }
    };
    auto succ = NewHook(hp, "eushully");
    hp.address = (DWORD)GetTextExtentPoint32W;
    hp.offset = stackoffset(2);
    succ |= NewHook(hp, "eushully");
    PcHooks::hookGDIFunctions(GetTextExtentPoint32A);
    return succ;
  }
}
bool Eushully::attach_function()
{

  return InsertEushullyHook() || TENMEI() || pchooks();
}