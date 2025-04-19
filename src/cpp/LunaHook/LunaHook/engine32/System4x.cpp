#include "System4x.h"

/**
 *  jichi 12/26/2013: Rance hook
 *
 *  ランス01 光をもとめて: /HSN4:-14@5506A9
 *  - addr: 5572265 (0x5596a9)
 *  - off: 4
 *  - split: 4294967272 (0xffffffe8 = -0x18)
 *  - type: 1041 (0x411)
 *
 *    the above code has the same pattern except int3.
 *    005506a9  |. e8 f2fb1600    call Rance01.006c02a0 ; hook here
 *    005506ae  |. 83c4 0c        add esp,0xc
 *    005506b1  |. 5f             pop edi
 *    005506b2  |. 5e             pop esi
 *    005506b3  |. b0 01          mov al,0x1
 *    005506b5  |. 5b             pop ebx
 *    005506b6  \. c2 0400        retn 0x4
 *    005506b9     cc             int3
 *
 *  ランス・クエス� /hsn4:-14@42e08a
 *    0042e08a  |. e8 91ed1f00    call Ranceque.0062ce20 ; hook here
 *    0042e08f  |. 83c4 0c        add esp,0xc
 *    0042e092  |. 5f             pop edi
 *    0042e093  |. 5e             pop esi
 *    0042e094  |. b0 01          mov al,0x1
 *    0042e096  |. 5b             pop ebx
 *    0042e097  \. c2 0400        retn 0x4
 *    0042e09a     cc             int3
 *
 *  5/7/2015  イブニクル version 1.0.1
 *  The hooked function is no longer get called after loading AliceRunPatch.dll.
 *  The hooked function is below.
 *  See also ATcode: http://capita.tistory.com/m/post/256
 *    005C40AE   CC               INT3
 *    005C40AF   CC               INT3
 *    005C40B0   53               PUSH EBX
 *    005C40B1   8B5C24 08        MOV EBX,DWORD PTR SS:[ESP+0x8]
 *    005C40B5   56               PUSH ESI
 *    005C40B6   57               PUSH EDI
 *    005C40B7   8B7B 10          MOV EDI,DWORD PTR DS:[EBX+0x10]
 *    005C40BA   8BF0             MOV ESI,EAX
 *    005C40BC   47               INC EDI
 *    005C40BD   3B7E 0C          CMP EDI,DWORD PTR DS:[ESI+0xC]
 *    005C40C0   76 0F            JBE SHORT .005C40D1
 *    005C40C2   E8 79F8FFFF      CALL .005C3940
 *    005C40C7   84C0             TEST AL,AL
 *    005C40C9   75 06            JNZ SHORT .005C40D1
 *    005C40CB   5F               POP EDI
 *    005C40CC   5E               POP ESI
 *    005C40CD   5B               POP EBX
 *    005C40CE   C2 0400          RETN 0x4
 *    005C40D1   837B 14 10       CMP DWORD PTR DS:[EBX+0x14],0x10
 *    005C40D5   72 02            JB SHORT .005C40D9
 *    005C40D7   8B1B             MOV EBX,DWORD PTR DS:[EBX]
 *    005C40D9   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
 *    005C40DD   75 15            JNZ SHORT .005C40F4
 *    005C40DF   57               PUSH EDI
 *    005C40E0   33C0             XOR EAX,EAX
 *    005C40E2   53               PUSH EBX
 *    005C40E3   50               PUSH EAX
 *    005C40E4   E8 B7400D00      CALL .006981A0
 *    005C40E9   83C4 0C          ADD ESP,0xC
 *    005C40EC   5F               POP EDI
 *    005C40ED   5E               POP ESI
 *    005C40EE   B0 01            MOV AL,0x1
 *    005C40F0   5B               POP EBX
 *    005C40F1   C2 0400          RETN 0x4
 *    005C40F4   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
 *    005C40F7   57               PUSH EDI
 *    005C40F8   53               PUSH EBX
 *    005C40F9   50               PUSH EAX
 *    005C40FA   E8 A1400D00      CALL .006981A0 ; jichi: call here
 *    005C40FF   83C4 0C          ADD ESP,0xC
 *    005C4102   5F               POP EDI
 *    005C4103   5E               POP ESI
 *    005C4104   B0 01            MOV AL,0x1
 *    005C4106   5B               POP EBX
 *    005C4107   C2 0400          RETN 0x4
 *    005C410A   CC               INT3
 *    005C410B   CC               INT3
 *    005C410C   CC               INT3 *
 */
