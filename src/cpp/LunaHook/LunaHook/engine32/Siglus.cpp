#include "Siglus.h"
namespace
{ // unnamed

  /**
   *  jichi 8/17/2013:  SiglusEngine from siglusengine.exe
   *  The old hook does not work for new games.
   *  The new hook cannot recognize character names.
   *  Insert old first. As the pattern could also be found in the old engine.
   */

  /** jichi 10/25/2014: new SiglusEngine3 that can extract character name
   *
   *  Sample game: リア兂�ラスメイト孕ませ催� -- /HW-4@F67DC:SiglusEngine.exe
   *  The character is in [edx+ecx*2]. Text in edx, and offset in ecx.
   *
   *  002667be   cc               int3
   *  002667bf   cc               int3
   *  002667c0   55               push ebp ; jichi: hook here
   *  002667c1   8bec             mov ebp,esp
   *  002667c3   8bd1             mov edx,ecx
   *  002667c5   8b4d 0c          mov ecx,dword ptr ss:[ebp+0xc]
   *  002667c8   83f9 01          cmp ecx,0x1
   *  002667cb   75 17            jnz short .002667e4
   *  002667cd   837a 14 08       cmp dword ptr ds:[edx+0x14],0x8
   *  002667d1   72 02            jb short .002667d5
   *  002667d3   8b12             mov edx,dword ptr ds:[edx]
   *  002667d5   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
   *  002667d8   66:8b45 10       mov ax,word ptr ss:[ebp+0x10]
   *  002667dc   66:89044a        mov word ptr ds:[edx+ecx*2],ax  ; jichi: wchar_t is in ax
   *  002667e0   5d               pop ebp
   *  002667e1   c2 0c00          retn 0xc
   *  002667e4   837a 14 08       cmp dword ptr ds:[edx+0x14],0x8
   *  002667e8   72 02            jb short .002667ec
   *  002667ea   8b12             mov edx,dword ptr ds:[edx]
   *  002667ec   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
   *  002667ef   57               push edi
   *  002667f0   8d3c42           lea edi,dword ptr ds:[edx+eax*2]
   *  002667f3   85c9             test ecx,ecx
   *  002667f5   74 16            je short .0026680d
   *  002667f7   8b45 10          mov eax,dword ptr ss:[ebp+0x10]
   *  002667fa   0fb7d0           movzx edx,ax
   *  002667fd   8bc2             mov eax,edx
   *  002667ff   c1e2 10          shl edx,0x10
   *  00266802   0bc2             or eax,edx
   *  00266804   d1e9             shr ecx,1
   *  00266806   f3:ab            rep stos dword ptr es:[edi]
   *  00266808   13c9             adc ecx,ecx
   *  0026680a   66:f3:ab         rep stos word ptr es:[edi]
   *  0026680d   5f               pop edi
   *  0026680e   5d               pop ebp
   *  0026680f   c2 0c00          retn 0xc
   *  00266812   cc               int3
   *  00266813   cc               int3
   *
   *  Stack when enter function call:
   *  04cee270   00266870  return to .00266870 from .002667c0
   *  04cee274   00000002  jichi: arg1, ecx
   *  04cee278   00000001  jichi: arg2, always 1
   *  04cee27c   000050ac  jichi: arg3, wchar_t
   *  04cee280   04cee4fc  jichi: text address
   *  04cee284   0ead055c  arg5
   *  04cee288   0ead0568  arg6, last text when arg6 = arg5 = 2
   *  04cee28c  /04cee2c0
   *  04cee290  |00266969  return to .00266969 from .00266820
   *  04cee294  |00000001
   *  04cee298  |000050ac
   *  04cee29c  |e1466fb2
   *  04cee2a0  |072f45f0
   *
   *  Target address (edx) is at [[ecx]] when enter function.
   */

  // jichi: 8/17/2013: Change return type to bool
  bool InsertSiglus3Hook()
  {
    const BYTE bytes[] = {
        0x8b, 0x12,             // 002667d3   8b12             mov edx,dword ptr ds:[edx]
        0x8b, 0x4d, 0x08,       // 002667d5   8b4d 08          mov ecx,dword ptr ss:[ebp+0x8]
        0x66, 0x8b, 0x45, 0x10, // 002667d8   66:8b45 10       mov ax,word ptr ss:[ebp+0x10]
        0x66, 0x89, 0x04, 0x4a  // 002667dc   66:89044a        mov word ptr ds:[edx+ecx*2],ax ; jichi: wchar_t in ax
                                // 002667e0   5d               pop ebp
                                // 002667e1   c2 0c00          retn 0xc
    };
    enum
    {
      addr_offset = sizeof(bytes) - 4
    };
    ULONG range = max(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
      // ConsoleOutput("Unknown SiglusEngine");
      ConsoleOutput("Siglus3: pattern not found");
      return false;
    }

    // addr = MemDbg::findEnclosingAlignedFunction(addr, 50); // 0x002667dc - 0x002667c0 = 28
    // if (!addr) {
    //   ConsoleOutput("Siglus3: enclosing function not found");
    //   return false;
    // }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset = regoffset(eax);
    hp.type = CODEC_UTF16;
    // hp.text_fun = SpecialHookSiglus3;

    ConsoleOutput("INSERT Siglus3");
    return NewHook(hp, "SiglusEngine3");
  }

  /** SiglusEngine4 5/23/2015
   *  Sample game: AngleBeats trial
   *  Alternative ATcode from EGDB:
   *  UNIKOFILTER(30),FORCEFONT(5),HOOK(SiglusEngine.exe!0x0018CF39,TRANS(EAX,UNICODE,SMSTR,ADDNULL),RETNPOS(SOURCE))
   *  Text address is [eax]
   *
   *  0042CEFD   CC               INT3
   *  0042CEFE   CC               INT3
   *  0042CEFF   CC               INT3
   *  0042CF00   55               PUSH EBP
   *  0042CF01   8BEC             MOV EBP,ESP
   *  0042CF03   51               PUSH ECX
   *  0042CF04   A1 005E8A00      MOV EAX,DWORD PTR DS:[0x8A5E00]
   *  0042CF09   53               PUSH EBX
   *  0042CF0A   56               PUSH ESI
   *  0042CF0B   57               PUSH EDI
   *  0042CF0C   8B40 10          MOV EAX,DWORD PTR DS:[EAX+0x10]
   *  0042CF0F   8BF9             MOV EDI,ECX
   *  0042CF11   33C9             XOR ECX,ECX
   *  0042CF13   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
   *  0042CF1A   6A FF            PUSH -0x1
   *  0042CF1C   51               PUSH ECX
   *  0042CF1D   83E8 18          SUB EAX,0x18
   *  0042CF20   C747 14 07000000 MOV DWORD PTR DS:[EDI+0x14],0x7
   *  0042CF27   C747 10 00000000 MOV DWORD PTR DS:[EDI+0x10],0x0
   *  0042CF2E   66:890F          MOV WORD PTR DS:[EDI],CX
   *  0042CF31   8BCF             MOV ECX,EDI
   *  0042CF33   50               PUSH EAX
   *  0042CF34   E8 E725F6FF      CALL .0038F520
   *  0042CF39   8B1D 005E8A00    MOV EBX,DWORD PTR DS:[0x8A5E00] ; jichi: ATcode hooked here, text sometimes in eax sometimes address in eax, size in [eax+0x16]
   *  0042CF3F   8B73 10          MOV ESI,DWORD PTR DS:[EBX+0x10]
   *  0042CF42   837E FC 08       CMP DWORD PTR DS:[ESI-0x4],0x8
   *  0042CF46   72 0B            JB SHORT .0042CF53
   *  0042CF48   FF76 E8          PUSH DWORD PTR DS:[ESI-0x18]
   *  0042CF4B   E8 EA131300      CALL .0055E33A
   *  0042CF50   83C4 04          ADD ESP,0x4
   *  0042CF53   33C0             XOR EAX,EAX
   *  0042CF55   C746 FC 07000000 MOV DWORD PTR DS:[ESI-0x4],0x7
   *  0042CF5C   C746 F8 00000000 MOV DWORD PTR DS:[ESI-0x8],0x0
   *  0042CF63   66:8946 E8       MOV WORD PTR DS:[ESI-0x18],AX
   *  0042CF67   8BC7             MOV EAX,EDI
   *  0042CF69   8343 10 E8       ADD DWORD PTR DS:[EBX+0x10],-0x18
   *  0042CF6D   5F               POP EDI
   *  0042CF6E   5E               POP ESI
   *  0042CF6F   5B               POP EBX
   *  0042CF70   8BE5             MOV ESP,EBP
   *  0042CF72   5D               POP EBP
   *  0042CF73   C3               RETN
   *  0042CF74   CC               INT3
   *  0042CF75   CC               INT3
   *  0042CF76   CC               INT3
   *  0042CF77   CC               INT3
   */
  void Siglus4Filter(TextBuffer *buffer, HookParam *)
  {
    // Remove "NNLI"
    // if (*len > 2 && ::all_ascii(text))
    //  return false;
    // if (*len == 2 && *text == L'N')
    //  return false;
    StringFilter(buffer, TEXTANDLEN(L"NLI"));
    // Replace 『�(300e, 300f) with 「�(300c,300d)
    // CharReplacer(text, len, 0x300e, 0x300c);
    // CharReplacer(text, len, 0x300f, 0x300d);
  }
  void SpecialHookSiglus4(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    // static uint64_t lastTextHash_;
    DWORD eax = context->eax;        // text
    if (!eax || !*(const BYTE *)eax) // empty data
      return;
    DWORD size = *(DWORD *)(eax + 0x10);
    if (!size)
      return;
    DWORD data;
    if (size < 8)
      data = eax;
    else
      data = *(DWORD *)eax;

    // Skip all ascii characters
    if (all_ascii((LPCWSTR)data))
      return;

    // Avoid duplication
    // LPCWSTR text = (LPCWSTR)*data;
    // auto hash = hashstr(text);
    // if (hash == lastTextHash_)
    //  return;
    // lastTextHash_ = hash;

    buffer->from(data, size * 2); // UTF-16
    DWORD s0 = context->retaddr;  // use stack[0] as split
    if (s0 <= 0xff)               // scenario text
      *split = FIXED_SPLIT_VALUE;
    else if (::IsBadReadPtr((LPCVOID)s0, 4))
      *split = s0;
    else
    {
      *split = *(DWORD *)s0; // This value is runtime dependent
      if (*split == 0x54)
        *split = FIXED_SPLIT_VALUE * 2;
    }
    *split += context->stack[1]; // plus stack[1] as split
  }
  bool InsertSiglus4Hook()
  {
    const BYTE bytes[] = {
        0xc7, 0x47, 0x14, 0x07, 0x00, 0x00, 0x00, // 0042cf20   c747 14 07000000 mov dword ptr ds:[edi+0x14],0x7
        0xc7, 0x47, 0x10, 0x00, 0x00, 0x00, 0x00, // 0042cf27   c747 10 00000000 mov dword ptr ds:[edi+0x10],0x0
        0x66, 0x89, 0x0f,                         // 0042cf2e   66:890f          mov word ptr ds:[edi],cx
        0x8b, 0xcf,                               // 0042cf31   8bcf             mov ecx,edi
        0x50,                                     // 0042cf33   50               push eax
        0xe8                                      // XX4                              // 0042cf34   e8 e725f6ff      call .0038f520
                                                  // hook here
    };
    enum
    {
      addr_offset = sizeof(bytes) + 4
    }; // +4 for the call address
    ULONG range = max(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    // ULONG addr = processStartAddress + 0x0018cf39;
    if (!addr)
    {
      // ConsoleOutput("Unknown SiglusEngine");
      ConsoleOutput("Siglus4: pattern not found");
      return false;
    }

    // addr = MemDbg::findEnclosingAlignedFunction(addr, 50); // 0x002667dc - 0x002667c0 = 28
    // if (!addr) {
    //   ConsoleOutput("Siglus3: enclosing function not found");
    //   return false;
    // }

    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = NO_CONTEXT | CODEC_UTF16;
    hp.text_fun = SpecialHookSiglus4;
    hp.filter_fun = Siglus4Filter;
    // hp.offset=regoffset(eax);
    // hp.type = CODEC_UTF16|DATA_INDIRECT|USING_SPLIT|NO_CONTEXT;
    // hp.type = CODEC_UTF16|USING_SPLIT|NO_CONTEXT;

    ConsoleOutput("INSERT Siglus4");
    return NewHook(hp, "SiglusEngine4");
  }

#if 0  // not all text can be extracted
/** jichi: 6/16/2015 Siglus4Engine for Frill games
 *  Sample game: 冺�少女
 *
 *  This function is found by tracking where the text length is modified
 *
 *  Base address: 0x070000
 *
 *  0020F51B   CC               INT3
 *  0020F51C   CC               INT3
 *  0020F51D   CC               INT3
 *  0020F51E   CC               INT3
 *  0020F51F   CC               INT3
 *  0020F520   55               PUSH EBP	; jichi: memory address in [arg1+0x4], text length in arg1
 *  0020F521   8BEC             MOV EBP,ESP
 *  0020F523   6A FF            PUSH -0x1
 *  0020F525   68 889B5900      PUSH .00599B88
 *  0020F52A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
 *  0020F530   50               PUSH EAX
 *  0020F531   83EC 1C          SUB ESP,0x1C
 *  0020F534   53               PUSH EBX
 *  0020F535   56               PUSH ESI
 *  0020F536   57               PUSH EDI
 *  0020F537   A1 E0946500      MOV EAX,DWORD PTR DS:[0x6594E0]
 *  0020F53C   33C5             XOR EAX,EBP
 *  0020F53E   50               PUSH EAX
 *  0020F53F   8D45 F4          LEA EAX,DWORD PTR SS:[EBP-0xC]
 *  0020F542   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
 *  0020F548   8BD1             MOV EDX,ECX
 *  0020F54A   8955 F0          MOV DWORD PTR SS:[EBP-0x10],EDX
 *  0020F54D   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
 *  0020F550   8B5D 10          MOV EBX,DWORD PTR SS:[EBP+0x10]
 *  0020F553   3BC3             CMP EAX,EBX
 *  0020F555   0F8D DF000000    JGE .0020F63A
 *  0020F55B   8B75 08          MOV ESI,DWORD PTR SS:[EBP+0x8]
 *  0020F55E   8D0C40           LEA ECX,DWORD PTR DS:[EAX+EAX*2]
 *  0020F561   C1E1 03          SHL ECX,0x3
 *  0020F564   2BD8             SUB EBX,EAX
 *  0020F566   894D 0C          MOV DWORD PTR SS:[EBP+0xC],ECX
 *  0020F569   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
 *  0020F570   8B82 A4000000    MOV EAX,DWORD PTR DS:[EDX+0xA4]
 *  0020F576   03C1             ADD EAX,ECX
 *  0020F578   C745 EC 07000000 MOV DWORD PTR SS:[EBP-0x14],0x7
 *  0020F57F   33C9             XOR ECX,ECX
 *  0020F581   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
 *  0020F588   6A FF            PUSH -0x1
 *  0020F58A   51               PUSH ECX
 *  0020F58B   66:894D D8       MOV WORD PTR SS:[EBP-0x28],CX
 *  0020F58F   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
 *  0020F592   50               PUSH EAX
 *  0020F593   E8 68EFF4FF      CALL .0015E500
 *  0020F598   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
 *  0020F59F   8BCE             MOV ECX,ESI
 *  0020F5A1   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  0020F5A4   8B7D E8          MOV EDI,DWORD PTR SS:[EBP-0x18]
 *  0020F5A7   83C0 04          ADD EAX,0x4
 *  0020F5AA   50               PUSH EAX
 *  0020F5AB   E8 209DF5FF      CALL .001692D0
 *  0020F5B0   8B0E             MOV ECX,DWORD PTR DS:[ESI]
 *  0020F5B2   8D55 D8          LEA EDX,DWORD PTR SS:[EBP-0x28]
 *  0020F5B5   33C0             XOR EAX,EAX
 *  0020F5B7   3B4E 04          CMP ECX,DWORD PTR DS:[ESI+0x4]
 *  0020F5BA   0F44C8           CMOVE ECX,EAX
 *  0020F5BD   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  0020F5C0   893C01           MOV DWORD PTR DS:[ECX+EAX],EDI	; jichi: text length modified here
 *  0020F5C3   8B45 E8          MOV EAX,DWORD PTR SS:[EBP-0x18]
 *  0020F5C6   8346 0C 04       ADD DWORD PTR DS:[ESI+0xC],0x4
 *  0020F5CA   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
 *  0020F5CD   8D3C00           LEA EDI,DWORD PTR DS:[EAX+EAX]
 *  0020F5D0   8B45 EC          MOV EAX,DWORD PTR SS:[EBP-0x14]
 *  0020F5D3   83F8 08          CMP EAX,0x8
 *  0020F5D6   0F43D1           CMOVNB EDX,ECX
 *  0020F5D9   8955 10          MOV DWORD PTR SS:[EBP+0x10],EDX
 *  0020F5DC   85FF             TEST EDI,EDI
 *  0020F5DE   7E 32            JLE SHORT .0020F612
 *  0020F5E0   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  0020F5E3   8BCE             MOV ECX,ESI
 *  0020F5E5   03C7             ADD EAX,EDI
 *  0020F5E7   50               PUSH EAX
 *  0020F5E8   E8 E39CF5FF      CALL .001692D0
 *  0020F5ED   8B0E             MOV ECX,DWORD PTR DS:[ESI]
 *  0020F5EF   33C0             XOR EAX,EAX
 *  0020F5F1   3B4E 04          CMP ECX,DWORD PTR DS:[ESI+0x4]
 *  0020F5F4   57               PUSH EDI
 *  0020F5F5   FF75 10          PUSH DWORD PTR SS:[EBP+0x10]
 *  0020F5F8   0F44C8           CMOVE ECX,EAX
 *  0020F5FB   8B46 0C          MOV EAX,DWORD PTR DS:[ESI+0xC]
 *  0020F5FE   03C1             ADD EAX,ECX
 *  0020F600   50               PUSH EAX
 *  0020F601   E8 EA1B1200      CALL .003311F0
 *  0020F606   8B45 EC          MOV EAX,DWORD PTR SS:[EBP-0x14]
 *  0020F609   83C4 0C          ADD ESP,0xC
 *  0020F60C   017E 0C          ADD DWORD PTR DS:[ESI+0xC],EDI
 *  0020F60F   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
 *  0020F612   C745 FC FFFFFFFF MOV DWORD PTR SS:[EBP-0x4],-0x1
 *  0020F619   83F8 08          CMP EAX,0x8
 *  0020F61C   72 09            JB SHORT .0020F627
 *  0020F61E   51               PUSH ECX
 *  0020F61F   E8 A6DC1100      CALL .0032D2CA
 *  0020F624   83C4 04          ADD ESP,0x4
 *  0020F627   8B4D 0C          MOV ECX,DWORD PTR SS:[EBP+0xC]
 *  0020F62A   8B55 F0          MOV EDX,DWORD PTR SS:[EBP-0x10]
 *  0020F62D   83C1 18          ADD ECX,0x18
 *  0020F630   894D 0C          MOV DWORD PTR SS:[EBP+0xC],ECX
 *  0020F633   4B               DEC EBX
 *  0020F634  ^0F85 36FFFFFF    JNZ .0020F570
 *  0020F63A   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
 *  0020F63D   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
 *  0020F644   59               POP ECX
 *  0020F645   5F               POP EDI
 *  0020F646   5E               POP ESI
 *  0020F647   5B               POP EBX
 *  0020F648   8BE5             MOV ESP,EBP
 *  0020F64A   5D               POP EBP
 *  0020F64B   C2 0C00          RETN 0xC
 *  0020F64E   CC               INT3
 *  0020F64F   CC               INT3
 */
void SpecialHookSiglus4(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  static uint64_t lastTextHash_;
  DWORD arg1 = argof(1, esp_base); // arg1
  DWORD addr = *(DWORD *)(arg1 + 4);
  int size = *(DWORD *)addr;
  if (size <= 0 || size > VNR_TEXT_CAPACITY)
    return;
  auto text = LPWSTR(addr + 4);
  if (!text || ::IsBadWritePtr(text, size * 2) || !*text || ::wcslen(text) != size || lastTextHash_ == hashstr(text)) //  || text[size+1], skip if text's size + 1 is not empty
    return;
  lastTextHash_ = hashstr(text); // skip last repetition
  *len = size * 2;
  *data = (DWORD)text;
  *split = argof(3, esp_base); // arg3
}
bool InsertSiglus4Hook()
{
  ULONG processStartAddress, processStopAddress;
  if (!FillRange(processName,&startAddress, &stopAddress)) { // need accurate stopAddress
    ConsoleOutput("Siglus4: failed to get memory range");
    return false;
  }
  const BYTE bytes[] = {
    0x8b,0x75, 0x08, // 0020f55b   8b75 08          mov esi,dword ptr ss:[ebp+0x8]
    0x8d,0x0c,0x40,  // 0020f55e   8d0c40           lea ecx,dword ptr ds:[eax+eax*2]
    0xc1,0xe1, 0x03, // 0020f561   c1e1 03          shl ecx,0x3
    0x2b,0xd8,       // 0020f564   2bd8             sub ebx,eax
    0x89,0x4d, 0x0c  // 0020f566   894d 0c          mov dword ptr ss:[ebp+0xc],ecx

    // The following pattern is not unique, there are at least four matches
    //                        // 0020f5b7   3b4e 04     cmp ecx,dword ptr ds:[esi+0x4]
    //                        // 0020f5ba   0f44c8      cmove ecx,eax
    //0x8b,0x46, 0x0c,        // 0020f5bd   8b46 0c     mov eax,dword ptr ds:[esi+0xc]
    //0x89,0x3c,0x01,         // 0020f5c0   893c01      mov dword ptr ds:[ecx+eax],edi	; jichi: text length modified here
    //0x8b,0x45, 0xe8,        // 0020f5c3   8b45 e8     mov eax,dword ptr ss:[ebp-0x18]
    //0x83,0x46, 0x0c, 0x04,  // 0020f5c6   8346 0c 04  add dword ptr ds:[esi+0xc],0x4
    //0x8b,0x4d, 0xd8,        // 0020f5ca   8b4d d8     mov ecx,dword ptr ss:[ebp-0x28]
    //0x8d,0x3c,0x00          // 0020f5cd   8d3c00      lea edi,dword ptr ds:[eax+eax]
    //                        // 0020f5d0   8b45 ec     mov eax,dword ptr ss:[ebp-0x14]
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr) {
    //ConsoleOutput("Unknown SiglusEngine");
    ConsoleOutput("Siglus4: pattern not found");
    return false;
  }
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100); // 0x0020f55b - 0x0020F520 = 59
  if (!addr) {
    ConsoleOutput("Siglus4: enclosing function not found");
    return false;
  }

  //addr += 0x0020f64b - 0x0020f520; // hook to ret instead

  HookParam hp;
  hp.address = addr;
  //hp.type = CODEC_UTF16;
  hp.type = NO_CONTEXT;
  hp.text_fun = SpecialHookSiglus4;
  hp.filter_fun = Siglus4Filter; // remove NLI from the game

  //GROWL_DWORD(addr);

  ConsoleOutput("INSERT Siglus4");
  NewHook(hp, "SiglusEngine4");

  ConsoleOutput("Siglus4: disable GDI hooks");
  
  return true;
}
#endif // 0

