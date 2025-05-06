#include "Pensil.h"
bool InsertPensilHook()
{
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
    if (*(DWORD *)i == 0x6381) // cmp *,8163
      if (DWORD j = SafeFindEnclosingAlignedFunction(i, 0x100))
      {
        // Artikash 7/20/2019: I don't understand how or why this is possible, but I found a game that by default has copy on write memory for its .text section
        VirtualProtect((void *)j, 1, PAGE_EXECUTE_READ, DUMMY);
        HookParam hp;
        hp.address = j;
        hp.offset = stackoffset(2);
        hp.split = stackoffset(1);
        hp.type = USING_SPLIT;
        ConsoleOutput("INSERT Pensil");
        return NewHook(hp, "Pensil");
        // RegisterEngineType(ENGINE_PENSIL);
      }
  // ConsoleOutput("Unknown Pensil engine.");
  ConsoleOutput("Pensil: failed");
  return false;
}

namespace
{
  void pensilfilter(TextBuffer *buffer, HookParam *hp)
  {
    // 「馬鹿な、\{軌道護符|サテラ}が封じられるとは！　ハーリーの仕業か。連中の魔法科学はそこまで進んだのか！？」
    buffer->from(re::sub(buffer->strA(), "\\\\\\{(.*?)\\|(.*?)\\}", "$1"));
  };
}

namespace
{ // unnamed
  namespace ScenarioHook
  {

