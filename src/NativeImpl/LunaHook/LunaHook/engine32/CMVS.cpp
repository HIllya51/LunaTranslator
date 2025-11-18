#include "CMVS.h"
namespace
{ // unnamed
  /********************************************************************************************
  CMVS hook:
    Process name is cmvs.exe or cnvs.exe or cmvs*.exe. Used by PurpleSoftware games.

    Font caching issue. Find call to GetGlyphOutlineA and the function entry.
  ********************************************************************************************/

  // jichi 3/6/2014: This is the original CMVS hook in ITH
  // It does not work for パ�プルソフトウェア games after しあわせ家族部 (2012)
  bool InsertCMVS1Hook()
  {
    const DWORD funcs[] = {
        0xec83, // caller pattern: sub esp = 0x83,0xec
        0xec8b55,
    };
    ULONG addr = MemDbg::findMultiCallerAddress((ULONG)::GetGlyphOutlineA, funcs, ARRAYSIZE(funcs), processStartAddress, processStopAddress);
    // 初恋サクラメント
    // 夏に奏でる僕らの詩
    if (!addr)
    {

      // 例外：
      // みはる -あるとアナザーストーリー-
      addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, false, XX);
      if (!addr)
        return false;
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        return false;
    }

    // クロノクロック
    // 会提前停止
    if (((*(DWORD *)(addr - 3)) & 0xffffff) == 0xec8b55)
      addr -= 3;
    HookParam hp;
    hp.address = addr;
    if (*(BYTE *)addr == 0x8b)
    {
      // みはる -あるとアナザーストーリー-
      // stdcall , mov     edx, [esp+arg_0]
      hp.offset = stackoffset(3);
    }
    else
      hp.offset = stackoffset(2);
    hp.split = regoffset(esp);
    hp.type = CODEC_ANSI_BE | USING_SPLIT;

    // RegisterEngineType(ENGINE_CMVS);
    return NewHook(hp, "CMVS");
  }

  /**
   *  CMSV
   *  Sample games:
   *  ハピメア: /HAC@48FF3:cmvs32.exe
   *  ハピメアFD: /HB-1C*0@44EE95
   *
   *  Optional: ハピメアFD: /HB-1C*0@44EE95
   *  This hook has issue that the text will be split to a large amount of threads
   *  - length_offset: 1
   *  - off: 4294967264 = 0xffffffe0 = -0x20
   *  - type: 8
   *
   *  ハピメア: /HAC@48FF3:cmvs32.exe
   *  base: 0x400000
   *  - length_offset: 1
   *  - off: 12 = 0xc
   *  - type: 68 = 0x44
   *
   *  00448fee     cc             int3
   *  00448fef     cc             int3
   *  00448ff0  /$ 55             push ebp
   *  00448ff1  |. 8bec           mov ebp,esp
   *  00448ff3  |. 83ec 68        sub esp,0x68 ; jichi: hook here, it is actually  tagTEXTMETRICA
   *  00448ff6  |. 8b01           mov eax,dword ptr ds:[ecx]
   *  00448ff8  |. 56             push esi
   *  00448ff9  |. 33f6           xor esi,esi
   *  00448ffb  |. 33d2           xor edx,edx
   *  00448ffd  |. 57             push edi
   *  00448ffe  |. 894d fc        mov dword ptr ss:[ebp-0x4],ecx
   *  00449001  |. 3bc6           cmp eax,esi
   *  00449003  |. 74 37          je short cmvs32.0044903c
   *  00449005  |> 66:8b78 08     /mov di,word ptr ds:[eax+0x8]
   *  00449009  |. 66:3b7d 0c     |cmp di,word ptr ss:[ebp+0xc]
   *  0044900d  |. 75 0a          |jnz short cmvs32.00449019
   *  0044900f  |. 66:8b7d 10     |mov di,word ptr ss:[ebp+0x10]
   *  00449013  |. 66:3978 0a     |cmp word ptr ds:[eax+0xa],di
   *  00449017  |. 74 0a          |je short cmvs32.00449023
   *  00449019  |> 8bd0           |mov edx,eax
   *  0044901b  |. 8b00           |mov eax,dword ptr ds:[eax]
   *  0044901d  |. 3bc6           |cmp eax,esi
   *  0044901f  |.^75 e4          \jnz short cmvs32.00449005
   *  00449021  |. eb 19          jmp short cmvs32.0044903c
   *  00449023  |> 3bd6           cmp edx,esi
   *  00449025  |. 74 0a          je short cmvs32.00449031
   *  00449027  |. 8b38           mov edi,dword ptr ds:[eax]
   *  00449029  |. 893a           mov dword ptr ds:[edx],edi
   *  0044902b  |. 8b11           mov edx,dword ptr ds:[ecx]
   *  0044902d  |. 8910           mov dword ptr ds:[eax],edx
   *  0044902f  |. 8901           mov dword ptr ds:[ecx],eax
   *  00449031  |> 8b40 04        mov eax,dword ptr ds:[eax+0x4]
   *  00449034  |. 3bc6           cmp eax,esi
   *  00449036  |. 0f85 64010000  jnz cmvs32.004491a0
   *  0044903c  |> 8b55 08        mov edx,dword ptr ss:[ebp+0x8]
   *  0044903f  |. 53             push ebx
   *  00449040  |. 0fb75d 0c      movzx ebx,word ptr ss:[ebp+0xc]
   *  00449044  |. b8 00000100    mov eax,0x10000
   *  00449049  |. 8945 e4        mov dword ptr ss:[ebp-0x1c],eax
   *  0044904c  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
   *  0044904f  |. 8d45 e4        lea eax,dword ptr ss:[ebp-0x1c]
   *  00449052  |. 50             push eax                                 ; /pMat2
   *  00449053  |. 56             push esi                                 ; |Buffer
   *  00449054  |. 56             push esi                                 ; |BufSize
   *  00449055  |. 8d4d d0        lea ecx,dword ptr ss:[ebp-0x30]          ; |
   *  00449058  |. 51             push ecx                                 ; |pMetrics
   *  00449059  |. 6a 05          push 0x5                                 ; |Format = GGO_GRAY4_BITMAP
   *  0044905b  |. 53             push ebx                                 ; |Char
   *  0044905c  |. 52             push edx                                 ; |hDC
   *  0044905d  |. 8975 e8        mov dword ptr ss:[ebp-0x18],esi          ; |
   *  00449060  |. 8975 ec        mov dword ptr ss:[ebp-0x14],esi          ; |
   *  00449063  |. ff15 5cf05300  call dword ptr ds:[<&gdi32.getglyphoutli>; \GetGlyphOutlineA
   *  00449069  |. 8b75 10        mov esi,dword ptr ss:[ebp+0x10]
   *  0044906c  |. 0faff6         imul esi,esi
   *  0044906f  |. 8bf8           mov edi,eax
   *  00449071  |. 8d04bd 0000000>lea eax,dword ptr ds:[edi*4]
   *  00449078  |. 3bc6           cmp eax,esi
   *  0044907a  |. 76 02          jbe short cmvs32.0044907e
   *  0044907c  |. 8bf0           mov esi,eax
   *  0044907e  |> 56             push esi                                 ; /Size
   *  0044907f  |. 6a 00          push 0x0                                 ; |Flags = LMEM_FIXED
   *  00449081  |. ff15 34f25300  call dword ptr ds:[<&kernel32.localalloc>; \LocalAlloc
   */
  bool InsertCMVS2Hook()
  {
    // There are multiple functions satisfy the pattern below.
    // Hook to any one of them is OK.
    const BYTE bytes[] = {
        // function begin
        0x55,             // 00448ff0  /$ 55             push ebp
        0x8b, 0xec,       // 00448ff1  |. 8bec           mov ebp,esp
        0x83, 0xec, 0x68, // 00448ff3  |. 83ec 68        sub esp,0x68 ; jichi: hook here
        0x8b, 0x01,       // 00448ff6  |. 8b01           mov eax,dword ptr ds:[ecx]
        0x56,             // 00448ff8  |. 56             push esi
        0x33, 0xf6,       // 00448ff9  |. 33f6           xor esi,esi
        0x33, 0xd2,       // 00448ffb  |. 33d2           xor edx,edx
        0x57,             // 00448ffd  |. 57             push edi
        0x89, 0x4d, 0xfc, // 00448ffe  |. 894d fc        mov dword ptr ss:[ebp-0x4],ecx
        0x3b, 0xc6,       // 00449001  |. 3bc6           cmp eax,esi
        0x74, 0x37        // 00449003  |. 74 37          je short cmvs32.0044903c
    };
    enum
    {
      addr_offset = 3
    }; // offset from the beginning of the function
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    // Artikash 11/9/2018: Not sure, but isn't findCallerAddress a better way to do this?
    if (!addr)
      addr = MemDbg::findCallerAddressAfterInt3((DWORD)GetGlyphOutlineA, processStartAddress, processStopAddress);
    if (!addr)
    {
      ConsoleOutput("CMVS2: pattern not found");
      return false;
    }

    // reladdr = 0x48ff0;
    // reladdr = 0x48ff3;
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = stackoffset(3);
    hp.type = CODEC_ANSI_BE;

    ConsoleOutput("INSERT CMVS2");

    return NewHook(hp, "CMVS2");
  }

} // unnamed namespace