  /**
   *  jichi 8/16/2013: Insert new siglus hook
   *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2531786952
   *  Issue: floating text
   *  Example:
   *  0153588b9534fdffff8b43583bd7
   *  0153 58          add dword ptr ds:[ebx+58],edx
   *  8b95 34fdffff    mov edx,dword ptr ss:[ebp-2cc]
   *  8b43 58          mov eax,dword ptr ds:[ebx+58]
   *  3bd7             cmp edx,edi    ; hook here
   *
   *  /HW-1C@D9DB2:SiglusEngine.exe
   *  - addr: 892338 (0xd9db2)
   *  - text_fun: 0x0
   *  - function: 0
   *  - hook_len: 0
   *  - ind: 0
   *  - length_offset: 1
   *  - module: 356004490 (0x1538328a)
   *  - off: 4294967264 (0xffffffe0L, 0x-20)
   *  - recover_len: 0
   *  - split: 0
   *  - split_ind: 0
   *  - type: 66   (0x42)
   *
   *  10/19/2014: There are currently two patterns to find the function to render scenario text.
   *  In the future, if both of them do not work again, try the following pattern instead.
   *  It is used to infer SiglusEngine2's logic in vnragent.
   *
   *  01140f8d   56               push esi
   *  01140f8e   8d8b 0c010000    lea ecx,dword ptr ds:[ebx+0x10c]
   *  01140f94   e8 67acfcff      call .0110bc00
   *  01140f99   837f 14 08       cmp dword ptr ds:[edi+0x14],0x8
   *  01140f9d   72 04            jb short .01140fa3
   *  01140f9f   8b37             mov esi,dword ptr ds:[edi]
   *  01140fa1   eb 02            jmp short .01140fa5
   *
   *  Type1 (聖娼女):
   *
   *  013aac6c   cc               int3
   *  013aac6d   cc               int3
   *  013aac6e   cc               int3
   *  013aac6f   cc               int3
   *  013aac70   55               push ebp    ; jichi: vnragent hooked here
   *  013aac71   8bec             mov ebp,esp
   *  013aac73   6a ff            push -0x1
   *  013aac75   68 d8306101      push .016130d8
   *  013aac7a   64:a1 00000000   mov eax,dword ptr fs:[0]
   *  013aac80   50               push eax
   *  013aac81   81ec dc020000    sub esp,0x2dc
   *  013aac87   a1 90f46a01      mov eax,dword ptr ds:[0x16af490]
   *  013aac8c   33c5             xor eax,ebp
   *  013aac8e   8945 f0          mov dword ptr ss:[ebp-0x10],eax
   *  013aac91   53               push ebx
   *  013aac92   56               push esi
   *  013aac93   57               push edi
   *  013aac94   50               push eax
   *  013aac95   8d45 f4          lea eax,dword ptr ss:[ebp-0xc]
   *  013aac98   64:a3 00000000   mov dword ptr fs:[0],eax
   *  013aac9e   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
   *  013aaca1   8b5d 08          mov ebx,dword ptr ss:[ebp+0x8]
   *  013aaca4   8bf9             mov edi,ecx
   *  013aaca6   8b77 10          mov esi,dword ptr ds:[edi+0x10]
   *  013aaca9   89bd 20fdffff    mov dword ptr ss:[ebp-0x2e0],edi
   *  013aacaf   8985 18fdffff    mov dword ptr ss:[ebp-0x2e8],eax
   *  013aacb5   85f6             test esi,esi
   *  013aacb7   0f84 77040000    je .013ab134
   *  013aacbd   8b93 18010000    mov edx,dword ptr ds:[ebx+0x118]
   *  013aacc3   2b93 14010000    sub edx,dword ptr ds:[ebx+0x114]
   *  013aacc9   8d8b 14010000    lea ecx,dword ptr ds:[ebx+0x114]
   *  013aaccf   b8 67666666      mov eax,0x66666667
   *  013aacd4   f7ea             imul edx
   *  013aacd6   c1fa 08          sar edx,0x8
   *  013aacd9   8bc2             mov eax,edx
   *  013aacdb   c1e8 1f          shr eax,0x1f
   *  013aacde   03c2             add eax,edx
   *  013aace0   03c6             add eax,esi
   *  013aace2   50               push eax
   *  013aace3   e8 5896fcff      call .01374340
   *  013aace8   837f 14 08       cmp dword ptr ds:[edi+0x14],0x8
   *  013aacec   72 04            jb short .013aacf2
   *  013aacee   8b07             mov eax,dword ptr ds:[edi]
   *  013aacf0   eb 02            jmp short .013aacf4
   *  013aacf2   8bc7             mov eax,edi
   *  013aacf4   8985 24fdffff    mov dword ptr ss:[ebp-0x2dc],eax
   *  013aacfa   8b57 14          mov edx,dword ptr ds:[edi+0x14]
   *  013aacfd   83fa 08          cmp edx,0x8
   *  013aad00   72 04            jb short .013aad06
   *  013aad02   8b0f             mov ecx,dword ptr ds:[edi]
   *  013aad04   eb 02            jmp short .013aad08
   *  013aad06   8bcf             mov ecx,edi
   *  013aad08   8b47 10          mov eax,dword ptr ds:[edi+0x10]
   *  013aad0b   8bb5 24fdffff    mov esi,dword ptr ss:[ebp-0x2dc]
   *  013aad11   03c0             add eax,eax
   *  013aad13   03c8             add ecx,eax
   *  013aad15   3bf1             cmp esi,ecx
   *  013aad17   0f84 17040000    je .013ab134
   *  013aad1d   c785 34fdffff 00>mov dword ptr ss:[ebp-0x2cc],0x0
   *  013aad27   c785 2cfdffff ff>mov dword ptr ss:[ebp-0x2d4],-0x1
   *  013aad31   89b5 1cfdffff    mov dword ptr ss:[ebp-0x2e4],esi
   *  013aad37   83fa 08          cmp edx,0x8
   *  013aad3a   72 04            jb short .013aad40
   *  013aad3c   8b0f             mov ecx,dword ptr ds:[edi]
   *  013aad3e   eb 02            jmp short .013aad42
   *  013aad40   8bcf             mov ecx,edi
   *  013aad42   03c1             add eax,ecx
   *  013aad44   8d8d 2cfdffff    lea ecx,dword ptr ss:[ebp-0x2d4]
   *  013aad4a   51               push ecx
   *  013aad4b   8d95 34fdffff    lea edx,dword ptr ss:[ebp-0x2cc]
   *  013aad51   52               push edx
   *  013aad52   50               push eax
   *  013aad53   8d85 24fdffff    lea eax,dword ptr ss:[ebp-0x2dc]
   *  013aad59   50               push eax
   *  013aad5a   e8 b183faff      call .01353110
   *  013aad5f   8bb5 2cfdffff    mov esi,dword ptr ss:[ebp-0x2d4]
   *  013aad65   83c4 10          add esp,0x10
   *  013aad68   83fe 0a          cmp esi,0xa
   *  013aad6b   75 09            jnz short .013aad76
   *  013aad6d   8bcb             mov ecx,ebx
   *  013aad6f   e8 ac050000      call .013ab320
   *  013aad74  ^eb 84            jmp short .013aacfa
   *  013aad76   83fe 07          cmp esi,0x7
   *  013aad79   75 2a            jnz short .013aada5
   *  013aad7b   33c9             xor ecx,ecx
   *  013aad7d   33c0             xor eax,eax
   *  013aad7f   66:898b ec000000 mov word ptr ds:[ebx+0xec],cx
   *  013aad86   8bcb             mov ecx,ebx
   *  013aad88   8983 e8000000    mov dword ptr ds:[ebx+0xe8],eax
   *  013aad8e   8983 f0000000    mov dword ptr ds:[ebx+0xf0],eax
   *  013aad94   e8 87050000      call .013ab320
   *  013aad99   c683 f9000000 01 mov byte ptr ds:[ebx+0xf9],0x1
   *  013aada0  ^e9 55ffffff      jmp .013aacfa
   *  013aada5   8b85 34fdffff    mov eax,dword ptr ss:[ebp-0x2cc]
   *  013aadab   85c0             test eax,eax
   *  013aadad   75 37            jnz short .013aade6
   *  013aadaf   85f6             test esi,esi
   *  013aadb1  ^0f84 43ffffff    je .013aacfa
   *  013aadb7   85c0             test eax,eax
   *  013aadb9   75 2b            jnz short .013aade6
   *  013aadbb   f605 c0be9f05 01 test byte ptr ds:[0x59fbec0],0x1
   *  013aadc2   75 0c            jnz short .013aadd0
   *  013aadc4   830d c0be9f05 01 or dword ptr ds:[0x59fbec0],0x1
   *  013aadcb   e8 f02a0b00      call .0145d8c0
   *  013aadd0   0fb7d6           movzx edx,si
   *  013aadd3   80ba c0be9e05 01 cmp byte ptr ds:[edx+0x59ebec0],0x1
   *  013aadda   75 0a            jnz short .013aade6
   *  013aaddc   8b43 68          mov eax,dword ptr ds:[ebx+0x68]
   *  013aaddf   99               cdq
   *  013aade0   2bc2             sub eax,edx
   *  013aade2   d1f8             sar eax,1
   *  013aade4   eb 03            jmp short .013aade9
   *  013aade6   8b43 68          mov eax,dword ptr ds:[ebx+0x68]
   *  013aade9   8b8b a0000000    mov ecx,dword ptr ds:[ebx+0xa0]
   *  013aadef   8b53 18          mov edx,dword ptr ds:[ebx+0x18]
   *  013aadf2   8985 30fdffff    mov dword ptr ss:[ebp-0x2d0],eax
   *  013aadf8   0343 58          add eax,dword ptr ds:[ebx+0x58]
   *  013aadfb   03d1             add edx,ecx
   *  013aadfd   3bc2             cmp eax,edx
   *  013aadff   7f 0f            jg short .013aae10
   *  013aae01   3bc1             cmp eax,ecx
   *  013aae03   7e 30            jle short .013aae35
   *  013aae05   8bc6             mov eax,esi
   *  013aae07   e8 94faffff      call .013aa8a0
   *  013aae0c   84c0             test al,al
   *  013aae0e   75 25            jnz short .013aae35
   *  013aae10   8bcb             mov ecx,ebx
   *  013aae12   e8 09050000      call .013ab320
   *  013aae17   83bd 34fdffff 00 cmp dword ptr ss:[ebp-0x2cc],0x0
   *  013aae1e   75 15            jnz short .013aae35
   *  013aae20   83fe 20          cmp esi,0x20
   *  013aae23  ^0f84 d1feffff    je .013aacfa
   *  013aae29   81fe 00300000    cmp esi,0x3000
   *  013aae2f  ^0f84 c5feffff    je .013aacfa
   *  013aae35   8b43 5c          mov eax,dword ptr ds:[ebx+0x5c]
   *  013aae38   3b83 a4000000    cmp eax,dword ptr ds:[ebx+0xa4]
   *  013aae3e   0f8d 7e020000    jge .013ab0c2
   *  013aae44   8d8d 38fdffff    lea ecx,dword ptr ss:[ebp-0x2c8]
   *  013aae4a   51               push ecx
   *  013aae4b   e8 30e4ffff      call .013a9280
   *  013aae50   c745 fc 01000000 mov dword ptr ss:[ebp-0x4],0x1
   *  013aae57   8b43 74          mov eax,dword ptr ds:[ebx+0x74]
   *  013aae5a   8b0d 88b26c01    mov ecx,dword ptr ds:[0x16cb288]
   *  013aae60   83f8 ff          cmp eax,-0x1
   *  013aae63   74 04            je short .013aae69
   *  013aae65   8bd0             mov edx,eax
   *  013aae67   eb 19            jmp short .013aae82
   *  013aae69   80b9 60010000 00 cmp byte ptr ds:[ecx+0x160],0x0
   *  013aae70   74 0d            je short .013aae7f
   *  013aae72   8b83 e0000000    mov eax,dword ptr ds:[ebx+0xe0]
   *  013aae78   8bd0             mov edx,eax
   *  013aae7a   83f8 ff          cmp eax,-0x1
   *  013aae7d   75 03            jnz short .013aae82
   *  013aae7f   8b53 24          mov edx,dword ptr ds:[ebx+0x24]
   *  013aae82   8b43 78          mov eax,dword ptr ds:[ebx+0x78]
   *  013aae85   83f8 ff          cmp eax,-0x1
   *  013aae88   75 17            jnz short .013aaea1
   *  013aae8a   80b9 60010000 00 cmp byte ptr ds:[ecx+0x160],0x0
   *  013aae91   74 0b            je short .013aae9e
   *  013aae93   8b83 e4000000    mov eax,dword ptr ds:[ebx+0xe4]
   *  013aae99   83f8 ff          cmp eax,-0x1
   *  013aae9c   75 03            jnz short .013aaea1
   *  013aae9e   8b43 28          mov eax,dword ptr ds:[ebx+0x28]
   *  013aaea1   8b4b 60          mov ecx,dword ptr ds:[ebx+0x60]
   *  013aaea4   8bb5 34fdffff    mov esi,dword ptr ss:[ebp-0x2cc]
   *  013aaeaa   034b 58          add ecx,dword ptr ds:[ebx+0x58]
   *  013aaead   8b7b 68          mov edi,dword ptr ds:[ebx+0x68]
   *  013aaeb0   8985 28fdffff    mov dword ptr ss:[ebp-0x2d8],eax
   *  013aaeb6   8b43 5c          mov eax,dword ptr ds:[ebx+0x5c]
   *  013aaeb9   0343 64          add eax,dword ptr ds:[ebx+0x64]
   *  013aaebc   83fe 01          cmp esi,0x1
   *  013aaebf   75 02            jnz short .013aaec3
   *  013aaec1   33d2             xor edx,edx
   *  013aaec3   80bb fa000000 00 cmp byte ptr ds:[ebx+0xfa],0x0
   *  013aaeca   89b5 38fdffff    mov dword ptr ss:[ebp-0x2c8],esi
   *  013aaed0   8bb5 2cfdffff    mov esi,dword ptr ss:[ebp-0x2d4]
   *  013aaed6   8995 44fdffff    mov dword ptr ss:[ebp-0x2bc],edx
   *  013aaedc   8b95 28fdffff    mov edx,dword ptr ss:[ebp-0x2d8]
   *  013aaee2   89b5 3cfdffff    mov dword ptr ss:[ebp-0x2c4],esi
   *  013aaee8   89bd 40fdffff    mov dword ptr ss:[ebp-0x2c0],edi
   *  013aaeee   8995 48fdffff    mov dword ptr ss:[ebp-0x2b8],edx
   *  013aaef4   898d 4cfdffff    mov dword ptr ss:[ebp-0x2b4],ecx
   *  013aaefa   8985 50fdffff    mov dword ptr ss:[ebp-0x2b0],eax
   *  013aaf00   74 19            je short .013aaf1b
   *  013aaf02   8b43 58          mov eax,dword ptr ds:[ebx+0x58]
   *  013aaf05   8b4b 5c          mov ecx,dword ptr ds:[ebx+0x5c]
   *  013aaf08   8983 fc000000    mov dword ptr ds:[ebx+0xfc],eax
   *  013aaf0e   898b 00010000    mov dword ptr ds:[ebx+0x100],ecx
   *  013aaf14   c683 fa000000 00 mov byte ptr ds:[ebx+0xfa],0x0
   *  013aaf1b   8b53 6c          mov edx,dword ptr ds:[ebx+0x6c]
   *  013aaf1e   0395 30fdffff    add edx,dword ptr ss:[ebp-0x2d0]
   *  013aaf24   33ff             xor edi,edi
   *  013aaf26   0153 58          add dword ptr ds:[ebx+0x58],edx
   *  013aaf29   8b95 34fdffff    mov edx,dword ptr ss:[ebp-0x2cc]
   *  013aaf2f   8b43 58          mov eax,dword ptr ds:[ebx+0x58]
   *  013aaf32   3bd7             cmp edx,edi             ; jichi: hook here
   *  013aaf34   75 4b            jnz short .013aaf81
   *  013aaf36   81fe 0c300000    cmp esi,0x300c  ; jichi 10/18/2014: searched here found the new siglus function
   *  013aaf3c   74 10            je short .013aaf4e
   *  013aaf3e   81fe 0e300000    cmp esi,0x300e
   *  013aaf44   74 08            je short .013aaf4e
   *  013aaf46   81fe 08ff0000    cmp esi,0xff08
   *  013aaf4c   75 33            jnz short .013aaf81
   *  013aaf4e   80bb f9000000 00 cmp byte ptr ds:[ebx+0xf9],0x0
   *  013aaf55   74 19            je short .013aaf70
   *  013aaf57   8983 e8000000    mov dword ptr ds:[ebx+0xe8],eax
   *  013aaf5d   66:89b3 ec000000 mov word ptr ds:[ebx+0xec],si
   *  013aaf64   c783 f0000000 01>mov dword ptr ds:[ebx+0xf0],0x1
   *  013aaf6e   eb 11            jmp short .013aaf81
   *  013aaf70   0fb783 ec000000  movzx eax,word ptr ds:[ebx+0xec]
   *  013aaf77   3bf0             cmp esi,eax
   *  013aaf79   75 06            jnz short .013aaf81
   *  013aaf7b   ff83 f0000000    inc dword ptr ds:[ebx+0xf0]
   *  013aaf81   8b8b f0000000    mov ecx,dword ptr ds:[ebx+0xf0]
   *  013aaf87   3bcf             cmp ecx,edi
   *  013aaf89   7e 71            jle short .013aaffc
   *  013aaf8b   3bd7             cmp edx,edi
   *  013aaf8d   75 50            jnz short .013aafdf
   *  013aaf8f   0fb783 ec000000  movzx eax,word ptr ds:[ebx+0xec]
   *  013aaf96   ba 0c300000      mov edx,0x300c
   *  013aaf9b   66:3bc2          cmp ax,dx
   *  013aaf9e   75 0f            jnz short .013aafaf
   *  013aafa0   81fe 0d300000    cmp esi,0x300d
   *  013aafa6   75 07            jnz short .013aafaf
   *  013aafa8   49               dec ecx
   *  013aafa9   898b f0000000    mov dword ptr ds:[ebx+0xf0],ecx
   *  013aafaf   b9 0e300000      mov ecx,0x300e
   *  013aafb4   66:3bc1          cmp ax,cx
   *  013aafb7   75 0e            jnz short .013aafc7
   *  013aafb9   81fe 0f300000    cmp esi,0x300f
   *  013aafbf   75 06            jnz short .013aafc7
   *  013aafc1   ff8b f0000000    dec dword ptr ds:[ebx+0xf0]
   *  013aafc7   ba 08ff0000      mov edx,0xff08
   *  013aafcc   66:3bc2          cmp ax,dx
   *  013aafcf   75 0e            jnz short .013aafdf
   *  013aafd1   81fe 09ff0000    cmp esi,0xff09
   *  013aafd7   75 06            jnz short .013aafdf
   *  013aafd9   ff8b f0000000    dec dword ptr ds:[ebx+0xf0]
   *  013aafdf   39bb f0000000    cmp dword ptr ds:[ebx+0xf0],edi
   *  013aafe5   75 15            jnz short .013aaffc
   *  013aafe7   33c0             xor eax,eax
   *  013aafe9   89bb e8000000    mov dword ptr ds:[ebx+0xe8],edi
   *  013aafef   66:8983 ec000000 mov word ptr ds:[ebx+0xec],ax
   *  013aaff6   89bb f0000000    mov dword ptr ds:[ebx+0xf0],edi
   *  013aaffc   8d8d 38fdffff    lea ecx,dword ptr ss:[ebp-0x2c8]
   *  013ab002   8dbb 14010000    lea edi,dword ptr ds:[ebx+0x114]
   *  013ab008   e8 b390fcff      call .013740c0
   *  013ab00d   33ff             xor edi,edi
   *  013ab00f   39bd 34fdffff    cmp dword ptr ss:[ebp-0x2cc],edi
   *  013ab015   75 0e            jnz short .013ab025
   *  013ab017   56               push esi
   *  013ab018   8d83 a8000000    lea eax,dword ptr ds:[ebx+0xa8]
   *  013ab01e   e8 5d080000      call .013ab880
   *  013ab023   eb 65            jmp short .013ab08a
   *  013ab025   8b85 1cfdffff    mov eax,dword ptr ss:[ebp-0x2e4]
   *  013ab02b   33c9             xor ecx,ecx
   *  013ab02d   66:894d d4       mov word ptr ss:[ebp-0x2c],cx
   *  013ab031   8b8d 24fdffff    mov ecx,dword ptr ss:[ebp-0x2dc]
   *  013ab037   c745 e8 07000000 mov dword ptr ss:[ebp-0x18],0x7
   *  013ab03e   897d e4          mov dword ptr ss:[ebp-0x1c],edi
   *  013ab041   3bc1             cmp eax,ecx
   *  013ab043   74 0d            je short .013ab052
   *  013ab045   2bc8             sub ecx,eax
   *  013ab047   d1f9             sar ecx,1
   *  013ab049   51               push ecx
   *  013ab04a   8d75 d4          lea esi,dword ptr ss:[ebp-0x2c]
   *  013ab04d   e8 de72f2ff      call .012d2330
   *  013ab052   6a ff            push -0x1
   *  013ab054   57               push edi
   *  013ab055   8d55 d4          lea edx,dword ptr ss:[ebp-0x2c]
   *  013ab058   52               push edx
   *  013ab059   8db3 a8000000    lea esi,dword ptr ds:[ebx+0xa8]
   *  013ab05f   c645 fc 02       mov byte ptr ss:[ebp-0x4],0x2
   *  013ab063   e8 3879f2ff      call .012d29a0
   *  013ab068   837d e8 08       cmp dword ptr ss:[ebp-0x18],0x8
   *  013ab06c   72 0c            jb short .013ab07a
   *  013ab06e   8b45 d4          mov eax,dword ptr ss:[ebp-0x2c]
   *  013ab071   50               push eax
   *  013ab072   e8 5fbe1900      call .01546ed6
   *  013ab077   83c4 04          add esp,0x4
   *  013ab07a   33c9             xor ecx,ecx
   *  013ab07c   c745 e8 07000000 mov dword ptr ss:[ebp-0x18],0x7
   *  013ab083   897d e4          mov dword ptr ss:[ebp-0x1c],edi
   *  013ab086   66:894d d4       mov word ptr ss:[ebp-0x2c],cx
   *  013ab08a   8bbd 20fdffff    mov edi,dword ptr ss:[ebp-0x2e0]
   *  013ab090   c683 f9000000 00 mov byte ptr ds:[ebx+0xf9],0x0
   *  013ab097   8d95 88feffff    lea edx,dword ptr ss:[ebp-0x178]
   *  013ab09d   52               push edx
   *  013ab09e   c745 fc 03000000 mov dword ptr ss:[ebp-0x4],0x3
   *  013ab0a5   e8 d6c70800      call .01437880
   *  013ab0aa   8d85 58fdffff    lea eax,dword ptr ss:[ebp-0x2a8]
   *  013ab0b0   50               push eax
   *  013ab0b1   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
   *  013ab0b8   e8 c3c70800      call .01437880
   *  013ab0bd  ^e9 38fcffff      jmp .013aacfa
   *  013ab0c2   8b9d 18fdffff    mov ebx,dword ptr ss:[ebp-0x2e8]
   *  013ab0c8   85db             test ebx,ebx
   *  013ab0ca   74 68            je short .013ab134
   *  013ab0cc   837f 14 08       cmp dword ptr ds:[edi+0x14],0x8
   *  013ab0d0   72 04            jb short .013ab0d6
   *  013ab0d2   8b07             mov eax,dword ptr ds:[edi]
   *  013ab0d4   eb 02            jmp short .013ab0d8
   *  013ab0d6   8bc7             mov eax,edi
   *  013ab0d8   8b4f 10          mov ecx,dword ptr ds:[edi+0x10]
   *  013ab0db   8d0448           lea eax,dword ptr ds:[eax+ecx*2]
   *  013ab0de   8b8d 1cfdffff    mov ecx,dword ptr ss:[ebp-0x2e4]
   *  013ab0e4   33d2             xor edx,edx
   *  013ab0e6   c745 cc 07000000 mov dword ptr ss:[ebp-0x34],0x7
   *  013ab0ed   c745 c8 00000000 mov dword ptr ss:[ebp-0x38],0x0
   *  013ab0f4   66:8955 b8       mov word ptr ss:[ebp-0x48],dx
   *  013ab0f8   3bc8             cmp ecx,eax
   *  013ab0fa   74 0f            je short .013ab10b
   *  013ab0fc   2bc1             sub eax,ecx
   *  013ab0fe   d1f8             sar eax,1
   *  013ab100   50               push eax
   *  013ab101   8bc1             mov eax,ecx
   *  013ab103   8d75 b8          lea esi,dword ptr ss:[ebp-0x48]
   *  013ab106   e8 2572f2ff      call .012d2330
   *  013ab10b   6a 00            push 0x0
   *  013ab10d   8d45 b8          lea eax,dword ptr ss:[ebp-0x48]
   *  013ab110   50               push eax
   *  013ab111   83c8 ff          or eax,0xffffffff
   *  013ab114   8bcb             mov ecx,ebx
   *  013ab116   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0
   *  013ab11d   e8 2e6ef2ff      call .012d1f50
   *  013ab122   837d cc 08       cmp dword ptr ss:[ebp-0x34],0x8
   *  013ab126   72 0c            jb short .013ab134
   *  013ab128   8b4d b8          mov ecx,dword ptr ss:[ebp-0x48]
   *  013ab12b   51               push ecx
   *  013ab12c   e8 a5bd1900      call .01546ed6
   *  013ab131   83c4 04          add esp,0x4
   *  013ab134   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
   *  013ab137   64:890d 00000000 mov dword ptr fs:[0],ecx
   *  013ab13e   59               pop ecx
   *  013ab13f   5f               pop edi
   *  013ab140   5e               pop esi
   *  013ab141   5b               pop ebx
   *  013ab142   8b4d f0          mov ecx,dword ptr ss:[ebp-0x10]
   *  013ab145   33cd             xor ecx,ebp
   *  013ab147   e8 6ab30e00      call .014964b6
   *  013ab14c   8be5             mov esp,ebp
   *  013ab14e   5d               pop ebp
   *  013ab14f   c2 0800          retn 0x8
   *  013ab152   cc               int3
   *  013ab153   cc               int3
   *  013ab154   cc               int3
   *
   *  10/18/2014 Type2: リア兂�ラスメイト孕ませ催�
   *
   *  01140edb   cc               int3
   *  01140edc   cc               int3
   *  01140edd   cc               int3
   *  01140ede   cc               int3
   *  01140edf   cc               int3
   *  01140ee0   55               push ebp
   *  01140ee1   8bec             mov ebp,esp
   *  01140ee3   6a ff            push -0x1
   *  01140ee5   68 c6514a01      push .014a51c6
   *  01140eea   64:a1 00000000   mov eax,dword ptr fs:[0]
   *  01140ef0   50               push eax
   *  01140ef1   81ec dc020000    sub esp,0x2dc
   *  01140ef7   a1 10745501      mov eax,dword ptr ds:[0x1557410]
   *  01140efc   33c5             xor eax,ebp
   *  01140efe   8945 f0          mov dword ptr ss:[ebp-0x10],eax
   *  01140f01   53               push ebx
   *  01140f02   56               push esi
   *  01140f03   57               push edi
   *  01140f04   50               push eax
   *  01140f05   8d45 f4          lea eax,dword ptr ss:[ebp-0xc]
   *  01140f08   64:a3 00000000   mov dword ptr fs:[0],eax
   *  01140f0e   8bd9             mov ebx,ecx
   *  01140f10   8b7d 08          mov edi,dword ptr ss:[ebp+0x8]
   *  01140f13   837f 10 00       cmp dword ptr ds:[edi+0x10],0x0
   *  01140f17   8b45 0c          mov eax,dword ptr ss:[ebp+0xc]
   *  01140f1a   8985 1cfdffff    mov dword ptr ss:[ebp-0x2e4],eax
   *  01140f20   8d47 10          lea eax,dword ptr ds:[edi+0x10]
   *  01140f23   89bd 38fdffff    mov dword ptr ss:[ebp-0x2c8],edi
   *  01140f29   8985 20fdffff    mov dword ptr ss:[ebp-0x2e0],eax
   *  01140f2f   0f84 2a050000    je .0114145f
   *  01140f35   8b8b 10010000    mov ecx,dword ptr ds:[ebx+0x110]
   *  01140f3b   b8 67666666      mov eax,0x66666667
   *  01140f40   2b8b 0c010000    sub ecx,dword ptr ds:[ebx+0x10c]
   *  01140f46   f7e9             imul ecx
   *  01140f48   8b85 20fdffff    mov eax,dword ptr ss:[ebp-0x2e0]
   *  01140f4e   8b8b 14010000    mov ecx,dword ptr ds:[ebx+0x114]
   *  01140f54   2b8b 0c010000    sub ecx,dword ptr ds:[ebx+0x10c]
   *  01140f5a   c1fa 08          sar edx,0x8
   *  01140f5d   8bf2             mov esi,edx
   *  01140f5f   c1ee 1f          shr esi,0x1f
   *  01140f62   03f2             add esi,edx
   *  01140f64   0330             add esi,dword ptr ds:[eax]
   *  01140f66   b8 67666666      mov eax,0x66666667
   *  01140f6b   f7e9             imul ecx
   *  01140f6d   c1fa 08          sar edx,0x8
   *  01140f70   8bc2             mov eax,edx
   *  01140f72   c1e8 1f          shr eax,0x1f
   *  01140f75   03c2             add eax,edx
   *  01140f77   3bc6             cmp eax,esi
   *  01140f79   73 1e            jnb short .01140f99
   *  01140f7b   81fe 66666600    cmp esi,0x666666                         ; unicode "s the data.
   *  01140f81   76 0a            jbe short .01140f8d
   *  01140f83   68 c00f4f01      push .014f0fc0                           ; ascii "vector<t> too long"
   *  01140f88   e8 b1a30e00      call .0122b33e
   *  01140f8d   56               push esi
   *  01140f8e   8d8b 0c010000    lea ecx,dword ptr ds:[ebx+0x10c]
   *  01140f94   e8 67acfcff      call .0110bc00
   *  01140f99   837f 14 08       cmp dword ptr ds:[edi+0x14],0x8
   *  01140f9d   72 04            jb short .01140fa3
   *  01140f9f   8b37             mov esi,dword ptr ds:[edi]
   *  01140fa1   eb 02            jmp short .01140fa5
   *  01140fa3   8bf7             mov esi,edi
   *  01140fa5   89b5 34fdffff    mov dword ptr ss:[ebp-0x2cc],esi
   *  01140fab   eb 03            jmp short .01140fb0
   *  01140fad   8d49 00          lea ecx,dword ptr ds:[ecx]
   *  01140fb0   8b57 14          mov edx,dword ptr ds:[edi+0x14]
   *  01140fb3   83fa 08          cmp edx,0x8
   *  01140fb6   72 04            jb short .01140fbc
   *  01140fb8   8b07             mov eax,dword ptr ds:[edi]
   *  01140fba   eb 02            jmp short .01140fbe
   *  01140fbc   8bc7             mov eax,edi
   *  01140fbe   8b8d 20fdffff    mov ecx,dword ptr ss:[ebp-0x2e0]
   *  01140fc4   8b09             mov ecx,dword ptr ds:[ecx]
   *  01140fc6   03c9             add ecx,ecx
   *  01140fc8   03c1             add eax,ecx
   *  01140fca   3bf0             cmp esi,eax
   *  01140fcc   0f84 8d040000    je .0114145f
   *  01140fd2   8b85 38fdffff    mov eax,dword ptr ss:[ebp-0x2c8]
   *  01140fd8   8bfe             mov edi,esi
   *  01140fda   c785 3cfdffff 00>mov dword ptr ss:[ebp-0x2c4],0x0
   *  01140fe4   c785 2cfdffff ff>mov dword ptr ss:[ebp-0x2d4],-0x1
   *  01140fee   83fa 08          cmp edx,0x8
   *  01140ff1   72 02            jb short .01140ff5
   *  01140ff3   8b00             mov eax,dword ptr ds:[eax]
   *  01140ff5   03c1             add eax,ecx
   *  01140ff7   8d95 3cfdffff    lea edx,dword ptr ss:[ebp-0x2c4]
   *  01140ffd   8d8d 2cfdffff    lea ecx,dword ptr ss:[ebp-0x2d4]
   *  01141003   51               push ecx
   *  01141004   50               push eax
   *  01141005   8d8d 34fdffff    lea ecx,dword ptr ss:[ebp-0x2cc]
   *  0114100b   e8 e033fbff      call .010f43f0
   *  01141010   8bb5 2cfdffff    mov esi,dword ptr ss:[ebp-0x2d4]
   *  01141016   83c4 08          add esp,0x8
   *  01141019   83fe 0a          cmp esi,0xa
   *  0114101c   75 18            jnz short .01141036
   *  0114101e   8bcb             mov ecx,ebx
   *  01141020   e8 2b060000      call .01141650
   *  01141025   8bb5 34fdffff    mov esi,dword ptr ss:[ebp-0x2cc]
   *  0114102b   8bbd 38fdffff    mov edi,dword ptr ss:[ebp-0x2c8]
   *  01141031  ^e9 7affffff      jmp .01140fb0
   *  01141036   83fe 07          cmp esi,0x7
   *  01141039   75 38            jnz short .01141073
   *  0114103b   33c0             xor eax,eax
   *  0114103d   c783 e0000000 00>mov dword ptr ds:[ebx+0xe0],0x0
   *  01141047   8bcb             mov ecx,ebx
   *  01141049   66:8983 e4000000 mov word ptr ds:[ebx+0xe4],ax
   *  01141050   8983 e8000000    mov dword ptr ds:[ebx+0xe8],eax
   *  01141056   e8 f5050000      call .01141650
   *  0114105b   8bb5 34fdffff    mov esi,dword ptr ss:[ebp-0x2cc]
   *  01141061   8bbd 38fdffff    mov edi,dword ptr ss:[ebp-0x2c8]
   *  01141067   c683 f1000000 01 mov byte ptr ds:[ebx+0xf1],0x1
   *  0114106e  ^e9 3dffffff      jmp .01140fb0
   *  01141073   8b85 3cfdffff    mov eax,dword ptr ss:[ebp-0x2c4]
   *  01141079   85c0             test eax,eax
   *  0114107b   75 36            jnz short .011410b3
   *  0114107d   85f6             test esi,esi
   *  0114107f   74 7f            je short .01141100
   *  01141081   85c0             test eax,eax
   *  01141083   75 2e            jnz short .011410b3
   *  01141085   a1 00358905      mov eax,dword ptr ds:[0x5893500]
   *  0114108a   a8 01            test al,0x1
   *  0114108c   75 0d            jnz short .0114109b
   *  0114108e   83c8 01          or eax,0x1
   *  01141091   a3 00358905      mov dword ptr ds:[0x5893500],eax
   *  01141096   e8 65160b00      call .011f2700
   *  0114109b   0fb7c6           movzx eax,si
   *  0114109e   80b8 10358905 01 cmp byte ptr ds:[eax+0x5893510],0x1
   *  011410a5   75 0c            jnz short .011410b3
   *  011410a7   8b43 68          mov eax,dword ptr ds:[ebx+0x68]
   *  011410aa   99               cdq
   *  011410ab   2bc2             sub eax,edx
   *  011410ad   8bc8             mov ecx,eax
   *  011410af   d1f9             sar ecx,1
   *  011410b1   eb 03            jmp short .011410b6
   *  011410b3   8b4b 68          mov ecx,dword ptr ds:[ebx+0x68]
   *  011410b6   8b43 18          mov eax,dword ptr ds:[ebx+0x18]
   *  011410b9   8b93 a0000000    mov edx,dword ptr ds:[ebx+0xa0]
   *  011410bf   03c2             add eax,edx
   *  011410c1   898d 28fdffff    mov dword ptr ss:[ebp-0x2d8],ecx
   *  011410c7   034b 58          add ecx,dword ptr ds:[ebx+0x58]
   *  011410ca   3bc8             cmp ecx,eax
   *  011410cc   7f 0f            jg short .011410dd
   *  011410ce   3bca             cmp ecx,edx
   *  011410d0   7e 3f            jle short .01141111
   *  011410d2   8bce             mov ecx,esi
   *  011410d4   e8 37faffff      call .01140b10
   *  011410d9   84c0             test al,al
   *  011410db   75 34            jnz short .01141111
   *  011410dd   8bcb             mov ecx,ebx
   *  011410df   e8 6c050000      call .01141650
   *  011410e4   83bd 3cfdffff 00 cmp dword ptr ss:[ebp-0x2c4],0x0
   *  011410eb   75 24            jnz short .01141111
   *  011410ed   83fe 20          cmp esi,0x20
   *  011410f0   74 0e            je short .01141100
   *  011410f2   81fe 00300000    cmp esi,0x3000
   *  011410f8   75 17            jnz short .01141111
   *  011410fa   8d9b 00000000    lea ebx,dword ptr ds:[ebx]
   *  01141100   8bb5 34fdffff    mov esi,dword ptr ss:[ebp-0x2cc]
   *  01141106   8bbd 38fdffff    mov edi,dword ptr ss:[ebp-0x2c8]
   *  0114110c  ^e9 9ffeffff      jmp .01140fb0
   *  01141111   8b43 5c          mov eax,dword ptr ds:[ebx+0x5c]
   *  01141114   3b83 a4000000    cmp eax,dword ptr ds:[ebx+0xa4]
   *  0114111a   0f8d cb020000    jge .011413eb
   *  01141120   8d8d 40fdffff    lea ecx,dword ptr ss:[ebp-0x2c0]
   *  01141126   e8 d5e3ffff      call .0113f500
   *  0114112b   c745 fc 01000000 mov dword ptr ss:[ebp-0x4],0x1
   *  01141132   8b4b 74          mov ecx,dword ptr ds:[ebx+0x74]
   *  01141135   8b15 98285701    mov edx,dword ptr ds:[0x1572898]
   *  0114113b   898d 30fdffff    mov dword ptr ss:[ebp-0x2d0],ecx
   *  01141141   83f9 ff          cmp ecx,-0x1
   *  01141144   75 23            jnz short .01141169
   *  01141146   80ba 58010000 00 cmp byte ptr ds:[edx+0x158],0x0
   *  0114114d   74 11            je short .01141160
   *  0114114f   8b8b d8000000    mov ecx,dword ptr ds:[ebx+0xd8]
   *  01141155   898d 30fdffff    mov dword ptr ss:[ebp-0x2d0],ecx
   *  0114115b   83f9 ff          cmp ecx,-0x1
   *  0114115e   75 09            jnz short .01141169
   *  01141160   8b43 24          mov eax,dword ptr ds:[ebx+0x24]
   *  01141163   8985 30fdffff    mov dword ptr ss:[ebp-0x2d0],eax
   *  01141169   8b43 78          mov eax,dword ptr ds:[ebx+0x78]
   *  0114116c   8985 24fdffff    mov dword ptr ss:[ebp-0x2dc],eax
   *  01141172   83f8 ff          cmp eax,-0x1
   *  01141175   75 23            jnz short .0114119a
   *  01141177   80ba 58010000 00 cmp byte ptr ds:[edx+0x158],0x0
   *  0114117e   74 11            je short .01141191
   *  01141180   8b83 dc000000    mov eax,dword ptr ds:[ebx+0xdc]
   *  01141186   8985 24fdffff    mov dword ptr ss:[ebp-0x2dc],eax
   *  0114118c   83f8 ff          cmp eax,-0x1
   *  0114118f   75 09            jnz short .0114119a
   *  01141191   8b43 28          mov eax,dword ptr ds:[ebx+0x28]
   *  01141194   8985 24fdffff    mov dword ptr ss:[ebp-0x2dc],eax
   *  0114119a   8b53 64          mov edx,dword ptr ds:[ebx+0x64]
   *  0114119d   0353 5c          add edx,dword ptr ds:[ebx+0x5c]
   *  011411a0   8b4b 60          mov ecx,dword ptr ds:[ebx+0x60]
   *  011411a3   034b 58          add ecx,dword ptr ds:[ebx+0x58]
   *  011411a6   83bd 3cfdffff 01 cmp dword ptr ss:[ebp-0x2c4],0x1
   *  011411ad   8bb5 30fdffff    mov esi,dword ptr ss:[ebp-0x2d0]
   *  011411b3   8b43 68          mov eax,dword ptr ds:[ebx+0x68]
   *  011411b6   c785 18fdffff 00>mov dword ptr ss:[ebp-0x2e8],0x0
   *  011411c0   0f44b5 18fdffff  cmove esi,dword ptr ss:[ebp-0x2e8]
   *  011411c7   80bb f2000000 00 cmp byte ptr ds:[ebx+0xf2],0x0
   *  011411ce   89b5 30fdffff    mov dword ptr ss:[ebp-0x2d0],esi
   *  011411d4   8bb5 3cfdffff    mov esi,dword ptr ss:[ebp-0x2c4]
   *  011411da   8985 48fdffff    mov dword ptr ss:[ebp-0x2b8],eax
   *  011411e0   8b85 30fdffff    mov eax,dword ptr ss:[ebp-0x2d0]
   *  011411e6   89b5 40fdffff    mov dword ptr ss:[ebp-0x2c0],esi
   *  011411ec   8bb5 2cfdffff    mov esi,dword ptr ss:[ebp-0x2d4]
   *  011411f2   8985 4cfdffff    mov dword ptr ss:[ebp-0x2b4],eax
   *  011411f8   8b85 24fdffff    mov eax,dword ptr ss:[ebp-0x2dc]
   *  011411fe   89b5 44fdffff    mov dword ptr ss:[ebp-0x2bc],esi
   *  01141204   8985 50fdffff    mov dword ptr ss:[ebp-0x2b0],eax
   *  0114120a   898d 54fdffff    mov dword ptr ss:[ebp-0x2ac],ecx
   *  01141210   8995 58fdffff    mov dword ptr ss:[ebp-0x2a8],edx
   *  01141216   74 19            je short .01141231
   *  01141218   8b43 58          mov eax,dword ptr ds:[ebx+0x58]
   *  0114121b   8983 f4000000    mov dword ptr ds:[ebx+0xf4],eax
   *  01141221   8b43 5c          mov eax,dword ptr ds:[ebx+0x5c]
   *  01141224   8983 f8000000    mov dword ptr ds:[ebx+0xf8],eax
   *  0114122a   c683 f2000000 00 mov byte ptr ds:[ebx+0xf2],0x0
   *  01141231   8b43 6c          mov eax,dword ptr ds:[ebx+0x6c]
   *  01141234   0385 28fdffff    add eax,dword ptr ss:[ebp-0x2d8]
   *  0114123a   0143 58          add dword ptr ds:[ebx+0x58],eax
   *  0114123d   8b85 3cfdffff    mov eax,dword ptr ss:[ebp-0x2c4]
   *  01141243   8b4b 58          mov ecx,dword ptr ds:[ebx+0x58]
   *  01141246   85c0             test eax,eax
   *  01141248   75 51            jnz short .0114129b
   *  0114124a   81fe 0c300000    cmp esi,0x300c  ; jichi: hook here, utf16 character is in esi
   *  01141250   74 10            je short .01141262
   *  01141252   81fe 0e300000    cmp esi,0x300e
   *  01141258   74 08            je short .01141262
   *  0114125a   81fe 08ff0000    cmp esi,0xff08
   *  01141260   75 39            jnz short .0114129b
   *  01141262   80bb f1000000 00 cmp byte ptr ds:[ebx+0xf1],0x0
   *  01141269   74 19            je short .01141284
   *  0114126b   898b e0000000    mov dword ptr ds:[ebx+0xe0],ecx
   *  01141271   66:89b3 e4000000 mov word ptr ds:[ebx+0xe4],si
   *  01141278   c783 e8000000 01>mov dword ptr ds:[ebx+0xe8],0x1
   *  01141282   eb 17            jmp short .0114129b
   *  01141284   0fb783 e4000000  movzx eax,word ptr ds:[ebx+0xe4]
   *  0114128b   3bf0             cmp esi,eax
   *  0114128d   8b85 3cfdffff    mov eax,dword ptr ss:[ebp-0x2c4]
   *  01141293   75 06            jnz short .0114129b
   *  01141295   ff83 e8000000    inc dword ptr ds:[ebx+0xe8]
   *  0114129b   8b93 e8000000    mov edx,dword ptr ds:[ebx+0xe8]
   *  011412a1   85d2             test edx,edx
   *  011412a3   7e 78            jle short .0114131d
   *  011412a5   85c0             test eax,eax
   *  011412a7   75 52            jnz short .011412fb
   *  011412a9   0fb78b e4000000  movzx ecx,word ptr ds:[ebx+0xe4]
   *  011412b0   b8 0c300000      mov eax,0x300c
   *  011412b5   66:3bc8          cmp cx,ax
   *  011412b8   75 11            jnz short .011412cb
   *  011412ba   81fe 0d300000    cmp esi,0x300d
   *  011412c0   75 09            jnz short .011412cb
   *  011412c2   8d42 ff          lea eax,dword ptr ds:[edx-0x1]
   *  011412c5   8983 e8000000    mov dword ptr ds:[ebx+0xe8],eax
   *  011412cb   b8 0e300000      mov eax,0x300e
   *  011412d0   66:3bc8          cmp cx,ax
   *  011412d3   75 0e            jnz short .011412e3
   *  011412d5   81fe 0f300000    cmp esi,0x300f
   *  011412db   75 06            jnz short .011412e3
   *  011412dd   ff8b e8000000    dec dword ptr ds:[ebx+0xe8]
   *  011412e3   b8 08ff0000      mov eax,0xff08
   *  011412e8   66:3bc8          cmp cx,ax
   *  011412eb   75 0e            jnz short .011412fb
   *  011412ed   81fe 09ff0000    cmp esi,0xff09
   *  011412f3   75 06            jnz short .011412fb
   *  011412f5   ff8b e8000000    dec dword ptr ds:[ebx+0xe8]
   *  011412fb   83bb e8000000 00 cmp dword ptr ds:[ebx+0xe8],0x0
   *  01141302   75 19            jnz short .0114131d
   *  01141304   33c0             xor eax,eax
   *  01141306   c783 e0000000 00>mov dword ptr ds:[ebx+0xe0],0x0
   *  01141310   66:8983 e4000000 mov word ptr ds:[ebx+0xe4],ax
   *  01141317   8983 e8000000    mov dword ptr ds:[ebx+0xe8],eax
   *  0114131d   8d85 40fdffff    lea eax,dword ptr ss:[ebp-0x2c0]
   *  01141323   50               push eax
   *  01141324   8d8b 0c010000    lea ecx,dword ptr ds:[ebx+0x10c]
   *  0114132a   e8 31a6fcff      call .0110b960
   *  0114132f   83bd 3cfdffff 00 cmp dword ptr ss:[ebp-0x2c4],0x0
   *  01141336   8bb5 34fdffff    mov esi,dword ptr ss:[ebp-0x2cc]
   *  0114133c   75 13            jnz short .01141351
   *  0114133e   ffb5 2cfdffff    push dword ptr ss:[ebp-0x2d4]
   *  01141344   8d8b a8000000    lea ecx,dword ptr ds:[ebx+0xa8]
   *  0114134a   e8 010a0000      call .01141d50
   *  0114134f   eb 64            jmp short .011413b5
   *  01141351   33c0             xor eax,eax
   *  01141353   c745 ec 07000000 mov dword ptr ss:[ebp-0x14],0x7
   *  0114135a   c745 e8 00000000 mov dword ptr ss:[ebp-0x18],0x0
   *  01141361   66:8945 d8       mov word ptr ss:[ebp-0x28],ax
   *  01141365   3bfe             cmp edi,esi
   *  01141367   74 10            je short .01141379
   *  01141369   8bc6             mov eax,esi
   *  0114136b   8d4d d8          lea ecx,dword ptr ss:[ebp-0x28]
   *  0114136e   2bc7             sub eax,edi
   *  01141370   d1f8             sar eax,1
   *  01141372   50               push eax
   *  01141373   57               push edi
   *  01141374   e8 b7daf2ff      call .0106ee30
   *  01141379   6a ff            push -0x1
   *  0114137b   6a 00            push 0x0
   *  0114137d   8d45 d8          lea eax,dword ptr ss:[ebp-0x28]
   *  01141380   c645 fc 02       mov byte ptr ss:[ebp-0x4],0x2
   *  01141384   50               push eax
   *  01141385   8d8b a8000000    lea ecx,dword ptr ds:[ebx+0xa8]
   *  0114138b   e8 205cf3ff      call .01076fb0
   *  01141390   837d ec 08       cmp dword ptr ss:[ebp-0x14],0x8
   *  01141394   72 0b            jb short .011413a1
   *  01141396   ff75 d8          push dword ptr ss:[ebp-0x28]
   *  01141399   e8 fccb0e00      call .0122df9a
   *  0114139e   83c4 04          add esp,0x4
   *  011413a1   33c0             xor eax,eax
   *  011413a3   c745 ec 07000000 mov dword ptr ss:[ebp-0x14],0x7
   *  011413aa   c745 e8 00000000 mov dword ptr ss:[ebp-0x18],0x0
   *  011413b1   66:8945 d8       mov word ptr ss:[ebp-0x28],ax
   *  011413b5   c683 f1000000 00 mov byte ptr ds:[ebx+0xf1],0x0
   *  011413bc   8d8d 90feffff    lea ecx,dword ptr ss:[ebp-0x170]
   *  011413c2   c745 fc 03000000 mov dword ptr ss:[ebp-0x4],0x3
   *  011413c9   e8 42bb0800      call .011ccf10
   *  011413ce   8d8d 60fdffff    lea ecx,dword ptr ss:[ebp-0x2a0]
   *  011413d4   c745 fc ffffffff mov dword ptr ss:[ebp-0x4],-0x1
   *  011413db   e8 30bb0800      call .011ccf10
   *  011413e0   8bbd 38fdffff    mov edi,dword ptr ss:[ebp-0x2c8]
   *  011413e6  ^e9 c5fbffff      jmp .01140fb0
   *  011413eb   8b9d 1cfdffff    mov ebx,dword ptr ss:[ebp-0x2e4]
   *  011413f1   85db             test ebx,ebx
   *  011413f3   74 6a            je short .0114145f
   *  011413f5   8b8d 38fdffff    mov ecx,dword ptr ss:[ebp-0x2c8]
   *  011413fb   8379 14 08       cmp dword ptr ds:[ecx+0x14],0x8
   *  011413ff   72 02            jb short .01141403
   *  01141401   8b09             mov ecx,dword ptr ds:[ecx]
   *  01141403   8b85 20fdffff    mov eax,dword ptr ss:[ebp-0x2e0]
   *  01141409   c745 d4 07000000 mov dword ptr ss:[ebp-0x2c],0x7
   *  01141410   c745 d0 00000000 mov dword ptr ss:[ebp-0x30],0x0
   *  01141417   8b00             mov eax,dword ptr ds:[eax]
   *  01141419   8d0441           lea eax,dword ptr ds:[ecx+eax*2]
   *  0114141c   33c9             xor ecx,ecx
   *  0114141e   66:894d c0       mov word ptr ss:[ebp-0x40],cx
   *  01141422   3bf8             cmp edi,eax
   *  01141424   74 0e            je short .01141434
   *  01141426   2bc7             sub eax,edi
   *  01141428   8d4d c0          lea ecx,dword ptr ss:[ebp-0x40]
   *  0114142b   d1f8             sar eax,1
   *  0114142d   50               push eax
   *  0114142e   57               push edi
   *  0114142f   e8 fcd9f2ff      call .0106ee30
   *  01141434   8d45 c0          lea eax,dword ptr ss:[ebp-0x40]
   *  01141437   c745 fc 00000000 mov dword ptr ss:[ebp-0x4],0x0
   *  0114143e   3bd8             cmp ebx,eax
   *  01141440   74 0c            je short .0114144e
   *  01141442   6a ff            push -0x1
   *  01141444   6a 00            push 0x0
   *  01141446   50               push eax
   *  01141447   8bcb             mov ecx,ebx
   *  01141449   e8 c2def2ff      call .0106f310
   *  0114144e   837d d4 08       cmp dword ptr ss:[ebp-0x2c],0x8
   *  01141452   72 0b            jb short .0114145f
   *  01141454   ff75 c0          push dword ptr ss:[ebp-0x40]
   *  01141457   e8 3ecb0e00      call .0122df9a
   *  0114145c   83c4 04          add esp,0x4
   *  0114145f   8b4d f4          mov ecx,dword ptr ss:[ebp-0xc]
   *  01141462   64:890d 00000000 mov dword ptr fs:[0],ecx
   *  01141469   59               pop ecx
   *  0114146a   5f               pop edi
   *  0114146b   5e               pop esi
   *  0114146c   5b               pop ebx
   *  0114146d   8b4d f0          mov ecx,dword ptr ss:[ebp-0x10]
   *  01141470   33cd             xor ecx,ebp
   *  01141472   e8 14cb0e00      call .0122df8b
   *  01141477   8be5             mov esp,ebp
   *  01141479   5d               pop ebp
   *  0114147a   c2 0800          retn 0x8
   *  0114147d   cc               int3
   *  0114147e   cc               int3
   *
   *  In AngleBeats, base = 0x09a0000
   *  00B6B87C   CC               INT3
   *  00B6B87D   CC               INT3
   *  00B6B87E   CC               INT3
   *  00B6B87F   CC               INT3
   *  00B6B880   55               PUSH EBP
   *  00B6B881   8BEC             MOV EBP,ESP
   *  00B6B883   6A FF            PUSH -0x1
   *  00B6B885   68 7964ED00      PUSH .00ED6479
   *  00B6B88A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
   *  00B6B890   50               PUSH EAX
   *  00B6B891   81EC 1C040000    SUB ESP,0x41C
   *  00B6B897   A1 E0A4F800      MOV EAX,DWORD PTR DS:[0xF8A4E0]
   *  00B6B89C   33C5             XOR EAX,EBP
   *  00B6B89E   8945 F0          MOV DWORD PTR SS:[EBP-0x10],EAX
   *  00B6B8A1   53               PUSH EBX
   *  00B6B8A2   56               PUSH ESI
   *  00B6B8A3   57               PUSH EDI
   *  00B6B8A4   50               PUSH EAX
   *  00B6B8A5   8D45 F4          LEA EAX,DWORD PTR SS:[EBP-0xC]
   *  00B6B8A8   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
   *  00B6B8AE   8BD9             MOV EBX,ECX
   *  00B6B8B0   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
   *  00B6B8B3   837F 10 00       CMP DWORD PTR DS:[EDI+0x10],0x0
   *  00B6B8B7   8B45 0C          MOV EAX,DWORD PTR SS:[EBP+0xC]
   *  00B6B8BA   8985 E0FBFFFF    MOV DWORD PTR SS:[EBP-0x420],EAX
   *  00B6B8C0   8D47 10          LEA EAX,DWORD PTR DS:[EDI+0x10]
   *  00B6B8C3   89BD FCFBFFFF    MOV DWORD PTR SS:[EBP-0x404],EDI
   *  00B6B8C9   8985 F0FBFFFF    MOV DWORD PTR SS:[EBP-0x410],EAX
   *  00B6B8CF   0F84 31060000    JE .00B6BF06
   *  00B6B8D5   8B8B 1C010000    MOV ECX,DWORD PTR DS:[EBX+0x11C]
   *  00B6B8DB   B8 71F8428A      MOV EAX,0x8A42F871
   *  00B6B8E0   2B8B 18010000    SUB ECX,DWORD PTR DS:[EBX+0x118]
   *  00B6B8E6   F7E9             IMUL ECX
   *  00B6B8E8   8B85 F0FBFFFF    MOV EAX,DWORD PTR SS:[EBP-0x410]
   *  00B6B8EE   03D1             ADD EDX,ECX
   *  00B6B8F0   8B8B 20010000    MOV ECX,DWORD PTR DS:[EBX+0x120]
   *  00B6B8F6   2B8B 18010000    SUB ECX,DWORD PTR DS:[EBX+0x118]
   *  00B6B8FC   C1FA 09          SAR EDX,0x9
   *  00B6B8FF   8BF2             MOV ESI,EDX
   *  00B6B901   C1EE 1F          SHR ESI,0x1F
   *  00B6B904   03F2             ADD ESI,EDX
   *  00B6B906   0330             ADD ESI,DWORD PTR DS:[EAX]
   *  00B6B908   B8 71F8428A      MOV EAX,0x8A42F871
   *  00B6B90D   F7E9             IMUL ECX
   *  00B6B90F   03D1             ADD EDX,ECX
   *  00B6B911   C1FA 09          SAR EDX,0x9
   *  00B6B914   8BC2             MOV EAX,EDX
   *  00B6B916   C1E8 1F          SHR EAX,0x1F
   *  00B6B919   03C2             ADD EAX,EDX
   *  00B6B91B   3BC6             CMP EAX,ESI
   *  00B6B91D   73 1E            JNB SHORT .00B6B93D
   *  00B6B91F   81FE 7C214500    CMP ESI,0x45217C
   *  00B6B925   76 0A            JBE SHORT .00B6B931
   *  00B6B927   68 C031F200      PUSH .00F231C0                           ; ASCII "vector<T> too long"
   *  00B6B92C   E8 D2FC0E00      CALL .00C5B603
   *  00B6B931   56               PUSH ESI
   *  00B6B932   8D8B 18010000    LEA ECX,DWORD PTR DS:[EBX+0x118]
   *  00B6B938   E8 A38DFCFF      CALL .00B346E0
   *  00B6B93D   837F 14 08       CMP DWORD PTR DS:[EDI+0x14],0x8
   *  00B6B941   72 04            JB SHORT .00B6B947
   *  00B6B943   8B37             MOV ESI,DWORD PTR DS:[EDI]
   *  00B6B945   EB 02            JMP SHORT .00B6B949
   *  00B6B947   8BF7             MOV ESI,EDI
   *  00B6B949   89B5 F8FBFFFF    MOV DWORD PTR SS:[EBP-0x408],ESI
   *  00B6B94F   90               NOP
   *  00B6B950   8B57 14          MOV EDX,DWORD PTR DS:[EDI+0x14]
   *  00B6B953   83FA 08          CMP EDX,0x8
   *  00B6B956   72 04            JB SHORT .00B6B95C
   *  00B6B958   8B07             MOV EAX,DWORD PTR DS:[EDI]
   *  00B6B95A   EB 02            JMP SHORT .00B6B95E
   *  00B6B95C   8BC7             MOV EAX,EDI
   *  00B6B95E   8B8D F0FBFFFF    MOV ECX,DWORD PTR SS:[EBP-0x410]
   *  00B6B964   8B09             MOV ECX,DWORD PTR DS:[ECX]
   *  00B6B966   03C9             ADD ECX,ECX
   *  00B6B968   03C1             ADD EAX,ECX
   *  00B6B96A   3BF0             CMP ESI,EAX
   *  00B6B96C   0F84 94050000    JE .00B6BF06
   *  00B6B972   8B85 FCFBFFFF    MOV EAX,DWORD PTR SS:[EBP-0x404]
   *  00B6B978   8BFE             MOV EDI,ESI
   *  00B6B97A   C785 00FCFFFF 00>MOV DWORD PTR SS:[EBP-0x400],0x0
   *  00B6B984   C785 E8FBFFFF FF>MOV DWORD PTR SS:[EBP-0x418],-0x1
   *  00B6B98E   83FA 08          CMP EDX,0x8
   *  00B6B991   72 02            JB SHORT .00B6B995
   *  00B6B993   8B00             MOV EAX,DWORD PTR DS:[EAX]
   *  00B6B995   03C1             ADD EAX,ECX
   *  00B6B997   8D95 00FCFFFF    LEA EDX,DWORD PTR SS:[EBP-0x400]
   *  00B6B99D   8D8D E8FBFFFF    LEA ECX,DWORD PTR SS:[EBP-0x418]
   *  00B6B9A3   51               PUSH ECX
   *  00B6B9A4   50               PUSH EAX
   *  00B6B9A5   8D8D F8FBFFFF    LEA ECX,DWORD PTR SS:[EBP-0x408]
   *  00B6B9AB   E8 5025FBFF      CALL .00B1DF00
   *  00B6B9B0   8BB5 E8FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x418]
   *  00B6B9B6   83C4 08          ADD ESP,0x8
   *  00B6B9B9   83FE 0A          CMP ESI,0xA
   *  00B6B9BC   75 18            JNZ SHORT .00B6B9D6
   *  00B6B9BE   8BCB             MOV ECX,EBX
   *  00B6B9C0   E8 FB070000      CALL .00B6C1C0
   *  00B6B9C5   8BB5 F8FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x408]
   *  00B6B9CB   8BBD FCFBFFFF    MOV EDI,DWORD PTR SS:[EBP-0x404]
   *  00B6B9D1  ^E9 7AFFFFFF      JMP .00B6B950
   *  00B6B9D6   83FE 07          CMP ESI,0x7
   *  00B6B9D9   75 38            JNZ SHORT .00B6BA13
   *  00B6B9DB   33C0             XOR EAX,EAX
   *  00B6B9DD   C783 EC000000 00>MOV DWORD PTR DS:[EBX+0xEC],0x0
   *  00B6B9E7   8BCB             MOV ECX,EBX
   *  00B6B9E9   66:8983 F0000000 MOV WORD PTR DS:[EBX+0xF0],AX
   *  00B6B9F0   8983 F4000000    MOV DWORD PTR DS:[EBX+0xF4],EAX
   *  00B6B9F6   E8 C5070000      CALL .00B6C1C0
   *  00B6B9FB   8BB5 F8FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x408]
   *  00B6BA01   8BBD FCFBFFFF    MOV EDI,DWORD PTR SS:[EBP-0x404]
   *  00B6BA07   C683 FD000000 01 MOV BYTE PTR DS:[EBX+0xFD],0x1
   *  00B6BA0E  ^E9 3DFFFFFF      JMP .00B6B950
   *  00B6BA13   8B85 00FCFFFF    MOV EAX,DWORD PTR SS:[EBP-0x400]
   *  00B6BA19   85C0             TEST EAX,EAX
   *  00B6BA1B   75 3A            JNZ SHORT .00B6BA57
   *  00B6BA1D   85F6             TEST ESI,ESI
   *  00B6BA1F   0F84 BE000000    JE .00B6BAE3
   *  00B6BA25   85C0             TEST EAX,EAX
   *  00B6BA27   75 2E            JNZ SHORT .00B6BA57
   *  00B6BA29   A1 486A2C05      MOV EAX,DWORD PTR DS:[0x52C6A48]
   *  00B6BA2E   A8 01            TEST AL,0x1
   *  00B6BA30   75 0D            JNZ SHORT .00B6BA3F
   *  00B6BA32   83C8 01          OR EAX,0x1
   *  00B6BA35   A3 486A2C05      MOV DWORD PTR DS:[0x52C6A48],EAX
   *  00B6BA3A   E8 B15F0B00      CALL .00C219F0
   *  00B6BA3F   0FB7C6           MOVZX EAX,SI
   *  00B6BA42   80B8 506A2C05 01 CMP BYTE PTR DS:[EAX+0x52C6A50],0x1
   *  00B6BA49   75 0C            JNZ SHORT .00B6BA57
   *  00B6BA4B   8B43 6C          MOV EAX,DWORD PTR DS:[EBX+0x6C]
   *  00B6BA4E   99               CDQ
   *  00B6BA4F   2BC2             SUB EAX,EDX
   *  00B6BA51   8BC8             MOV ECX,EAX
   *  00B6BA53   D1F9             SAR ECX,1
   *  00B6BA55   EB 03            JMP SHORT .00B6BA5A
   *  00B6BA57   8B4B 6C          MOV ECX,DWORD PTR DS:[EBX+0x6C]
   *  00B6BA5A   8B15 9C5DFA00    MOV EDX,DWORD PTR DS:[0xFA5D9C]
   *  00B6BA60   898D ECFBFFFF    MOV DWORD PTR SS:[EBP-0x414],ECX
   *  00B6BA66   83BA 84CF0000 01 CMP DWORD PTR DS:[EDX+0xCF84],0x1
   *  00B6BA6D   75 26            JNZ SHORT .00B6BA95
   *  00B6BA6F   8B43 60          MOV EAX,DWORD PTR DS:[EBX+0x60]
   *  00B6BA72   03C1             ADD EAX,ECX
   *  00B6BA74   8B8B AC000000    MOV ECX,DWORD PTR DS:[EBX+0xAC]
   *  00B6BA7A   8985 04FCFFFF    MOV DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BA80   8B43 18          MOV EAX,DWORD PTR DS:[EBX+0x18]
   *  00B6BA83   03C1             ADD EAX,ECX
   *  00B6BA85   3985 04FCFFFF    CMP DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BA8B   7F 39            JG SHORT .00B6BAC6
   *  00B6BA8D   398D 04FCFFFF    CMP DWORD PTR SS:[EBP-0x3FC],ECX
   *  00B6BA93   EB 24            JMP SHORT .00B6BAB9
   *  00B6BA95   8B43 5C          MOV EAX,DWORD PTR DS:[EBX+0x5C]
   *  00B6BA98   03C1             ADD EAX,ECX
   *  00B6BA9A   8B8B A8000000    MOV ECX,DWORD PTR DS:[EBX+0xA8]
   *  00B6BAA0   8985 04FCFFFF    MOV DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BAA6   8B43 18          MOV EAX,DWORD PTR DS:[EBX+0x18]
   *  00B6BAA9   03C1             ADD EAX,ECX
   *  00B6BAAB   3985 04FCFFFF    CMP DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BAB1   7F 13            JG SHORT .00B6BAC6
   *  00B6BAB3   398D 04FCFFFF    CMP DWORD PTR SS:[EBP-0x3FC],ECX
   *  00B6BAB9   7E 3F            JLE SHORT .00B6BAFA
   *  00B6BABB   8BCE             MOV ECX,ESI
   *  00B6BABD   E8 EEF9FFFF      CALL .00B6B4B0
   *  00B6BAC2   84C0             TEST AL,AL
   *  00B6BAC4   75 34            JNZ SHORT .00B6BAFA
   *  00B6BAC6   8BCB             MOV ECX,EBX
   *  00B6BAC8   E8 F3060000      CALL .00B6C1C0
   *  00B6BACD   83BD 00FCFFFF 00 CMP DWORD PTR SS:[EBP-0x400],0x0
   *  00B6BAD4   75 1E            JNZ SHORT .00B6BAF4
   *  00B6BAD6   83FE 20          CMP ESI,0x20
   *  00B6BAD9   74 08            JE SHORT .00B6BAE3
   *  00B6BADB   81FE 00300000    CMP ESI,0x3000
   *  00B6BAE1   75 11            JNZ SHORT .00B6BAF4
   *  00B6BAE3   8BB5 F8FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x408]
   *  00B6BAE9   8BBD FCFBFFFF    MOV EDI,DWORD PTR SS:[EBP-0x404]
   *  00B6BAEF  ^E9 5CFEFFFF      JMP .00B6B950
   *  00B6BAF4   8B15 9C5DFA00    MOV EDX,DWORD PTR DS:[0xFA5D9C]
   *  00B6BAFA   83BA 84CF0000 01 CMP DWORD PTR DS:[EDX+0xCF84],0x1
   *  00B6BB01   75 66            JNZ SHORT .00B6BB69
   *  00B6BB03   8B83 A8000000    MOV EAX,DWORD PTR DS:[EBX+0xA8]
   *  00B6BB09   F7D8             NEG EAX
   *  00B6BB0B   3943 5C          CMP DWORD PTR DS:[EBX+0x5C],EAX
   *  00B6BB0E   7F 68            JG SHORT .00B6BB78
   *  00B6BB10   8B9D E0FBFFFF    MOV EBX,DWORD PTR SS:[EBP-0x420]
   *  00B6BB16   85DB             TEST EBX,EBX
   *  00B6BB18   0F84 E8030000    JE .00B6BF06
   *  00B6BB1E   8B8D FCFBFFFF    MOV ECX,DWORD PTR SS:[EBP-0x404]
   *  00B6BB24   8379 14 08       CMP DWORD PTR DS:[ECX+0x14],0x8
   *  00B6BB28   72 02            JB SHORT .00B6BB2C
   *  00B6BB2A   8B09             MOV ECX,DWORD PTR DS:[ECX]
   *  00B6BB2C   8B85 F0FBFFFF    MOV EAX,DWORD PTR SS:[EBP-0x410]
   *  00B6BB32   C745 EC 07000000 MOV DWORD PTR SS:[EBP-0x14],0x7
   *  00B6BB39   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
   *  00B6BB40   8B00             MOV EAX,DWORD PTR DS:[EAX]
   *  00B6BB42   8D0441           LEA EAX,DWORD PTR DS:[ECX+EAX*2]
   *  00B6BB45   33C9             XOR ECX,ECX
   *  00B6BB47   66:894D D8       MOV WORD PTR SS:[EBP-0x28],CX
   *  00B6BB4B   3BF8             CMP EDI,EAX
   *  00B6BB4D   74 0E            JE SHORT .00B6BB5D
   *  00B6BB4F   2BC7             SUB EAX,EDI
   *  00B6BB51   8D4D D8          LEA ECX,DWORD PTR SS:[EBP-0x28]
   *  00B6BB54   D1F8             SAR EAX,1
   *  00B6BB56   50               PUSH EAX
   *  00B6BB57   57               PUSH EDI
   *  00B6BB58   E8 E334F2FF      CALL .00A8F040
   *  00B6BB5D   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0
   *  00B6BB64   E9 82030000      JMP .00B6BEEB
   *  00B6BB69   8B43 60          MOV EAX,DWORD PTR DS:[EBX+0x60]
   *  00B6BB6C   3B83 AC000000    CMP EAX,DWORD PTR DS:[EBX+0xAC]
   *  00B6BB72   0F8D 23030000    JGE .00B6BE9B
   *  00B6BB78   8D8D 08FCFFFF    LEA ECX,DWORD PTR SS:[EBP-0x3F8]
   *  00B6BB7E   E8 EDDEFFFF      CALL .00B69A70
   *  00B6BB83   C745 FC 02000000 MOV DWORD PTR SS:[EBP-0x4],0x2
   *  00B6BB8A   8B43 78          MOV EAX,DWORD PTR DS:[EBX+0x78]
   *  00B6BB8D   8B15 C05DFA00    MOV EDX,DWORD PTR DS:[0xFA5DC0]
   *  00B6BB93   8985 F4FBFFFF    MOV DWORD PTR SS:[EBP-0x40C],EAX
   *  00B6BB99   83F8 FF          CMP EAX,-0x1
   *  00B6BB9C   75 23            JNZ SHORT .00B6BBC1
   *  00B6BB9E   80BA 60010000 00 CMP BYTE PTR DS:[EDX+0x160],0x0
   *  00B6BBA5   74 11            JE SHORT .00B6BBB8
   *  00B6BBA7   8B83 E0000000    MOV EAX,DWORD PTR DS:[EBX+0xE0]
   *  00B6BBAD   8985 F4FBFFFF    MOV DWORD PTR SS:[EBP-0x40C],EAX
   *  00B6BBB3   83F8 FF          CMP EAX,-0x1
   *  00B6BBB6   75 09            JNZ SHORT .00B6BBC1
   *  00B6BBB8   8B43 24          MOV EAX,DWORD PTR DS:[EBX+0x24]
   *  00B6BBBB   8985 F4FBFFFF    MOV DWORD PTR SS:[EBP-0x40C],EAX
   *  00B6BBC1   8B4B 7C          MOV ECX,DWORD PTR DS:[EBX+0x7C]
   *  00B6BBC4   898D E4FBFFFF    MOV DWORD PTR SS:[EBP-0x41C],ECX
   *  00B6BBCA   83F9 FF          CMP ECX,-0x1
   *  00B6BBCD   75 23            JNZ SHORT .00B6BBF2
   *  00B6BBCF   80BA 60010000 00 CMP BYTE PTR DS:[EDX+0x160],0x0
   *  00B6BBD6   74 11            JE SHORT .00B6BBE9
   *  00B6BBD8   8B8B E4000000    MOV ECX,DWORD PTR DS:[EBX+0xE4]
   *  00B6BBDE   898D E4FBFFFF    MOV DWORD PTR SS:[EBP-0x41C],ECX
   *  00B6BBE4   83F9 FF          CMP ECX,-0x1
   *  00B6BBE7   75 09            JNZ SHORT .00B6BBF2
   *  00B6BBE9   8B43 28          MOV EAX,DWORD PTR DS:[EBX+0x28]
   *  00B6BBEC   8985 E4FBFFFF    MOV DWORD PTR SS:[EBP-0x41C],EAX
   *  00B6BBF2   8B83 80000000    MOV EAX,DWORD PTR DS:[EBX+0x80]
   *  00B6BBF8   8985 04FCFFFF    MOV DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BBFE   83F8 FF          CMP EAX,-0x1
   *  00B6BC01   75 23            JNZ SHORT .00B6BC26
   *  00B6BC03   80BA 60010000 00 CMP BYTE PTR DS:[EDX+0x160],0x0
   *  00B6BC0A   74 11            JE SHORT .00B6BC1D
   *  00B6BC0C   8B83 E8000000    MOV EAX,DWORD PTR DS:[EBX+0xE8]
   *  00B6BC12   8985 04FCFFFF    MOV DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BC18   83F8 FF          CMP EAX,-0x1
   *  00B6BC1B   75 09            JNZ SHORT .00B6BC26
   *  00B6BC1D   8B43 2C          MOV EAX,DWORD PTR DS:[EBX+0x2C]
   *  00B6BC20   8985 04FCFFFF    MOV DWORD PTR SS:[EBP-0x3FC],EAX
   *  00B6BC26   8B53 68          MOV EDX,DWORD PTR DS:[EBX+0x68]
   *  00B6BC29   0353 60          ADD EDX,DWORD PTR DS:[EBX+0x60]
   *  00B6BC2C   8B4B 5C          MOV ECX,DWORD PTR DS:[EBX+0x5C]
   *  00B6BC2F   034B 64          ADD ECX,DWORD PTR DS:[EBX+0x64]
   *  00B6BC32   83BD 00FCFFFF 01 CMP DWORD PTR SS:[EBP-0x400],0x1
   *  00B6BC39   8BB5 F4FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x40C]
   *  00B6BC3F   8B43 6C          MOV EAX,DWORD PTR DS:[EBX+0x6C]
   *  00B6BC42   C785 DCFBFFFF 00>MOV DWORD PTR SS:[EBP-0x424],0x0
   *  00B6BC4C   0F44B5 DCFBFFFF  CMOVE ESI,DWORD PTR SS:[EBP-0x424]
   *  00B6BC53   80BB FE000000 00 CMP BYTE PTR DS:[EBX+0xFE],0x0
   *  00B6BC5A   89B5 F4FBFFFF    MOV DWORD PTR SS:[EBP-0x40C],ESI
   *  00B6BC60   8BB5 00FCFFFF    MOV ESI,DWORD PTR SS:[EBP-0x400]
   *  00B6BC66   8985 10FCFFFF    MOV DWORD PTR SS:[EBP-0x3F0],EAX
   *  00B6BC6C   8B85 F4FBFFFF    MOV EAX,DWORD PTR SS:[EBP-0x40C]
   *  00B6BC72   8985 14FCFFFF    MOV DWORD PTR SS:[EBP-0x3EC],EAX
   *  00B6BC78   8B85 E4FBFFFF    MOV EAX,DWORD PTR SS:[EBP-0x41C]
   *  00B6BC7E   89B5 08FCFFFF    MOV DWORD PTR SS:[EBP-0x3F8],ESI
   *  00B6BC84   8BB5 E8FBFFFF    MOV ESI,DWORD PTR SS:[EBP-0x418]
   *  00B6BC8A   8985 18FCFFFF    MOV DWORD PTR SS:[EBP-0x3E8],EAX
   *  00B6BC90   8B85 04FCFFFF    MOV EAX,DWORD PTR SS:[EBP-0x3FC]
   *  00B6BC96   89B5 0CFCFFFF    MOV DWORD PTR SS:[EBP-0x3F4],ESI
   *  00B6BC9C   8985 1CFCFFFF    MOV DWORD PTR SS:[EBP-0x3E4],EAX
   *  00B6BCA2   898D 20FCFFFF    MOV DWORD PTR SS:[EBP-0x3E0],ECX
   *  00B6BCA8   8995 24FCFFFF    MOV DWORD PTR SS:[EBP-0x3DC],EDX
   *  00B6BCAE   74 19            JE SHORT .00B6BCC9
   *  00B6BCB0   8B43 5C          MOV EAX,DWORD PTR DS:[EBX+0x5C]
   *  00B6BCB3   8983 00010000    MOV DWORD PTR DS:[EBX+0x100],EAX
   *  00B6BCB9   8B43 60          MOV EAX,DWORD PTR DS:[EBX+0x60]
   *  00B6BCBC   8983 04010000    MOV DWORD PTR DS:[EBX+0x104],EAX
   *  00B6BCC2   C683 FE000000 00 MOV BYTE PTR DS:[EBX+0xFE],0x0
   *  00B6BCC9   A1 9C5DFA00      MOV EAX,DWORD PTR DS:[0xFA5D9C]
   *  00B6BCCE   83B8 84CF0000 01 CMP DWORD PTR DS:[EAX+0xCF84],0x1
   *  00B6BCD5   8B43 70          MOV EAX,DWORD PTR DS:[EBX+0x70]
   *  00B6BCD8   75 0B            JNZ SHORT .00B6BCE5
   *  00B6BCDA   0385 ECFBFFFF    ADD EAX,DWORD PTR SS:[EBP-0x414]
   *  00B6BCE0   0143 60          ADD DWORD PTR DS:[EBX+0x60],EAX
   *  00B6BCE3   EB 09            JMP SHORT .00B6BCEE
   *  00B6BCE5   0385 ECFBFFFF    ADD EAX,DWORD PTR SS:[EBP-0x414]
   *  00B6BCEB   0143 5C          ADD DWORD PTR DS:[EBX+0x5C],EAX
   *  00B6BCEE   8B8D 00FCFFFF    MOV ECX,DWORD PTR SS:[EBP-0x400]
   *  00B6BCF4   85C9             TEST ECX,ECX
   *  00B6BCF6   75 42            JNZ SHORT .00B6BD3A
   *  00B6BCF8   81FE 0C300000    CMP ESI,0x300C ; jichi: type2 found here
   *  00B6BCFE   74 10            JE SHORT .00B6BD10
   *  00B6BD00   81FE 0E300000    CMP ESI,0x300E
   *  00B6BD06   74 08            JE SHORT .00B6BD10
   *  00B6BD08   81FE 08FF0000    CMP ESI,0xFF08
   *  00B6BD0E   75 2A            JNZ SHORT .00B6BD3A
   *  00B6BD10   80BB FD000000 00 CMP BYTE PTR DS:[EBX+0xFD],0x0
   *  00B6BD17   74 10            JE SHORT .00B6BD29
   *  00B6BD19   56               PUSH ESI
   */
  bool InsertSiglus2Hook()
  {
    // const BYTE bytes[] = { // size = 14
    //   0x01,0x53, 0x58,                // 0153 58          add dword ptr ds:[ebx+58],edx
    //   0x8b,0x95, 0x34,0xfd,0xff,0xff, // 8b95 34fdffff    mov edx,dword ptr ss:[ebp-2cc]
    //   0x8b,0x43, 0x58,                // 8b43 58          mov eax,dword ptr ds:[ebx+58]
    //   0x3b,0xd7                       // 3bd7             cmp edx,edi ; hook here
    // };
    // enum { cur_ins_size = 2 };
    // enum { addr_offset = sizeof(bytes) - cur_ins_size }; // = 14 - 2  = 12, current inst is the last one

    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr;
    { // type 1
      const BYTE bytes[] = {
          0x3b, 0xd7, // cmp edx,edi ; hook here
          0x75, 0x4b  // jnz short
      };
      // enum { addr_offset = 0 };
      addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
      if (addr)
        ConsoleOutput("Siglus2: type 1 pattern found");
    }
    if (!addr)
    {
      // 81fe0c300000
      const BYTE bytes[] = {
          0x81, 0xfe, 0x0c, 0x30, 0x00, 0x00 // 0114124a   81fe 0c300000    cmp esi,0x300c  ; jichi: hook here
      };
      // enum { addr_offset = 0 };
      addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
      if (addr)
        ConsoleOutput("Siglus2: type 2 pattern found");
    }

    if (!addr)
    {
      ConsoleOutput("Siglus2: both type1 and type2 patterns not found");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(esi);
    hp.type = CODEC_UTF16 | FIXING_SPLIT; // jichi 6/1/2014: fixing the split value

    ConsoleOutput("INSERT Siglus2");
    return NewHook(hp, "SiglusEngine2");
  }
  static void SpecialHookSiglus1(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    // 写回有乱码
    auto textu = (TextUnionW *)(context->ecx + 4);
    buffer->from(textu->view());
  }

  // jichi: 8/17/2013: Change return type to bool
  bool InsertSiglus1Hook()
  {
    const BYTE bytes[] = {0x33, 0xc0, 0x8b, 0xf9, 0x89, 0x7c, 0x24};
    ULONG range = max(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    { // jichi 8/17/2013: Add "== 0" check to prevent breaking new games
      // ConsoleOutput("Unknown SiglusEngine");
      ConsoleOutput("Siglus: pattern not found");
      return false;
    }

    DWORD limit = addr - 0x100;
    while (addr > limit)
    {
      if (*(WORD *)addr == 0xff6a)
      {
        HookParam hp;
        hp.address = addr;
        hp.text_fun = SpecialHookSiglus1;
        hp.type = CODEC_UTF16;
        ConsoleOutput("INSERT Siglus");
        return NewHook(hp, "SiglusEngine");
      }
      addr--;
    }
    ConsoleOutput("Siglus: failed");
    return false;
  }

} // unnamed namespace

// jichi 8/17/2013: Insert old first. As the pattern could also be found in the old engine.
bool InsertSiglusHook()
{
  if (InsertSiglus1Hook())
    return true;
  bool ok = InsertSiglus2Hook();
  ok = InsertSiglus3Hook() || ok;
  ok = InsertSiglus4Hook() || ok;
  return ok;
}
bool InsertSiglusHookZ()
{
  BYTE bytes[] = {
      0x8b, 0x12,
      0x66, 0x89, 0x04, 0x72};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("SiglusHookZ %p", addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 2;
  hp.offset = regoffset(eax);
  hp.type = CODEC_UTF16;
  return NewHook(hp, "SiglusHookZ");
}
namespace
{
  namespace ScenarioHook
  {
    namespace Private
    {
      /**
       *  jichi 8/16/2013: Insert new siglus hook
       *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2531786952
       *
       *  013bac6e     cc             int3
       *  013bac6f     cc             int3
       *  013bac70  /$ 55             push ebp ; jichi: function starts
       *  013bac71  |. 8bec           mov ebp,esp
       *  013bac73  |. 6a ff          push -0x1
       *  013bac75  |. 68 d8306201    push siglusen.016230d8
       *  013bac7a  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
       *  013bac80  |. 50             push eax
       *  013bac81  |. 81ec dc020000  sub esp,0x2dc
       *  013bac87  |. a1 90f46b01    mov eax,dword ptr ds:[0x16bf490]
       *  013bac8c  |. 33c5           xor eax,ebp
       *  013bac8e  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
       *  013bac91  |. 53             push ebx
       *  013bac92  |. 56             push esi
       *  013bac93  |. 57             push edi
       *  013bac94  |. 50             push eax
       *  ...
       *  013baf32  |. 3bd7           |cmp edx,edi ; jichi: ITH hook here, char saved in edi
       *  013baf34  |. 75 4b          |jnz short siglusen.013baf81
       */
      enum Type
      {
        Type1 // Old SiglusEngine2, arg in ecx
        ,
        Type2  // New SiglusENgine2, arg in arg1, since リア充クラスメイト孕ませ催眠 in 9/26/2014
      } type_; // static
      /**
       *  Sample game: 聖娼女 体験版
       *
       *  IDA: sub_4DAC70 proc near ; Attributes: bp-based frame
       *
       *  Observations:
       *  - return: number of bytes = 2 * number of size
       *  - arg1: unknown pointer, remains the same
       *  - arg2: unknown, remains the same
       *  - this (ecx)
       *    - union
       *      - char x 3: if size < (3 * 2 - 1) &&
       *      - pointer x 4
       *        - 0x0: UTF-16 text
       *        - 0x4: the same as 0x0
       *        - 0x8: unknown variate pointer
       *    - 0xc: wchar_t pointer to a flag, the pointed value is zero when union is used as a char
       *    - 0x10: size of the text without null char
       *    - 0x14: unknown size, always slightly larger than size
       *    - 0x18: constant pointer
       *    ...
       *
       *  Sample stack:
       *  0025edf0  a8 f3 13 0a a8 f3 13 0a  ｨ・.ｨ・.   ; jichi: ecx = 0025edf0
       *            LPCWSTR     LPCWSTR
       *  0025edf8  10 ee 25 00 d0 ee 37 01  ・.ﾐ・
       *            LPCWSTR     LPCWSTR
       *  0025ee00  13 00 00 00 17 00 00 00  ...…
       *            SIZE_T      SIZE_T
       *
       *  0025ee08  18 0c f6 09 27 00 00 00  .・'... ; jichi: following three lines are constants
       *  0025ee10  01 00 00 00 01 00 00 00  ......
       *  0025ee18  d2 d9 5d 9f 1c a2 e7 09  ﾒﾙ]・｢・
       *
       *  0025ee20  40 8c 10 07 00 00 00 00  @・....
       *  0025ee28  00 00 00 00 00 00 00 00  ........
       *  0025ee30  b8 ee ce 0c b8 ee ce 0c  ｸ﨩.ｸ﨩.
       *  0025ee38  b8 ee ce 0c 00 00 00 00  ｸ﨩.....
       *  0025ee40  00 00 00 00 01 00 00 00  .......
       *  0025ee48  00 00 00 00 00 00 00 00  ........
       *  0025ee50  00 00 00 00 00 00 00 00  ........
       *  0025ee58  00 00 00 00 00 00 00 00  ........
       *
       *  0025ee60  01 00 00 00 01 00 00 00  ......
       */
      ULONG search(ULONG startAddress, ULONG stopAddress, Type *type)
      {
        ULONG addr;
        {
          const uint8_t bytes1[] = {
              0x3b, 0xd7, // 013baf32  |. 3bd7       |cmp edx,edi ; jichi: ITH hook here, char saved in edi
              0x75, 0x4b  // 013baf34  |. 75 4b      |jnz short siglusen.013baf81
          };
          addr = MemDbg::findBytes(bytes1, sizeof(bytes1), startAddress, stopAddress);
          if (addr && type)
            *type = Type1;
        }
        if (!addr)
        {
          const uint8_t bytes2[] = {
              // 81fe0c300000
              0x81, 0xfe, 0x0c, 0x30, 0x00, 0x00 // 0114124a   81fe 0c300000    cmp esi,0x300c  ; jichi: hook here
          };
          addr = MemDbg::findBytes(bytes2, sizeof(bytes2), startAddress, stopAddress);
          if (addr && type)
            *type = Type2;
        }
        if (!addr)
          return 0;

        const uint8_t bytes[] = {
            0x55,       // 013bac70  /$ 55       push ebp ; jichi: function starts
            0x8b, 0xec, // 013bac71  |. 8bec     mov ebp,esp
            0x6a, 0xff  // 013bac73  |. 6a ff    push -0x1
        };
        // enum { range = 0x300 };   // 0x013baf32 - 0x013bac70 = 706 = 0x2c2
        // enum { range = 0x400 };   // 0x013baf32 - 0x013bac70 = 0x36a
        enum
        {
          range = 0x500
        }; // 0x00b6bcf8 - 0x00b6b880 = 0x478
        return MemDbg::findBytes(bytes, sizeof(bytes), addr - range, addr);
        // if (!reladdr)
        //   //ConsoleOutput("Siglus2: pattern not found");
        //   return 0;
        // addr += reladdr;
        // return addr;
      }

      void text_fun(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {

        auto arg = (TextUnionW *)(type_ == Type1 ? s->ecx : s->stack[1]);
        if (!arg || !arg->isValid())
          return;
        buffer->from(arg->view());
      }
      void hookafter(hook_context *s, TextBuffer buffer)
      {
        auto arg = (TextUnionW *)(type_ == Type1 ? s->ecx : s->stack[1]);
        arg->setText(buffer.viewW());
      }
    }
    bool attach(ULONG startAddress, ULONG stopAddress) // attach scenario
    {
      ULONG addr = Private::search(startAddress, stopAddress, &Private::type_);
      ConsoleOutput("%p", addr);
      if (!addr)
        return false;
      // return Private::oldHookFun = (Private::hook_fun_t)winhook::replace_fun(addr, (ULONG)Private::newHookFun);
      HookParam hp;
      hp.address = addr;
      hp.type = EMBED_ABLE | CODEC_UTF16 | EMBED_INSERT_SPACE_AFTER_UNENCODABLE | NO_CONTEXT; // 0x41
      hp.text_fun = Private::text_fun;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineW;
      return NewHook(hp, "EmbedSiglus");
    }
  }
}

namespace OtherHook
{
  namespace Private
  {

    void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
    {
      static std::wstring text_;
      auto arg = (TextUnionW *)s->stack[0];
      if (!arg || !arg->isValid())
        return;
      auto vw = arg->view();
      LPCWSTR text = vw.data();
      // Skip all ascii
      if (!text || !*text || *text <= 127 || vw.size() > 1500) // there could be garbage
        return;

      *role = Engine::OtherRole;
      ULONG split = s->stack[3];
      if (split <= 0xffff || !Engine::isAddressReadable(split))
      { // skip modifying scenario thread
        // role = Engine::ScenarioRole;
        return;
      }
      else
      {
        split = *(DWORD *)split;
        switch (split)
        {
        case 0x54:
        case 0x26:
          *role = Engine::NameRole;
        }
      }
      // auto sig = Engine::hashThreadSignature(role, split);

      buffer->from(vw);
      //           newText = EngineController::instance()->dispatchTextWSTD(oldText, role, sig);
    }
    void hookafter2(hook_context *s, TextBuffer buffer)
    {
      auto arg = (TextUnionW *)s->stack[0];
      arg->setText(buffer.viewW());
    }

    ULONG search(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0xc7, 0x47, 0x14, 0x07, 0x00, 0x00, 0x00, // 0042cf20   c747 14 07000000 mov dword ptr ds:[edi+0x14],0x7
          0xc7, 0x47, 0x10, 0x00, 0x00, 0x00, 0x00, // 0042cf27   c747 10 00000000 mov dword ptr ds:[edi+0x10],0x0
          0x66, 0x89, 0x0f,                         // 0042cf2e   66:890f          mov word ptr ds:[edi],cx
          0x8b, 0xcf,                               // 0042cf31   8bcf             mov ecx,edi
          0x50,                                     // 0042cf33   50               push eax
          0xe8                                      // XX4                              // 0042cf34   e8 e725f6ff      call .0038f520 ; jichi: hook here
      };
      enum
      {
        addr_offset = sizeof(bytes) - 1
      }; // +4 for the call address
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return 0;
      return addr + addr_offset;
    }

  } // namespace Private

  bool attach(ULONG startAddress, ULONG stopAddress)
  {
    ULONG addr = Private::search(startAddress, stopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = EMBED_ABLE | CODEC_UTF16 | EMBED_INSERT_SPACE_AFTER_UNENCODABLE | NO_CONTEXT; // 0x41
    hp.text_fun = Private::hookBefore;
    hp.embed_fun = Private::hookafter2;
    hp.embed_hook_font = F_GetGlyphOutlineW;
    return NewHook(hp, "EmbedSiglus");
  }

} // namespace OtherHook

bool Siglus::attach_function()
{

  bool b3 = ScenarioHook::attach(processStartAddress, processStopAddress);
  if (b3)
    OtherHook::attach(processStartAddress, processStopAddress);
  bool b1 = InsertSiglusHook();
  bool b2 = InsertSiglusHookZ();
  return b1 || b2 || b3;
}