    /**
     *  Sample game: はにつま
     *
     *  Debugging method:
     *  1. Hook to GetGlyphOutlineA
     *  2. Find text in memory
     *     There are three matches. The static scenario text is found
     *  3. Looking for text on the stack
     *     The text is just above Windows Message calls on the stack.
     *
     *  Name/Scenario/Other texts can be translated.
     *  History cannot be translated.
     *
     *  Text in arg2.
     *
     *  0046AFE8   CC               INT3
     *  0046AFE9   CC               INT3
     *  0046AFEA   CC               INT3
     *  0046AFEB   CC               INT3
     *  0046AFEC   CC               INT3
     *  0046AFED   CC               INT3
     *  0046AFEE   CC               INT3
     *  0046AFEF   CC               INT3
     *  0046AFF0   83EC 10          SUB ESP,0x10
     *  0046AFF3   56               PUSH ESI
     *  0046AFF4   57               PUSH EDI
     *  0046AFF5   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
     *  0046AFF9   85FF             TEST EDI,EDI
     *  0046AFFB   0F84 D6020000    JE .0046B2D7
     *  0046B001   8B7424 20        MOV ESI,DWORD PTR SS:[ESP+0x20]
     *  0046B005   85F6             TEST ESI,ESI
     *  0046B007   0F84 CA020000    JE .0046B2D7
     *  0046B00D   55               PUSH EBP
     *  0046B00E   33ED             XOR EBP,EBP
     *  0046B010   392D A8766C00    CMP DWORD PTR DS:[0x6C76A8],EBP
     *  0046B016   75 09            JNZ SHORT .0046B021
     *  0046B018   5D               POP EBP
     *  0046B019   5F               POP EDI
     *  0046B01A   33C0             XOR EAX,EAX
     *  0046B01C   5E               POP ESI
     *  0046B01D   83C4 10          ADD ESP,0x10
     *  0046B020   C3               RETN
     *  0046B021   8B47 24          MOV EAX,DWORD PTR DS:[EDI+0x24]
     *  0046B024   8B4F 28          MOV ECX,DWORD PTR DS:[EDI+0x28]
     *  0046B027   8B57 2C          MOV EDX,DWORD PTR DS:[EDI+0x2C]
     *  0046B02A   894424 0C        MOV DWORD PTR SS:[ESP+0xC],EAX
     *  0046B02E   8B47 30          MOV EAX,DWORD PTR DS:[EDI+0x30]
     *  0046B031   53               PUSH EBX
     *  0046B032   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
     *  0046B036   895424 18        MOV DWORD PTR SS:[ESP+0x18],EDX
     *  0046B03A   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
     *  0046B03E   8A1E             MOV BL,BYTE PTR DS:[ESI]
     *  0046B040   84DB             TEST BL,BL
     *  0046B042   0F84 95000000    JE .0046B0DD
     *  0046B048   EB 06            JMP SHORT .0046B050
     *  0046B04A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  0046B050   0FB716           MOVZX EDX,WORD PTR DS:[ESI]
     *  0046B053   0FB7C2           MOVZX EAX,DX
     *  0046B056   3D 5C630000      CMP EAX,0x635C
     *  0046B05B   0F8F 93010000    JG .0046B1F4
     *  0046B061   0F84 2B010000    JE .0046B192
     *  0046B067   3D 5C4E0000      CMP EAX,0x4E5C
     *  0046B06C   0F8F DF000000    JG .0046B151
     *  0046B072   0F84 9E010000    JE .0046B216
     *  0046B078   3D 5C430000      CMP EAX,0x435C
     *  0046B07D   0F84 0F010000    JE .0046B192
     *  0046B083   3D 5C460000      CMP EAX,0x465C
     *  0046B088   0F84 80000000    JE .0046B10E
     *  0046B08E   3D 5C470000      CMP EAX,0x475C
     *  0046B093   0F85 CA010000    JNZ .0046B263
     *  0046B099   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  0046B09C   83C6 02          ADD ESI,0x2
     *  0046B09F   33C9             XOR ECX,ECX
     *  0046B0A1   3C 39            CMP AL,0x39
     *  0046B0A3   77 17            JA SHORT .0046B0BC
     *  0046B0A5   3C 30            CMP AL,0x30
     *  0046B0A7   72 13            JB SHORT .0046B0BC
     *  0046B0A9   83C6 01          ADD ESI,0x1
     *  0046B0AC   0FB6D0           MOVZX EDX,AL
     *  0046B0AF   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0046B0B1   3C 39            CMP AL,0x39
     *  0046B0B3   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  0046B0B6   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  0046B0BA  ^76 E9            JBE SHORT .0046B0A5
     *  0046B0BC   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  0046B0C0   50               PUSH EAX
     *  0046B0C1   81C1 00FFFFFF    ADD ECX,-0x100
     *  0046B0C7   51               PUSH ECX
     *  0046B0C8   57               PUSH EDI
     *  0046B0C9   E8 92F1FFFF      CALL .0046A260
     *  0046B0CE   83C4 0C          ADD ESP,0xC
     *  0046B0D1   03E8             ADD EBP,EAX
     *  0046B0D3   8A1E             MOV BL,BYTE PTR DS:[ESI]
     *  0046B0D5   84DB             TEST BL,BL
     *  0046B0D7  ^0F85 73FFFFFF    JNZ .0046B050
     *  0046B0DD   F647 10 01       TEST BYTE PTR DS:[EDI+0x10],0x1
     *  0046B0E1   74 09            JE SHORT .0046B0EC
     *  0046B0E3   57               PUSH EDI
     *  0046B0E4   E8 F7DDFFFF      CALL .00468EE0
     *  0046B0E9   83C4 04          ADD ESP,0x4
     *  0046B0EC   F647 10 08       TEST BYTE PTR DS:[EDI+0x10],0x8
     *  0046B0F0   74 12            JE SHORT .0046B104
     *  0046B0F2   833D 98026C00 00 CMP DWORD PTR DS:[0x6C0298],0x0
     *  0046B0F9   74 09            JE SHORT .0046B104
     *  0046B0FB   57               PUSH EDI
     *  0046B0FC   E8 6FE4FFFF      CALL .00469570
     *  0046B101   83C4 04          ADD ESP,0x4
     *  0046B104   5B               POP EBX
     *  0046B105   8BC5             MOV EAX,EBP
     *  0046B107   5D               POP EBP
     *  0046B108   5F               POP EDI
     *  0046B109   5E               POP ESI
     *  0046B10A   83C4 10          ADD ESP,0x10
     *  0046B10D   C3               RETN
     *  0046B10E   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  0046B111   83C6 02          ADD ESI,0x2
     *  0046B114   33C9             XOR ECX,ECX
     *  0046B116   3C 39            CMP AL,0x39
     *  0046B118   77 1D            JA SHORT .0046B137
     *  0046B11A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  0046B120   3C 30            CMP AL,0x30
     *  0046B122   72 13            JB SHORT .0046B137
     *  0046B124   83C6 01          ADD ESI,0x1
     *  0046B127   0FB6D0           MOVZX EDX,AL
     *  0046B12A   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0046B12C   3C 39            CMP AL,0x39
     *  0046B12E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  0046B131   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  0046B135  ^76 E9            JBE SHORT .0046B120
     *  0046B137   6A 01            PUSH 0x1
     *  0046B139   8B0C8D 580D6C00  MOV ECX,DWORD PTR DS:[ECX*4+0x6C0D58]
     *  0046B140   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
     *  0046B144   50               PUSH EAX
     *  0046B145   51               PUSH ECX
     *  0046B146   57               PUSH EDI
     *  0046B147   E8 84FBFFFF      CALL .0046ACD0
     *  0046B14C   83C4 10          ADD ESP,0x10
     *  0046B14F  ^EB 80            JMP SHORT .0046B0D1
     *  0046B151   3D 5C520000      CMP EAX,0x525C
     *  0046B156   0F84 BA000000    JE .0046B216
     *  0046B15C   3D 5C530000      CMP EAX,0x535C
     *  0046B161  ^0F84 32FFFFFF    JE .0046B099
     *  0046B167   3D 5C5C0000      CMP EAX,0x5C5C
     *  0046B16C   0F85 F1000000    JNZ .0046B263
     *  0046B172   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
     *  0046B176   52               PUSH EDX
     *  0046B177   6A 5C            PUSH 0x5C
     *  0046B179   57               PUSH EDI
     *  0046B17A   E8 81F3FFFF      CALL .0046A500
     *  0046B17F   83C4 0C          ADD ESP,0xC
     *  0046B182   85C0             TEST EAX,EAX
     *  0046B184   0F84 43010000    JE .0046B2CD
     *  0046B18A   83C6 01          ADD ESI,0x1
     *  0046B18D  ^E9 41FFFFFF      JMP .0046B0D3
     *  0046B192   33C9             XOR ECX,ECX
     *  0046B194   83C6 02          ADD ESI,0x2
     *  0046B197   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0046B199   3C 39            CMP AL,0x39
     *  0046B19B   77 14            JA SHORT .0046B1B1
     *  0046B19D   3C 30            CMP AL,0x30
     *  0046B19F   72 10            JB SHORT .0046B1B1
     *  0046B1A1   83C1 FD          ADD ECX,-0x3
     *  0046B1A4   0FB6C0           MOVZX EAX,AL
     *  0046B1A7   C1E1 04          SHL ECX,0x4
     *  0046B1AA   03C8             ADD ECX,EAX
     *  0046B1AC   83C6 01          ADD ESI,0x1
     *  0046B1AF  ^EB E6            JMP SHORT .0046B197
     *  0046B1B1   3C 46            CMP AL,0x46
     *  0046B1B3   77 13            JA SHORT .0046B1C8
     *  0046B1B5   3C 41            CMP AL,0x41
     *  0046B1B7   72 0F            JB SHORT .0046B1C8
     *  0046B1B9   0FB6D0           MOVZX EDX,AL
     *  0046B1BC   C1E1 04          SHL ECX,0x4
     *  0046B1BF   8D4C11 C9        LEA ECX,DWORD PTR DS:[ECX+EDX-0x37]
     *  0046B1C3   83C6 01          ADD ESI,0x1
     *  0046B1C6  ^EB CF            JMP SHORT .0046B197
     *  0046B1C8   3C 66            CMP AL,0x66
     *  0046B1CA   77 13            JA SHORT .0046B1DF
     *  0046B1CC   3C 61            CMP AL,0x61
     *  0046B1CE   72 0F            JB SHORT .0046B1DF
     *  0046B1D0   0FB6C0           MOVZX EAX,AL
     *  0046B1D3   C1E1 04          SHL ECX,0x4
     *  0046B1D6   8D4C01 A9        LEA ECX,DWORD PTR DS:[ECX+EAX-0x57]
     *  0046B1DA   83C6 01          ADD ESI,0x1
     *  0046B1DD  ^EB B8            JMP SHORT .0046B197
     *  0046B1DF   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
     *  0046B1E3   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
     *  0046B1E7   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
     *  0046B1EB   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
     *  0046B1EF  ^E9 DFFEFFFF      JMP .0046B0D3
     *  0046B1F4   3D 5C720000      CMP EAX,0x725C
     *  0046B1F9   7F 56            JG SHORT .0046B251
     *  0046B1FB   74 19            JE SHORT .0046B216
     *  0046B1FD   3D 5C660000      CMP EAX,0x665C
     *  0046B202   74 23            JE SHORT .0046B227
     *  0046B204   3D 5C670000      CMP EAX,0x675C
     *  0046B209  ^0F84 8AFEFFFF    JE .0046B099
     *  0046B20F   3D 5C6E0000      CMP EAX,0x6E5C
     *  0046B214   75 4D            JNZ SHORT .0046B263
     *  0046B216   57               PUSH EDI
     *  0046B217   E8 54DBFFFF      CALL .00468D70
     *  0046B21C   83C4 04          ADD ESP,0x4
     *  0046B21F   83C6 02          ADD ESI,0x2
     *  0046B222  ^E9 ACFEFFFF      JMP .0046B0D3
     *  0046B227   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  0046B22A   83C6 02          ADD ESI,0x2
     *  0046B22D   33C9             XOR ECX,ECX
     *  0046B22F   3C 39            CMP AL,0x39
     *  0046B231   77 17            JA SHORT .0046B24A
     *  0046B233   3C 30            CMP AL,0x30
     *  0046B235   72 13            JB SHORT .0046B24A
     *  0046B237   83C6 01          ADD ESI,0x1
     *  0046B23A   0FB6D0           MOVZX EDX,AL
     *  0046B23D   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0046B23F   3C 39            CMP AL,0x39
     *  0046B241   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  0046B244   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  0046B248  ^76 E9            JBE SHORT .0046B233
     *  0046B24A   6A 00            PUSH 0x0
     *  0046B24C  ^E9 E8FEFFFF      JMP .0046B139
     *  0046B251   3D 5C730000      CMP EAX,0x735C
     *  0046B256  ^0F84 3DFEFFFF    JE .0046B099
     *  0046B25C   3D 5C7B0000      CMP EAX,0x7B5C
     *  0046B261   74 49            JE SHORT .0046B2AC
     *  0046B263   52               PUSH EDX
     *  0046B264   E8 C7D5FFFF      CALL .00468830
     *  0046B269   83C4 04          ADD ESP,0x4
     *  0046B26C   85C0             TEST EAX,EAX
     *  0046B26E   74 1E            JE SHORT .0046B28E
     *  0046B270   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  0046B274   50               PUSH EAX
     *  0046B275   52               PUSH EDX
     *  0046B276   57               PUSH EDI
     *  0046B277   E8 E4EFFFFF      CALL .0046A260
     *  0046B27C   83C4 0C          ADD ESP,0xC
     *  0046B27F   85C0             TEST EAX,EAX
     *  0046B281   74 4A            JE SHORT .0046B2CD
     *  0046B283   83C6 02          ADD ESI,0x2
     *  0046B286   83C5 01          ADD EBP,0x1
     *  0046B289  ^E9 45FEFFFF      JMP .0046B0D3
     *  0046B28E   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
     *  0046B292   51               PUSH ECX
     *  0046B293   53               PUSH EBX
     *  0046B294   57               PUSH EDI
     *  0046B295   E8 66F2FFFF      CALL .0046A500
     *  0046B29A   83C4 0C          ADD ESP,0xC
     *  0046B29D   85C0             TEST EAX,EAX
     *  0046B29F   74 2C            JE SHORT .0046B2CD
     *  0046B2A1   83C6 01          ADD ESI,0x1
     *  0046B2A4   83C5 01          ADD EBP,0x1
     *  0046B2A7  ^E9 27FEFFFF      JMP .0046B0D3
     *  0046B2AC   8D5424 24        LEA EDX,DWORD PTR SS:[ESP+0x24]
     *  0046B2B0   52               PUSH EDX
     *  0046B2B1   83C6 02          ADD ESI,0x2
     *  0046B2B4   56               PUSH ESI
     *  0046B2B5   57               PUSH EDI
     *  0046B2B6   E8 F5F4FFFF      CALL .0046A7B0
     *  0046B2BB   8BF0             MOV ESI,EAX
     *  0046B2BD   83C4 0C          ADD ESP,0xC
     *  0046B2C0   85F6             TEST ESI,ESI
     *  0046B2C2   74 09            JE SHORT .0046B2CD
     *  0046B2C4   036C24 24        ADD EBP,DWORD PTR SS:[ESP+0x24]
     *  0046B2C8  ^E9 06FEFFFF      JMP .0046B0D3
     *  0046B2CD   5B               POP EBX
     *  0046B2CE   5D               POP EBP
     *  0046B2CF   5F               POP EDI
     *  0046B2D0   33C0             XOR EAX,EAX
     *  0046B2D2   5E               POP ESI
     *  0046B2D3   83C4 10          ADD ESP,0x10
     *  0046B2D6   C3               RETN
     *  0046B2D7   5F               POP EDI
     *  0046B2D8   33C0             XOR EAX,EAX
     *  0046B2DA   5E               POP ESI
     *  0046B2DB   83C4 10          ADD ESP,0x10
     *  0046B2DE   C3               RETN
     *  0046B2DF   CC               INT3
     *
     *  Sample game: 母子愛2 (2RM)
     *  0047120D   CC               INT3
     *  0047120E   CC               INT3
     *  0047120F   CC               INT3
     *  00471210   83EC 10          SUB ESP,0x10
     *  00471213   56               PUSH ESI
     *  00471214   57               PUSH EDI
     *  00471215   8B7C24 1C        MOV EDI,DWORD PTR SS:[ESP+0x1C]
     *  00471219   85FF             TEST EDI,EDI
     *  0047121B   0F84 98030000    JE oyakoai2.004715B9
     *  00471221   8B7424 20        MOV ESI,DWORD PTR SS:[ESP+0x20]
     *  00471225   85F6             TEST ESI,ESI
     *  00471227   0F84 8C030000    JE oyakoai2.004715B9
     *  0047122D   55               PUSH EBP
     *  0047122E   33ED             XOR EBP,EBP
     *  00471230   392D 48E16C00    CMP DWORD PTR DS:[0x6CE148],EBP
     *  00471236   75 09            JNZ SHORT oyakoai2.00471241
     *  00471238   5D               POP EBP
     *  00471239   5F               POP EDI
     *  0047123A   33C0             XOR EAX,EAX
     *  0047123C   5E               POP ESI
     *  0047123D   83C4 10          ADD ESP,0x10
     *  00471240   C3               RETN
     *  00471241   8B47 60          MOV EAX,DWORD PTR DS:[EDI+0x60]
     *  00471244   8B4F 64          MOV ECX,DWORD PTR DS:[EDI+0x64]
     *  00471247   8B57 68          MOV EDX,DWORD PTR DS:[EDI+0x68]
     *  0047124A   894424 0C        MOV DWORD PTR SS:[ESP+0xC],EAX
     *  0047124E   8B47 6C          MOV EAX,DWORD PTR DS:[EDI+0x6C]
     *  00471251   894424 18        MOV DWORD PTR SS:[ESP+0x18],EAX
     *  00471255   8B47 4C          MOV EAX,DWORD PTR DS:[EDI+0x4C]
     *  00471258   25 00F00000      AND EAX,0xF000
     *  0047125D   3D 00100000      CMP EAX,0x1000
     *  00471262   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
     *  00471266   895424 14        MOV DWORD PTR SS:[ESP+0x14],EDX
     *  0047126A   74 26            JE SHORT oyakoai2.00471292
     *  0047126C   3D 00200000      CMP EAX,0x2000
     *  00471271   74 13            JE SHORT oyakoai2.00471286
     *  00471273   3D 00300000      CMP EAX,0x3000
     *  00471278   75 30            JNZ SHORT oyakoai2.004712AA
     *  0047127A   8D4C24 0C        LEA ECX,DWORD PTR SS:[ESP+0xC]
     *  0047127E   51               PUSH ECX
     *  0047127F   68 81770000      PUSH 0x7781
     *  00471284   EB 16            JMP SHORT oyakoai2.0047129C
     *  00471286   8D5424 0C        LEA EDX,DWORD PTR SS:[ESP+0xC]
     *  0047128A   52               PUSH EDX
     *  0047128B   68 81750000      PUSH 0x7581
     *  00471290   EB 0A            JMP SHORT oyakoai2.0047129C
     *  00471292   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
     *  00471296   50               PUSH EAX
     *  00471297   68 81790000      PUSH 0x7981
     *  0047129C   57               PUSH EDI
     *  0047129D   E8 3EF0FFFF      CALL oyakoai2.004702E0
     *  004712A2   83C4 0C          ADD ESP,0xC
     *  004712A5   BD 02000000      MOV EBP,0x2
     *  004712AA   53               PUSH EBX
     *  004712AB   8A1E             MOV BL,BYTE PTR DS:[ESI]
     *  004712AD   84DB             TEST BL,BL
     *  004712AF   0F84 93000000    JE oyakoai2.00471348
     *  004712B5   0FB716           MOVZX EDX,WORD PTR DS:[ESI]
     *  004712B8   0FB7C2           MOVZX EAX,DX
     *  004712BB   3D 5C630000      CMP EAX,0x635C
     *  004712C0   0F8F A7010000    JG oyakoai2.0047146D
     *  004712C6   0F84 39010000    JE oyakoai2.00471405
     *  004712CC   3D 5C4E0000      CMP EAX,0x4E5C
     *  004712D1   0F8F ED000000    JG oyakoai2.004713C4
     *  004712D7   0F84 B2010000    JE oyakoai2.0047148F
     *  004712DD   3D 5C430000      CMP EAX,0x435C
     *  004712E2   0F84 1D010000    JE oyakoai2.00471405
     *  004712E8   3D 5C460000      CMP EAX,0x465C
     *  004712ED   0F84 8D000000    JE oyakoai2.00471380
     *  004712F3   3D 5C470000      CMP EAX,0x475C
     *  004712F8   0F85 E2010000    JNZ oyakoai2.004714E0
     *  004712FE   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  00471301   83C6 02          ADD ESI,0x2
     *  00471304   33C9             XOR ECX,ECX
     *  00471306   3C 39            CMP AL,0x39
     *  00471308   77 1D            JA SHORT oyakoai2.00471327
     *  0047130A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  00471310   3C 30            CMP AL,0x30
     *  00471312   72 13            JB SHORT oyakoai2.00471327
     *  00471314   83C6 01          ADD ESI,0x1
     *  00471317   0FB6D0           MOVZX EDX,AL
     *  0047131A   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0047131C   3C 39            CMP AL,0x39
     *  0047131E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  00471321   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  00471325  ^76 E9            JBE SHORT oyakoai2.00471310
     *  00471327   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  0047132B   50               PUSH EAX
     *  0047132C   81C1 00FFFFFF    ADD ECX,-0x100
     *  00471332   51               PUSH ECX
     *  00471333   57               PUSH EDI
     *  00471334   E8 A7EFFFFF      CALL oyakoai2.004702E0
     *  00471339   83C4 0C          ADD ESP,0xC
     *  0047133C   03E8             ADD EBP,EAX
     *  0047133E   8A1E             MOV BL,BYTE PTR DS:[ESI]
     *  00471340   84DB             TEST BL,BL
     *  00471342  ^0F85 6DFFFFFF    JNZ oyakoai2.004712B5
     *  00471348   8B47 4C          MOV EAX,DWORD PTR DS:[EDI+0x4C]
     *  0047134B   25 00F00000      AND EAX,0xF000
     *  00471350   3D 00100000      CMP EAX,0x1000
     *  00471355   0F84 05020000    JE oyakoai2.00471560
     *  0047135B   3D 00200000      CMP EAX,0x2000
     *  00471360   0F84 EE010000    JE oyakoai2.00471554
     *  00471366   3D 00300000      CMP EAX,0x3000
     *  0047136B   0F85 05020000    JNZ oyakoai2.00471576
     *  00471371   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
     *  00471375   51               PUSH ECX
     *  00471376   68 81780000      PUSH 0x7881
     *  0047137B   E9 EA010000      JMP oyakoai2.0047156A
     *  00471380   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  00471383   83C6 02          ADD ESI,0x2
     *  00471386   33C9             XOR ECX,ECX
     *  00471388   3C 39            CMP AL,0x39
     *  0047138A   77 1B            JA SHORT oyakoai2.004713A7
     *  0047138C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
     *  00471390   3C 30            CMP AL,0x30
     *  00471392   72 13            JB SHORT oyakoai2.004713A7
     *  00471394   83C6 01          ADD ESI,0x1
     *  00471397   0FB6D0           MOVZX EDX,AL
     *  0047139A   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  0047139C   3C 39            CMP AL,0x39
     *  0047139E   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  004713A1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  004713A5  ^76 E9            JBE SHORT oyakoai2.00471390
     *  004713A7   6A 01            PUSH 0x1
     *  004713A9   8B0C8D E8776C00  MOV ECX,DWORD PTR DS:[ECX*4+0x6C77E8]
     *  004713B0   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
     *  004713B4   50               PUSH EAX
     *  004713B5   51               PUSH ECX
     *  004713B6   57               PUSH EDI
     *  004713B7   E8 34FBFFFF      CALL oyakoai2.00470EF0
     *  004713BC   83C4 10          ADD ESP,0x10
     *  004713BF  ^E9 78FFFFFF      JMP oyakoai2.0047133C
     *  004713C4   3D 5C520000      CMP EAX,0x525C
     *  004713C9   0F84 C0000000    JE oyakoai2.0047148F
     *  004713CF   3D 5C530000      CMP EAX,0x535C
     *  004713D4  ^0F84 24FFFFFF    JE oyakoai2.004712FE
     *  004713DA   3D 5C5C0000      CMP EAX,0x5C5C
     *  004713DF   0F85 FB000000    JNZ oyakoai2.004714E0
     *  004713E5   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
     *  004713E9   52               PUSH EDX
     *  004713EA   6A 5C            PUSH 0x5C
     *  004713EC   57               PUSH EDI
     *  004713ED   E8 2EF2FFFF      CALL oyakoai2.00470620
     *  004713F2   83C4 0C          ADD ESP,0xC
     *  004713F5   85C0             TEST EAX,EAX
     *  004713F7   0F84 4D010000    JE oyakoai2.0047154A
     *  004713FD   83C6 01          ADD ESI,0x1
     *  00471400  ^E9 39FFFFFF      JMP oyakoai2.0047133E
     *  00471405   33C9             XOR ECX,ECX
     *  00471407   83C6 02          ADD ESI,0x2
     *  0047140A   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
     *  00471410   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  00471412   3C 39            CMP AL,0x39
     *  00471414   77 14            JA SHORT oyakoai2.0047142A
     *  00471416   3C 30            CMP AL,0x30
     *  00471418   72 10            JB SHORT oyakoai2.0047142A
     *  0047141A   83C1 FD          ADD ECX,-0x3
     *  0047141D   0FB6C0           MOVZX EAX,AL
     *  00471420   C1E1 04          SHL ECX,0x4
     *  00471423   03C8             ADD ECX,EAX
     *  00471425   83C6 01          ADD ESI,0x1
     *  00471428  ^EB E6            JMP SHORT oyakoai2.00471410
     *  0047142A   3C 46            CMP AL,0x46
     *  0047142C   77 13            JA SHORT oyakoai2.00471441
     *  0047142E   3C 41            CMP AL,0x41
     *  00471430   72 0F            JB SHORT oyakoai2.00471441
     *  00471432   0FB6D0           MOVZX EDX,AL
     *  00471435   C1E1 04          SHL ECX,0x4
     *  00471438   8D4C11 C9        LEA ECX,DWORD PTR DS:[ECX+EDX-0x37]
     *  0047143C   83C6 01          ADD ESI,0x1
     *  0047143F  ^EB CF            JMP SHORT oyakoai2.00471410
     *  00471441   3C 66            CMP AL,0x66
     *  00471443   77 13            JA SHORT oyakoai2.00471458
     *  00471445   3C 61            CMP AL,0x61
     *  00471447   72 0F            JB SHORT oyakoai2.00471458
     *  00471449   0FB6C0           MOVZX EAX,AL
     *  0047144C   C1E1 04          SHL ECX,0x4
     *  0047144F   8D4C01 A9        LEA ECX,DWORD PTR DS:[ECX+EAX-0x57]
     *  00471453   83C6 01          ADD ESI,0x1
     *  00471456  ^EB B8            JMP SHORT oyakoai2.00471410
     *  00471458   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
     *  0047145C   894C24 18        MOV DWORD PTR SS:[ESP+0x18],ECX
     *  00471460   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
     *  00471464   894C24 10        MOV DWORD PTR SS:[ESP+0x10],ECX
     *  00471468  ^E9 D1FEFFFF      JMP oyakoai2.0047133E
     *  0047146D   3D 5C720000      CMP EAX,0x725C
     *  00471472   7F 5A            JG SHORT oyakoai2.004714CE
     *  00471474   74 19            JE SHORT oyakoai2.0047148F
     *  00471476   3D 5C660000      CMP EAX,0x665C
     *  0047147B   74 23            JE SHORT oyakoai2.004714A0
     *  0047147D   3D 5C670000      CMP EAX,0x675C
     *  00471482  ^0F84 76FEFFFF    JE oyakoai2.004712FE
     *  00471488   3D 5C6E0000      CMP EAX,0x6E5C
     *  0047148D   75 51            JNZ SHORT oyakoai2.004714E0
     *  0047148F   57               PUSH EDI
     *  00471490   E8 BBD2FFFF      CALL oyakoai2.0046E750
     *  00471495   83C4 04          ADD ESP,0x4
     *  00471498   83C6 02          ADD ESI,0x2
     *  0047149B  ^E9 9EFEFFFF      JMP oyakoai2.0047133E
     *  004714A0   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
     *  004714A3   83C6 02          ADD ESI,0x2
     *  004714A6   33C9             XOR ECX,ECX
     *  004714A8   3C 39            CMP AL,0x39
     *  004714AA   77 1B            JA SHORT oyakoai2.004714C7
     *  004714AC   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
     *  004714B0   3C 30            CMP AL,0x30
     *  004714B2   72 13            JB SHORT oyakoai2.004714C7
     *  004714B4   83C6 01          ADD ESI,0x1
     *  004714B7   0FB6D0           MOVZX EDX,AL
     *  004714BA   8A06             MOV AL,BYTE PTR DS:[ESI]
     *  004714BC   3C 39            CMP AL,0x39
     *  004714BE   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
     *  004714C1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
     *  004714C5  ^76 E9            JBE SHORT oyakoai2.004714B0
     *  004714C7   6A 00            PUSH 0x0
     *  004714C9  ^E9 DBFEFFFF      JMP oyakoai2.004713A9
     *  004714CE   3D 5C730000      CMP EAX,0x735C
     *  004714D3  ^0F84 25FEFFFF    JE oyakoai2.004712FE
     *  004714D9   3D 5C7B0000      CMP EAX,0x7B5C
     *  004714DE   74 49            JE SHORT oyakoai2.00471529
     *  004714E0   52               PUSH EDX
     *  004714E1   E8 5ACDFFFF      CALL oyakoai2.0046E240
     *  004714E6   83C4 04          ADD ESP,0x4
     *  004714E9   85C0             TEST EAX,EAX
     *  004714EB   74 1E            JE SHORT oyakoai2.0047150B
     *  004714ED   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  004714F1   50               PUSH EAX
     *  004714F2   52               PUSH EDX
     *  004714F3   57               PUSH EDI
     *  004714F4   E8 E7EDFFFF      CALL oyakoai2.004702E0
     *  004714F9   83C4 0C          ADD ESP,0xC
     *  004714FC   85C0             TEST EAX,EAX
     *  004714FE   74 4A            JE SHORT oyakoai2.0047154A
     *  00471500   83C6 02          ADD ESI,0x2
     *  00471503   83C5 01          ADD EBP,0x1
     *  00471506  ^E9 33FEFFFF      JMP oyakoai2.0047133E
     *  0047150B   8D4C24 10        LEA ECX,DWORD PTR SS:[ESP+0x10]
     *  0047150F   51               PUSH ECX
     *  00471510   53               PUSH EBX
     *  00471511   57               PUSH EDI
     *  00471512   E8 09F1FFFF      CALL oyakoai2.00470620
     *  00471517   83C4 0C          ADD ESP,0xC
     *  0047151A   85C0             TEST EAX,EAX
     *  0047151C   74 2C            JE SHORT oyakoai2.0047154A
     *  0047151E   83C6 01          ADD ESI,0x1
     *  00471521   83C5 01          ADD EBP,0x1
     *  00471524  ^E9 15FEFFFF      JMP oyakoai2.0047133E
     *  00471529   8D5424 24        LEA EDX,DWORD PTR SS:[ESP+0x24]
     *  0047152D   52               PUSH EDX
     *  0047152E   83C6 02          ADD ESI,0x2
     *  00471531   56               PUSH ESI
     *  00471532   57               PUSH EDI
     *  00471533   E8 38F4FFFF      CALL oyakoai2.00470970
     *  00471538   8BF0             MOV ESI,EAX
     *  0047153A   83C4 0C          ADD ESP,0xC
     *  0047153D   85F6             TEST ESI,ESI
     *  0047153F   74 09            JE SHORT oyakoai2.0047154A
     *  00471541   036C24 24        ADD EBP,DWORD PTR SS:[ESP+0x24]
     *  00471545  ^E9 F4FDFFFF      JMP oyakoai2.0047133E
     *  0047154A   5B               POP EBX
     *  0047154B   5D               POP EBP
     *  0047154C   5F               POP EDI
     *  0047154D   33C0             XOR EAX,EAX
     *  0047154F   5E               POP ESI
     *  00471550   83C4 10          ADD ESP,0x10
     *  00471553   C3               RETN
     *  00471554   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
     *  00471558   52               PUSH EDX
     *  00471559   68 81760000      PUSH 0x7681
     *  0047155E   EB 0A            JMP SHORT oyakoai2.0047156A
     *  00471560   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  00471564   50               PUSH EAX
     *  00471565   68 817A0000      PUSH 0x7A81
     *  0047156A   57               PUSH EDI
     *  0047156B   E8 70EDFFFF      CALL oyakoai2.004702E0
     *  00471570   83C4 0C          ADD ESP,0xC
     *  00471573   83C5 02          ADD EBP,0x2
     *  00471576   F647 4C 01       TEST BYTE PTR DS:[EDI+0x4C],0x1
     *  0047157A   74 09            JE SHORT oyakoai2.00471585
     *  0047157C   57               PUSH EDI
     *  0047157D   E8 4ED3FFFF      CALL oyakoai2.0046E8D0
     *  00471582   83C4 04          ADD ESP,0x4
     *  00471585   F747 4C 00010000 TEST DWORD PTR DS:[EDI+0x4C],0x100
     *  0047158C   74 09            JE SHORT oyakoai2.00471597
     *  0047158E   57               PUSH EDI
     *  0047158F   E8 4CD6FFFF      CALL oyakoai2.0046EBE0
     *  00471594   83C4 04          ADD ESP,0x4
     *  00471597   F647 4C 08       TEST BYTE PTR DS:[EDI+0x4C],0x8
     *  0047159B   74 12            JE SHORT oyakoai2.004715AF
     *  0047159D   833D 306D6C00 00 CMP DWORD PTR DS:[0x6C6D30],0x0
     *  004715A4   74 09            JE SHORT oyakoai2.004715AF
     *  004715A6   57               PUSH EDI
     *  004715A7   E8 C4DCFFFF      CALL oyakoai2.0046F270
     *  004715AC   83C4 04          ADD ESP,0x4
     *  004715AF   5B               POP EBX
     *  004715B0   8BC5             MOV EAX,EBP
     *  004715B2   5D               POP EBP
     *  004715B3   5F               POP EDI
     *  004715B4   5E               POP ESI
     *  004715B5   83C4 10          ADD ESP,0x10
     *  004715B8   C3               RETN
     *  004715B9   5F               POP EDI
     *  004715BA   33C0             XOR EAX,EAX
     *  004715BC   5E               POP ESI
     *  004715BD   83C4 10          ADD ESP,0x10
     *  004715C0   C3               RETN
     *  004715C1   CC               INT3
     *  004715C2   CC               INT3
     *  004715C3   CC               INT3
     *  004715C4   CC               INT3
     *  004715C5   CC               INT3
     *  004715C6   CC               INT3
     *  004715C7   CC               INT3
     *  004715C8   CC               INT3
     *  004715C9   CC               INT3
     *  004715CA   CC               INT3
     *  004715CB   CC               INT3
     *  004715CC   CC               INT3
     *  004715CD   CC               INT3
     *  004715CE   CC               INT3
     *  004715CF   CC               INT3
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x75, 0x09,       // 00471236   75 09            jnz short oyakoai2.00471241
          0x5d,             // 00471238   5d               pop ebp
          0x5f,             // 00471239   5f               pop edi
          0x33, 0xc0,       // 0047123a   33c0             xor eax,eax
          0x5e,             // 0047123c   5e               pop esi
          0x83, 0xc4, 0x10, // 0047123d   83c4 10          add esp,0x10
          0xc3              // 00471240   c3               retn
      };
      const BYTE pattern[] = {
          // プリズム☆ま～じカル　～Prism Generations!～
          // プリズム☆ま～じカル！AFTERSTORYS迷える子羊といけにえの山
          //[141128][bootUP!] はにつま
          0x0f, XX2,
          0x3d, 0x5c, 0x63, 0x00, 0x00};
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);

      auto _do = [](ULONG addr)
      {
        addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
        if (!addr)
          return false;
        HookParam hp;
        hp.address = addr;
        hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
        hp.offset = stackoffset(2);
        hp.filter_fun = pensilfilter;
        hp.embed_hook_font = F_GetGlyphOutlineA;
        return NewHook(hp, "EmbedPensil");
      };
      if (addr && _do(addr))
        return true;
      bool ok = false;
      for (auto addr : Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, processStartAddress, processStopAddress))
      {
        ok = _do(addr) || ok;
      }
      return ok;
    }

  } // namespace ScenarioHook
  namespace OtherHook
  {
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x83, 0x7e, 0x14, 0x00, // 004250f6   837e 14 00       cmp dword ptr ds:[esi+0x14],0x0
          0x75, 0x09,             // 004250fa   75 09            jnz short oyakoai2.00425105
          0x33, 0xc0,             // 004250fc   33c0             xor eax,eax
          0x5e,                   // 004250fe   5e               pop esi
          0x83, 0xc4, 0x28,       // 004250ff   83c4 28          add esp,0x28
          0xc2, 0x08, 0x00        // 00425102   c2 0800          retn 0x8
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr;
      hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.offset = stackoffset(1);
      hp.filter_fun = pensilfilter;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      return NewHook(hp, "EmbedPensilChoice");
    }

  } // namespace OtherHook
}
#if 0  // jich 3/8/2015: disabled
bool IsPensilSetup()
{
  HANDLE hFile = IthCreateFile(L"PSetup.exe", FILE_READ_DATA, FILE_SHARE_READ, FILE_OPEN);
  FILE_STANDARD_INFORMATION info;
  IO_STATUS_BLOCK ios;
  LPVOID buffer = nullptr;
  NtQueryInformationFile(hFile, &ios, &info, sizeof(info), FileStandardInformation);
  NtAllocateVirtualMemory(GetCurrentProcess(), &buffer, 0,
      &info.AllocationSize.LowPart, MEM_RESERVE|MEM_COMMIT, PAGE_READWRITE);
  NtReadFile(hFile, 0,0,0, &ios, buffer, info.EndOfFile.LowPart, 0, 0);
  CloseHandle(hFile);
  BYTE *b = (BYTE *)buffer;
  DWORD len = info.EndOfFile.LowPart & ~1;
  if (len == info.AllocationSize.LowPart)
    len -= 2;
  b[len] = 0;
  b[len + 1] = 0;
  bool ret = wcsstr((LPWSTR)buffer, L"PENSIL") || wcsstr((LPWSTR)buffer, L"Pensil");
  NtFreeVirtualMemory(GetCurrentProcess(), &buffer, &info.AllocationSize.LowPart, MEM_RELEASE);
  return ret;
}
#endif // if 0

/** jichi 8/2/2014 2RM
 *  Sample games:
 *  - [エロイッ�] 父娘� �いけなね�作り2- /HBN-20*0@54925:oyakoai.exe
 *  - [エロイッ�] ぁ�なね�作り �親友�お母さんに種付けしまくる1週間�-- /HS-1C@46FC9D (not used)
 *
 *  Observations from Debug of 父娘�:
 *  - The executable shows product name as 2RM - Adventure Engine
 *  - 2 calls to GetGlyphOutlineA with incompleted game
 *  - Memory location of the text is fixed
 *  - The LAST place accessing the text is hooked
 *  - The actual text has pattern like this {surface,ruby} and hence not hooked
 *
 *  /HBN-20*0@54925:oyakoai.exe
 *  - addr: 346405 = 0x54925
 *  - length_offset: 1
 *  - module: 3918223605
 *  - off: 4294967260 = 0xffffffdc = -0x24 -- 0x24 comes from  mov ebp,dword ptr ss:[esp+0x24]
 *  - type: 1096 = 0x448
 *
 *  This is a very long function
 *  父娘�:
 *  - 004548e1  |. 84db           test bl,bl
 *  - 004548e3  |. 8b7424 20      mov esi,dword ptr ss:[esp+0x20]
 *  - 004548e7  |. 74 08          je short oyakoai.004548f1
 *  - 004548e9  |. c74424 24 0000>mov dword ptr ss:[esp+0x24],0x0
 *  - 004548f1  |> 8b6c24 3c      mov ebp,dword ptr ss:[esp+0x3c]
 *  - 004548f5  |. 837d 5c 00     cmp dword ptr ss:[ebp+0x5c],0x0
 *  - 004548f9  |. c74424 18 0000>mov dword ptr ss:[esp+0x18],0x0
 *  - 00454901  |. 0f8e da000000  jle oyakoai.004549e1
 *  - 00454907  |. 8b6c24 24      mov ebp,dword ptr ss:[esp+0x24]
 *  - 0045490b  |. eb 0f          jmp short oyakoai.0045491c
 *  - 0045490d  |  8d49 00        lea ecx,dword ptr ds:[ecx]
 *  - 00454910  |> 8b15 50bd6c00  mov edx,dword ptr ds:[0x6cbd50]
 *  - 00454916  |. 8b0d 94bd6c00  mov ecx,dword ptr ds:[0x6cbd94]
 *  - 0045491c  |> 803f 00        cmp byte ptr ds:[edi],0x0
 *  - 0045491f  |. 0f84 db000000  je oyakoai.00454a00
 *  - 00454925  |. 0fb717         movzx edx,word ptr ds:[edi]   ; jichi: hook here
 *  - 00454928  |. 8b4c24 10      mov ecx,dword ptr ss:[esp+0x10]
 *  - 0045492c  |. 52             push edx
 *  - 0045492d  |. 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx
 *  - 00454931  |. e8 9a980100    call oyakoai.0046e1d0
 *  - 00454936  |. 83c4 04        add esp,0x4
 *  - 00454939  |. 85c0           test eax,eax
 *  - 0045493b  |. 74 50          je short oyakoai.0045498d
 *  - 0045493d  |. 0335 50bd6c00  add esi,dword ptr ds:[0x6cbd50]
 *  - 00454943  |. 84db           test bl,bl
 *  - 00454945  |. 74 03          je short oyakoai.0045494a
 *  - 00454947  |. 83c5 02        add ebp,0x2
 *  - 0045494a  |> 3b7424 1c      cmp esi,dword ptr ss:[esp+0x1c]
 *  - 0045494e  |. a1 54bd6c00    mov eax,dword ptr ds:[0x6cbd54]
 *  - 00454953  |. 7f 12          jg short oyakoai.00454967
 *  - 00454955  |. 84db           test bl,bl
 *  - 00454957  |. 0f84 ea000000  je oyakoai.00454a47
 *  - 0045495d  |. 3b6c24 40      cmp ebp,dword ptr ss:[esp+0x40]
 *  - 00454961  |. 0f85 e0000000  jnz oyakoai.00454a47
 *  - 00454967  |> 014424 10      add dword ptr ss:[esp+0x10],eax
 *  - 0045496b  |. 84db           test bl,bl
 *  - 0045496d  |. 8b7424 20      mov esi,dword ptr ss:[esp+0x20]
 *  - 00454971  |. 0f84 d0000000  je oyakoai.00454a47
 *  - 00454977  |. 3b6c24 40      cmp ebp,dword ptr ss:[esp+0x40]
 *  - 0045497b  |. 0f85 c6000000  jnz oyakoai.00454a47
 *  - 00454981  |. 33ed           xor ebp,ebp
 *  - 00454983  |. 83c7 02        add edi,0x2
 *  - 00454986  |. 834424 18 01   add dword ptr ss:[esp+0x18],0x1
 *  - 0045498b  |. eb 3c          jmp short oyakoai.004549c9
 *  - 0045498d  |> a1 50bd6c00    mov eax,dword ptr ds:[0x6cbd50]
 *  - 00454992  |. d1e8           shr eax,1
 *  - 00454994  |. 03f0           add esi,eax
 *  - 00454996  |. 84db           test bl,bl
 *  - 00454998  |. 74 03          je short oyakoai.0045499d
 *  - 0045499a  |. 83c5 01        add ebp,0x1
 *  - 0045499d  |> 3b7424 1c      cmp esi,dword ptr ss:[esp+0x1c]
 *  - 004549a1  |. a1 54bd6c00    mov eax,dword ptr ds:[0x6cbd54]
 *  - 004549a6  |. 7f 0a          jg short oyakoai.004549b2
 *  - 004549a8  |. 84db           test bl,bl
 *
 *  ぁ�なね�作り:
 *  00454237   c74424 24 020000>mov dword ptr ss:[esp+0x24],0x2
 *  0045423f   3bf5             cmp esi,ebp
 *  00454241   7f 0e            jg short .00454251
 *  00454243   84db             test bl,bl
 *  00454245   74 1e            je short .00454265
 *  00454247   8b6c24 24        mov ebp,dword ptr ss:[esp+0x24]
 *  0045424b   3b6c24 40        cmp ebp,dword ptr ss:[esp+0x40]
 *  0045424f   75 14            jnz short .00454265
 *  00454251   014424 10        add dword ptr ss:[esp+0x10],eax
 *  00454255   84db             test bl,bl
 *  00454257   8b7424 20        mov esi,dword ptr ss:[esp+0x20]
 *  0045425b   74 08            je short .00454265
 *  0045425d   c74424 24 000000>mov dword ptr ss:[esp+0x24],0x0
 *  00454265   8b6c24 3c        mov ebp,dword ptr ss:[esp+0x3c]
 *  00454269   837d 5c 00       cmp dword ptr ss:[ebp+0x5c],0x0
 *  0045426d   c74424 18 000000>mov dword ptr ss:[esp+0x18],0x0
 *  00454275   0f8e d7000000    jle .00454352
 *  0045427b   8b6c24 24        mov ebp,dword ptr ss:[esp+0x24]
 *  0045427f   eb 0c            jmp short .0045428d
 *  00454281   8b15 18ad6c00    mov edx,dword ptr ds:[0x6cad18]
 *  00454287   8b0d 5cad6c00    mov ecx,dword ptr ds:[0x6cad5c]
 *  0045428d   803f 00          cmp byte ptr ds:[edi],0x0
 *  00454290   0f84 db000000    je .00454371
 *  00454296   0fb717           movzx edx,word ptr ds:[edi] ; jichi: hook here
 *  00454299   8b4c24 10        mov ecx,dword ptr ss:[esp+0x10]
 *  0045429d   52               push edx
 *  0045429e   894c24 2c        mov dword ptr ss:[esp+0x2c],ecx
 *  004542a2   e8 498a0100      call .0046ccf0
 *  004542a7   83c4 04          add esp,0x4
 *  004542aa   85c0             test eax,eax
 *  004542ac   74 50            je short .004542fe
 *  004542ae   0335 18ad6c00    add esi,dword ptr ds:[0x6cad18]
 *  004542b4   84db             test bl,bl
 *  004542b6   74 03            je short .004542bb
 *  004542b8   83c5 02          add ebp,0x2
 *  004542bb   3b7424 1c        cmp esi,dword ptr ss:[esp+0x1c]
 *  004542bf   a1 1cad6c00      mov eax,dword ptr ds:[0x6cad1c]
 *  004542c4   7f 12            jg short .004542d8
 *  004542c6   84db             test bl,bl
 *  004542c8   0f84 ea000000    je .004543b8
 *  004542ce   3b6c24 40        cmp ebp,dword ptr ss:[esp+0x40]
 *  004542d2   0f85 e0000000    jnz .004543b8
 *  004542d8   014424 10        add dword ptr ss:[esp+0x10],eax
 *  004542dc   84db             test bl,bl
 *  004542de   8b7424 20        mov esi,dword ptr ss:[esp+0x20]
 *  004542e2   0f84 d0000000    je .004543b8
 *  004542e8   3b6c24 40        cmp ebp,dword ptr ss:[esp+0x40]
 *  004542ec   0f85 c6000000    jnz .004543b8
 *  004542f2   33ed             xor ebp,ebp
 *  004542f4   83c7 02          add edi,0x2
 *  004542f7   834424 18 01     add dword ptr ss:[esp+0x18],0x1
 *  004542fc   eb 3c            jmp short .0045433a
 *  004542fe   a1 18ad6c00      mov eax,dword ptr ds:[0x6cad18]
 *  00454303   d1e8             shr eax,1
 *  00454305   03f0             add esi,eax
 *  00454307   84db             test bl,bl
 *  00454309   74 03            je short .0045430e
 *  0045430b   83c5 01          add ebp,0x1
 */
bool Insert2RMHook()
{
  const BYTE bytes[] = {
      0x80, 0x3f, 0x00,                   // 0045428d   803f 00          cmp byte ptr ds:[edi],0x0
      0x0f, 0x84, 0xdb, 0x00, 0x00, 0x00, // 00454290   0f84 db000000    je .00454371
      0x0f, 0xb7, 0x17,                   // 00454296   0fb717           movzx edx,word ptr ds:[edi] ; jichi: hook here
      0x8b, 0x4c, 0x24, 0x10,             // 00454299   8b4c24 10        mov ecx,dword ptr ss:[esp+0x10]
      0x52,                               // 0045429d   52               push edx
      0x89, 0x4c, 0x24, 0x2c,             // 0045429e   894c24 2c        mov dword ptr ss:[esp+0x2c],ecx
      0xe8                                //, 498a0100               // 004542a2   e8 498a0100      call .0046ccf0
  };
  enum
  {
    addr_offset = 0x00454296 - 0x0045428d
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(addr); // supposed to be 0x4010e0
  if (!addr)
  {
    ConsoleOutput("2RM: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(edi);
  hp.type = NO_CONTEXT | DATA_INDIRECT;
  ConsoleOutput("INSERT 2RM");
  return NewHook(hp, "2RM");
}
namespace
{
  bool abalone()
  {
    // 鬼孕の学園～スク水少女異種姦凌辱劇～
    BYTE bs[] = {
        0xD8, 0x0D, XX4,
        0xd9, 0x50, XX,
        0xd9, 0x58, XX,
        0xdb, 0x44, 0x24, XX,
        0xD8, 0x0D, XX4,
        0xd9, 0x50, XX,
        0xd9, 0x58, XX,
        0xdb, 0x44, 0x24, XX,
        0xD8, 0x0D, XX4,
        0xd9, 0x50, XX,
        0xd9, 0x58, XX};
    auto addr = MemDbg::findBytes(bs, sizeof(bs), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(3);
    hp.split = stackoffset(4);
    hp.type = USING_SPLIT;
    return NewHook(hp, "abalone");
  }
}
bool Pensil::attach_function()
{
  bool _1 = ScenarioHook::attach(processStartAddress, processStopAddress);
  if (_1)
    OtherHook::attach(processStartAddress, processStopAddress);
  bool _2rm = Insert2RMHook();
  auto _abalone = abalone();
  return InsertPensilHook() || _1 || _2rm || _abalone;
}