// jichi 3/7/2014: Insert the old hook first since GetGlyphOutlineA can NOT be found in new games
bool InsertCMVSHook()
{
  // Both CMVS1 and CMVS2 exists in new games.
  // Insert the CMVS2 first. Since CMVS1 could break CMVS2
  // And the CMVS1 games do not have CMVS2 patterns.
  // return InsertCMVS2Hook() || InsertCMVS1Hook();

  // 初恋サクラメント
  // 夏に奏でる僕らの詩
  // まじぷり＼Wonder Cradle
  // 等等一堆游戏，都能搜索到2，但没文字。
  //  bool b2=InsertCMVS2Hook();
  //  //先插入1会崩溃。
  //  bool b1=InsertCMVS1Hook();
  // return b1||b2;
  return InsertCMVS1Hook();
}
/**
 *  Sample game: クロノクロック (CMVS2)
 *
 *  This function is found by back-tracking GetGlyphOutlineA
 *  Until I found a function with GetDC.
 *
 *  0045111B   CC               INT3
 *  0045111C   CC               INT3
 *  0045111D   CC               INT3
 *  0045111E   CC               INT3
 *  0045111F   CC               INT3
 *  00451120   55               PUSH EBP
 *  00451121   8BEC             MOV EBP,ESP
 *  00451123   83EC 58          SUB ESP,0x58
 *  00451126   53               PUSH EBX
 *  00451127   33C0             XOR EAX,EAX
 *  00451129   56               PUSH ESI
 *  0045112A   8BF1             MOV ESI,ECX
 *  0045112C   57               PUSH EDI
 *  0045112D   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  00451130   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  00451133   8945 F4          MOV DWORD PTR SS:[EBP-0xC],EAX
 *  00451136   8945 E8          MOV DWORD PTR SS:[EBP-0x18],EAX
 *  00451139   8B86 58010000    MOV EAX,DWORD PTR DS:[ESI+0x158]
 *  0045113F   50               PUSH EAX
 *  00451140   FF15 C0735400    CALL DWORD PTR DS:[0x5473C0]             ; user32.GetDC
 *  00451146   68 80000000      PUSH 0x80
 *  0045114B   8D9E B8000000    LEA EBX,DWORD PTR DS:[ESI+0xB8]
 *  00451151   6A 00            PUSH 0x0
 *  00451153   53               PUSH EBX
 *  00451154   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  00451157   E8 C4A00D00      CALL .0052B220
 *  0045115C   83C4 0C          ADD ESP,0xC
 *  0045115F   83BE A4000000 00 CMP DWORD PTR DS:[ESI+0xA4],0x0
 *  00451166   74 29            JE SHORT .00451191
 *  00451168   6A 00            PUSH 0x0
 *  0045116A   6A 00            PUSH 0x0
 *  0045116C   53               PUSH EBX
 *  0045116D   8BCF             MOV ECX,EDI
 *  0045116F   51               PUSH ECX
 *  00451170   8BCE             MOV ECX,ESI
 *  00451172   E8 29F8FFFF      CALL .004509A0
 *  00451177   833B 00          CMP DWORD PTR DS:[EBX],0x0
 *  0045117A   77 09            JA SHORT .00451185
 *  0045117C   83BE AC000000 00 CMP DWORD PTR DS:[ESI+0xAC],0x0
 *  00451183   74 0C            JE SHORT .00451191
 *  00451185   8B96 B0000000    MOV EDX,DWORD PTR DS:[ESI+0xB0]
 *  0045118B   0196 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EDX
 *  00451191   8B4E 7C          MOV ECX,DWORD PTR DS:[ESI+0x7C]
 *  00451194   8B56 70          MOV EDX,DWORD PTR DS:[ESI+0x70]
 *  00451197   B8 28000000      MOV EAX,0x28
 *  0045119C   66:8945 A8       MOV WORD PTR SS:[EBP-0x58],AX
 *  004511A0   8B46 74          MOV EAX,DWORD PTR DS:[ESI+0x74]
 *  004511A3   894D CC          MOV DWORD PTR SS:[EBP-0x34],ECX
 *  004511A6   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  004511A9   8945 C4          MOV DWORD PTR SS:[EBP-0x3C],EAX
 *  004511AC   8B86 80000000    MOV EAX,DWORD PTR DS:[ESI+0x80]
 *  004511B2   894D BC          MOV DWORD PTR SS:[EBP-0x44],ECX
 *  004511B5   33C9             XOR ECX,ECX
 *  004511B7   48               DEC EAX
 *  004511B8   8955 C0          MOV DWORD PTR SS:[EBP-0x40],EDX
 *  004511BB   894D B0          MOV DWORD PTR SS:[EBP-0x50],ECX
 *  004511BE   74 18            JE SHORT .004511D8
 *  004511C0   48               DEC EAX
 *  004511C1   74 0C            JE SHORT .004511CF
 *  004511C3   48               DEC EAX
 *  004511C4   75 19            JNZ SHORT .004511DF
 *  004511C6   C745 B0 03000000 MOV DWORD PTR SS:[EBP-0x50],0x3
 *  004511CD   EB 10            JMP SHORT .004511DF
 *  004511CF   C745 B0 02000000 MOV DWORD PTR SS:[EBP-0x50],0x2
 *  004511D6   EB 07            JMP SHORT .004511DF
 *  004511D8   C745 B0 01000000 MOV DWORD PTR SS:[EBP-0x50],0x1
 *  004511DF   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  004511E2   3BC1             CMP EAX,ECX
 *  004511E4   74 1B            JE SHORT .00451201
 *  004511E6   8B50 0C          MOV EDX,DWORD PTR DS:[EAX+0xC]
 *  004511E9   8955 C8          MOV DWORD PTR SS:[EBP-0x38],EDX
 *  004511EC   3948 10          CMP DWORD PTR DS:[EAX+0x10],ECX
 *  004511EF   74 05            JE SHORT .004511F6
 *  004511F1   894D F0          MOV DWORD PTR SS:[EBP-0x10],ECX
 *  004511F4   EB 26            JMP SHORT .0045121C
 *  004511F6   8B96 8C000000    MOV EDX,DWORD PTR DS:[ESI+0x8C]
 *  004511FC   0FAF10           IMUL EDX,DWORD PTR DS:[EAX]
 *  004511FF   EB 0E            JMP SHORT .0045120F
 *  00451201   8B46 78          MOV EAX,DWORD PTR DS:[ESI+0x78]
 *  00451204   8B96 8C000000    MOV EDX,DWORD PTR DS:[ESI+0x8C]
 *  0045120A   8945 C8          MOV DWORD PTR SS:[EBP-0x38],EAX
 *  0045120D   03D2             ADD EDX,EDX
 *  0045120F   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  00451214   F7E2             MUL EDX
 *  00451216   C1EA 03          SHR EDX,0x3
 *  00451219   8955 F0          MOV DWORD PTR SS:[EBP-0x10],EDX
 *  0045121C   8BC7             MOV EAX,EDI
 *  0045121E   3808             CMP BYTE PTR DS:[EAX],CL
 *  00451220   0F84 5A040000    JE .00451680
 *  00451226   EB 02            JMP SHORT .0045122A
 *  00451228   33C9             XOR ECX,ECX
 *  0045122A   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  0045122D   3C 5C            CMP AL,0x5C
 *  0045122F   0F84 AE030000    JE .004515E3
 *  00451235   3C 7B            CMP AL,0x7B
 *  00451237   0F84 65010000    JE .004513A2
 *  0045123D   50               PUSH EAX
 *  0045123E   E8 DD59FBFF      CALL .00406C20
 *  00451243  Hook 85C0             TEST EAX,EAX
 *  00451245   0F84 A6000000    JE .004512F1
 *  0045124B   66:0FBE47 01     MOVSX AX,BYTE PTR DS:[EDI+0x1]
 *  00451250   66:0FBE17        MOVSX DX,BYTE PTR DS:[EDI]
 *  00451254   B9 FF000000      MOV ECX,0xFF
 *  00451259   66:23C1          AND AX,CX
 *  0045125C   66:C1E2 08       SHL DX,0x8
 *  00451260   66:0BC2          OR AX,DX
 *  00451263   B9 4A810000      MOV ECX,0x814A
 *  00451268   83C7 02          ADD EDI,0x2
 *  0045126B   33DB             XOR EBX,EBX
 *  0045126D   66:8945 AA       MOV WORD PTR SS:[EBP-0x56],AX
 *  00451271   66:3BC1          CMP AX,CX
 *  00451274   75 05            JNZ SHORT .0045127B
 *  00451276   BB 01000000      MOV EBX,0x1
 *  0045127B   8B45 AA          MOV EAX,DWORD PTR SS:[EBP-0x56]
 *  0045127E   8D55 F4          LEA EDX,DWORD PTR SS:[EBP-0xC]
 *  00451281   52               PUSH EDX
 *  00451282   50               PUSH EAX
 *  00451283   6A 00            PUSH 0x0
 *  00451285   8BCE             MOV ECX,ESI
 *  00451287   E8 44F9FFFF      CALL .00450BD0
 *  0045128C   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  00451292   8B96 9C000000    MOV EDX,DWORD PTR DS:[ESI+0x9C]
 *  00451298   894D B4          MOV DWORD PTR SS:[EBP-0x4C],ECX
 *  0045129B   8955 B8          MOV DWORD PTR SS:[EBP-0x48],EDX
 *  0045129E   85DB             TEST EBX,EBX
 *  004512A0   74 0E            JE SHORT .004512B0
 *  004512A2   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  004512A7   F766 1C          MUL DWORD PTR DS:[ESI+0x1C]
 *  004512AA   C1EA 02          SHR EDX,0x2
 *  004512AD   2955 B4          SUB DWORD PTR SS:[EBP-0x4C],EDX
 *  004512B0   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
 *  004512B3   8D45 DC          LEA EAX,DWORD PTR SS:[EBP-0x24]
 *  004512B6   50               PUSH EAX
 *  004512B7   8D4D A8          LEA ECX,DWORD PTR SS:[EBP-0x58]
 *  004512BA   51               PUSH ECX
 *  004512BB   52               PUSH EDX
 *  004512BC   8BCE             MOV ECX,ESI
 *  004512BE   E8 EDEEFFFF      CALL .004501B0
 *  004512C3   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  004512C6   85DB             TEST EBX,EBX
 *  004512C8   75 11            JNZ SHORT .004512DB
 *  004512CA   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
 *  004512CD   0346 1C          ADD EAX,DWORD PTR DS:[ESI+0x1C]
 *  004512D0   0186 98000000    ADD DWORD PTR DS:[ESI+0x98],EAX
 *  004512D6   E9 A4000000      JMP .0045137F
 *  004512DB   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  004512DE   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  004512E3   F7E1             MUL ECX
 *  004512E5   C1EA 02          SHR EDX,0x2
 *  004512E8   D1E9             SHR ECX,1
 *  004512EA   2BCA             SUB ECX,EDX
 *  004512EC   E9 85000000      JMP .00451376
 *  004512F1   66:0FBE0F        MOVSX CX,BYTE PTR DS:[EDI]
 *  004512F5   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  004512F8   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  004512FB   2BD0             SUB EDX,EAX
 *  004512FD   2B56 20          SUB EDX,DWORD PTR DS:[ESI+0x20]
 *  00451300   66:894D AA       MOV WORD PTR SS:[EBP-0x56],CX
 *  00451304   8B4E 0C          MOV ECX,DWORD PTR DS:[ESI+0xC]
 *  00451307   03D1             ADD EDX,ECX
 *  00451309   47               INC EDI
 *  0045130A   3996 98000000    CMP DWORD PTR DS:[ESI+0x98],EDX
 *  00451310   72 37            JB SHORT .00451349
 *  00451312   8B55 F4          MOV EDX,DWORD PTR SS:[EBP-0xC]
 *  00451315   42               INC EDX
 *  00451316   83BC96 B8000000 >CMP DWORD PTR DS:[ESI+EDX*4+0xB8],0x0
 *  0045131E   8955 F4          MOV DWORD PTR SS:[EBP-0xC],EDX
 *  00451321   77 09            JA SHORT .0045132C
 *  00451323   83BE AC000000 00 CMP DWORD PTR DS:[ESI+0xAC],0x0
 *  0045132A   74 0C            JE SHORT .00451338
 *  0045132C   8B96 B0000000    MOV EDX,DWORD PTR DS:[ESI+0xB0]
 *  00451332   0196 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EDX
 *  00451338   898E 98000000    MOV DWORD PTR DS:[ESI+0x98],ECX
 *  0045133E   8B4E 24          MOV ECX,DWORD PTR DS:[ESI+0x24]
 *  00451341   03C8             ADD ECX,EAX
 *  00451343   018E 9C000000    ADD DWORD PTR DS:[ESI+0x9C],ECX
 *  00451349   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  0045134F   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  00451355   8D4D DC          LEA ECX,DWORD PTR SS:[EBP-0x24]
 *  00451358   51               PUSH ECX
 *  00451359   8955 B4          MOV DWORD PTR SS:[EBP-0x4C],EDX
 *  0045135C   8D55 A8          LEA EDX,DWORD PTR SS:[EBP-0x58]
 *  0045135F   8945 B8          MOV DWORD PTR SS:[EBP-0x48],EAX
 *  00451362   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  00451365   52               PUSH EDX
 *  00451366   50               PUSH EAX
 *  00451367   8BCE             MOV ECX,ESI
 *  00451369   E8 42EEFFFF      CALL .004501B0
 *  0045136E   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  00451371   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  00451374   D1E9             SHR ECX,1
 *  00451376   034E 20          ADD ECX,DWORD PTR DS:[ESI+0x20]
 *  00451379   018E 98000000    ADD DWORD PTR DS:[ESI+0x98],ECX
 *  0045137F   8B55 F0          MOV EDX,DWORD PTR SS:[EBP-0x10]
 *  00451382   8B45 E8          MOV EAX,DWORD PTR SS:[EBP-0x18]
 *  00451385   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  00451388   52               PUSH EDX
 *  00451389   8B55 0C          MOV EDX,DWORD PTR SS:[EBP+0xC]
 *  0045138C   50               PUSH EAX
 *  0045138D   8B45 F8          MOV EAX,DWORD PTR SS:[EBP-0x8]
 *  00451390   51               PUSH ECX
 *  00451391   52               PUSH EDX
 *  00451392   50               PUSH EAX
 *  00451393   8BCE             MOV ECX,ESI
 *  00451395   E8 36F9FFFF      CALL .00450CD0
 *  0045139A   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  0045139D   E9 D5020000      JMP .00451677
 *  004513A2   8D55 F4          LEA EDX,DWORD PTR SS:[EBP-0xC]
 *  004513A5   52               PUSH EDX
 *  004513A6   51               PUSH ECX
 *  004513A7   51               PUSH ECX
 *  004513A8   8BCE             MOV ECX,ESI
 *  004513AA   E8 21F8FFFF      CALL .00450BD0
 *  004513AF   8B86 98000000    MOV EAX,DWORD PTR DS:[ESI+0x98]
 *  004513B5   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  004513B8   8B55 BC          MOV EDX,DWORD PTR SS:[EBP-0x44]
 *  004513BB   8945 08          MOV DWORD PTR SS:[EBP+0x8],EAX
 *  004513BE   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  004513C4   2B86 B0000000    SUB EAX,DWORD PTR DS:[ESI+0xB0]
 *  004513CA   894D D8          MOV DWORD PTR SS:[EBP-0x28],ECX
 *  004513CD   8945 D4          MOV DWORD PTR SS:[EBP-0x2C],EAX
 *  004513D0   BB 01000000      MOV EBX,0x1
 *  004513D5  Hook 47               INC EDI
 *  004513D6   8955 D0          MOV DWORD PTR SS:[EBP-0x30],EDX
 *  004513D9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  004513E0   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  004513E3   50               PUSH EAX
 *  004513E4   E8 3758FBFF      CALL .00406C20
 *  004513E9   85C0             TEST EAX,EAX
 *  004513EB   74 55            JE SHORT .00451442
 *  004513ED   66:0FBE4F 01     MOVSX CX,BYTE PTR DS:[EDI+0x1]
 *  004513F2   66:0FBE07        MOVSX AX,BYTE PTR DS:[EDI]
 *  004513F6   BA FF000000      MOV EDX,0xFF
 *  004513FB   66:23CA          AND CX,DX
 *  004513FE   8B96 9C000000    MOV EDX,DWORD PTR DS:[ESI+0x9C]
 *  00451404   66:C1E0 08       SHL AX,0x8
 *  00451408   66:0BC8          OR CX,AX
 *  0045140B   66:894D AA       MOV WORD PTR SS:[EBP-0x56],CX
 *  0045140F   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  00451415   894D B4          MOV DWORD PTR SS:[EBP-0x4C],ECX
 *  00451418   8D45 DC          LEA EAX,DWORD PTR SS:[EBP-0x24]
 *  0045141B   50               PUSH EAX
 *  0045141C   8D4D A8          LEA ECX,DWORD PTR SS:[EBP-0x58]
 *  0045141F   8955 B8          MOV DWORD PTR SS:[EBP-0x48],EDX
 *  00451422   8B55 E4          MOV EDX,DWORD PTR SS:[EBP-0x1C]
 *  00451425   51               PUSH ECX
 *  00451426   52               PUSH EDX
 *  00451427   8BCE             MOV ECX,ESI
 *  00451429   83C7 02          ADD EDI,0x2
 *  0045142C   E8 7FEDFFFF      CALL .004501B0
 *  00451431   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  00451434   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
 *  00451437   0346 1C          ADD EAX,DWORD PTR DS:[ESI+0x1C]
 *  0045143A   0186 98000000    ADD DWORD PTR DS:[ESI+0x98],EAX
 *  00451440   EB 08            JMP SHORT .0045144A
 *  00451442   803F 2F          CMP BYTE PTR DS:[EDI],0x2F
 *  00451445   75 02            JNZ SHORT .00451449
 *  00451447   33DB             XOR EBX,EBX
 *  00451449   47               INC EDI
 *  0045144A   8B4D F0          MOV ECX,DWORD PTR SS:[EBP-0x10]
 *  0045144D   8B55 E8          MOV EDX,DWORD PTR SS:[EBP-0x18]
 *  00451450   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  00451453   51               PUSH ECX
 *  00451454   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  00451457   52               PUSH EDX
 *  00451458   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  0045145B   50               PUSH EAX
 *  0045145C   51               PUSH ECX
 *  0045145D   52               PUSH EDX
 *  0045145E   8BCE             MOV ECX,ESI
 *  00451460   E8 6BF8FFFF      CALL .00450CD0
 *  00451465   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  00451468   85DB             TEST EBX,EBX
 *  0045146A  ^0F85 70FFFFFF    JNZ .004513E0
 *  00451470   399E A4000000    CMP DWORD PTR DS:[ESI+0xA4],EBX
 *  00451476   0F84 3F010000    JE .004515BB
 *  0045147C   8BDF             MOV EBX,EDI
 *  0045147E   C745 E0 00000000 MOV DWORD PTR SS:[EBP-0x20],0x0
 *  00451485   C745 EC 01000000 MOV DWORD PTR SS:[EBP-0x14],0x1
 *  0045148C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00451490   0FB603           MOVZX EAX,BYTE PTR DS:[EBX]
 *  00451493   50               PUSH EAX
 *  00451494   E8 8757FBFF      CALL .00406C20
 *  00451499   85C0             TEST EAX,EAX
 *  0045149B   74 08            JE SHORT .004514A5
 *  0045149D   FF45 E0          INC DWORD PTR SS:[EBP-0x20]
 *  004514A0   83C3 02          ADD EBX,0x2
 *  004514A3   EB 0D            JMP SHORT .004514B2
 *  004514A5   803B 7D          CMP BYTE PTR DS:[EBX],0x7D
 *  004514A8   75 07            JNZ SHORT .004514B1
 *  004514AA   C745 EC 00000000 MOV DWORD PTR SS:[EBP-0x14],0x0
 *  004514B1   43               INC EBX
 *  004514B2   837D EC 00       CMP DWORD PTR SS:[EBP-0x14],0x0
 *  004514B6  ^75 D8            JNZ SHORT .00451490
 *  004514B8   8B9E B0000000    MOV EBX,DWORD PTR DS:[ESI+0xB0]
 *  004514BE   8B4D E0          MOV ECX,DWORD PTR SS:[EBP-0x20]
 *  004514C1   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  004514C4   8BC3             MOV EAX,EBX
 *  004514C6   0FAFC1           IMUL EAX,ECX
 *  004514C9   03C9             ADD ECX,ECX
 *  004514CB   894D E0          MOV DWORD PTR SS:[EBP-0x20],ECX
 *  004514CE   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  004514D4   2BCA             SUB ECX,EDX
 *  004514D6   C1E0 0A          SHL EAX,0xA
 *  004514D9   C1E1 0A          SHL ECX,0xA
 *  004514DC   C1E2 0A          SHL EDX,0xA
 *  004514DF   895D BC          MOV DWORD PTR SS:[EBP-0x44],EBX
 *  004514E2   C745 EC 01000000 MOV DWORD PTR SS:[EBP-0x14],0x1
 *  004514E9   8955 08          MOV DWORD PTR SS:[EBP+0x8],EDX
 *  004514EC   3BC1             CMP EAX,ECX
 *  004514EE   76 0F            JBE SHORT .004514FF
 *  004514F0   2BC1             SUB EAX,ECX
 *  004514F2   D1E8             SHR EAX,1
 *  004514F4   2945 08          SUB DWORD PTR SS:[EBP+0x8],EAX
 *  004514F7   C1E3 0A          SHL EBX,0xA
 *  004514FA   895D E0          MOV DWORD PTR SS:[EBP-0x20],EBX
 *  004514FD   EB 21            JMP SHORT .00451520
 *  004514FF   2BC8             SUB ECX,EAX
 *  00451501   33D2             XOR EDX,EDX
 *  00451503   8BC1             MOV EAX,ECX
 *  00451505   F775 E0          DIV DWORD PTR SS:[EBP-0x20]
 *  00451508   8B96 B4000000    MOV EDX,DWORD PTR DS:[ESI+0xB4]
 *  0045150E   C1E3 09          SHL EBX,0x9
 *  00451511   0145 08          ADD DWORD PTR SS:[EBP+0x8],EAX
 *  00451514   03D8             ADD EBX,EAX
 *  00451516   8D045A           LEA EAX,DWORD PTR DS:[EDX+EBX*2]
 *  00451519   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  0045151C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  00451520   0FB60F           MOVZX ECX,BYTE PTR DS:[EDI]
 *  00451523   51               PUSH ECX
 *  00451524   E8 F756FBFF      CALL .00406C20
 *  00451529   85C0             TEST EAX,EAX
 *  0045152B   74 4E            JE SHORT .0045157B
 *  0045152D   66:0FBE57 01     MOVSX DX,BYTE PTR DS:[EDI+0x1]
 *  00451532   66:0FBE0F        MOVSX CX,BYTE PTR DS:[EDI]
 *  00451536   8B5D 08          MOV EBX,DWORD PTR SS:[EBP+0x8]
 *  00451539   B8 FF000000      MOV EAX,0xFF
 *  0045153E   66:23D0          AND DX,AX
 *  00451541   8B45 D4          MOV EAX,DWORD PTR SS:[EBP-0x2C]
 *  00451544   66:C1E1 08       SHL CX,0x8
 *  00451548   66:0BD1          OR DX,CX
 *  0045154B   66:8955 AA       MOV WORD PTR SS:[EBP-0x56],DX
 *  0045154F   8BD3             MOV EDX,EBX
 *  00451551   C1EA 0A          SHR EDX,0xA
 *  00451554   8D4D DC          LEA ECX,DWORD PTR SS:[EBP-0x24]
 *  00451557   51               PUSH ECX
 *  00451558   8955 B4          MOV DWORD PTR SS:[EBP-0x4C],EDX
 *  0045155B   8D55 A8          LEA EDX,DWORD PTR SS:[EBP-0x58]
 *  0045155E   8945 B8          MOV DWORD PTR SS:[EBP-0x48],EAX
 *  00451561   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  00451564   52               PUSH EDX
 *  00451565   50               PUSH EAX
 *  00451566   8BCE             MOV ECX,ESI
 *  00451568   83C7 02          ADD EDI,0x2
 *  0045156B   E8 40ECFFFF      CALL .004501B0
 *  00451570   035D E0          ADD EBX,DWORD PTR SS:[EBP-0x20]
 *  00451573   8945 F8          MOV DWORD PTR SS:[EBP-0x8],EAX
 *  00451576   895D 08          MOV DWORD PTR SS:[EBP+0x8],EBX
 *  00451579   EB 0D            JMP SHORT .00451588
 *  0045157B   803F 7D          CMP BYTE PTR DS:[EDI],0x7D
 *  0045157E   75 07            JNZ SHORT .00451587
 *  00451580   C745 EC 00000000 MOV DWORD PTR SS:[EBP-0x14],0x0
 *  00451587   47               INC EDI
 *  00451588   8B4D F0          MOV ECX,DWORD PTR SS:[EBP-0x10]
 *  0045158B   8B55 E8          MOV EDX,DWORD PTR SS:[EBP-0x18]
 *  0045158E   8B45 D8          MOV EAX,DWORD PTR SS:[EBP-0x28]
 *  00451591   51               PUSH ECX
 *  00451592   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  00451595   52               PUSH EDX
 *  00451596   8B55 F8          MOV EDX,DWORD PTR SS:[EBP-0x8]
 *  00451599   50               PUSH EAX
 *  0045159A   51               PUSH ECX
 *  0045159B   52               PUSH EDX
 *  0045159C   8BCE             MOV ECX,ESI
 *  0045159E   E8 2DF7FFFF      CALL .00450CD0
 *  004515A3   837D EC 00       CMP DWORD PTR SS:[EBP-0x14],0x0
 *  004515A7   8945 D8          MOV DWORD PTR SS:[EBP-0x28],EAX
 *  004515AA  ^0F85 70FFFFFF    JNZ .00451520
 *  004515B0   8B45 D0          MOV EAX,DWORD PTR SS:[EBP-0x30]
 *  004515B3   8945 BC          MOV DWORD PTR SS:[EBP-0x44],EAX
 *  004515B6   E9 BC000000      JMP .00451677
 *  004515BB   BB 01000000      MOV EBX,0x1
 *  004515C0   0FB60F           MOVZX ECX,BYTE PTR DS:[EDI]
 *  004515C3   51               PUSH ECX
 *  004515C4   E8 5756FBFF      CALL .00406C20
 *  004515C9   85C0             TEST EAX,EAX
 *  004515CB   74 05            JE SHORT .004515D2
 *  004515CD   83C7 02          ADD EDI,0x2
 *  004515D0   EB 08            JMP SHORT .004515DA
 *  004515D2   803F 7D          CMP BYTE PTR DS:[EDI],0x7D
 *  004515D5   75 02            JNZ SHORT .004515D9
 *  004515D7   33DB             XOR EBX,EBX
 *  004515D9   47               INC EDI
 *  004515DA   85DB             TEST EBX,EBX
 *  004515DC  ^75 E2            JNZ SHORT .004515C0
 *  004515DE   E9 94000000      JMP .00451677
 *  004515E3   0FBE47 01        MOVSX EAX,BYTE PTR DS:[EDI+0x1]
 *  004515E7   83C0 9D          ADD EAX,-0x63
 *  004515EA   83F8 14          CMP EAX,0x14
 *  004515ED   0F87 84000000    JA .00451677
 *  004515F3   0FB690 B4164500  MOVZX EDX,BYTE PTR DS:[EAX+0x4516B4]
 *  004515FA   FF2495 A0164500  JMP DWORD PTR DS:[EDX*4+0x4516A0]
 *  00451601   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  00451604   8B4E 24          MOV ECX,DWORD PTR DS:[ESI+0x24]
 *  00451607   034E 1C          ADD ECX,DWORD PTR DS:[ESI+0x1C]
 *  0045160A   8986 98000000    MOV DWORD PTR DS:[ESI+0x98],EAX
 *  00451610   8B45 F4          MOV EAX,DWORD PTR SS:[EBP-0xC]
 *  00451613   018E 9C000000    ADD DWORD PTR DS:[ESI+0x9C],ECX
 *  00451619   8B8E 9C000000    MOV ECX,DWORD PTR DS:[ESI+0x9C]
 *  0045161F   40               INC EAX
 *  00451620   83BC86 B8000000 >CMP DWORD PTR DS:[ESI+EAX*4+0xB8],0x0
 *  00451628   8945 F4          MOV DWORD PTR SS:[EBP-0xC],EAX
 *  0045162B   77 09            JA SHORT .00451636
 *  0045162D   83BE AC000000 00 CMP DWORD PTR DS:[ESI+0xAC],0x0
 *  00451634   74 3E            JE SHORT .00451674
 *  00451636   8B96 B0000000    MOV EDX,DWORD PTR DS:[ESI+0xB0]
 *  0045163C   03D1             ADD EDX,ECX
 *  0045163E   8996 9C000000    MOV DWORD PTR DS:[ESI+0x9C],EDX
 *  00451644   EB 2E            JMP SHORT .00451674
 *  00451646   8BCE             MOV ECX,ESI
 *  00451648   E8 53F0FFFF      CALL .004506A0
 *  0045164D   EB 25            JMP SHORT .00451674
 *  0045164F   8A47 02          MOV AL,BYTE PTR DS:[EDI+0x2]
 *  00451652   3C 63            CMP AL,0x63
 *  00451654   74 0C            JE SHORT .00451662
 *  00451656   3C 73            CMP AL,0x73
 *  00451658   75 12            JNZ SHORT .0045166C
 *  0045165A   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0045165D   83C7 03          ADD EDI,0x3
 *  00451660   EB 15            JMP SHORT .00451677
 *  00451662   C745 E8 01000000 MOV DWORD PTR SS:[EBP-0x18],0x1
 *  00451669   894D FC          MOV DWORD PTR SS:[EBP-0x4],ECX
 *  0045166C   83C7 03          ADD EDI,0x3
 *  0045166F   EB 06            JMP SHORT .00451677
 *  00451671   894D FC          MOV DWORD PTR SS:[EBP-0x4],ECX
 *  00451674   83C7 02          ADD EDI,0x2
 *  00451677   803F 00          CMP BYTE PTR DS:[EDI],0x0
 *  0045167A  ^0F85 A8FBFFFF    JNZ .00451228
 *  00451680   8B45 E4          MOV EAX,DWORD PTR SS:[EBP-0x1C]
 *  00451683   8B8E 58010000    MOV ECX,DWORD PTR DS:[ESI+0x158]
 *  00451689   50               PUSH EAX
 *  0045168A   51               PUSH ECX
 *  0045168B   FF15 C4735400    CALL DWORD PTR DS:[0x5473C4]             ; user32.ReleaseDC
 *  00451691   5F               POP EDI
 *  00451692   5E               POP ESI
 *  00451693   B8 01000000      MOV EAX,0x1
 *  00451698   5B               POP EBX
 *  00451699   8BE5             MOV ESP,EBP
 *  0045169B   5D               POP EBP
 *  0045169C   C2 0800          RETN 0x8
 *  0045169F   90               NOP
 *  004516A0   46               INC ESI
 *  004516A1   16               PUSH SS
 *  004516A2   45               INC EBP
 *  004516A3   0001             ADD BYTE PTR DS:[ECX],AL
 *  004516A5   16               PUSH SS
 *  004516A6   45               INC EBP
 *  004516A7   0071 16          ADD BYTE PTR DS:[ECX+0x16],DH
 *  004516AA   45               INC EBP
 *  004516AB   004F 16          ADD BYTE PTR DS:[EDI+0x16],CL
 *  004516AE   45               INC EBP
 *  004516AF   0077 16          ADD BYTE PTR DS:[EDI+0x16],DH
 *  004516B2   45               INC EBP
 *  004516B3   0000             ADD BYTE PTR DS:[EAX],AL
 *  004516B5   04 04            ADD AL,0x4
 *  004516B7   04 04            ADD AL,0x4
 *  004516B9   04 04            ADD AL,0x4
 *  004516BB   04 04            ADD AL,0x4
 *  004516BD   04 04            ADD AL,0x4
 *  004516BF   010404           ADD DWORD PTR SS:[ESP+EAX],EAX
 *  004516C2   04 04            ADD AL,0x4
 *  004516C4   04 02            ADD AL,0x2
 *  004516C6   04 04            ADD AL,0x4
 *  004516C8   03CC             ADD ECX,ESP
 *  004516CA   CC               INT3
 *  004516CB   CC               INT3
 *  004516CC   CC               INT3
 *  004516CD   CC               INT3
 *  004516CE   CC               INT3
 *
 *  EAX 080E2FFA
 *  ECX 015A74A0
 *  EDX 0012FDB4
 *  EBX 015A78D8
 *  ESP 0012FD98
 *  EBP 0012FDCC
 *  ESI 014F05E8
 *  EDI 01504BD0
 *  EIP 00451120 .00451120
 *
 *  0012FD98   00452439  RETURN to .00452439 from .00451120
 *  0012FD9C   080E2FFA ; jichi: text here
 *  0012FDA0   0012FDB4
 *  0012FDA4   00002004
 *  0012FDA8   014F05E8
 *  0012FDAC   00000000
 *  0012FDB0   00000000
 *  0012FDB4   00000002
 *  0012FDB8   00000001
 *  0012FDBC   00000001
 *  0012FDC0   00000001
 *  0012FDC4   00000000
 *
 *  Sample game: 未来ノスタルジア (CMVS1)
 *  004425DC   CC               INT3
 *  004425DD   CC               INT3
 *  004425DE   CC               INT3
 *  004425DF   CC               INT3
 *  004425E0   83EC 58          SUB ESP,0x58
 *  004425E3   53               PUSH EBX
 *  004425E4   55               PUSH EBP
 *  004425E5   56               PUSH ESI
 *  004425E6   8BF1             MOV ESI,ECX
 *  004425E8   8B86 58010000    MOV EAX,DWORD PTR DS:[ESI+0x158]
 *  004425EE   57               PUSH EDI
 *  004425EF   8B7C24 6C        MOV EDI,DWORD PTR SS:[ESP+0x6C]
 *  004425F3   33ED             XOR EBP,EBP
 *  004425F5   50               PUSH EAX
 *  004425F6   896C24 70        MOV DWORD PTR SS:[ESP+0x70],EBP
 *  004425FA   896C24 18        MOV DWORD PTR SS:[ESP+0x18],EBP
 *  004425FE  Hook 896C24 24        MOV DWORD PTR SS:[ESP+0x24],EBP
 *  00442602   FF15 D8335200    CALL DWORD PTR DS:[0x5233D8]             ; user32.GetDC
 *  00442608   68 80000000      PUSH 0x80
 *  0044260D   8D9E B8000000    LEA EBX,DWORD PTR DS:[ESI+0xB8]
 *  00442613   55               PUSH EBP
 *  00442614   53               PUSH EBX
 *  00442615   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
 *  00442619   E8 82340C00      CALL .00505AA0
 *  0044261E   83C4 0C          ADD ESP,0xC
 *  00442621   39AE A4000000    CMP DWORD PTR DS:[ESI+0xA4],EBP
 *  00442627   74 23            JE SHORT .0044264C
 *  00442629   55               PUSH EBP
 *  0044262A   55               PUSH EBP
 *  0044262B   53               PUSH EBX
 *  0044262C   57               PUSH EDI
 *  0044262D   8BCE             MOV ECX,ESI
 *  0044262F   E8 FCF7FFFF      CALL .00441E30
 *  00442634   392B             CMP DWORD PTR DS:[EBX],EBP
 *  00442636   77 08            JA SHORT .00442640
 *  00442638   39AE AC000000    CMP DWORD PTR DS:[ESI+0xAC],EBP
 *  0044263E   74 0C            JE SHORT .0044264C
 *  00442640   8B8E B0000000    MOV ECX,DWORD PTR DS:[ESI+0xB0]
 *  00442646   018E 9C000000    ADD DWORD PTR DS:[ESI+0x9C],ECX
 *  0044264C   8B46 7C          MOV EAX,DWORD PTR DS:[ESI+0x7C]
 *  0044264F   8B4E 70          MOV ECX,DWORD PTR DS:[ESI+0x70]
 *  00442652   894424 64        MOV DWORD PTR SS:[ESP+0x64],EAX
 *  00442656   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  00442659   BA 28000000      MOV EDX,0x28
 *  0044265E   894424 54        MOV DWORD PTR SS:[ESP+0x54],EAX
 *  00442662   8B86 80000000    MOV EAX,DWORD PTR DS:[ESI+0x80]
 *  00442668   83E8 01          SUB EAX,0x1
 *  0044266B   66:895424 40     MOV WORD PTR SS:[ESP+0x40],DX
 *  00442670   8B56 74          MOV EDX,DWORD PTR DS:[ESI+0x74]
 *  00442673   894C24 58        MOV DWORD PTR SS:[ESP+0x58],ECX
 *  00442677   895424 5C        MOV DWORD PTR SS:[ESP+0x5C],EDX
 *  0044267B   896C24 48        MOV DWORD PTR SS:[ESP+0x48],EBP
 *  0044267F   74 1E            JE SHORT .0044269F
 *  00442681   83E8 01          SUB EAX,0x1
 *  00442684   74 0F            JE SHORT .00442695
 *  00442686   83E8 01          SUB EAX,0x1
 *  00442689   75 1C            JNZ SHORT .004426A7
 *  0044268B   C74424 48 030000>MOV DWORD PTR SS:[ESP+0x48],0x3
 *  00442693   EB 12            JMP SHORT .004426A7
 *  00442695   C74424 48 020000>MOV DWORD PTR SS:[ESP+0x48],0x2
 *  0044269D   EB 08            JMP SHORT .004426A7
 *  0044269F   C74424 48 010000>MOV DWORD PTR SS:[ESP+0x48],0x1
 *  004426A7   8B6C24 70        MOV EBP,DWORD PTR SS:[ESP+0x70]
 *  004426AB   33DB             XOR EBX,EBX
 *  004426AD   3BEB             CMP EBP,EBX
 *  004426AF   74 25            JE SHORT .004426D6
 *  004426B1   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  004426B4   894C24 60        MOV DWORD PTR SS:[ESP+0x60],ECX
 *  004426B8   395D 10          CMP DWORD PTR SS:[EBP+0x10],EBX
 *  004426BB   74 06            JE SHORT .004426C3
 *  004426BD   895C24 18        MOV DWORD PTR SS:[ESP+0x18],EBX
 *  004426C1   EB 30            JMP SHORT .004426F3
 *  004426C3   8B96 8C000000    MOV EDX,DWORD PTR DS:[ESI+0x8C]
 *  004426C9   0FAF55 00        IMUL EDX,DWORD PTR SS:[EBP]
 *  004426CD   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  004426D2   F7E2             MUL EDX
 *  004426D4   EB 16            JMP SHORT .004426EC
 *  004426D6   8B46 78          MOV EAX,DWORD PTR DS:[ESI+0x78]
 *  004426D9   8B8E 8C000000    MOV ECX,DWORD PTR DS:[ESI+0x8C]
 *  004426DF   894424 60        MOV DWORD PTR SS:[ESP+0x60],EAX
 *  004426E3   03C9             ADD ECX,ECX
 *  004426E5   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  004426EA   F7E1             MUL ECX
 *  004426EC   C1EA 03          SHR EDX,0x3
 *  004426EF   895424 18        MOV DWORD PTR SS:[ESP+0x18],EDX
 *  004426F3   381F             CMP BYTE PTR DS:[EDI],BL
 *  004426F5   0F84 79040000    JE .00442B74
 *  004426FB   EB 05            JMP SHORT .00442702
 *  004426FD   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00442700   33DB             XOR EBX,EBX
 *  00442702   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  00442705   3C 5C            CMP AL,0x5C
 *  00442707   0F84 C6030000    JE .00442AD3
 *  0044270D   3C 7B            CMP AL,0x7B
 *  0044270F   0F84 70010000    JE .00442885
 *  00442715   50               PUSH EAX
 *  00442716   E8 A50EFCFF      CALL .004035C0
 *  0044271B   85C0             TEST EAX,EAX
 *  0044271D   0F84 A8000000    JE .004427CB
 *  00442723   66:0FBE47 01     MOVSX AX,BYTE PTR DS:[EDI+0x1]
 *  00442728   66:0FBE0F        MOVSX CX,BYTE PTR DS:[EDI]
 *  0044272C   BA FF000000      MOV EDX,0xFF
 *  00442731   66:23C2          AND AX,DX
 *  00442734   66:C1E1 08       SHL CX,0x8
 *  00442738   66:0BC1          OR AX,CX
 *  0044273B   BA 4A810000      MOV EDX,0x814A
 *  00442740   83C7 02          ADD EDI,0x2
 *  00442743   66:894424 42     MOV WORD PTR SS:[ESP+0x42],AX
 *  00442748   66:3BC2          CMP AX,DX
 *  0044274B   75 05            JNZ SHORT .00442752
 *  0044274D   BB 01000000      MOV EBX,0x1
 *  00442752   8B4C24 42        MOV ECX,DWORD PTR SS:[ESP+0x42]
 *  00442756   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  0044275A   50               PUSH EAX
 *  0044275B   51               PUSH ECX
 *  0044275C   6A 00            PUSH 0x0
 *  0044275E   8BCE             MOV ECX,ESI
 *  00442760   E8 1BF9FFFF      CALL .00442080
 *  00442765   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  0044276B   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  00442771   895424 4C        MOV DWORD PTR SS:[ESP+0x4C],EDX
 *  00442775   894424 50        MOV DWORD PTR SS:[ESP+0x50],EAX
 *  00442779   85DB             TEST EBX,EBX
 *  0044277B   74 0F            JE SHORT .0044278C
 *  0044277D   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  00442782   F766 1C          MUL DWORD PTR DS:[ESI+0x1C]
 *  00442785   C1EA 02          SHR EDX,0x2
 *  00442788   295424 4C        SUB DWORD PTR SS:[ESP+0x4C],EDX
 *  0044278C   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
 *  00442790   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  00442794   51               PUSH ECX
 *  00442795   8D5424 44        LEA EDX,DWORD PTR SS:[ESP+0x44]
 *  00442799   52               PUSH EDX
 *  0044279A   50               PUSH EAX
 *  0044279B   8BCE             MOV ECX,ESI
 *  0044279D   E8 0EEFFFFF      CALL .004416B0
 *  004427A2   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  004427A6   85DB             TEST EBX,EBX
 *  004427A8   75 0B            JNZ SHORT .004427B5
 *  004427AA   8B4E 20          MOV ECX,DWORD PTR DS:[ESI+0x20]
 *  004427AD   034E 1C          ADD ECX,DWORD PTR DS:[ESI+0x1C]
 *  004427B0   E9 A5000000      JMP .0044285A
 *  004427B5   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  004427B8   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  004427BD   F7E1             MUL ECX
 *  004427BF   C1EA 02          SHR EDX,0x2
 *  004427C2   D1E9             SHR ECX,1
 *  004427C4   2BCA             SUB ECX,EDX
 *  004427C6   E9 8C000000      JMP .00442857
 *  004427CB  Hook 66:0FBE17        MOVSX DX,BYTE PTR DS:[EDI]
 *  004427CF   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  004427D2   8B4E 0C          MOV ECX,DWORD PTR DS:[ESI+0xC]
 *  004427D5   66:895424 42     MOV WORD PTR SS:[ESP+0x42],DX
 *  004427DA   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  004427DD   2BD0             SUB EDX,EAX
 *  004427DF   2B56 20          SUB EDX,DWORD PTR DS:[ESI+0x20]
 *  004427E2   47               INC EDI
 *  004427E3   03D1             ADD EDX,ECX
 *  004427E5   3996 98000000    CMP DWORD PTR DS:[ESI+0x98],EDX
 *  004427EB   72 37            JB SHORT .00442824
 *  004427ED   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  004427F1   42               INC EDX
 *  004427F2   895424 14        MOV DWORD PTR SS:[ESP+0x14],EDX
 *  004427F6   399C96 B8000000  CMP DWORD PTR DS:[ESI+EDX*4+0xB8],EBX
 *  004427FD   77 08            JA SHORT .00442807
 *  004427FF   399E AC000000    CMP DWORD PTR DS:[ESI+0xAC],EBX
 *  00442805   74 0C            JE SHORT .00442813
 *  00442807   8B96 B0000000    MOV EDX,DWORD PTR DS:[ESI+0xB0]
 *  0044280D   0196 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EDX
 *  00442813   898E 98000000    MOV DWORD PTR DS:[ESI+0x98],ECX
 *  00442819   8B4E 24          MOV ECX,DWORD PTR DS:[ESI+0x24]
 *  0044281C   03C8             ADD ECX,EAX
 *  0044281E   018E 9C000000    ADD DWORD PTR DS:[ESI+0x9C],ECX
 *  00442824   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  0044282A   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  00442830   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  00442834   51               PUSH ECX
 *  00442835   895424 50        MOV DWORD PTR SS:[ESP+0x50],EDX
 *  00442839   8D5424 44        LEA EDX,DWORD PTR SS:[ESP+0x44]
 *  0044283D   894424 54        MOV DWORD PTR SS:[ESP+0x54],EAX
 *  00442841   8B4424 28        MOV EAX,DWORD PTR SS:[ESP+0x28]
 *  00442845   52               PUSH EDX
 *  00442846   50               PUSH EAX
 *  00442847   8BCE             MOV ECX,ESI
 *  00442849   E8 62EEFFFF      CALL .004416B0
 *  0044284E   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  00442851   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  00442855   D1E9             SHR ECX,1
 *  00442857   034E 20          ADD ECX,DWORD PTR DS:[ESI+0x20]
 *  0044285A   8B5424 18        MOV EDX,DWORD PTR SS:[ESP+0x18]
 *  0044285E   018E 98000000    ADD DWORD PTR DS:[ESI+0x98],ECX
 *  00442864   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  00442868   8B4C24 6C        MOV ECX,DWORD PTR SS:[ESP+0x6C]
 *  0044286C   52               PUSH EDX
 *  0044286D   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00442871   50               PUSH EAX
 *  00442872   51               PUSH ECX
 *  00442873   55               PUSH EBP
 *  00442874   52               PUSH EDX
 *  00442875   8BCE             MOV ECX,ESI
 *  00442877   E8 F4F8FFFF      CALL .00442170
 *  0044287C   894424 6C        MOV DWORD PTR SS:[ESP+0x6C],EAX
 *  00442880   E9 E6020000      JMP .00442B6B
 *  00442885   8D4424 14        LEA EAX,DWORD PTR SS:[ESP+0x14]
 *  00442889   50               PUSH EAX
 *  0044288A   53               PUSH EBX
 *  0044288B   53               PUSH EBX
 *  0044288C   8BCE             MOV ECX,ESI
 *  0044288E   E8 EDF7FFFF      CALL .00442080
 *  00442893   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  00442899   2B86 B0000000    SUB EAX,DWORD PTR DS:[ESI+0xB0]
 *  0044289F   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  004428A5   8B5424 6C        MOV EDX,DWORD PTR SS:[ESP+0x6C]
 *  004428A9   894424 38        MOV DWORD PTR SS:[ESP+0x38],EAX
 *  004428AD   8B4424 54        MOV EAX,DWORD PTR SS:[ESP+0x54]
 *  004428B1   894C24 30        MOV DWORD PTR SS:[ESP+0x30],ECX
 *  004428B5   895424 2C        MOV DWORD PTR SS:[ESP+0x2C],EDX
 *  004428B9   BB 01000000      MOV EBX,0x1
 *  004428BE   47               INC EDI
 *  004428BF   894424 3C        MOV DWORD PTR SS:[ESP+0x3C],EAX
 *  004428C3   0FB60F           MOVZX ECX,BYTE PTR DS:[EDI]
 *  004428C6   51               PUSH ECX
 *  004428C7   E8 F40CFCFF      CALL .004035C0
 *  004428CC   85C0             TEST EAX,EAX
 *  004428CE   74 5C            JE SHORT .0044292C
 *  004428D0   66:0FBE57 01     MOVSX DX,BYTE PTR DS:[EDI+0x1]
 *  004428D5   66:0FBE0F        MOVSX CX,BYTE PTR DS:[EDI]
 *  004428D9   B8 FF000000      MOV EAX,0xFF
 *  004428DE   66:23D0          AND DX,AX
 *  004428E1   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  004428E7   66:C1E1 08       SHL CX,0x8
 *  004428EB   66:0BD1          OR DX,CX
 *  004428EE   66:895424 42     MOV WORD PTR SS:[ESP+0x42],DX
 *  004428F3   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  004428F9   8D4C24 28        LEA ECX,DWORD PTR SS:[ESP+0x28]
 *  004428FD   51               PUSH ECX
 *  004428FE   895424 50        MOV DWORD PTR SS:[ESP+0x50],EDX
 *  00442902   8D5424 44        LEA EDX,DWORD PTR SS:[ESP+0x44]
 *  00442906   894424 54        MOV DWORD PTR SS:[ESP+0x54],EAX
 *  0044290A   8B4424 28        MOV EAX,DWORD PTR SS:[ESP+0x28]
 *  0044290E   52               PUSH EDX
 *  0044290F   50               PUSH EAX
 *  00442910   8BCE             MOV ECX,ESI
 *  00442912   83C7 02          ADD EDI,0x2
 *  00442915   E8 96EDFFFF      CALL .004416B0
 *  0044291A   8B4E 20          MOV ECX,DWORD PTR DS:[ESI+0x20]
 *  0044291D   034E 1C          ADD ECX,DWORD PTR DS:[ESI+0x1C]
 *  00442920   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  00442924   018E 98000000    ADD DWORD PTR DS:[ESI+0x98],ECX
 *  0044292A   EB 08            JMP SHORT .00442934
 *  0044292C   803F 2F          CMP BYTE PTR DS:[EDI],0x2F
 *  0044292F   75 02            JNZ SHORT .00442933
 *  00442931   33DB             XOR EBX,EBX
 *  00442933   47               INC EDI
 *  00442934   8B5424 18        MOV EDX,DWORD PTR SS:[ESP+0x18]
 *  00442938   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  0044293C   8B4C24 6C        MOV ECX,DWORD PTR SS:[ESP+0x6C]
 *  00442940   52               PUSH EDX
 *  00442941   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00442945   50               PUSH EAX
 *  00442946   51               PUSH ECX
 *  00442947   55               PUSH EBP
 *  00442948   52               PUSH EDX
 *  00442949   8BCE             MOV ECX,ESI
 *  0044294B   E8 20F8FFFF      CALL .00442170
 *  00442950   894424 6C        MOV DWORD PTR SS:[ESP+0x6C],EAX
 *  00442954   85DB             TEST EBX,EBX
 *  00442956  ^0F85 67FFFFFF    JNZ .004428C3
 *  0044295C   399E A4000000    CMP DWORD PTR DS:[ESI+0xA4],EBX
 *  00442962   0F84 42010000    JE .00442AAA
 *  00442968   8BDF             MOV EBX,EDI
 *  0044296A   33ED             XOR EBP,EBP
 *  0044296C   C74424 1C 010000>MOV DWORD PTR SS:[ESP+0x1C],0x1
 *  00442974   0FB603           MOVZX EAX,BYTE PTR DS:[EBX]
 *  00442977   50               PUSH EAX
 *  00442978   E8 430CFCFF      CALL .004035C0
 *  0044297D   85C0             TEST EAX,EAX
 *  0044297F   74 06            JE SHORT .00442987
 *  00442981   45               INC EBP
 *  00442982   83C3 02          ADD EBX,0x2
 *  00442985   EB 0E            JMP SHORT .00442995
 *  00442987   803B 7D          CMP BYTE PTR DS:[EBX],0x7D
 *  0044298A   75 08            JNZ SHORT .00442994
 *  0044298C   C74424 1C 000000>MOV DWORD PTR SS:[ESP+0x1C],0x0
 *  00442994   43               INC EBX
 *  00442995   837C24 1C 00     CMP DWORD PTR SS:[ESP+0x1C],0x0
 *  0044299A  ^75 D8            JNZ SHORT .00442974
 *  0044299C   8B9E B0000000    MOV EBX,DWORD PTR DS:[ESI+0xB0]
 *  004429A2   8BC3             MOV EAX,EBX
 *  004429A4   0FAFC5           IMUL EAX,EBP
 *  004429A7   8D4C2D 00        LEA ECX,DWORD PTR SS:[EBP+EBP]
 *  004429AB   8B6C24 30        MOV EBP,DWORD PTR SS:[ESP+0x30]
 *  004429AF   894C24 34        MOV DWORD PTR SS:[ESP+0x34],ECX
 *  004429B3   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  004429B9   2BCD             SUB ECX,EBP
 *  004429BB   C1E0 0A          SHL EAX,0xA
 *  004429BE   C1E1 0A          SHL ECX,0xA
 *  004429C1   C1E5 0A          SHL EBP,0xA
 *  004429C4   895C24 54        MOV DWORD PTR SS:[ESP+0x54],EBX
 *  004429C8   C74424 1C 010000>MOV DWORD PTR SS:[ESP+0x1C],0x1
 *  004429D0   3BC1             CMP EAX,ECX
 *  004429D2   76 0B            JBE SHORT .004429DF
 *  004429D4   2BC1             SUB EAX,ECX
 *  004429D6   D1E8             SHR EAX,1
 *  004429D8   2BE8             SUB EBP,EAX
 *  004429DA   C1E3 0A          SHL EBX,0xA
 *  004429DD   EB 21            JMP SHORT .00442A00
 *  004429DF   2BC8             SUB ECX,EAX
 *  004429E1   33D2             XOR EDX,EDX
 *  004429E3   8BC1             MOV EAX,ECX
 *  004429E5   F77424 34        DIV DWORD PTR SS:[ESP+0x34]
 *  004429E9   8B96 B4000000    MOV EDX,DWORD PTR DS:[ESI+0xB4]
 *  004429EF   C1E3 09          SHL EBX,0x9
 *  004429F2   03E8             ADD EBP,EAX
 *  004429F4   03D8             ADD EBX,EAX
 *  004429F6   8D1C5A           LEA EBX,DWORD PTR DS:[EDX+EBX*2]
 *  004429F9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  00442A00   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  00442A03   50               PUSH EAX
 *  00442A04   E8 B70BFCFF      CALL .004035C0
 *  00442A09   85C0             TEST EAX,EAX
 *  00442A0B   74 4F            JE SHORT .00442A5C
 *  00442A0D   66:0FBE4F 01     MOVSX CX,BYTE PTR DS:[EDI+0x1]
 *  00442A12   66:0FBE07        MOVSX AX,BYTE PTR DS:[EDI]
 *  00442A16   BA FF000000      MOV EDX,0xFF
 *  00442A1B   66:23CA          AND CX,DX
 *  00442A1E   8B5424 38        MOV EDX,DWORD PTR SS:[ESP+0x38]
 *  00442A22   66:C1E0 08       SHL AX,0x8
 *  00442A26   66:0BC8          OR CX,AX
 *  00442A29   66:894C24 42     MOV WORD PTR SS:[ESP+0x42],CX
 *  00442A2E   8BCD             MOV ECX,EBP
 *  00442A30   C1E9 0A          SHR ECX,0xA
 *  00442A33   894C24 4C        MOV DWORD PTR SS:[ESP+0x4C],ECX
 *  00442A37   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
 *  00442A3B   50               PUSH EAX
 *  00442A3C   8D4C24 44        LEA ECX,DWORD PTR SS:[ESP+0x44]
 *  00442A40   895424 54        MOV DWORD PTR SS:[ESP+0x54],EDX
 *  00442A44   8B5424 28        MOV EDX,DWORD PTR SS:[ESP+0x28]
 *  00442A48   51               PUSH ECX
 *  00442A49   52               PUSH EDX
 *  00442A4A   8BCE             MOV ECX,ESI
 *  00442A4C   83C7 02          ADD EDI,0x2
 *  00442A4F   E8 5CECFFFF      CALL .004416B0
 *  00442A54   894424 10        MOV DWORD PTR SS:[ESP+0x10],EAX
 *  00442A58   03EB             ADD EBP,EBX
 *  00442A5A   EB 0E            JMP SHORT .00442A6A
 *  00442A5C   803F 7D          CMP BYTE PTR DS:[EDI],0x7D
 *  00442A5F   75 08            JNZ SHORT .00442A69
 *  00442A61   C74424 1C 000000>MOV DWORD PTR SS:[ESP+0x1C],0x0
 *  00442A69   47               INC EDI
 *  00442A6A   8B4424 18        MOV EAX,DWORD PTR SS:[ESP+0x18]
 *  00442A6E   8B4C24 20        MOV ECX,DWORD PTR SS:[ESP+0x20]
 *  00442A72   8B5424 2C        MOV EDX,DWORD PTR SS:[ESP+0x2C]
 *  00442A76   50               PUSH EAX
 *  00442A77   8B4424 74        MOV EAX,DWORD PTR SS:[ESP+0x74]
 *  00442A7B   51               PUSH ECX
 *  00442A7C   8B4C24 18        MOV ECX,DWORD PTR SS:[ESP+0x18]
 *  00442A80   52               PUSH EDX
 *  00442A81   50               PUSH EAX
 *  00442A82   51               PUSH ECX
 *  00442A83   8BCE             MOV ECX,ESI
 *  00442A85   E8 E6F6FFFF      CALL .00442170
 *  00442A8A   837C24 1C 00     CMP DWORD PTR SS:[ESP+0x1C],0x0
 *  00442A8F   894424 2C        MOV DWORD PTR SS:[ESP+0x2C],EAX
 *  00442A93  ^0F85 67FFFFFF    JNZ .00442A00
 *  00442A99   8B5424 3C        MOV EDX,DWORD PTR SS:[ESP+0x3C]
 *  00442A9D   8B6C24 70        MOV EBP,DWORD PTR SS:[ESP+0x70]
 *  00442AA1   895424 54        MOV DWORD PTR SS:[ESP+0x54],EDX
 *  00442AA5   E9 C1000000      JMP .00442B6B
 *  00442AAA   BB 01000000      MOV EBX,0x1
 *  00442AAF   90               NOP
 *  00442AB0   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  00442AB3   50               PUSH EAX
 *  00442AB4   E8 070BFCFF      CALL .004035C0
 *  00442AB9   85C0             TEST EAX,EAX
 *  00442ABB   74 05            JE SHORT .00442AC2
 *  00442ABD   83C7 02          ADD EDI,0x2
 *  00442AC0   EB 08            JMP SHORT .00442ACA
 *  00442AC2   803F 7D          CMP BYTE PTR DS:[EDI],0x7D
 *  00442AC5   75 02            JNZ SHORT .00442AC9
 *  00442AC7   33DB             XOR EBX,EBX
 *  00442AC9   47               INC EDI
 *  00442ACA   85DB             TEST EBX,EBX
 *  00442ACC  ^75 E2            JNZ SHORT .00442AB0
 *  00442ACE   E9 98000000      JMP .00442B6B
 *  00442AD3   0FBE47 01        MOVSX EAX,BYTE PTR DS:[EDI+0x1]
 *  00442AD7   83C0 9D          ADD EAX,-0x63
 *  00442ADA   83F8 14          CMP EAX,0x14
 *  00442ADD   0F87 88000000    JA .00442B6B
 *  00442AE3   0FB688 AC2B4400  MOVZX ECX,BYTE PTR DS:[EAX+0x442BAC]
 *  00442AEA   FF248D 982B4400  JMP DWORD PTR DS:[ECX*4+0x442B98]
 *  00442AF1   8B46 24          MOV EAX,DWORD PTR DS:[ESI+0x24]
 *  00442AF4   0346 1C          ADD EAX,DWORD PTR DS:[ESI+0x1C]
 *  00442AF7   8B4C24 14        MOV ECX,DWORD PTR SS:[ESP+0x14]
 *  00442AFB   8B56 0C          MOV EDX,DWORD PTR DS:[ESI+0xC]
 *  00442AFE   0186 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EAX
 *  00442B04   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  00442B0A   41               INC ECX
 *  00442B0B   8996 98000000    MOV DWORD PTR DS:[ESI+0x98],EDX
 *  00442B11   894C24 14        MOV DWORD PTR SS:[ESP+0x14],ECX
 *  00442B15   399C8E B8000000  CMP DWORD PTR DS:[ESI+ECX*4+0xB8],EBX
 *  00442B1C   77 08            JA SHORT .00442B26
 *  00442B1E   399E AC000000    CMP DWORD PTR DS:[ESI+0xAC],EBX
 *  00442B24   74 42            JE SHORT .00442B68
 *  00442B26   8B8E B0000000    MOV ECX,DWORD PTR DS:[ESI+0xB0]
 *  00442B2C   03C8             ADD ECX,EAX
 *  00442B2E   898E 9C000000    MOV DWORD PTR DS:[ESI+0x9C],ECX
 *  00442B34   EB 32            JMP SHORT .00442B68
 *  00442B36   8BCE             MOV ECX,ESI
 *  00442B38   E8 03F0FFFF      CALL .00441B40
 *  00442B3D   EB 29            JMP SHORT .00442B68
 *  00442B3F   8A47 02          MOV AL,BYTE PTR DS:[EDI+0x2]
 *  00442B42   3C 63            CMP AL,0x63
 *  00442B44   74 0D            JE SHORT .00442B53
 *  00442B46   3C 73            CMP AL,0x73
 *  00442B48   75 15            JNZ SHORT .00442B5F
 *  00442B4A   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
 *  00442B4E   83C7 03          ADD EDI,0x3
 *  00442B51   EB 18            JMP SHORT .00442B6B
 *  00442B53   C74424 20 010000>MOV DWORD PTR SS:[ESP+0x20],0x1
 *  00442B5B   895C24 6C        MOV DWORD PTR SS:[ESP+0x6C],EBX
 *  00442B5F   83C7 03          ADD EDI,0x3
 *  00442B62   EB 07            JMP SHORT .00442B6B
 *  00442B64   895C24 6C        MOV DWORD PTR SS:[ESP+0x6C],EBX
 *  00442B68   83C7 02          ADD EDI,0x2
 *  00442B6B   803F 00          CMP BYTE PTR DS:[EDI],0x0
 *  00442B6E  ^0F85 8CFBFFFF    JNZ .00442700
 *  00442B74   8B5424 24        MOV EDX,DWORD PTR SS:[ESP+0x24]
 *  00442B78   8B86 58010000    MOV EAX,DWORD PTR DS:[ESI+0x158]
 *  00442B7E   52               PUSH EDX
 *  00442B7F   50               PUSH EAX
 *  00442B80   FF15 DC335200    CALL DWORD PTR DS:[0x5233DC]             ; user32.ReleaseDC
 *  00442B86   5F               POP EDI
 *  00442B87   5E               POP ESI
 *  00442B88   5D               POP EBP
 *  00442B89   B8 01000000      MOV EAX,0x1
 *  00442B8E   5B               POP EBX
 *  00442B8F   83C4 58          ADD ESP,0x58
 *  00442B92   C2 0800          RETN 0x8
 *  00442B95   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  00442B98   36:2B4400 F1     SUB EAX,DWORD PTR SS:[EAX+EAX-0xF]
 *  00442B9D   2A4400 64        SUB AL,BYTE PTR DS:[EAX+EAX+0x64]
 *  00442BA1   2B4400 3F        SUB EAX,DWORD PTR DS:[EAX+EAX+0x3F]
 *  00442BA5   2B4400 6B        SUB EAX,DWORD PTR DS:[EAX+EAX+0x6B]
 *  00442BA9   2B4400 00        SUB EAX,DWORD PTR DS:[EAX+EAX]
 *  00442BAD   04 04            ADD AL,0x4
 *  00442BAF   04 04            ADD AL,0x4
 *  00442BB1   04 04            ADD AL,0x4
 *  00442BB3   04 04            ADD AL,0x4
 *  00442BB5   04 04            ADD AL,0x4
 *  00442BB7   010404           ADD DWORD PTR SS:[ESP+EAX],EAX
 *  00442BBA   04 04            ADD AL,0x4
 *  00442BBC   04 02            ADD AL,0x2
 *  00442BBE   04 04            ADD AL,0x4
 *  00442BC0   03CC             ADD ECX,ESP
 *  00442BC2   CC               INT3
 *  00442BC3   CC               INT3
 *  00442BC4   CC               INT3
 *  00442BC5   CC               INT3
 *  00442BC6   CC               INT3
 *  00442BC7   CC               INT3
 *  00442BC8   CC               INT3
 *  00442BC9   CC               INT3
 *  00442BCA   CC               INT3
 */