static bool InsertSystem43OldHook(ULONG startAddress, ULONG stopAddress, LPCSTR hookName)
{
  // i.e. 83c40c5f5eb0015bc20400cccc without leading 0xe8
  // const BYTE ins[] = {  //   005506a9  |. e8 f2fb1600    call rance01.006c02a0 ; hook here
  //  0x83,0xc4, 0x0c,    //   005506ae  |. 83c4 0c        add esp,0xc
  //  0x5f,               //   005506b1  |. 5f             pop edi
  //  0x5e,               //   005506b2  |. 5e             pop esi
  //  0xb0, 0x01,         //   005506b3  |. b0 01          mov al,0x1
  //  0x5b,               //   005506b5  |. 5b             pop ebx
  //  0xc2, 0x04,0x00,    //   005506b6  \. c2 0400        retn 0x4
  //  0xcc, 0xcc // patching a few int3 to make sure that this is at the end of the code block
  //};
  // enum { addr_offset = -5 }; // the function call before the ins
  // ULONG addr = processStartAddress; //- sizeof(ins);
  ////addr = 0x5506a9;
  // enum { near_call = 0xe8 }; // intra-module function call
  // do {
  //   //addr += sizeof(ins); // so that each time return diff address -- not needed
  //   ULONG range = min(processStopAddress - addr, MAX_REL_ADDR);
  //   addr = MemDbg::findBytes(ins, sizeof(ins), addr, addr + range);
  //   if (!addr) {
  //     //ITH_MSG(L"failed");
  //     ConsoleOutput("System43: pattern not found");
  //     return false;
  //   }
  //   addr += addr_offset;
  // } while(near_call != *(BYTE *)addr); // function call
  // GROWL_DWORD(addr);

  // i.e. 83c40c5f5eb0015bc20400cccc without leading 0xe8
  const BYTE bytes[] = {
      0xe8, XX4,        //   005506a9  |. e8 f2fb1600    call rance01.006c02a0 ; hook here
      0x83, 0xc4, 0x0c, //   005506ae  |. 83c4 0c        add esp,0xc
      XX,               //   005506b1  |. 5f             pop edi ; Artikash 2/9/2019 change these to wildcards: Evenicle 2 has the pops and moves switched order
      XX,               //   005506b2  |. 5e             pop esi
      XX, XX,           //   005506b3  |. b0 01          mov al,0x1
      0x5b,             //   005506b5  |. 5b             pop ebx
      0xc2, 0x04, 0x00, //   005506b6  \. c2 0400        retn 0x4
      0xcc, 0xcc        // patching a few int3 to make sure that this is at the end of the code block
  };
  enum
  {
    addr_offset = 0
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL_DWORD(addr);
  if (!addr)
  {
    ConsoleOutput("System43: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = stackoffset(1);
  hp.split = regoffset(esp);
  hp.type = NO_CONTEXT | USING_SPLIT | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  ConsoleOutput("INSERT System43");
  ConsoleOutput("System43: disable GDI hooks"); // disable hooking to TextOutA, which is cached
  return NewHook(hp, hookName);
}

/** 5/13/2015 Add new hook for System43 engine that has no garbage threads and can detect character name
 *  Sample game: Evenicle
 *  See: http://capita.tistory.com/m/post/256
 *
 *  004EEA6C   CC               INT3
 *  004EEA6D   CC               INT3
 *  004EEA6E   CC               INT3
 *  004EEA6F   CC               INT3
 *  004EEA70   6A FF            PUSH -0x1
 *  004EEA72   68 E8267000      PUSH .007026E8
 *  004EEA77   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  004EEA7D   50               PUSH EAX
 *  004EEA7E   83EC 20          SUB ESP,0x20
 *  004EEA81   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  004EEA86   33C4             XOR EAX,ESP
 *  004EEA88   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  004EEA8C   53               PUSH EBX
 *  004EEA8D   55               PUSH EBP
 *  004EEA8E   56               PUSH ESI
 *  004EEA8F   57               PUSH EDI
 *  004EEA90   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  004EEA95   33C4             XOR EAX,ESP
 *  004EEA97   50               PUSH EAX
 *  004EEA98   8D4424 34        LEA EAX,DWORD PTR SS:[ESP+0x34]
 *  004EEA9C   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  004EEAA2   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  004EEAA6   8BF1             MOV ESI,ECX
 *  004EEAA8   E8 8346FBFF      CALL .004A3130
 *  004EEAAD   8BE8             MOV EBP,EAX
 *  004EEAAF   33DB             XOR EBX,EBX
 *  004EEAB1   3BEB             CMP EBP,EBX
 *  004EEAB3   75 07            JNZ SHORT .004EEABC
 *  004EEAB5   32C0             XOR AL,AL
 *  004EEAB7   E9 92000000      JMP .004EEB4E
 *  004EEABC   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  004EEABE   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  004EEAC0   8BCE             MOV ECX,ESI
 *  004EEAC2   FFD2             CALL EDX
 *  004EEAC4   8BC8             MOV ECX,EAX
 *  004EEAC6   C74424 28 0F0000>MOV DWORD PTR SS:[ESP+0x28],0xF
 *  004EEACE   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
 *  004EEAD2   885C24 14        MOV BYTE PTR SS:[ESP+0x14],BL
 *  004EEAD6   8D71 01          LEA ESI,DWORD PTR DS:[ECX+0x1]
 *  004EEAD9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  004EEAE0   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  004EEAE2   41               INC ECX
 *  004EEAE3   3AD3             CMP DL,BL
 *  004EEAE5  ^75 F9            JNZ SHORT .004EEAE0
 *  004EEAE7   2BCE             SUB ECX,ESI
 *  004EEAE9   50               PUSH EAX
 *  004EEAEA   8BF9             MOV EDI,ECX
 *  004EEAEC   8D7424 18        LEA ESI,DWORD PTR SS:[ESP+0x18]
 *  004EEAF0   E8 CB27F1FF      CALL .004012C0
 *  004EEAF5   8B7C24 48        MOV EDI,DWORD PTR SS:[ESP+0x48]
 *  004EEAF9   895C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EBX
 *  004EEAFD   8B75 3C          MOV ESI,DWORD PTR SS:[EBP+0x3C]
 *  004EEB00   E8 1B4A0100      CALL .00503520
 *  004EEB05   8BF8             MOV EDI,EAX
 *  004EEB07   8DB7 E4000000    LEA ESI,DWORD PTR DS:[EDI+0xE4]
 *  004EEB0D   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  004EEB11   8BD6             MOV EDX,ESI
 *  004EEB13   E8 985CF1FF      CALL .004047B0
 *  004EEB18   BD 10000000      MOV EBP,0x10
 *  004EEB1D   84C0             TEST AL,AL
 *  004EEB1F   75 18            JNZ SHORT .004EEB39
 *  004EEB21   895E 10          MOV DWORD PTR DS:[ESI+0x10],EBX
 *  004EEB24   396E 14          CMP DWORD PTR DS:[ESI+0x14],EBP
 *  004EEB27   72 02            JB SHORT .004EEB2B
 *  004EEB29   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  004EEB2B   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  004EEB2F   50               PUSH EAX
 *  004EEB30   8BCF             MOV ECX,EDI
 *  004EEB32   881E             MOV BYTE PTR DS:[ESI],BL
 *  004EEB34   E8 67CB0100      CALL .0050B6A0  ; jichi: ATcode modified here, text is on the top of the stack
 *  004EEB39   396C24 28        CMP DWORD PTR SS:[ESP+0x28],EBP
 *  004EEB3D   72 0D            JB SHORT .004EEB4C
 *  004EEB3F   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  004EEB43   51               PUSH ECX
 *  004EEB44   E8 42DC1900      CALL .0068C78B
 *  004EEB49   83C4 04          ADD ESP,0x4
 *  004EEB4C   B0 01            MOV AL,0x1
 *  004EEB4E   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  004EEB52   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  004EEB59   59               POP ECX
 *  004EEB5A   5F               POP EDI
 *  004EEB5B   5E               POP ESI
 *  004EEB5C   5D               POP EBP
 *  004EEB5D   5B               POP EBX
 *  004EEB5E   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
 *  004EEB62   33CC             XOR ECX,ESP
 *  004EEB64   E8 9CD61900      CALL .0068C205
 *  004EEB69   83C4 2C          ADD ESP,0x2C
 *  004EEB6C   C3               RETN
 *  004EEB6D   CC               INT3
 *  004EEB6E   CC               INT3
 *
 *  Actual binary patch for Evenicle exe: http://capita.tistory.com/m/post/256
 *  {005E393B(EB), 004EEB34(E9 13 B6 21 00), 005C71E0(E9 48 2F 14 00), 005B6494(E9 10 3D 15 00), 0070A10F(90 90 90 90 90 E8 F7 9F EB FF E9 C7 D0 EB FF 90 90 90 90 90 E8 78 15 E0 FF E9 0C 4A DE FF 50 8B 87 B0 00 00 00 66 81 38 84 00 75 0E 83 78 EA 5B 75 08 E8 A2 00 00 00 58 EB C6 58 EB C8 50 52 BA E0 0B 7A 00 60 89 D7 8B 74 E4 28 B9 06 00 00 00 F3 A5 61 8B 44 E4 08 8B 40 10 85 C0 74 29 8B 44 E4 08 8B 40 14 83 F8 0F 75 08 89 54 E4 08 5A 58 EB 9D 8D 42 20 60 89 C7 8B 32 8B 4A 14 83 C1 09 F3 A4 61 89 02 EB E3 5A 58 EB 89 90 90 90 90 90 E8 6C 9F EB FF E9 F0 C2 EA FF 50 8B 44 E4 04 83 78 0C 01 76 31 8B 87 84 02 00 00 66 83 78 FC 46 75 24 83 78 F8 22 74 16 83 78 F8 13 75 18 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 90 E8 06 00 00 00 58 EB B5 58 EB B7 60 8B 74 E4 28 BF E0 0B 7A 00 89 7C E4 28 B9 0C 00 00 00 F3 A5 61 C3)}
 *
 *  ATcode: FORCEFONT(5),ENCODEKOR,FONT(Malgun Gothic,-13),HOOK(0x0070A10F,TRANS([[ESP]+0x8],LEN([ESP]+0XC),PTRCHEAT),RETNPOS(COPY)),HOOK(0x0070A11E,TRANS([ESP],SMSTR(IGNORE)),RETNPOS(COPY)),HOOK(0x0070A19A,TRANS([[ESP]+0x8],LEN([ESP]+0XC),PTRCHEAT),RETNPOS(COPY))
 *  FilterCode: DenyWord{CUT(2)},FixLine{},KoFilter{},DumpText{},CustomDic{CDic},CustomScript{Write,Pass(-1),Cache}
 *
 *  The second hooked address pointed to the text address.
 *  The logic here is simplify buffer the read text, and replace the text by zero
 *  Then translate/paint them together.
 *  Several variables near the text address is used to check if the text is finished or not.
 *
 *  Function immediately before patched code:
 *  0070A09E   CC               INT3
 *  0070A09F   CC               INT3
 *  0070A0A0   6A FF            PUSH -0x1
 *  0070A0A2   68 358A7000      PUSH .00708A35
 *  0070A0A7   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0070A0AD   50               PUSH EAX
 *  0070A0AE   51               PUSH ECX
 *  0070A0AF   56               PUSH ESI
 *  0070A0B0   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  0070A0B5   33C4             XOR EAX,ESP
 *  0070A0B7   50               PUSH EAX
 *  0070A0B8   8D4424 0C        LEA EAX,DWORD PTR SS:[ESP+0xC]
 *  0070A0BC   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0070A0C2   C74424 14 000000>MOV DWORD PTR SS:[ESP+0x14],0x0
 *  0070A0CA   A1 54D17900      MOV EAX,DWORD PTR DS:[0x79D154]
 *  0070A0CF   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  0070A0D1   50               PUSH EAX
 *  0070A0D2   51               PUSH ECX
 *  0070A0D3   8D7424 10        LEA ESI,DWORD PTR SS:[ESP+0x10]
 *  0070A0D7   E8 6416F8FF      CALL .0068B740
 *  0070A0DC   A1 54D17900      MOV EAX,DWORD PTR DS:[0x79D154]
 *  0070A0E1   50               PUSH EAX
 *  0070A0E2   E8 A426F8FF      CALL .0068C78B
 *  0070A0E7   83C4 04          ADD ESP,0x4
 *  0070A0EA   8B4C24 0C        MOV ECX,DWORD PTR SS:[ESP+0xC]
 *  0070A0EE   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  0070A0F5   59               POP ECX
 *  0070A0F6   5E               POP ESI
 *  0070A0F7   83C4 10          ADD ESP,0x10
 *  0070A0FA   C3               RETN
 *  0070A0FB   C705 C4C17900 64>MOV DWORD PTR DS:[0x79C1C4],.0070B664
 *  0070A105   B9 C4C17900      MOV ECX,.0079C1C4
 *  0070A10A  ^E9 0722F8FF      JMP .0068C316
 *
 *  Patched code:
 *  0070A10F   90               NOP ; jichi: ATcode hooked here
 *  0070A110   90               NOP
 *  0070A111   90               NOP
 *  0070A112   90               NOP
 *  0070A113   90               NOP
 *  0070A114   E8 F79FEBFF      CALL .005C4110
 *  0070A119  ^E9 C7D0EBFF      JMP .005C71E5
 *  0070A11E   90               NOP
 *  0070A11F   90               NOP
 *  0070A120   90               NOP
 *  0070A121   90               NOP
 *  0070A122   90               NOP
 *  0070A123   E8 7815E0FF      CALL .0050B6A0                  ; jichi: call the original function for hookpoint #2
 *  0070A128  ^E9 0C4ADEFF      JMP .004EEB39                   ; jichi: come back to hookpoint#2
 *  0070A12D   50               PUSH EAX    ; jichi: this is for hookpoint #3, translate the text before send it to paint
 *  0070A12E   8B87 B0000000    MOV EAX,DWORD PTR DS:[EDI+0xB0]
 *  0070A134   66:8138 8400     CMP WORD PTR DS:[EAX],0x84
 *  0070A139   75 0E            JNZ SHORT .0070A149
 *  0070A13B   8378 EA 5B       CMP DWORD PTR DS:[EAX-0x16],0x5B
 *  0070A13F   75 08            JNZ SHORT .0070A149
 *  0070A141   E8 A2000000      CALL .0070A1E8
 *  0070A146   58               POP EAX
 *  0070A147  ^EB C6            JMP SHORT .0070A10F
 *  0070A149   58               POP EAX
 *  0070A14A  ^EB C8            JMP SHORT .0070A114
 *  0070A14C   50               PUSH EAX                        ; jichi: hookpoint#2 jmp here, text address is in [esp]
 *  0070A14D   52               PUSH EDX
 *  0070A14E   BA E00B7A00      MOV EDX,.007A0BE0               ; jichi: 007A0BE0 points to unused zeroed memory
 *  0070A153   60               PUSHAD                          ; jichi esp -= 0x20, now, esp[0x28] is text address, esp[0x24] = eax, and esp[0x20] = edx
 *  0070A154   89D7             MOV EDI,EDX                     ; set 007A0BE0 as the target buffer to save text, edx is never modified
 *  0070A156   8B74E4 28        MOV ESI,DWORD PTR SS:[ESP+0x28] ; set source text as target
 *  0070A15A   B9 06000000      MOV ECX,0x6                     ; move for 6 bytes
 *  0070A15F   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
 *  0070A161   61               POPAD   ; finished saving text, now [esp] is old edx, esp[0x4] is old eax, esp[0x8] is old text address
 *  0070A162   8B44E4 08        MOV EAX,DWORD PTR SS:[ESP+0x8]  ; eax = original text address
 *  0070A166   8B40 10          MOV EAX,DWORD PTR DS:[EAX+0x10] ; eax = text[0x10]
 *  0070A169   85C0             TEST EAX,EAX                    ; if end of text,
 *  0070A16B   74 29            JE SHORT .0070A196              ; jump if eax is zero, comeback to hookpoint and ignore it
 *  0070A16D   8B44E4 08        MOV EAX,DWORD PTR SS:[ESP+0x8]  ; otherwise, if eax is not zero
 *  0070A171   8B40 14          MOV EAX,DWORD PTR DS:[EAX+0x14] ; eax = text[0x14]
 *  0070A174   83F8 0F          CMP EAX,0xF                     ; jichi: compare text[0x14] with 0xf
 *  0070A177   75 08            JNZ SHORT .0070A181             ; jump if not zero leaving text not modified, other continue and modify the text
 *  0070A179   8954E4 08        MOV DWORD PTR SS:[ESP+0x8],EDX  ; override esp+8 with edx, i.e. override text address by new text address and do translation
 *  0070A17D   5A               POP EDX
 *  0070A17E   58               POP EAX                         ; jichi: restore edx and eax, now esp is back to normal. [esp] is the new text address
 *  0070A17F  ^EB 9D            JMP SHORT .0070A11E             ; jichi: jump to the top of the hooked place (nop) and do translation before coming back
 *  0070A181   8D42 20          LEA EAX,DWORD PTR DS:[EDX+0x20] ; text is not modified, esp[0x8] is the text address, edx is the modified buffer, eax = buffer[0x20] address
 *  0070A184   60               PUSHAD                          ; jichi: esp[0x28] is now the text address
 *  0070A185   89C7             MOV EDI,EAX                     ; jichi: edx[0x20] is the target
 *  0070A187   8B32             MOV ESI,DWORD PTR DS:[EDX]      ; jichi: edx is the source
 *  0070A189   8B4A 14          MOV ECX,DWORD PTR DS:[EDX+0x14]
 *  0070A18C   83C1 09          ADD ECX,0x9                     ; move for [edx+0x14]+0x9 time
 *  0070A18F   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]    ; jichi: shift text by 0x14 dword ptr
 *  0070A191   61               POPAD                           ; jichi: now esp[0x8] is the text address
 *  0070A192   8902             MOV DWORD PTR DS:[EDX],EAX      ; eax is the new text address (edx+0x20), move the address to beginning of buffer ([edx]), i.e. edx is pointed to zero memory now
 *  0070A194  ^EB E3            JMP SHORT .0070A179             ; come bback to modify the text address
 *  0070A196   5A               POP EDX
 *  0070A197   58               POP EAX
 *  0070A198  ^EB 89            JMP SHORT .0070A123             ; jichi: come back to call
 *  0070A19A   90               NOP
 *  0070A19B   90               NOP
 *  0070A19C   90               NOP
 *  0070A19D   90               NOP
 *  0070A19E   90               NOP
 *  0070A19F   E8 6C9FEBFF      CALL .005C4110
 *  0070A1A4  ^E9 F0C2EAFF      JMP .005B6499
 *  0070A1A9   50               PUSH EAX                        ; jichi: from hookpoint #4
 *  0070A1AA   8B44E4 04        MOV EAX,DWORD PTR SS:[ESP+0x4]  ; jichi: move top of the old stack address to eax
 *  0070A1AE   8378 0C 01       CMP DWORD PTR DS:[EAX+0xC],0x1
 *  0070A1B2   76 31            JBE SHORT .0070A1E5             ; jichi: jump to leave if text[0xc] <= 0x1
 *  0070A1B4   8B87 84020000    MOV EAX,DWORD PTR DS:[EDI+0x284]
 *  0070A1BA   66:8378 FC 46    CMP WORD PTR DS:[EAX-0x4],0x46
 *  0070A1BF   75 24            JNZ SHORT .0070A1E5
 *  0070A1C1   8378 F8 22       CMP DWORD PTR DS:[EAX-0x8],0x22
 *  0070A1C5   74 16            JE SHORT .0070A1DD
 *  0070A1C7   8378 F8 13       CMP DWORD PTR DS:[EAX-0x8],0x13
 *  0070A1CB   75 18            JNZ SHORT .0070A1E5
 *  0070A1CD   90               NOP
 *  0070A1CE   90               NOP
 *  0070A1CF   90               NOP
 *  0070A1D0   90               NOP
 *  0070A1D1   90               NOP
 *  0070A1D2   90               NOP
 *  0070A1D3   90               NOP
 *  0070A1D4   90               NOP
 *  0070A1D5   90               NOP
 *  0070A1D6   90               NOP
 *  0070A1D7   90               NOP
 *  0070A1D8   90               NOP
 *  0070A1D9   90               NOP
 *  0070A1DA   90               NOP
 *  0070A1DB   90               NOP
 *  0070A1DC   90               NOP
 *  0070A1DD   E8 06000000      CALL .0070A1E8
 *  0070A1E2   58               POP EAX
 *  0070A1E3  ^EB B5            JMP SHORT .0070A19A
 *  0070A1E5   58               POP EAX
 *  0070A1E6  ^EB B7            JMP SHORT .0070A19F
 *  0070A1E8   60               PUSHAD
 *  0070A1E9   8B74E4 28        MOV ESI,DWORD PTR SS:[ESP+0x28]
 *  0070A1ED   BF E00B7A00      MOV EDI,.007A0BE0
 *  0070A1F2   897CE4 28        MOV DWORD PTR SS:[ESP+0x28],EDI
 *  0070A1F6   B9 0C000000      MOV ECX,0xC
 *  0070A1FB   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
 *  0070A1FD   61               POPAD
 *  0070A1FE   C3               RETN
 *  0070A1FF   0000             ADD BYTE PTR DS:[EAX],AL
 *  0070A201   0000             ADD BYTE PTR DS:[EAX],AL
 *  0070A203   0000             ADD BYTE PTR DS:[EAX],AL
 *
 *  Modified places:
 *
 *  005E391C   CC               INT3
 *  005E391D   CC               INT3
 *  005E391E   CC               INT3
 *  005E391F   CC               INT3
 *  005E3920   55               PUSH EBP
 *  005E3921   8BEC             MOV EBP,ESP
 *  005E3923   83E4 C0          AND ESP,0xFFFFFFC0
 *  005E3926   83EC 34          SUB ESP,0x34
 *  005E3929   53               PUSH EBX
 *  005E392A   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
 *  005E392D   817B 04 00010000 CMP DWORD PTR DS:[EBX+0x4],0x100
 *  005E3934   56               PUSH ESI
 *  005E3935   57               PUSH EDI
 *  005E3936   8B7D 0C          MOV EDI,DWORD PTR SS:[EBP+0xC]
 *  005E3939   8BF0             MOV ESI,EAX
 *  005E393B   EB 67            JMP SHORT .005E39A4 ; jichi: here modified point#1, change to always jump to 5e39a4, when enabled it will change font size
 *  005E393D   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
 *  005E3941   50               PUSH EAX
 *  005E3942   8D4C24 30        LEA ECX,DWORD PTR SS:[ESP+0x30]
 *
 *  004EEA6E   CC               INT3
 *  004EEA6F   CC               INT3
 *  004EEA70   6A FF            PUSH -0x1
 *  004EEA72   68 E8267000      PUSH .007026E8
 *  004EEA77   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  004EEA7D   50               PUSH EAX
 *  004EEA7E   83EC 20          SUB ESP,0x20
 *  004EEA81   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  004EEA86   33C4             XOR EAX,ESP
 *  004EEA88   894424 1C        MOV DWORD PTR SS:[ESP+0x1C],EAX
 *  004EEA8C   53               PUSH EBX
 *  004EEA8D   55               PUSH EBP
 *  004EEA8E   56               PUSH ESI
 *  004EEA8F   57               PUSH EDI
 *  004EEA90   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  004EEA95   33C4             XOR EAX,ESP
 *  004EEA97   50               PUSH EAX
 *  004EEA98   8D4424 34        LEA EAX,DWORD PTR SS:[ESP+0x34]
 *  004EEA9C   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  004EEAA2   8B4424 44        MOV EAX,DWORD PTR SS:[ESP+0x44]
 *  004EEAA6   8BF1             MOV ESI,ECX
 *  004EEAA8   E8 8346FBFF      CALL .004A3130
 *  004EEAAD   8BE8             MOV EBP,EAX
 *  004EEAAF   33DB             XOR EBX,EBX
 *  004EEAB1   3BEB             CMP EBP,EBX
 *  004EEAB3   75 07            JNZ SHORT .004EEABC
 *  004EEAB5   32C0             XOR AL,AL
 *  004EEAB7   E9 92000000      JMP .004EEB4E
 *  004EEABC   8B06             MOV EAX,DWORD PTR DS:[ESI]
 *  004EEABE   8B10             MOV EDX,DWORD PTR DS:[EAX]
 *  004EEAC0   8BCE             MOV ECX,ESI
 *  004EEAC2   FFD2             CALL EDX
 *  004EEAC4   8BC8             MOV ECX,EAX
 *  004EEAC6   C74424 28 0F0000>MOV DWORD PTR SS:[ESP+0x28],0xF
 *  004EEACE   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
 *  004EEAD2   885C24 14        MOV BYTE PTR SS:[ESP+0x14],BL
 *  004EEAD6   8D71 01          LEA ESI,DWORD PTR DS:[ECX+0x1]
 *  004EEAD9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  004EEAE0   8A11             MOV DL,BYTE PTR DS:[ECX]
 *  004EEAE2   41               INC ECX
 *  004EEAE3   3AD3             CMP DL,BL
 *  004EEAE5  ^75 F9            JNZ SHORT .004EEAE0
 *  004EEAE7   2BCE             SUB ECX,ESI
 *  004EEAE9   50               PUSH EAX
 *  004EEAEA   8BF9             MOV EDI,ECX
 *  004EEAEC   8D7424 18        LEA ESI,DWORD PTR SS:[ESP+0x18]
 *  004EEAF0   E8 CB27F1FF      CALL .004012C0
 *  004EEAF5   8B7C24 48        MOV EDI,DWORD PTR SS:[ESP+0x48]
 *  004EEAF9   895C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EBX
 *  004EEAFD   8B75 3C          MOV ESI,DWORD PTR SS:[EBP+0x3C]
 *  004EEB00   E8 1B4A0100      CALL .00503520
 *  004EEB05   8BF8             MOV EDI,EAX
 *  004EEB07   8DB7 E4000000    LEA ESI,DWORD PTR DS:[EDI+0xE4]
 *  004EEB0D   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  004EEB11   8BD6             MOV EDX,ESI
 *  004EEB13   E8 985CF1FF      CALL .004047B0
 *  004EEB18   BD 10000000      MOV EBP,0x10
 *  004EEB1D   84C0             TEST AL,AL
 *  004EEB1F   75 18            JNZ SHORT .004EEB39
 *  004EEB21   895E 10          MOV DWORD PTR DS:[ESI+0x10],EBX
 *  004EEB24   396E 14          CMP DWORD PTR DS:[ESI+0x14],EBP
 *  004EEB27   72 02            JB SHORT .004EEB2B
 *  004EEB29   8B36             MOV ESI,DWORD PTR DS:[ESI]
 *  004EEB2B   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  004EEB2F   50               PUSH EAX
 *  004EEB30   8BCF             MOV ECX,EDI
 *  004EEB32   881E             MOV BYTE PTR DS:[ESI],BL
 *  004EEB34   E9 13B62100      JMP .0070A14C   ; jichi: here hookpoint#2, name is modified here, scenario and names are here accessed char by char on the top of the stack
 *  004EEB39   396C24 28        CMP DWORD PTR SS:[ESP+0x28],EBP
 *  004EEB3D   72 0D            JB SHORT .004EEB4C
 *  004EEB3F   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  004EEB43   51               PUSH ECX
 *  004EEB44   E8 42DC1900      CALL .0068C78B
 *  004EEB49   83C4 04          ADD ESP,0x4
 *  004EEB4C   B0 01            MOV AL,0x1
 *  004EEB4E   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  004EEB52   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  004EEB59   59               POP ECX
 *  004EEB5A   5F               POP EDI
 *  004EEB5B   5E               POP ESI
 *  004EEB5C   5D               POP EBP
 *  004EEB5D   5B               POP EBX
 *  004EEB5E   8B4C24 1C        MOV ECX,DWORD PTR SS:[ESP+0x1C]
 *  004EEB62   33CC             XOR ECX,ESP
 *  004EEB64   E8 9CD61900      CALL .0068C205
 *  004EEB69   83C4 2C          ADD ESP,0x2C
 *  004EEB6C   C3               RETN
 *  004EEB6D   CC               INT3
 *  004EEB6E   CC               INT3
 *
 *  005C70EE   CC               INT3
 *  005C70EF   CC               INT3
 *  005C70F0   83EC 18          SUB ESP,0x18
 *  005C70F3   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  005C70F8   33C4             XOR EAX,ESP
 *  005C70FA   894424 14        MOV DWORD PTR SS:[ESP+0x14],EAX
 *  005C70FE   53               PUSH EBX
 *  005C70FF   8B5C24 20        MOV EBX,DWORD PTR SS:[ESP+0x20]
 *  005C7103   55               PUSH EBP
 *  005C7104   8B6C24 2C        MOV EBP,DWORD PTR SS:[ESP+0x2C]
 *  005C7108   8B45 1C          MOV EAX,DWORD PTR SS:[EBP+0x1C]
 *  005C710B   56               PUSH ESI
 *  005C710C   8BF2             MOV ESI,EDX
 *  005C710E   57               PUSH EDI
 *  005C710F   8BF9             MOV EDI,ECX
 *  005C7111   897424 10        MOV DWORD PTR SS:[ESP+0x10],ESI
 *  005C7115   83F8 44          CMP EAX,0x44
 *  005C7118   77 7A            JA SHORT .005C7194
 *  005C711A   0FB680 7C735C00  MOVZX EAX,BYTE PTR DS:[EAX+0x5C737C]
 *  005C7121   FF2485 60735C00  JMP DWORD PTR DS:[EAX*4+0x5C7360]
 *  005C7128   8B4B 0C          MOV ECX,DWORD PTR DS:[EBX+0xC]
 *  005C712B   8B4424 30        MOV EAX,DWORD PTR SS:[ESP+0x30]
 *  005C712F   C1E9 02          SHR ECX,0x2
 *  005C7132   3BC1             CMP EAX,ECX
 *  005C7134   73 5E            JNB SHORT .005C7194
 *  005C7136   837B 0C 00       CMP DWORD PTR DS:[EBX+0xC],0x0
 *  005C713A   75 1C            JNZ SHORT .005C7158
 *  005C713C   33DB             XOR EBX,EBX
 *  005C713E   5F               POP EDI
 *  005C713F   893483           MOV DWORD PTR DS:[EBX+EAX*4],ESI
 *  005C7142   5E               POP ESI
 *  005C7143   5D               POP EBP
 *  005C7144   B0 01            MOV AL,0x1
 *  005C7146   5B               POP EBX
 *  005C7147   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  005C714B   33CC             XOR ECX,ESP
 *  005C714D   E8 B3500C00      CALL .0068C205
 *  005C7152   83C4 18          ADD ESP,0x18
 *  005C7155   C2 0C00          RETN 0xC
 *  005C7158   8B5B 08          MOV EBX,DWORD PTR DS:[EBX+0x8]
 *  005C715B   5F               POP EDI
 *  005C715C   893483           MOV DWORD PTR DS:[EBX+EAX*4],ESI
 *  005C715F   5E               POP ESI
 *  005C7160   5D               POP EBP
 *  005C7161   B0 01            MOV AL,0x1
 *  005C7163   5B               POP EBX
 *  005C7164   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  005C7168   33CC             XOR ECX,ESP
 *  005C716A   E8 96500C00      CALL .0068C205
 *  005C716F   83C4 18          ADD ESP,0x18
 *  005C7172   C2 0C00          RETN 0xC
 *  005C7175   F3:0F104424 10   MOVSS XMM0,DWORD PTR SS:[ESP+0x10]
 *  005C717B   51               PUSH ECX
 *  005C717C   8B4C24 34        MOV ECX,DWORD PTR SS:[ESP+0x34]
 *  005C7180   8BC3             MOV EAX,EBX
 *  005C7182   F3:0F110424      MOVSS DWORD PTR SS:[ESP],XMM0
 *  005C7187   E8 14C7FFFF      CALL .005C38A0
 *  005C718C   84C0             TEST AL,AL
 *  005C718E   0F85 B2010000    JNZ .005C7346
 *  005C7194   5F               POP EDI
 *  005C7195   5E               POP ESI
 *  005C7196   5D               POP EBP
 *  005C7197   32C0             XOR AL,AL
 *  005C7199   5B               POP EBX
 *  005C719A   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  005C719E   33CC             XOR ECX,ESP
 *  005C71A0   E8 60500C00      CALL .0068C205
 *  005C71A5   83C4 18          ADD ESP,0x18
 *  005C71A8   C2 0C00          RETN 0xC
 *  005C71AB   8B4C24 30        MOV ECX,DWORD PTR SS:[ESP+0x30]
 *  005C71AF   8D5424 10        LEA EDX,DWORD PTR SS:[ESP+0x10]
 *  005C71B3   52               PUSH EDX
 *  005C71B4   8BC3             MOV EAX,EBX
 *  005C71B6   E8 25C7FFFF      CALL .005C38E0
 *  005C71BB   84C0             TEST AL,AL
 *  005C71BD  ^74 D5            JE SHORT .005C7194
 *  005C71BF   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
 *  005C71C3   8BC7             MOV EAX,EDI
 *  005C71C5   E8 D6F0FFFF      CALL .005C62A0
 *  005C71CA   8BD8             MOV EBX,EAX
 *  005C71CC   8BCE             MOV ECX,ESI
 *  005C71CE   8BC7             MOV EAX,EDI
 *  005C71D0   E8 CBF0FFFF      CALL .005C62A0
 *  005C71D5   85DB             TEST EBX,EBX
 *  005C71D7  ^74 BB            JE SHORT .005C7194
 *  005C71D9   85C0             TEST EAX,EAX
 *  005C71DB  ^74 B7            JE SHORT .005C7194
 *  005C71DD   50               PUSH EAX
 *  005C71DE   8BC3             MOV EAX,EBX
 *  005C71E0   E8 2BCFFFFF      CALL .005C4110  ; original function call
 *  //005C71E0   E9 482F1400      JMP .0070A12D   ; jichi: here hookpoint#3, text is modified here, text in [[esp]+0x8]], length in [esp]+0xc
 *  005C71E5  ^EB A5            JMP SHORT .005C718C
 *  005C71E7   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
 *  005C71EA   8B4F 0C          MOV ECX,DWORD PTR DS:[EDI+0xC]
 *  005C71ED   2BC8             SUB ECX,EAX
 *  005C71EF   C1F9 02          SAR ECX,0x2
 *  005C71F2   3BF1             CMP ESI,ECX
 *  005C71F4  ^73 9E            JNB SHORT .005C7194
 *  005C71F6   8B34B0           MOV ESI,DWORD PTR DS:[EAX+ESI*4]
 *  005C71F9   85F6             TEST ESI,ESI
 *  005C71FB  ^74 97            JE SHORT .005C7194
 *
 *  005B640E   CC               INT3
 *  005B640F   CC               INT3
 *  005B6410   53               PUSH EBX
 *  005B6411   56               PUSH ESI
 *  005B6412   B9 FCFFFFFF      MOV ECX,-0x4
 *  005B6417   57               PUSH EDI
 *  005B6418   8BF8             MOV EDI,EAX
 *  005B641A   018F B0020000    ADD DWORD PTR DS:[EDI+0x2B0],ECX
 *  005B6420   8B87 B0020000    MOV EAX,DWORD PTR DS:[EDI+0x2B0]
 *  005B6426   8B30             MOV ESI,DWORD PTR DS:[EAX]
 *  005B6428   018F B0020000    ADD DWORD PTR DS:[EDI+0x2B0],ECX
 *  005B642E   8B87 B0020000    MOV EAX,DWORD PTR DS:[EDI+0x2B0]
 *  005B6434   8B08             MOV ECX,DWORD PTR DS:[EAX]
 *  005B6436   8B87 E0010000    MOV EAX,DWORD PTR DS:[EDI+0x1E0]
 *  005B643C   2B87 DC010000    SUB EAX,DWORD PTR DS:[EDI+0x1DC]
 *  005B6442   C1F8 02          SAR EAX,0x2
 *  005B6445   3BF0             CMP ESI,EAX
 *  005B6447   73 0D            JNB SHORT .005B6456
 *  005B6449   8B87 DC010000    MOV EAX,DWORD PTR DS:[EDI+0x1DC]
 *  005B644F   8B14B0           MOV EDX,DWORD PTR DS:[EAX+ESI*4]
 *  005B6452   85D2             TEST EDX,EDX
 *  005B6454   75 13            JNZ SHORT .005B6469
 *  005B6456   68 70757200      PUSH .00727570
 *  005B645B   8BCF             MOV ECX,EDI
 *  005B645D   E8 AEC9FFFF      CALL .005B2E10
 *  005B6462   83C4 04          ADD ESP,0x4
 *  005B6465   5F               POP EDI
 *  005B6466   5E               POP ESI
 *  005B6467   5B               POP EBX
 *  005B6468   C3               RETN
 *  005B6469   8B9F E0010000    MOV EBX,DWORD PTR DS:[EDI+0x1E0]
 *  005B646F   2BD8             SUB EBX,EAX
 *  005B6471   C1FB 02          SAR EBX,0x2
 *  005B6474   3BCB             CMP ECX,EBX
 *  005B6476   73 07            JNB SHORT .005B647F
 *  005B6478   8B0488           MOV EAX,DWORD PTR DS:[EAX+ECX*4]
 *  005B647B   85C0             TEST EAX,EAX
 *  005B647D   75 14            JNZ SHORT .005B6493
 *  005B647F   51               PUSH ECX
 *  005B6480   68 A0757200      PUSH .007275A0
 *  005B6485   8BCF             MOV ECX,EDI
 *  005B6487   E8 84C9FFFF      CALL .005B2E10
 *  005B648C   83C4 08          ADD ESP,0x8
 *  005B648F   5F               POP EDI
 *  005B6490   5E               POP ESI
 *  005B6491   5B               POP EBX
 *  005B6492   C3               RETN
 *  005B6493   52               PUSH EDX
 *  005B6494   E8 77DC0000      CALL .005C4110
 *  //005B6494   E9 103D1500      JMP .0070A1A9   ; jichi: here hookpoint#4
 *  005B6499   84C0             TEST AL,AL
 *  005B649B   75 16            JNZ SHORT .005B64B3
 *  005B649D   68 D4757200      PUSH .007275D4
 *  005B64A2   B9 F0757200      MOV ECX,.007275F0                        ; ASCII "S_ASSIGN"
 *  005B64A7   E8 84C8FFFF      CALL .005B2D30
 *  005B64AC   83C4 04          ADD ESP,0x4
 *  005B64AF   5F               POP EDI
 *  005B64B0   5E               POP ESI
 *  005B64B1   5B               POP EBX
 *  005B64B2   C3               RETN
 *  005B64B3   8B8F B0020000    MOV ECX,DWORD PTR DS:[EDI+0x2B0]
 *  005B64B9   8931             MOV DWORD PTR DS:[ECX],ESI
 *  005B64BB   8387 B0020000 04 ADD DWORD PTR DS:[EDI+0x2B0],0x4
 *  005B64C2   5F               POP EDI
 *  005B64C3   5E               POP ESI
 *  005B64C4   5B               POP EBX
 *  005B64C5   C3               RETN
 *  005B64C6   CC               INT3
 *  005B64C7   CC               INT3
 *  005B64C8   CC               INT3
 *
 *  Slightly modified #4 in AliceRunPatch.dll
 *  101B6C10   5B               POP EBX
 *  101B6C11   59               POP ECX
 *  101B6C12   C3               RETN
 *  101B6C13   52               PUSH EDX
 *  101B6C14   8BC1             MOV EAX,ECX
 *  101B6C16   E9 4E7D1600      JMP .1031E969   ; jichi: hook here
 *  101B6C1B   84C0             TEST AL,AL
 *  101B6C1D   75 18            JNZ SHORT .101B6C37
 *  101B6C1F   68 FCB53310      PUSH .1033B5FC
 *  101B6C24   B9 18B63310      MOV ECX,.1033B618                        ; ASCII "S_ASSIGN"
 *  101B6C29   E8 92B8FFFF      CALL .101B24C0
 *  101B6C2E   83C4 04          ADD ESP,0x4
 *  101B6C31   5F               POP EDI
 *  101B6C32   5E               POP ESI
 *  101B6C33   5D               POP EBP
 *  101B6C34   5B               POP EBX
 *  101B6C35   59               POP ECX
 *  101B6C36   C3               RETN
 *  101B6C37   53               PUSH EBX
 *  101B6C38   56               PUSH ESI
 *  101B6C39   E8 E29C0100      CALL .101D0920
 *  101B6C3E   5F               POP EDI
 *  101B6C3F   5E               POP ESI
 *  101B6C40   5D               POP EBP
 *  101B6C41   5B               POP EBX
 *  101B6C42   59               POP ECX
 *  101B6C43   C3               RETN
 *  101B6C44   CC               INT3
 *  101B6C45   CC               INT3
 *  101B6C46   CC               INT3
 *
 *  The function get called to paint string of names for hookpoint #2, text in arg1:
 *  0050B69E   CC               INT3
 *  0050B69F   CC               INT3
 *  0050B6A0   55               PUSH EBP
 *  0050B6A1   8BEC             MOV EBP,ESP
 *  0050B6A3   83E4 F8          AND ESP,0xFFFFFFF8
 *  0050B6A6   6A FF            PUSH -0x1
 *  0050B6A8   68 F8277000      PUSH .007027F8
 *  0050B6AD   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0050B6B3   50               PUSH EAX
 *  0050B6B4   83EC 18          SUB ESP,0x18
 *  0050B6B7   53               PUSH EBX
 *  0050B6B8   56               PUSH ESI
 *  0050B6B9   57               PUSH EDI
 *  0050B6BA   A1 DCC47700      MOV EAX,DWORD PTR DS:[0x77C4DC]
 *  0050B6BF   33C4             XOR EAX,ESP
 *  0050B6C1   50               PUSH EAX
 *  0050B6C2   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
 *  0050B6C6   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0050B6CC   8BF9             MOV EDI,ECX
 *  0050B6CE   57               PUSH EDI
 *  0050B6CF   E8 5CEAFFFF      CALL .0050A130
 *  0050B6D4   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
 *  0050B6D7   6A FF            PUSH -0x1
 *  0050B6D9   33DB             XOR EBX,EBX
 *  0050B6DB   53               PUSH EBX
 *  0050B6DC   8DB7 E4000000    LEA ESI,DWORD PTR DS:[EDI+0xE4]
 *  0050B6E2   50               PUSH EAX
 *  0050B6E3   E8 886BEFFF      CALL .00402270
 *  0050B6E8   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  0050B6EC   895C24 18        MOV DWORD PTR SS:[ESP+0x18],EBX
 *  0050B6F0   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
 *  0050B6F4   56               PUSH ESI
 *  0050B6F5   8D4C24 18        LEA ECX,DWORD PTR SS:[ESP+0x18]
 *  0050B6F9   51               PUSH ECX
 *  0050B6FA   57               PUSH EDI
 *  0050B6FB   895C24 3C        MOV DWORD PTR SS:[ESP+0x3C],EBX
 *  0050B6FF   E8 6C290000      CALL .0050E070
 *  0050B704   8D5424 14        LEA EDX,DWORD PTR SS:[ESP+0x14]
 *  0050B708   8BCF             MOV ECX,EDI
 *  0050B70A   E8 B1010000      CALL .0050B8C0
 *  0050B70F   8B7424 14        MOV ESI,DWORD PTR SS:[ESP+0x14]
 *  0050B713   C687 E0000000 01 MOV BYTE PTR DS:[EDI+0xE0],0x1
 *  0050B71A   3BF3             CMP ESI,EBX
 *  0050B71C   74 14            JE SHORT .0050B732
 *  0050B71E   8B7C24 18        MOV EDI,DWORD PTR SS:[ESP+0x18]
 *  0050B722   8BC6             MOV EAX,ESI
 *  0050B724   E8 7751F0FF      CALL .004108A0
 *  0050B729   56               PUSH ESI
 *  0050B72A   E8 5C101800      CALL .0068C78B
 *  0050B72F   83C4 04          ADD ESP,0x4
 *  0050B732   8B4C24 28        MOV ECX,DWORD PTR SS:[ESP+0x28]
 *  0050B736   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  0050B73D   59               POP ECX
 *  0050B73E   5F               POP EDI
 *  0050B73F   5E               POP ESI
 *  0050B740   5B               POP EBX
 *  0050B741   8BE5             MOV ESP,EBP
 *  0050B743   5D               POP EBP
 *  0050B744   C2 0400          RETN 0x4
 *  0050B747   CC               INT3
 *  0050B748   CC               INT3
 *  0050B749   CC               INT3
 *  0050B74A   CC               INT3
 *  0050B74B   CC               INT3
 *  0050B74C   CC               INT3
 *
 *  Function get called for hookpoint #3, text in [arg1+0x10], length in arg1+0xc, only for scenario, function call is looped
 *  005C410D   CC               INT3
 *  005C410E   CC               INT3
 *  005C410F   CC               INT3
 *  005C4110   53               PUSH EBX
 *  005C4111   8B5C24 08        MOV EBX,DWORD PTR SS:[ESP+0x8]
 *  005C4115   837B 0C 00       CMP DWORD PTR DS:[EBX+0xC],0x0
 *  005C4119   56               PUSH ESI
 *  005C411A   57               PUSH EDI
 *  005C411B   8BF0             MOV ESI,EAX
 *  005C411D   74 07            JE SHORT .005C4126
 *  005C411F   8B43 08          MOV EAX,DWORD PTR DS:[EBX+0x8]
 *  005C4122   85C0             TEST EAX,EAX
 *  005C4124   75 04            JNZ SHORT .005C412A
 *  005C4126   33C0             XOR EAX,EAX
 *  005C4128   EB 0F            JMP SHORT .005C4139
 *  005C412A   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
 *  005C412D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  005C4130   8A08             MOV CL,BYTE PTR DS:[EAX]
 *  005C4132   40               INC EAX
 *  005C4133   84C9             TEST CL,CL
 *  005C4135  ^75 F9            JNZ SHORT .005C4130
 *  005C4137   2BC2             SUB EAX,EDX
 *  005C4139   8D78 01          LEA EDI,DWORD PTR DS:[EAX+0x1]
 *  005C413C   3B7E 0C          CMP EDI,DWORD PTR DS:[ESI+0xC]
 *  005C413F   76 0F            JBE SHORT .005C4150
 *  005C4141   E8 FAF7FFFF      CALL .005C3940
 *  005C4146   84C0             TEST AL,AL
 *  005C4148   75 06            JNZ SHORT .005C4150
 *  005C414A   5F               POP EDI
 *  005C414B   5E               POP ESI
 *  005C414C   5B               POP EBX
 *  005C414D   C2 0400          RETN 0x4
 *  005C4150   837B 0C 00       CMP DWORD PTR DS:[EBX+0xC],0x0
 *  005C4154   75 04            JNZ SHORT .005C415A
 *  005C4156   33C9             XOR ECX,ECX
 *  005C4158   EB 03            JMP SHORT .005C415D
 *  005C415A   8B4B 08          MOV ECX,DWORD PTR DS:[EBX+0x8]
 *  005C415D   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
 *  005C4161   75 15            JNZ SHORT .005C4178
 *  005C4163   57               PUSH EDI
 *  005C4164   33C0             XOR EAX,EAX
 *  005C4166   51               PUSH ECX
 *  005C4167   50               PUSH EAX
 *  005C4168   E8 33400D00      CALL .006981A0
 *  005C416D   83C4 0C          ADD ESP,0xC
 *  005C4170   5F               POP EDI
 *  005C4171   5E               POP ESI
 *  005C4172   B0 01            MOV AL,0x1
 *  005C4174   5B               POP EBX
 *  005C4175   C2 0400          RETN 0x4
 *  005C4178   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
 *  005C417B   57               PUSH EDI
 *  005C417C   51               PUSH ECX
 *  005C417D   50               PUSH EAX
 *  005C417E   E8 1D400D00      CALL .006981A0
 *  005C4183   83C4 0C          ADD ESP,0xC
 *  005C4186   5F               POP EDI
 *  005C4187   5E               POP ESI
 *  005C4188   B0 01            MOV AL,0x1
 *  005C418A   5B               POP EBX
 *  005C418B   C2 0400          RETN 0x4
 *  005C418E   CC               INT3
 */
static bool InsertSystem43NewHook(ULONG startAddress, ULONG stopAddress, LPCSTR hookName)
{
  const BYTE bytes[] = {
      0xe8, XX4,              // 004eeb34   e8 67cb0100      call .0050b6a0  ; jichi: hook here, text on the top of the stack
      0x39, 0x6c, 0x24, 0x28, // 004eeb39   396c24 28        cmp dword ptr ss:[esp+0x28],ebp
      0x72, 0x0d,             // 004eeb3d   72 0d            jb short .004eeb4c
      0x8b, 0x4c, 0x24, 0x14, // 004eeb3f   8b4c24 14        mov ecx,dword ptr ss:[esp+0x14]
      0x51,                   // 004eeb43   51               push ecx
      0xe8                    //, XX4,           // 004eeb44   e8 42dc1900      call .0068c78b
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  // GROWL_DWORD(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = NO_CONTEXT | USING_STRING | USING_SPLIT | SPLIT_INDIRECT;
  // hp.type = NO_CONTEXT|USING_STRING|FIXING_SPLIT;
  hp.split_index = 0x10; // use [[esp]+0x10] to differentiate name and thread

  return NewHook(hp, hookName);
}
void System43aFilter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);

  CharReplacer(buffer, '\n', ' ');

  if (cpp_strnstr(text, "${", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("${"), TEXTANDLEN("}"));
  }
}

bool InsertSystem43aHook()
{

  /*
   * Sample games:
   * https://vndb.org/r84067
   */
  const BYTE bytes[] = {
      0xC7, 0x46, 0x10, XX4,  // mov [esi+10],00000000
      0x72, 0x02,             // jb dohnadohna.exe+1BFA7E
      0x8B, 0x36,             // mov esi,[esi]
      0x8B, 0x4C, 0x24, 0x14, // mov ecx,[esp+14]
      0x57,                   // push edi
      0xC6, 0x06, 0x00        // mov byte ptr [esi],00   << hook here
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + sizeof(bytes) - 3;
  hp.offset = regoffset(edx);
  hp.split = regoffset(esp);
  hp.type = NO_CONTEXT | USING_STRING | USING_SPLIT;
  hp.filter_fun = System43aFilter;
  return NewHook(hp, "System43new");
}

bool InsertSystem43bHook()
{
  /*
   * Sample games:
   * https://vndb.org/v10732
   */
  const BYTE bytes[] = {
      0x8B, 0xCE,             // mov ecx,esi            << hook here
      0xE8, XX4,              // call Oyakorankan.exe+13D890
      0x8B, 0x43, 0x04,       // mov eax,[ebx+04]
      0x8D, 0x4C, 0x24, 0x10, // lea ecx,[esp+10]
      0x3B, 0xC8,             // cmp ecx,eax
      0x73, 0x64              // jae Oyakorankan.exe+1403B2
  };

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp = {};
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.split = stackoffset(12);
  hp.type = USING_STRING | USING_SPLIT;
  NewHook(hp, "System43b");
  return true;
}
bool InsertSystem43Hook()
{
  if (InsertSystem43aHook() || InsertSystem43bHook())
    return true;
  // bool patched = Util::CheckFile(L"AliceRunPatch.dll");
  bool patched = ::GetModuleHandleA("AliceRunPatch.dll");
  // Insert new hook first
  bool ok = InsertSystem43OldHook(processStartAddress, processStopAddress, patched ? "AliceRunPatch43" : "System43");
  ok = InsertSystem43NewHook(processStartAddress, processStopAddress, "System43+") || ok;
  return ok;
}

namespace
{ // unnamed

  struct TextArgument // first argument of the scenario hook
  {
    ULONG *unknown[2];
    LPCSTR text;
    int size; // text data size including '\0', length = size - 1
    int capacity;
    ULONG split;

    bool isValid() const
    {
      return size <= capacity && size >= 4 && text && ::strlen(text) + 1 == size // skip translating single text
                                                                                 //&& !Util::allAscii(text)
             && (UINT8)text[0] > 127 && (UINT8)text[size - 3] > 127              // skip text beginning / ending with ascii
             && !::strstr(text, "\x81\x5e");                                     // "／"
    }
  };

  namespace ScenarioHook
  {

    namespace Private
    {
      bool isOtherText(LPCSTR text)
      {
        static const char *s[] = {
            "\x82\xa2\x82\xa2\x82\xa6" /* いいえ */
            ,
            "\x82\xcd\x82\xa2" /* はい */
        };
        for (int i = 0; i < sizeof(s) / sizeof(*s); i++)
          if (::strcmp(text, s[i]) == 0)
            return true;
        return false;
      }

      TextArgument *arg_,
          argValue_;
      /**
       *  Sample game: Rance03
       *
       *  Caller that related to load/save, which is the only caller get kept:
       *  005C68A7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
       *  005C68AD   8B1CA8           MOV EBX,DWORD PTR DS:[EAX+EBP*4]
       *  005C68B0   85DB             TEST EBX,EBX
       *  005C68B2   74 63            JE SHORT Rance03T.005C6917
       *  005C68B4   8B86 78010000    MOV EAX,DWORD PTR DS:[ESI+0x178]
       *  005C68BA   2B86 74010000    SUB EAX,DWORD PTR DS:[ESI+0x174]
       *  005C68C0   C1F8 02          SAR EAX,0x2
       *  005C68C3   3BD0             CMP EDX,EAX
       *  005C68C5   73 3C            JNB SHORT Rance03T.005C6903
       *  005C68C7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
       *  005C68CD   8B0C90           MOV ECX,DWORD PTR DS:[EAX+EDX*4]
       *  005C68D0   85C9             TEST ECX,ECX
       *  005C68D2   74 2F            JE SHORT Rance03T.005C6903
       *  005C68D4   53               PUSH EBX
       *  005C68D5  -E9 26976B09      JMP 09C80000  ; jichi: called
       *  005C68DA   84C0             TEST AL,AL
       *  005C68DC   75 18            JNZ SHORT Rance03T.005C68F6
       *  005C68DE   68 94726E00      PUSH Rance03T.006E7294
       *  005C68E3   68 00736E00      PUSH Rance03T.006E7300                   ; ASCII "S_ASSIGN"
       *  005C68E8   56               PUSH ESI
       *  005C68E9   E8 12BBFFFF      CALL Rance03T.005C2400
       *  005C68EE   83C4 0C          ADD ESP,0xC
       *  005C68F1   5F               POP EDI
       *  005C68F2   5E               POP ESI
       *
       *  Caller of the scenario thread:
       *
       *  005D6F80  ^74 BE            JE SHORT Rance03T.005D6F40
       *  005D6F82   85C0             TEST EAX,EAX
       *  005D6F84  ^74 BA            JE SHORT Rance03T.005D6F40
       *  005D6F86   50               PUSH EAX
       *  005D6F87   8BCF             MOV ECX,EDI
       *  005D6F89  -E9 72907009      JMP 09CE0000  ; jichi: called here
       *  005D6F8E  ^EB A8            JMP SHORT Rance03T.005D6F38
       *  005D6F90   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
       *  005D6F93   2B46 08          SUB EAX,DWORD PTR DS:[ESI+0x8]
       *  005D6F96   C1F8 02          SAR EAX,0x2
       *  005D6F99   3BD8             CMP EBX,EAX
       *  005D6F9B  ^73 A3            JNB SHORT Rance03T.005D6F40
       *  005D6F9D   8B46 08          MOV EAX,DWORD PTR DS:[ESI+0x8]
       *  005D6FA0   8B1C98           MOV EBX,DWORD PTR DS:[EAX+EBX*4]
       */
      std::unordered_set<uint64_t> hashes_;
      void hookafter2(hook_context *s, TextBuffer buffer)
      {
        auto newData = buffer.strA();
        static std::string data_;
        data_ = newData;
        auto arg = (TextArgument *)s->stack[0]; // arg1
        arg_ = arg;
        argValue_ = *arg;

        arg->text = data_.c_str();
        arg->size = data_.size() + 1;
        arg->capacity = arg->size;

        hashes_.insert(simplehash::hashCharArray(arg->text));
      }
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
      {
        static std::string data_; // persistent storage, which makes this function not thread-safe

        // auto split = s->stack[5]; // parent function return address
        // auto split = s->stack[10]; // parent's parent function return address
        // auto split = *(DWORD *)(s->ecx + 0x10);
        auto split = *(DWORD *)(s->ecx + 0x34);
        // auto split = *(DWORD *)(s->ecx + 0x48);
        //  005C68DA   84C0             TEST AL,AL
        // if (*(WORD *)retaddr == 0xc084) // otherwise system text will be translated
        //   return true;
        // if (*(WORD *)retaddr != 0xc084) // only translate one caller
        //   return true;
        //  005D6F8E  ^EB A8            JMP SHORT Rance03T.005D6F38
        // if (*(WORD *)retaddr != 0xa8eb) // this function has 7 callers, and only one is kept
        //   return true;
        if (split > 0xff || split && split < 0xf)
          return;
        auto arg = (TextArgument *)s->stack[0]; // arg1
        if (!arg || !arg->isValid() || hashes_.find(simplehash::hashCharArray(arg->text)) != hashes_.end())
          return;
        if (arg->size < 0xf && split > 0 && !isOtherText(arg->text))
          return;
        // auto sig = Engine::hashThreadSignature(role, split);
        // auto role = Engine::OtherRole;
        *role = Engine::OtherRole;
        if (!isOtherText(arg->text))
        {
          if (split == 0 && arg->size <= 0x10)
            *role = Engine::NameRole;
          else if (split >= 2 && split <= 0x14 && split != 3 && split != 0xb || split == 0x22)
            *role = Engine::ScenarioRole;
        }
        buffer->from(arg->text);
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
     *  Sample game: Rance03
     *
     *  Function that is similar to memcpy, found by debugging where game text get modified:
     *
     *  0069D84F   CC               INT3
     *  0069D850   57               PUSH EDI
     *  0069D851   56               PUSH ESI
     *  0069D852   8B7424 10        MOV ESI,DWORD PTR SS:[ESP+0x10]
     *  0069D856   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
     *  0069D85A   8B7C24 0C        MOV EDI,DWORD PTR SS:[ESP+0xC]
     *  0069D85E   8BC1             MOV EAX,ECX
     *  0069D860   8BD1             MOV EDX,ECX
     *  0069D862   03C6             ADD EAX,ESI
     *  0069D864   3BFE             CMP EDI,ESI
     *  0069D866   76 08            JBE SHORT Rance03T.0069D870
     *  0069D868   3BF8             CMP EDI,EAX
     *  0069D86A   0F82 68030000    JB Rance03T.0069DBD8
     *  0069D870   0FBA25 5CC97500 >BT DWORD PTR DS:[0x75C95C],0x1
     *  0069D878   73 07            JNB SHORT Rance03T.0069D881
     *  0069D87A   F3:A4            REP MOVS BYTE PTR ES:[EDI],BYTE PTR DS:[ESI]
     *  0069D87C   E9 17030000      JMP Rance03T.0069DB98
     *  0069D881   81F9 80000000    CMP ECX,0x80
     *  0069D887   0F82 CE010000    JB Rance03T.0069DA5B
     *  0069D88D   8BC7             MOV EAX,EDI
     *  0069D88F   33C6             XOR EAX,ESI
     *  0069D891   A9 0F000000      TEST EAX,0xF
     *  0069D896   75 0E            JNZ SHORT Rance03T.0069D8A6
     *  0069D898   0FBA25 10A47400 >BT DWORD PTR DS:[0x74A410],0x1
     *  0069D8A0   0F82 DA040000    JB Rance03T.0069DD80
     *  0069D8A6   0FBA25 5CC97500 >BT DWORD PTR DS:[0x75C95C],0x0
     *  0069D8AE   0F83 A7010000    JNB Rance03T.0069DA5B
     *  0069D8B4   F7C7 03000000    TEST EDI,0x3
     *  0069D8BA   0F85 B8010000    JNZ Rance03T.0069DA78
     *  0069D8C0   F7C6 03000000    TEST ESI,0x3
     *  0069D8C6   0F85 97010000    JNZ Rance03T.0069DA63
     *  0069D8CC   0FBAE7 02        BT EDI,0x2
     *  0069D8D0   73 0D            JNB SHORT Rance03T.0069D8DF
     *  0069D8D2   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  0069D8D4   83E9 04          SUB ECX,0x4
     *  0069D8D7   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
     *  0069D8DA   8907             MOV DWORD PTR DS:[EDI],EAX
     *  0069D8DC   8D7F 04          LEA EDI,DWORD PTR DS:[EDI+0x4]
     *  0069D8DF   0FBAE7 03        BT EDI,0x3
     *  0069D8E3   73 11            JNB SHORT Rance03T.0069D8F6
     *  0069D8E5   F3:              PREFIX REP:                                   ; Superfluous prefix
     *  0069D8E6   0F7E0E           MOVD DWORD PTR DS:[ESI],MM1
     *  0069D8E9   83E9 08          SUB ECX,0x8
     *  0069D8EC   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
     *  0069D8EF   66:0FD6          ???                                           ; Unknown command
     *  0069D8F2  -0F8D 7F08F7C6    JGE C760E177
     *  0069D8F8   07               POP ES                                        ; Modification of segment register
     *  0069D8F9   0000             ADD BYTE PTR DS:[EAX],AL
     *  0069D8FB   007463 0F        ADD BYTE PTR DS:[EBX+0xF],DH
     *  0069D8FF   BA E6030F83      MOV EDX,0x830F03E6
     *  0069D904   B2 00            MOV DL,0x0
     *  0069D906   0000             ADD BYTE PTR DS:[EAX],AL
     *  0069D908   66:0F6F4E F4     MOVQ MM1,QWORD PTR DS:[ESI-0xC]
     *  0069D90D   8D76 F4          LEA ESI,DWORD PTR DS:[ESI-0xC]
     *  0069D910   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
     *  0069D915   83E9 30          SUB ECX,0x30
     *  0069D918   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
     *  0069D91D   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
     *  0069D922   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
     *  0069D925   83F9 30          CMP ECX,0x30
     *  0069D928   66:0F6FD3        MOVQ MM2,MM3
     *  0069D92C   66:0F3A          ???                                           ; Unknown command
     *  0069D92F   0FD90C66         PSUBUSW MM1,QWORD PTR DS:[ESI]
     *  0069D933   0F7F1F           MOVQ QWORD PTR DS:[EDI],MM3
     *  0069D936   66:0F6FE0        MOVQ MM4,MM0
     *  0069D93A   66:0F3A          ???                                           ; Unknown command
     *  0069D93D   0FC20C66 0F      CMPPS XMM1,DQWORD PTR DS:[ESI],0xF
     *  0069D942   7F 47            JG SHORT Rance03T.0069D98B
     *  0069D944   1066 0F          ADC BYTE PTR DS:[ESI+0xF],AH
     *  0069D947   6F               OUTS DX,DWORD PTR ES:[EDI]                    ; I/O command
     *  0069D948   CD 66            INT 0x66
     *  0069D94A   0F3A             ???                                           ; Unknown command
     *  0069D94C   0FEC0C66         PADDSB MM1,QWORD PTR DS:[ESI]
     *  0069D950   0F7F6F 20        MOVQ QWORD PTR DS:[EDI+0x20],MM5
     *  0069D954   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
     *  0069D957  ^7D B7            JGE SHORT Rance03T.0069D910
     *  0069D959   8D76 0C          LEA ESI,DWORD PTR DS:[ESI+0xC]
     *  0069D95C   E9 AF000000      JMP Rance03T.0069DA10
     *  0069D961   66:0F6F4E F8     MOVQ MM1,QWORD PTR DS:[ESI-0x8]
     *  0069D966   8D76 F8          LEA ESI,DWORD PTR DS:[ESI-0x8]
     *  0069D969   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
     *  0069D96C   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
     *  0069D971   83E9 30          SUB ECX,0x30
     *  0069D974   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
     *  0069D979   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
     *  0069D97E   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
     *  0069D981   83F9 30          CMP ECX,0x30
     *  0069D984   66:0F6FD3        MOVQ MM2,MM3
     *  0069D988   66:0F3A          ???                                           ; Unknown command
     *  0069D98B   0FD908           PSUBUSW MM1,QWORD PTR DS:[EAX]
     *  0069D98E   66:0F7F1F        MOVQ QWORD PTR DS:[EDI],MM3
     *  0069D992   66:0F6FE0        MOVQ MM4,MM0
     *  0069D996   66:0F3A          ???                                           ; Unknown command
     *  0069D999   0FC208 66        CMPPS XMM1,DQWORD PTR DS:[EAX],0x66
     *  0069D99D   0F7F47 10        MOVQ QWORD PTR DS:[EDI+0x10],MM0
     *  0069D9A1   66:0F6FCD        MOVQ MM1,MM5
     *  0069D9A5   66:0F3A          ???                                           ; Unknown command
     *  0069D9A8   0FEC08           PADDSB MM1,QWORD PTR DS:[EAX]
     *  0069D9AB   66:0F7F6F 20     MOVQ QWORD PTR DS:[EDI+0x20],MM5
     *  0069D9B0   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
     *  0069D9B3  ^7D B7            JGE SHORT Rance03T.0069D96C
     *  0069D9B5   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
     *  0069D9B8   EB 56            JMP SHORT Rance03T.0069DA10
     *  0069D9BA   66:0F6F4E FC     MOVQ MM1,QWORD PTR DS:[ESI-0x4]
     *  0069D9BF   8D76 FC          LEA ESI,DWORD PTR DS:[ESI-0x4]
     *  0069D9C2   8BFF             MOV EDI,EDI
     *  0069D9C4   66:0F6F5E 10     MOVQ MM3,QWORD PTR DS:[ESI+0x10]
     *  0069D9C9   83E9 30          SUB ECX,0x30
     *  0069D9CC   66:0F6F46 20     MOVQ MM0,QWORD PTR DS:[ESI+0x20]
     *  0069D9D1   66:0F6F6E 30     MOVQ MM5,QWORD PTR DS:[ESI+0x30]
     *  0069D9D6   8D76 30          LEA ESI,DWORD PTR DS:[ESI+0x30]
     *  0069D9D9   83F9 30          CMP ECX,0x30
     *  0069D9DC   66:0F6FD3        MOVQ MM2,MM3
     *  0069D9E0   66:0F3A          ???                                           ; Unknown command
     *  0069D9E3   0FD90466         PSUBUSW MM0,QWORD PTR DS:[ESI]
     *  0069D9E7   0F7F1F           MOVQ QWORD PTR DS:[EDI],MM3
     *  0069D9EA   66:0F6FE0        MOVQ MM4,MM0
     *  0069D9EE   66:0F3A          ???                                           ; Unknown command
     *  0069D9F1   0FC20466 0F      CMPPS XMM0,DQWORD PTR DS:[ESI],0xF
     *  0069D9F6   7F 47            JG SHORT Rance03T.0069DA3F
     *  0069D9F8   1066 0F          ADC BYTE PTR DS:[ESI+0xF],AH
     *  0069D9FB   6F               OUTS DX,DWORD PTR ES:[EDI]                    ; I/O command
     *  0069D9FC   CD 66            INT 0x66
     *  0069D9FE   0F3A             ???                                           ; Unknown command
     *  0069DA00   0FEC0466         PADDSB MM0,QWORD PTR DS:[ESI]
     *  0069DA04   0F7F6F 20        MOVQ QWORD PTR DS:[EDI+0x20],MM5
     *  0069DA08   8D7F 30          LEA EDI,DWORD PTR DS:[EDI+0x30]
     *  0069DA0B  ^7D B7            JGE SHORT Rance03T.0069D9C4
     *  0069DA0D   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
     *  0069DA10   83F9 10          CMP ECX,0x10
     *  0069DA13   7C 13            JL SHORT Rance03T.0069DA28
     *  0069DA15   F3:              PREFIX REP:                                   ; Superfluous prefix
     *  0069DA16   0F6F0E           MOVQ MM1,QWORD PTR DS:[ESI]
     *  0069DA19   83E9 10          SUB ECX,0x10
     *  0069DA1C   8D76 10          LEA ESI,DWORD PTR DS:[ESI+0x10]
     *  0069DA1F   66:0F7F0F        MOVQ QWORD PTR DS:[EDI],MM1
     *  0069DA23   8D7F 10          LEA EDI,DWORD PTR DS:[EDI+0x10]
     *  0069DA26  ^EB E8            JMP SHORT Rance03T.0069DA10
     *  0069DA28   0FBAE1 02        BT ECX,0x2
     *  0069DA2C   73 0D            JNB SHORT Rance03T.0069DA3B
     *  0069DA2E   8B06             MOV EAX,DWORD PTR DS:[ESI]
     *  0069DA30   83E9 04          SUB ECX,0x4
     *  0069DA33   8D76 04          LEA ESI,DWORD PTR DS:[ESI+0x4]
     *  0069DA36   8907             MOV DWORD PTR DS:[EDI],EAX
     *  0069DA38   8D7F 04          LEA EDI,DWORD PTR DS:[EDI+0x4]
     *  0069DA3B   0FBAE1 03        BT ECX,0x3
     *  0069DA3F   73 11            JNB SHORT Rance03T.0069DA52
     *  0069DA41   F3:              PREFIX REP:                                   ; Superfluous prefix
     *  0069DA42   0F7E0E           MOVD DWORD PTR DS:[ESI],MM1
     *  0069DA45   83E9 08          SUB ECX,0x8
     *  0069DA48   8D76 08          LEA ESI,DWORD PTR DS:[ESI+0x8]
     *  0069DA4B   66:0FD6          ???                                           ; Unknown command
     *  0069DA4E  -0F8D 7F088B04    JGE 04F4E2D3
     *  0069DA54   8D88 DB6900FF    LEA ECX,DWORD PTR DS:[EAX+0xFF0069DB]
     *  0069DA5A  ^E0 F7            LOOPDNE SHORT Rance03T.0069DA53
     *  0069DA5C   C703 00000075    MOV DWORD PTR DS:[EBX],0x75000000
     *  0069DA62   15 C1E90283      ADC EAX,0x8302E9C1
     *  0069DA67   E2 03            LOOPD SHORT Rance03T.0069DA6C
     *  0069DA69   83F9 08          CMP ECX,0x8
     *  0069DA6C   72 2A            JB SHORT Rance03T.0069DA98
     *  0069DA6E   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI>
     *  0069DA70   FF2495 88DB6900  JMP DWORD PTR DS:[EDX*4+0x69DB88]
     *  0069DA77   90               NOP
     *
     *  0012F810   0B4D3F30
     *  0012F814   06128970
     *  0012F818   005D3E12  RETURN to Rance03T.005D3E12 from Rance03T.0069D850
     *  0012F81C   06160B98	; jichi: target text
     *  0012F820   07F8CA80 ; jichi: source text
     *  0012F824   00000017 ; jichi: size including \0
     *  0012F828   00384460
     *  0012F82C   00384240
     *  0012F830   0B4D3F30
     *  0012F834   005C68DA  RETURN to Rance03T.005C68DA from Rance03T.005D3D90
     *  0012F838   0B4D3F30
     *  0012F83C   0012FAA8
     *  0012F840   00384240
     *  0012F844   0012F85C
     *  0012F848   0012FF18
     *  0012F84C   005C1693  RETURN to Rance03T.005C1693 from Rance03T.005C6870
     *  0012F850   0012FAA8
     *  0012F854   00384240
     *  0012F858   0000000F
     *  0012F85C  /0012FF3C
     *
     *  Actual hooked function:
     *  005D3D8B   CC               INT3
     *  005D3D8C   CC               INT3
     *  005D3D8D   CC               INT3
     *  005D3D8E   CC               INT3
     *  005D3D8F   CC               INT3
     *  005D3D90   53               PUSH EBX
     *  005D3D91   56               PUSH ESI
     *  005D3D92   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
     *  005D3D96   57               PUSH EDI
     *  005D3D97   8BF9             MOV EDI,ECX
     *  005D3D99   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
     *  005D3D9D   74 1C            JE SHORT Rance03T.005D3DBB
     *  005D3D9F   8B56 08          MOV EDX,DWORD PTR DS:[ESI+0x8]
     *  005D3DA2   85D2             TEST EDX,EDX
     *  005D3DA4   74 15            JE SHORT Rance03T.005D3DBB
     *  005D3DA6   8D4A 01          LEA ECX,DWORD PTR DS:[EDX+0x1]
     *  005D3DA9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
     *  005D3DB0   8A02             MOV AL,BYTE PTR DS:[EDX]
     *  005D3DB2   42               INC EDX
     *  005D3DB3   84C0             TEST AL,AL
     *  005D3DB5  ^75 F9            JNZ SHORT Rance03T.005D3DB0
     *  005D3DB7   2BD1             SUB EDX,ECX
     *  005D3DB9   EB 02            JMP SHORT Rance03T.005D3DBD
     *  005D3DBB   33D2             XOR EDX,EDX
     *  005D3DBD   8D5A 01          LEA EBX,DWORD PTR DS:[EDX+0x1]
     *  005D3DC0   3B5F 0C          CMP EBX,DWORD PTR DS:[EDI+0xC]
     *  005D3DC3   76 1A            JBE SHORT Rance03T.005D3DDF
     *  005D3DC5   53               PUSH EBX
     *  005D3DC6   8D4F 04          LEA ECX,DWORD PTR DS:[EDI+0x4]
     *  005D3DC9   C747 0C 00000000 MOV DWORD PTR DS:[EDI+0xC],0x0
     *  005D3DD0   E8 DB700700      CALL Rance03T.0064AEB0
     *  005D3DD5   84C0             TEST AL,AL
     *  005D3DD7   75 06            JNZ SHORT Rance03T.005D3DDF
     *  005D3DD9   5F               POP EDI
     *  005D3DDA   5E               POP ESI
     *  005D3DDB   5B               POP EBX
     *  005D3DDC   C2 0400          RETN 0x4
     *  005D3DDF   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
     *  005D3DE3   75 04            JNZ SHORT Rance03T.005D3DE9
     *  005D3DE5   33C9             XOR ECX,ECX
     *  005D3DE7   EB 03            JMP SHORT Rance03T.005D3DEC
     *  005D3DE9   8B4E 08          MOV ECX,DWORD PTR DS:[ESI+0x8]
     *  005D3DEC   837F 0C 00       CMP DWORD PTR DS:[EDI+0xC],0x0
     *  005D3DF0   75 15            JNZ SHORT Rance03T.005D3E07
     *  005D3DF2   53               PUSH EBX
     *  005D3DF3   33C0             XOR EAX,EAX
     *  005D3DF5   51               PUSH ECX
     *  005D3DF6   50               PUSH EAX
     *  005D3DF7   E8 549A0C00      CALL Rance03T.0069D850
     *  005D3DFC   83C4 0C          ADD ESP,0xC
     *  005D3DFF   B0 01            MOV AL,0x1
     *  005D3E01   5F               POP EDI
     *  005D3E02   5E               POP ESI
     *  005D3E03   5B               POP EBX
     *  005D3E04   C2 0400          RETN 0x4
     *  005D3E07   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
     *  005D3E0A   53               PUSH EBX
     *  005D3E0B   51               PUSH ECX
     *  005D3E0C   50               PUSH EAX
     *  005D3E0D  -E9 EEC1A201      JMP 02000000    ; jichi: called here
     *  005D3E12   83C4 0C          ADD ESP,0xC
     *  005D3E15   B0 01            MOV AL,0x1
     *  005D3E17   5F               POP EDI
     *  005D3E18   5E               POP ESI
     *  005D3E19   5B               POP EBX
     *  005D3E1A   C2 0400          RETN 0x4
     *  005D3E1D   CC               INT3
     *  005D3E1E   CC               INT3
     *  005D3E1F   CC               INT3
     *
     *  Arg1 of this function:
     *  07B743F8  90 7A 70 00 F4 87 70 00 70 0E 27 08 1B 00 00 00  諏p.p.p'...
     *  07B74408  20 00 00 00 02 00 00 00 01 00 00 00 CC 7F 2D 00   .........ﾌ-.
     *  07B74418  B3 52 41 00 FF FF FF FF EC 87 70 00 10 E3 1D 08  ｳRA.・p.・
     *
     *  Caller that preserved:
     *  005C68A7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
     *  005C68AD   8B1CA8           MOV EBX,DWORD PTR DS:[EAX+EBP*4]
     *  005C68B0   85DB             TEST EBX,EBX
     *  005C68B2   74 63            JE SHORT Rance03T.005C6917
     *  005C68B4   8B86 78010000    MOV EAX,DWORD PTR DS:[ESI+0x178]
     *  005C68BA   2B86 74010000    SUB EAX,DWORD PTR DS:[ESI+0x174]
     *  005C68C0   C1F8 02          SAR EAX,0x2
     *  005C68C3   3BD0             CMP EDX,EAX
     *  005C68C5   73 3C            JNB SHORT Rance03T.005C6903
     *  005C68C7   8B86 74010000    MOV EAX,DWORD PTR DS:[ESI+0x174]
     *  005C68CD   8B0C90           MOV ECX,DWORD PTR DS:[EAX+EDX*4]
     *  005C68D0   85C9             TEST ECX,ECX
     *  005C68D2   74 2F            JE SHORT Rance03T.005C6903
     *  005C68D4   53               PUSH EBX
     *  005C68D5   E8 B6D40000      CALL Rance03T.005D3D90 ; jichi: called
     *  005C68DA   84C0             TEST AL,AL      ; jichi: retaddr
     *  005C68DC   75 18            JNZ SHORT Rance03T.005C68F6
     *  005C68DE   68 94726E00      PUSH Rance03T.006E7294
     *  005C68E3   68 00736E00      PUSH Rance03T.006E7300                   ; ASCII "S_ASSIGN"
     *  005C68E8   56               PUSH ESI
     *  005C68E9   E8 12BBFFFF      CALL Rance03T.005C2400
     *  005C68EE   83C4 0C          ADD ESP,0xC
     *  005C68F1   5F               POP EDI
     *  005C68F2   5E               POP ESI
     */
    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x53,                                     // 005D3D90   53               PUSH EBX
          0x56,                                     // 005D3D91   56               PUSH ESI
          0x8B, 0x74, 0x24, 0x0C,                   // 005D3D92   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
          0x57,                                     // 005D3D96   57               PUSH EDI
          0x8B, 0xF9,                               // 005D3D97   8BF9             MOV EDI,ECX
          0x83, 0x7E, 0x0C, 0x00,                   // 005D3D99   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
          0x74, 0x1C,                               // 005D3D9D   74 1C            JE SHORT Rance03T.005D3DBB
          0x8B, 0x56, 0x08,                         // 005D3D9F   8B56 08          MOV EDX,DWORD PTR DS:[ESI+0x8]
          0x85, 0xD2,                               // 005D3DA2   85D2             TEST EDX,EDX
          0x74, 0x15,                               // 005D3DA4   74 15            JE SHORT Rance03T.005D3DBB
          0x8D, 0x4A, 0x01,                         // 005D3DA6   8D4A 01          LEA ECX,DWORD PTR DS:[EDX+0x1]
          0x8D, 0xA4, 0x24, 0x00, 0x00, 0x00, 0x00, // 005D3DA9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
          0x8A, 0x02,                               // 005D3DB0   8A02             MOV AL,BYTE PTR DS:[EDX]
          0x42,                                     // 005D3DB2   42               INC EDX
          0x84, 0xC0                                // 005D3DB3   84C0             TEST AL,AL
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      // addr = MemDbg::findEnclosingAlignedFunction(addr);
      // if (!addr)
      //   return false;
      // addr = 0x005D3D90;
      // return winhook::hook_before(addr, Private::hookBefore);

      int count = 0;
      auto fun = [&count](ULONG addr) -> bool
      {
        auto retaddr = addr + 5;
        // 005C68DA   84C0             TEST AL,AL
        if (*(WORD *)retaddr == 0xc084)
          // auto before = std::bind(Private::hookBefore, addr + 5, std::placeholders::_1);
          count += 1;
        HookParam hp;
        hp.address = addr;
        hp.type = EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
        hp.text_fun = Private::hookBefore;
        hp.embed_fun = Private::hookafter2;
        auto succ = NewHook(hp, "EmbedSysmtem44");
        hp.address = addr + 5;
        hp.text_fun = Private::hookAfter;
        succ |= NewHook(hp, "EmbedSysmtem44");
        return succ; // replace all functions
      };
      MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);

      return count;
    }

  } // namespace ScenarioHook

} // unnamed namespace

bool attachSystem44(ULONG startAddress, ULONG stopAddress)
{
  return ScenarioHook::attach(startAddress, stopAddress);
}
namespace
{ // unnamed

  // - Search -

  ULONG searchScenarioAddress(ULONG startAddress, ULONG stopAddress)
  {
    const uint8_t bytes[] = {
        0xe8, XX4,        // 005c71e0   e8 2bcfffff      call .005c4110  ; original function call
        0xeb, 0xa5,       // 005c71e5  ^eb a5            jmp short .005c718c
        0x8b, 0x47, 0x08, // 005c71e7   8b47 08          mov eax,dword ptr ds:[edi+0x8]
        0x8b, 0x4f, 0x0c  // 005c71ea   8b4f 0c          mov ecx,dword ptr ds:[edi+0xc]
    };
    return MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  }

  ULONG searchNameAddress(ULONG startAddress, ULONG stopAddress)
  {
    const uint8_t bytes[] = {
        0xe8, XX4,              // 004eeb34   e8 67cb0100      call .0050b6a0  ; jichi: hook here
        0x39, 0x6c, 0x24, 0x28, // 004eeb39   396c24 28        cmp dword ptr ss:[esp+0x28],ebp
        0x72, 0x0d,             // 004eeb3d   72 0d            jb short .004eeb4c
        0x8b, 0x4c, 0x24, 0x14, // 004eeb3f   8b4c24 14        mov ecx,dword ptr ss:[esp+0x14]
        0x51,                   // 004eeb43   51               push ecx
        0xe8                    //, XX4,           // 004eeb44   e8 42dc1900      call .0068c78b
    };
    return MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  }

  ULONG searchOtherAddress(ULONG startAddress, ULONG stopAddress)
  {
    const char *pattern = "S_ASSIGN";
    const uint8_t bytes[] = {
        // 0xc3,       // 005b6492   c3               retn
        // 0x52,       // 005b6493   52               push edx
        0xe8, XX4,  // 005b6494   e8 77dc0000      call .005c4110     ; jichi: hook here
        0x84, 0xc0, // 005b6499   84c0             test al,al
        0x75, XX,   // 005b649b   75 16            jnz short .005b64b3
        0x68, XX4,  // 005b649d   68 d4757200      push .007275d4
        0xb9        //, XX4, // 005b64a2   b9 f0757200      mov ecx,.007275f0  ; ascii "S_ASSIGN"
                    // 0xe8, XX4   // 005b64a7   e8 84c8ffff      call .005b2d30
    };

    for (ULONG addr = startAddress; addr < stopAddress;)
    {
      addr = MemDbg::findBytes(bytes, sizeof(bytes), addr, stopAddress);
      if (!addr)
        return 0;
      addr += sizeof(bytes);
      DWORD ecx = *(DWORD *)addr;
      if (::strcmp((LPCSTR)ecx, pattern) == 0)
        return addr - sizeof(bytes);
    };
    return 0;
  }

  // - Hook -

  struct TextHookBase
  {
    struct TextArgument // first argument of the scenario hook
    {
      DWORD unknown1,
          unknown2;
      LPCSTR text;
      DWORD size; // text data size, length = size - 1
      // DWORD split; // not a good split to distinguish translable text out
    };

    bool enabled_,
        editable_;       // for debugging only, whether text is not read-only
    std::string buffer_; // persistent storage, which makes this function not thread-safe
    TextArgument *arg_;  // last argument
    LPCSTR text_;        // last text
    DWORD size_;         // last size

    TextHookBase()
        : enabled_(true), editable_(true), arg_(nullptr), text_(nullptr), size_(0)
    {
    }
  };
  /*
  class ScenarioHook43 : protected TextHookBase
  {
  public:
    bool hookBefore(hook_context*s,void* data, size_t* len,uintptr_t*role)
    {
      // See ATcode patch:
      // 0070A12E   8B87 B0000000    MOV EAX,DWORD PTR DS:[EDI+0xB0]
      // 0070A134   66:8138 8400     CMP WORD PTR DS:[EAX],0x84
      // 0070A139   75 0E            JNZ SHORT .0070A149
      // 0070A13B   8378 EA 5B       CMP DWORD PTR DS:[EAX-0x16],0x5B
      // 0070A13F   75 08            JNZ SHORT .0070A149
      DWORD split = *(WORD *)(s->edi + 0xb0);
      if (split && split != 0x27f2) // new System43 after Evenicle
        return false;
      if (!split) { // old System43 before Evenicle where edi split is zero
        split = s->stack[1];
        if (split != 0x84)
          return false;
        // Stack structure observed from 武想少女隊
        // 0012F4BC   07EAFD48 ; text address
        // 0012F4C0   000002EC ; use this value as split
        // 0012F4C4   00000011
        // 0012F4C8   0012F510
        // 0012F4CC   00000012
        // 0012F4D0   00001BAA
        // 0012F4D4   00000012
        // 0012F4D8   06D2E24C
        // 0012F4DC   00581125  RETURN to .00581125 from .0057DC30
        //if (s->stack[1] != 0x84)
        //  return true;
        //if (s->stack[2] != 0x3)
        //  return true;
      }

      auto arg = (TextArgument *)s->stack[0]; // top of the stack
      LPCSTR text = arg->text;
      if (arg->size <= 1 || !text || !*text || all_ascii(text))
        return false;

      *role = Engine::ScenarioRole ;
      return write_string_overwrite(data,len,text);
    }

    bool hookAfter(hook_context*s,void* data, size_t* len,uintptr_t*role)
    {
      if (arg_) {
        arg_->text = text_;
        arg_->size = size_;
        arg_ = nullptr;
      }
      return true;
    }
  };

  class OtherHook43 : protected TextHookBase
  {
  public:
    bool hookBefore(hook_context*s,void* data, size_t* len,uintptr_t*role)
    {
      if (!enabled_)
        return false;
      DWORD splitBase = *(DWORD *)(s->edi + 0x284); // [edi + 0x284]
      if (!Engine::isAddressReadable(splitBase)) {
        enabled_ = false;
        return false;
      }
      DWORD split1 = *(WORD *)(splitBase - 0x4), // word [[edi + 0x284] - 0x4]
            split2 = *(WORD *)(splitBase - 0x8); // word [[edi + 0x284] - 0x8]
      enum : WORD { OtherSplit = 0x46 }; // 0x440046 if use dword split
      if (split1 != OtherSplit || split2 <= 2) // split internal system messages
        return false;

      auto arg = (TextArgument *)s->stack[0]; // top of the stack

    //  auto g = EngineController::instance();
      LPCSTR text = arg->text;
      if (arg->size <= 1 || !text || !*text ||   all_ascii(text))
        return false;
      return write_string_overwrite(data,len,text);
    }

    bool hookAfter(hook_context*s,void* data, size_t* len,uintptr_t*role)
    {
      if (arg_) {
        arg_->text = text_;
        arg_->size = size_;
        arg_ = nullptr;
      }
      return false;
    }
  };

  // Text with fixed size
  bool fixedTextHook(hook_context*s,void* data, size_t* len,uintptr_t*role)
  {
    enum { FixedSize = 0x10 };
    struct FixedArgument // first argument of the name hook
    {
      char text[FixedSize]; // 0x10
      DWORD type, // [[esp]+0x10]
            type2; // [[esp]+0x14]
    };

    auto arg = (FixedArgument *)s->stack[0];
    if (arg->type2 != 0xf) // non 0xf is garbage text
      return false;

    char *text = arg->text;
    if (!text || !*text || all_ascii(text))
      return false;

    * role;
    long sig;
    if (arg->type == 0x6 || arg->type == 0xc) {
      *role = Engine::NameRole;
    } else if (::strlen(text) <= 2)  // skip translating very short other text
      return false;
    else {
      *role = Engine::OtherRole;

    }
    return write_string_overwrite(data,len,text);
  }
  */
} // unnamed namespace

bool attachSystem43(ULONG startAddress, ULONG stopAddress)
{
  // 太麻煩 放棄。
  return false;
  {
    // ULONG addr = 0x005c71e0;
    ULONG addr = ::searchScenarioAddress(startAddress, stopAddress);
    if (!addr)
      return false;
    /*   static auto h = new ScenarioHook43; // never deleted
       if (!winhook::hook_both(addr,
           std::bind(&ScenarioHook43::hookBefore, h, _1),
           std::bind(&ScenarioHook43::hookAfter, h, _1)))
         return false;
      */
  }
  /*
    if (ULONG addr = ::searchOtherAddress(startAddress, stopAddress)) {
      static auto h = new OtherHook; // never deleted
      if (!winhook::hook_both(addr,
          std::bind(&OtherHook43::hookBefore, h, _1),
          std::bind(&OtherHook43::hookAfter, h, _1)))
        DOUT("other text NOT FOUND");
      else
        DOUT("other text address" << QString::number(addr, 16));
    }

    if (ULONG addr = ::searchNameAddress(startAddress, stopAddress)) {
      if (winhook::hook_before(addr, ::fixedTextHook))
        DOUT("name text address" << QString::number(addr, 16));
      else
        DOUT("name text NOT FOUND");
    }
  */
  // HijackManager::instance()->attachFunction((ULONG)::MultiByteToWideChar);

  return true;
}
namespace
{
  bool system4X(ULONG startAddress, ULONG stopAddress)
  {
    if (attachSystem43(startAddress, stopAddress))
    {
      return true;
    }
    else if (attachSystem44(startAddress, stopAddress))
    {
      return true;
    }
    else
      return false;
  }
}
namespace
{
  void System42Filter(TextBuffer *buffer, HookParam *)
  {
    auto text = reinterpret_cast<LPSTR>(buffer->buff);

    if (buffer->size == 1)
      return buffer->clear();
    if (all_ascii(text, buffer->size))
    {
      CharReplacer(buffer, '`', ' ');
      CharReplacer(buffer, '\x7D', '-');
    }
  }

  bool InsertSystem42Hook()
  {

    /*
     * Sample games:
     * https://vndb.org/v1427
     */
    const BYTE bytes[] = {
        0x8B, 0x46, 0x04, // mov eax,[esi+04]
        0x57,             // push edi
        0x52,             // push edx
        0x50,             // push eax
        0xE8, XX4         // call Sys42VM.DLL+4B5B0
    };

    HMODULE module = GetModuleHandleW(L"Sys42VM.dll");
    auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.split = regoffset(esp);
    hp.type = NO_CONTEXT | USING_STRING | USING_SPLIT;
    hp.filter_fun = System42Filter;
    return NewHook(hp, "System42");
  }
}
static bool Evenicle()
{
  // https://vndb.org/v16640
  const BYTE bytes[] = {
      0xb8, XX4,
      0xe8, XX4,
      0x83, 0xec, 0x18,
      0x8b, 0x01,
      0x56,
      0x8b, 0xf2,
      0xff, 0x10, // v3 = (const char *)(**a1)(a1); ->EAX
      0x50,
      0x8d, 0x4d, 0xdc,
      0xe8, XX4,
      0x83, 0x65, 0xfc, 0x00,
      0x8d, 0x45, 0xdc,
      0x8b, 0x0d, XX4,
      0x56,
      0x50,
      0x8d, 0x49, 0x04,
      0xe8, XX4,
      0x8d, 0x4d, 0xdc,
      0xe8, XX4,
      0x8b, 0x4d, 0xf4,
      0x5e,
      0x64, 0x89, 0x0d, 0x00, 0x00, 0x00, 0x00,
      0xc9,
      0xc3};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 5 + 5 + 3 + 2 + 1 + 2 + 2;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  return NewHook(hp, "Evenicle");
}
bool System4x::attach_function()
{
  if (Util::CheckFile(L"DLL/Sys42VM.dll"))
    if (InsertSystem42Hook())
      return true;
  auto _ = system4X(processStartAddress, processStopAddress);
  return InsertSystem43Hook() || _ || Evenicle();
}