namespace
{
  bool attach(const uint8_t pattern[], int patternSize, DWORD startAddress, DWORD stopAddress)
  {
    ULONG addr = MemDbg::findBytes(pattern, patternSize, startAddress, stopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = EMBED_ABLE | USING_STRING | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      std::string str = buffer->strA();
      std::string result1 = re::sub(str, "\\{(.*?)/(.*?)\\}", "$1");
      buffer->from(result1);
    };

    return NewHook(hp, "EmbedCMVS");
  };
}
bool attachScenarioHook(ULONG startAddress, ULONG stopAddress)
{

  // This pattern is selected by comparing two CMVS games
  const uint8_t bytes[] = {
      0xb8, 0xcd, 0xcc, 0xcc, 0xcc, // 004512de   b8 cdcccccc      mov eax,0xcccccccd
      0xf7, 0xe1,                   // 004512e3   f7e1             mul ecx
      0xc1, 0xea, 0x02,             // 004512e5   c1ea 02          shr edx,0x2
      0xd1, 0xe9,                   // 004512e8   d1e9             shr ecx,1
      0x2b, 0xca                    // 004512ea   2bca             sub ecx,edx
  };
  // const uint8_t bytes[] = {  //青春&国记的人名&选择支
  //   0xb8, 0xcd,0xcc,0xcc,0xcc,  // 004512de   b8 cdcccccc      mov eax,0xcccccccd
  //   0xf7,0xe1,                  // 004512e3   f7e1             mul ecx
  //   0xd1,0xe9,                  // 004512e8   d1e9             shr ecx,1

  //  0xc1,0xea, 0x02,            // 004512e5   c1ea 02          shr edx,0x2
  //  0x2b,0xca                   // 004512ea   2bca             sub ecx,edx
  //};
  const uint8_t bytes_kunado_kukoki[] = {

      0xf7, 0xe1,
      0x8b, 0x85, 0xd8, 0xfd, 0xff, 0xff,
      0xd1, 0xe9,
      0xc1, 0xea, 0x02,
      0x2b, 0xca};
  return attach(bytes, sizeof(bytes), startAddress, stopAddress) || attach(bytes_kunado_kukoki, sizeof(bytes_kunado_kukoki), startAddress, stopAddress);
}
/**
 *  FIXME: This function exists but is not called for クロノクロック when painting backlog.
 *
 *  Sample bake: ハピメア
 *
 *  Backlog function, found by tracking all callers of ::GetDC:
 *
 *  0044ACAE   CC               INT3
 *  0044ACAF   CC               INT3
 *  0044ACB0   55               PUSH EBP
 *  0044ACB1   8BEC             MOV EBP,ESP
 *  0044ACB3   83EC 30          SUB ESP,0x30
 *  0044ACB6   56               PUSH ESI
 *  0044ACB7   8BF1             MOV ESI,ECX
 *  0044ACB9   8B86 58010000    MOV EAX,DWORD PTR DS:[ESI+0x158]
 *  0044ACBF   57               PUSH EDI
 *  0044ACC0   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
 *  0044ACC3   50               PUSH EAX
 *  0044ACC4   C745 08 00000000 MOV DWORD PTR SS:[EBP+0x8],0x0
 *  0044ACCB   FF15 D4F35300    CALL DWORD PTR DS:[0x53F3D4]             ; user32.GetDC
 *  0044ACD1   68 80000000      PUSH 0x80
 *  0044ACD6   8D8E B8000000    LEA ECX,DWORD PTR DS:[ESI+0xB8]
 *  0044ACDC   6A 00            PUSH 0x0
 *  0044ACDE   51               PUSH ECX
 *  0044ACDF   8945 FC          MOV DWORD PTR SS:[EBP-0x4],EAX
 *  0044ACE2   E8 F9870D00      CALL .005234E0
 *  0044ACE7   8B46 7C          MOV EAX,DWORD PTR DS:[ESI+0x7C]
 *  0044ACEA   8B4E 70          MOV ECX,DWORD PTR DS:[ESI+0x70]
 *  0044ACED   8945 F4          MOV DWORD PTR SS:[EBP-0xC],EAX
 *  0044ACF0   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  0044ACF3   BA 28000000      MOV EDX,0x28
 *  0044ACF8   8945 E4          MOV DWORD PTR SS:[EBP-0x1C],EAX
 *  0044ACFB   8B86 80000000    MOV EAX,DWORD PTR DS:[ESI+0x80]
 *  0044AD01   66:8955 D0       MOV WORD PTR SS:[EBP-0x30],DX
 *  0044AD05   8B56 74          MOV EDX,DWORD PTR DS:[ESI+0x74]
 *  0044AD08   83C4 0C          ADD ESP,0xC
 *  0044AD0B   48               DEC EAX
 *  0044AD0C   894D E8          MOV DWORD PTR SS:[EBP-0x18],ECX
 *  0044AD0F   8955 EC          MOV DWORD PTR SS:[EBP-0x14],EDX
 *  0044AD12   C745 D8 00000000 MOV DWORD PTR SS:[EBP-0x28],0x0
 *  0044AD19   74 18            JE SHORT .0044AD33
 *  0044AD1B   48               DEC EAX
 *  0044AD1C   74 0C            JE SHORT .0044AD2A
 *  0044AD1E   48               DEC EAX
 *  0044AD1F   75 19            JNZ SHORT .0044AD3A
 *  0044AD21   C745 D8 03000000 MOV DWORD PTR SS:[EBP-0x28],0x3
 *  0044AD28   EB 10            JMP SHORT .0044AD3A
 *  0044AD2A   C745 D8 02000000 MOV DWORD PTR SS:[EBP-0x28],0x2
 *  0044AD31   EB 07            JMP SHORT .0044AD3A
 *  0044AD33   C745 D8 01000000 MOV DWORD PTR SS:[EBP-0x28],0x1
 *  0044AD3A   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  0044AD3D   85C0             TEST EAX,EAX
 *  0044AD3F   74 08            JE SHORT .0044AD49
 *  0044AD41   8B48 0C          MOV ECX,DWORD PTR DS:[EAX+0xC]
 *  0044AD44   894D F0          MOV DWORD PTR SS:[EBP-0x10],ECX
 *  0044AD47   EB 06            JMP SHORT .0044AD4F
 *  0044AD49   8B56 78          MOV EDX,DWORD PTR DS:[ESI+0x78]
 *  0044AD4C   8955 F0          MOV DWORD PTR SS:[EBP-0x10],EDX
 *  0044AD4F   803F 00          CMP BYTE PTR DS:[EDI],0x0
 *  0044AD52   0F84 65020000    JE .0044AFBD
 *  0044AD58   53               PUSH EBX
 *  0044AD59   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  0044AD60   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  0044AD63   3C 5C            CMP AL,0x5C
 *  0044AD65   0F84 16020000    JE .0044AF81
 *  0044AD6B   3C 7B            CMP AL,0x7B
 *  0044AD6D   0F84 63010000    JE .0044AED6
 *  0044AD73   50               PUSH EAX
 *  0044AD74   E8 778DFBFF      CALL .00403AF0
 *  0044AD79   85C0             TEST EAX,EAX
 *  0044AD7B   0F84 AC000000    JE .0044AE2D
 *  0044AD81   66:0FBE47 01     MOVSX AX,BYTE PTR DS:[EDI+0x1]
 *  0044AD86   66:0FBE17        MOVSX DX,BYTE PTR DS:[EDI]
 *  0044AD8A   B9 FF000000      MOV ECX,0xFF
 *  0044AD8F   66:23C1          AND AX,CX
 *  0044AD92   66:C1E2 08       SHL DX,0x8
 *  0044AD96   66:0BC2          OR AX,DX
 *  0044AD99   B9 4A810000      MOV ECX,0x814A
 *  0044AD9E   83C7 02          ADD EDI,0x2
 *  0044ADA1   33DB             XOR EBX,EBX
 *  0044ADA3   66:8945 D2       MOV WORD PTR SS:[EBP-0x2E],AX
 *  0044ADA7   66:3BC1          CMP AX,CX
 *  0044ADAA   75 05            JNZ SHORT .0044ADB1
 *  0044ADAC   BB 01000000      MOV EBX,0x1
 *  0044ADB1   8B45 D2          MOV EAX,DWORD PTR SS:[EBP-0x2E]
 *  0044ADB4   8D55 08          LEA EDX,DWORD PTR SS:[EBP+0x8]
 *  0044ADB7   52               PUSH EDX
 *  0044ADB8   50               PUSH EAX
 *  0044ADB9   6A 00            PUSH 0x0
 *  0044ADBB   8BCE             MOV ECX,ESI
 *  0044ADBD   E8 FEFCFFFF      CALL .0044AAC0
 *  0044ADC2   8B8E 98000000    MOV ECX,DWORD PTR DS:[ESI+0x98]
 *  0044ADC8   8B96 9C000000    MOV EDX,DWORD PTR DS:[ESI+0x9C]
 *  0044ADCE   894D DC          MOV DWORD PTR SS:[EBP-0x24],ECX
 *  0044ADD1   8955 E0          MOV DWORD PTR SS:[EBP-0x20],EDX
 *  0044ADD4   85DB             TEST EBX,EBX
 *  0044ADD6   74 0E            JE SHORT .0044ADE6
 *  0044ADD8   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  0044ADDD   F766 1C          MUL DWORD PTR DS:[ESI+0x1C]
 *  0044ADE0   C1EA 02          SHR EDX,0x2
 *  0044ADE3   2955 DC          SUB DWORD PTR SS:[EBP-0x24],EDX
 *  0044ADE6   8B55 FC          MOV EDX,DWORD PTR SS:[EBP-0x4]
 *  0044ADE9   8D45 F8          LEA EAX,DWORD PTR SS:[EBP-0x8]
 *  0044ADEC   50               PUSH EAX
 *  0044ADED   8D4D D0          LEA ECX,DWORD PTR SS:[EBP-0x30]
 *  0044ADF0   51               PUSH ECX
 *  0044ADF1   52               PUSH EDX
 *  0044ADF2   8BCE             MOV ECX,ESI
 *  0044ADF4   E8 87F2FFFF      CALL .0044A080
 *  0044ADF9   85DB             TEST EBX,EBX
 *  0044ADFB   75 11            JNZ SHORT .0044AE0E
 *  0044ADFD   8B46 20          MOV EAX,DWORD PTR DS:[ESI+0x20]
 *  0044AE00   0346 1C          ADD EAX,DWORD PTR DS:[ESI+0x1C]
 *  0044AE03   0186 98000000    ADD DWORD PTR DS:[ESI+0x98],EAX
 *  0044AE09   E9 A5010000      JMP .0044AFB3
 *  0044AE0E   8B4E 1C          MOV ECX,DWORD PTR DS:[ESI+0x1C]
 *  0044AE11   B8 CDCCCCCC      MOV EAX,0xCCCCCCCD
 *  0044AE16   F7E1             MUL ECX
 *  0044AE18   D1E9             SHR ECX,1
 *  0044AE1A   C1EA 02          SHR EDX,0x2
 *  0044AE1D   2BCA             SUB ECX,EDX
 *  0044AE1F   034E 20          ADD ECX,DWORD PTR DS:[ESI+0x20]
 *  0044AE22   018E 98000000    ADD DWORD PTR DS:[ESI+0x98],ECX
 *  0044AE28   E9 86010000      JMP .0044AFB3
 *  0044AE2D   66:0FBE0F        MOVSX CX,BYTE PTR DS:[EDI]
 *  0044AE31   8B56 14          MOV EDX,DWORD PTR DS:[ESI+0x14]
 *  0044AE34   2B56 20          SUB EDX,DWORD PTR DS:[ESI+0x20]
 *  0044AE37   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  0044AE3A   66:894D D2       MOV WORD PTR SS:[EBP-0x2E],CX
 *  0044AE3E   8B4E 0C          MOV ECX,DWORD PTR DS:[ESI+0xC]
 *  0044AE41   2BD0             SUB EDX,EAX
 *  0044AE43   03D1             ADD EDX,ECX
 *  0044AE45   47               INC EDI
 *  0044AE46   3996 98000000    CMP DWORD PTR DS:[ESI+0x98],EDX
 *  0044AE4C   72 37            JB SHORT .0044AE85
 *  0044AE4E   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
 *  0044AE51   42               INC EDX
 *  0044AE52   83BC96 B8000000 >CMP DWORD PTR DS:[ESI+EDX*4+0xB8],0x0
 *  0044AE5A   8955 08          MOV DWORD PTR SS:[EBP+0x8],EDX
 *  0044AE5D   77 09            JA SHORT .0044AE68
 *  0044AE5F   83BE AC000000 00 CMP DWORD PTR DS:[ESI+0xAC],0x0
 *  0044AE66   74 0C            JE SHORT .0044AE74
 *  0044AE68   8B96 B0000000    MOV EDX,DWORD PTR DS:[ESI+0xB0]
 *  0044AE6E   0196 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EDX
 *  0044AE74   898E 98000000    MOV DWORD PTR DS:[ESI+0x98],ECX
 *  0044AE7A   8B4E 24          MOV ECX,DWORD PTR DS:[ESI+0x24]
 *  0044AE7D   03C8             ADD ECX,EAX
 *  0044AE7F   018E 9C000000    ADD DWORD PTR DS:[ESI+0x9C],ECX
 *  0044AE85   8B96 98000000    MOV EDX,DWORD PTR DS:[ESI+0x98]
 *  0044AE8B   8B86 9C000000    MOV EAX,DWORD PTR DS:[ESI+0x9C]
 *  0044AE91   8D4D F8          LEA ECX,DWORD PTR SS:[EBP-0x8]
 *  0044AE94   51               PUSH ECX
 *  0044AE95   8955 DC          MOV DWORD PTR SS:[EBP-0x24],EDX
 *  0044AE98   8D55 D0          LEA EDX,DWORD PTR SS:[EBP-0x30]
 *  0044AE9B   8945 E0          MOV DWORD PTR SS:[EBP-0x20],EAX
 *  0044AE9E   8B45 FC          MOV EAX,DWORD PTR SS:[EBP-0x4]
 *  0044AEA1   52               PUSH EDX
 *  0044AEA2   50               PUSH EAX
 *  0044AEA3   8BCE             MOV ECX,ESI
 *  0044AEA5   E8 D6F1FFFF      CALL .0044A080
 *  0044AEAA   8B46 1C          MOV EAX,DWORD PTR DS:[ESI+0x1C]
 *  0044AEAD   8B4D F8          MOV ECX,DWORD PTR SS:[EBP-0x8]
 *  0044AEB0   D1E8             SHR EAX,1
 *  0044AEB2   3BC8             CMP ECX,EAX
 *  0044AEB4   77 10            JA SHORT .0044AEC6
 *  0044AEB6   8B4E 20          MOV ECX,DWORD PTR DS:[ESI+0x20]
 *  0044AEB9   03C8             ADD ECX,EAX
 *  0044AEBB   018E 98000000    ADD DWORD PTR DS:[ESI+0x98],ECX
 *  0044AEC1   E9 ED000000      JMP .0044AFB3
 *  0044AEC6   8B56 20          MOV EDX,DWORD PTR DS:[ESI+0x20]
 *  0044AEC9   03D1             ADD EDX,ECX
 *  0044AECB   0196 98000000    ADD DWORD PTR DS:[ESI+0x98],EDX
 *  0044AED1   E9 DD000000      JMP .0044AFB3
 *  0044AED6   47               INC EDI
 *  0044AED7   BB 01000000      MOV EBX,0x1
 *  0044AEDC   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  0044AEE0   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  0044AEE3   50               PUSH EAX
 *  0044AEE4   E8 078CFBFF      CALL .00403AF0
 *  0044AEE9   85C0             TEST EAX,EAX
 *  0044AEEB   74 63            JE SHORT .0044AF50
 *  0044AEED   66:0FBE4F 01     MOVSX CX,BYTE PTR DS:[EDI+0x1]
 *  0044AEF2   66:0FBE07        MOVSX AX,BYTE PTR DS:[EDI]
 *  0044AEF6   BA FF000000      MOV EDX,0xFF
 *  0044AEFB   66:23CA          AND CX,DX
 *  0044AEFE   66:C1E0 08       SHL AX,0x8
 *  0044AF02   66:0BC8          OR CX,AX
 *  0044AF05   66:894D D2       MOV WORD PTR SS:[EBP-0x2E],CX
 *  0044AF09   8B55 D2          MOV EDX,DWORD PTR SS:[EBP-0x2E]
 *  0044AF0C   8D4D 08          LEA ECX,DWORD PTR SS:[EBP+0x8]
 *  0044AF0F   51               PUSH ECX
 *  0044AF10   52               PUSH EDX
 *  0044AF11   6A 00            PUSH 0x0
 *  0044AF13   8BCE             MOV ECX,ESI
 *  0044AF15   83C7 02          ADD EDI,0x2
 *  0044AF18   E8 A3FBFFFF      CALL .0044AAC0
 *  0044AF1D   8B86 98000000    MOV EAX,DWORD PTR DS:[ESI+0x98]
 *  0044AF23   8B8E 9C000000    MOV ECX,DWORD PTR DS:[ESI+0x9C]
 *  0044AF29   8D55 F8          LEA EDX,DWORD PTR SS:[EBP-0x8]
 *  0044AF2C   8945 DC          MOV DWORD PTR SS:[EBP-0x24],EAX
 *  0044AF2F   52               PUSH EDX
 *  0044AF30   894D E0          MOV DWORD PTR SS:[EBP-0x20],ECX
 *  0044AF33   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  0044AF36   8D45 D0          LEA EAX,DWORD PTR SS:[EBP-0x30]
 *  0044AF39   50               PUSH EAX
 *  0044AF3A   51               PUSH ECX
 *  0044AF3B   8BCE             MOV ECX,ESI
 *  0044AF3D   E8 3EF1FFFF      CALL .0044A080
 *  0044AF42   8B56 20          MOV EDX,DWORD PTR DS:[ESI+0x20]
 *  0044AF45   0356 1C          ADD EDX,DWORD PTR DS:[ESI+0x1C]
 *  0044AF48   0196 98000000    ADD DWORD PTR DS:[ESI+0x98],EDX
 *  0044AF4E   EB 08            JMP SHORT .0044AF58
 *  0044AF50   803F 2F          CMP BYTE PTR DS:[EDI],0x2F
 *  0044AF53   75 02            JNZ SHORT .0044AF57
 *  0044AF55   33DB             XOR EBX,EBX
 *  0044AF57   47               INC EDI
 *  0044AF58   85DB             TEST EBX,EBX
 *  0044AF5A  ^75 84            JNZ SHORT .0044AEE0
 *  0044AF5C   BB 01000000      MOV EBX,0x1
 *  0044AF61   0FB607           MOVZX EAX,BYTE PTR DS:[EDI]
 *  0044AF64   50               PUSH EAX
 *  0044AF65   E8 868BFBFF      CALL .00403AF0
 *  0044AF6A   85C0             TEST EAX,EAX
 *  0044AF6C   74 05            JE SHORT .0044AF73
 *  0044AF6E   83C7 02          ADD EDI,0x2
 *  0044AF71   EB 08            JMP SHORT .0044AF7B
 *  0044AF73   803F 7D          CMP BYTE PTR DS:[EDI],0x7D
 *  0044AF76   75 02            JNZ SHORT .0044AF7A
 *  0044AF78   33DB             XOR EBX,EBX
 *  0044AF7A   47               INC EDI
 *  0044AF7B   85DB             TEST EBX,EBX
 *  0044AF7D  ^75 E2            JNZ SHORT .0044AF61
 *  0044AF7F   EB 32            JMP SHORT .0044AFB3
 *  0044AF81   0FBE47 01        MOVSX EAX,BYTE PTR DS:[EDI+0x1]
 *  0044AF85   83C0 9D          ADD EAX,-0x63
 *  0044AF88   83F8 14          CMP EAX,0x14
 *  0044AF8B   77 26            JA SHORT .0044AFB3
 *  0044AF8D   0FB688 F0AF4400  MOVZX ECX,BYTE PTR DS:[EAX+0x44AFF0]
 *  0044AF94   FF248D E0AF4400  JMP DWORD PTR DS:[ECX*4+0x44AFE0]
 *  0044AF9B   8B46 24          MOV EAX,DWORD PTR DS:[ESI+0x24]
 *  0044AF9E   0346 1C          ADD EAX,DWORD PTR DS:[ESI+0x1C]
 *  0044AFA1   8B56 0C          MOV EDX,DWORD PTR DS:[ESI+0xC]
 *  0044AFA4   0186 9C000000    ADD DWORD PTR DS:[ESI+0x9C],EAX
 *  0044AFAA   8996 98000000    MOV DWORD PTR DS:[ESI+0x98],EDX
 *  0044AFB0   83C7 02          ADD EDI,0x2
 *  0044AFB3   803F 00          CMP BYTE PTR DS:[EDI],0x0
 *  0044AFB6  ^0F85 A4FDFFFF    JNZ .0044AD60
 *  0044AFBC   5B               POP EBX
 *  0044AFBD   8B4D FC          MOV ECX,DWORD PTR SS:[EBP-0x4]
 *  0044AFC0   8B96 58010000    MOV EDX,DWORD PTR DS:[ESI+0x158]
 *  0044AFC6   51               PUSH ECX
 *  0044AFC7   52               PUSH EDX
 *  0044AFC8   FF15 D8F35300    CALL DWORD PTR DS:[0x53F3D8]             ; user32.ReleaseDC
 *  0044AFCE   5F               POP EDI
 *  0044AFCF   B8 01000000      MOV EAX,0x1
 *  0044AFD4   5E               POP ESI
 *  0044AFD5   8BE5             MOV ESP,EBP
 *  0044AFD7   5D               POP EBP
 *  0044AFD8   C2 0800          RETN 0x8
 *  0044AFDB   83C7 03          ADD EDI,0x3
 *  0044AFDE  ^EB D3            JMP SHORT .0044AFB3
 *  0044AFE0   B0 AF            MOV AL,0xAF
 *  0044AFE2   44               INC ESP
 *  0044AFE3   009B AF4400DB    ADD BYTE PTR DS:[EBX+0xDB0044AF],BL
 *  0044AFE9   AF               SCAS DWORD PTR ES:[EDI]
 *  0044AFEA   44               INC ESP
 *  0044AFEB   00B3 AF440000    ADD BYTE PTR DS:[EBX+0x44AF],DH
 *  0044AFF1   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFF3   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFF5   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFF7   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFF9   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFFB   0103             ADD DWORD PTR DS:[EBX],EAX
 *  0044AFFD   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044AFFF   0303             ADD EAX,DWORD PTR DS:[EBX]
 *  0044B001   0003             ADD BYTE PTR DS:[EBX],AL
 *  0044B003   0302             ADD EAX,DWORD PTR DS:[EDX]
 *  0044B005   CC               INT3
 *  0044B006   CC               INT3
 *  0044B007   CC               INT3
 *  0044B008   CC               INT3
 */

bool attachHistoryHook(ULONG startAddress, ULONG stopAddress)
{
  const uint8_t bytes[] = {
      0xb8, 0xcd, 0xcc, 0xcc, 0xcc, // 0044ae11   b8 cdcccccc      mov eax,0xcccccccd
      0xf7, 0xe1,                   // 0044ae16   f7e1             mul ecx
      0xd1, 0xe9,                   // 0044ae18   d1e9             shr ecx,1
      0xc1, 0xea, 0x02,             // 0044ae1a   c1ea 02          shr edx,0x2
      0x2b, 0xca                    // 0044ae1d   2bca             sub ecx,edx
  };

  return attach(bytes, sizeof(bytes), startAddress, stopAddress);
}
static bool h2()
{
  const uint8_t BYTES_happymeafd[] = {
      // ハピメアFD RE.ver
      0x8a, 0x0f,
      0x8a, 0xc1,
      0x3c, 0x5c,
      0x0f, 0x84, XX4,
      0x3c, 0x7b,
      0x0f, 0x84, XX4,
      0x51,
      0xe8, XX4,
      0x85, 0xc0};
  for (auto addr : Util::SearchMemory(BYTES_happymeafd, sizeof(BYTES_happymeafd), PAGE_EXECUTE_READWRITE, processStartAddress, processStopAddress))
  {
    auto faddr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!faddr)
      continue;
    BYTE check[] = {
        0x66, 0x0f, 0xbe, 0x07,
        0x66, 0x0f, 0xbe, 0x4f, 0x01,
        0x83, 0xc7, 0x02,
        0x66, 0xc1, 0xe0, 0x08,
        0x66, 0x23, 0xcb,
        0x33, 0xdb,
        0x66, 0x0b, 0xc8,
        0xb8, 0x4a, 0x81, 0x00, 0x00};
    if (!MemDbg::findBytes(check, sizeof(check), addr, addr + 0x100))
      continue;
    HookParam hp;
    hp.address = faddr;
    hp.offset = stackoffset(1);
    hp.type = EMBED_ABLE | USING_STRING | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "EmbedCMVS");
  }
  return false;
}
bool CMVS::attach_function()
{
  bool embed = attachScenarioHook(processStartAddress, processStopAddress);
  if (embed)
    attachHistoryHook(processStartAddress, processStopAddress);
  embed |= h2();
  return InsertCMVSHook() || embed;
}