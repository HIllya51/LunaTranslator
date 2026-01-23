#include "Taskforce2.h"
/**
 *  jichi 1/2/2014: Taskforce2 Engine
 *
 *  Examples:
 *  神�仮)-カミサマカヂ�カリ- 路地裏繚乱編 (1.1)
 *  /HS-8@178872:Taskforce2.exe
 *
 *  00578819   . 50             push eax                                 ; |arg1
 *  0057881a   . c745 f4 cc636b>mov dword ptr ss:[ebp-0xc],taskforc.006b>; |
 *  00578821   . e8 31870000    call taskforc.00580f57                   ; \taskforc.00580f57
 *  00578826   . cc             int3
 *  00578827  /$ 8b4c24 04      mov ecx,dword ptr ss:[esp+0x4]
 *  0057882b  |. 53             push ebx
 *  0057882c  |. 33db           xor ebx,ebx
 *  0057882e  |. 3bcb           cmp ecx,ebx
 *  00578830  |. 56             push esi
 *  00578831  |. 57             push edi
 *  00578832  |. 74 08          je short taskforc.0057883c
 *  00578834  |. 8b7c24 14      mov edi,dword ptr ss:[esp+0x14]
 *  00578838  |. 3bfb           cmp edi,ebx
 *  0057883a  |. 77 1b          ja short taskforc.00578857
 *  0057883c  |> e8 28360000    call taskforc.0057be69
 *  00578841  |. 6a 16          push 0x16
 *  00578843  |. 5e             pop esi
 *  00578844  |. 8930           mov dword ptr ds:[eax],esi
 *  00578846  |> 53             push ebx
 *  00578847  |. 53             push ebx
 *  00578848  |. 53             push ebx
 *  00578849  |. 53             push ebx
 *  0057884a  |. 53             push ebx
 *  0057884b  |. e8 6a050000    call taskforc.00578dba
 *  00578850  |. 83c4 14        add esp,0x14
 *  00578853  |. 8bc6           mov eax,esi
 *  00578855  |. eb 31          jmp short taskforc.00578888
 *  00578857  |> 8b7424 18      mov esi,dword ptr ss:[esp+0x18]
 *  0057885b  |. 3bf3           cmp esi,ebx
 *  0057885d  |. 75 04          jnz short taskforc.00578863
 *  0057885f  |. 8819           mov byte ptr ds:[ecx],bl
 *  00578861  |.^eb d9          jmp short taskforc.0057883c
 *  00578863  |> 8bd1           mov edx,ecx
 *  00578865  |> 8a06           /mov al,byte ptr ds:[esi]
 *  00578867  |. 8802           |mov byte ptr ds:[edx],al
 *  00578869  |. 42             |inc edx
 *  0057886a  |. 46             |inc esi
 *  0057886b  |. 3ac3           |cmp al,bl
 *  0057886d  |. 74 03          |je short taskforc.00578872
 *  0057886f  |. 4f             |dec edi
 *  00578870  |.^75 f3          \jnz short taskforc.00578865
 *  00578872  |> 3bfb           cmp edi,ebx ; jichi: hook here
 *  00578874  |. 75 10          jnz short taskforc.00578886
 *  00578876  |. 8819           mov byte ptr ds:[ecx],bl
 *  00578878  |. e8 ec350000    call taskforc.0057be69
 *  0057887d  |. 6a 22          push 0x22
 *  0057887f  |. 59             pop ecx
 *  00578880  |. 8908           mov dword ptr ds:[eax],ecx
 *  00578882  |. 8bf1           mov esi,ecx
 *  00578884  |.^eb c0          jmp short taskforc.00578846
 *  00578886  |> 33c0           xor eax,eax
 *  00578888  |> 5f             pop edi
 *  00578889  |. 5e             pop esi
 *  0057888a  |. 5b             pop ebx
 *  0057888b  \. c3             retn
 *
 *  [131129] [Digital Cute] オトメスイッ� -OtomeSwitch- �彼が持ってる彼女のリモコン(1.1)
 *  /HS-8@1948E9:Taskforce2.exe
 *  - addr: 0x1948e9
 *  - off: 4294967284 (0xfffffff4 = -0xc)
 *  - type: 65  (0x41)
 *
 *  00594890   . 50             push eax                                 ; |arg1
 *  00594891   . c745 f4 64c56d>mov dword ptr ss:[ebp-0xc],taskforc.006d>; |
 *  00594898   . e8 88880000    call taskforc.0059d125                   ; \taskforc.0059d125
 *  0059489d   . cc             int3
 *  0059489e  /$ 8b4c24 04      mov ecx,dword ptr ss:[esp+0x4]
 *  005948a2  |. 53             push ebx
 *  005948a3  |. 33db           xor ebx,ebx
 *  005948a5  |. 3bcb           cmp ecx,ebx
 *  005948a7  |. 56             push esi
 *  005948a8  |. 57             push edi
 *  005948a9  |. 74 08          je short taskforc.005948b3
 *  005948ab  |. 8b7c24 14      mov edi,dword ptr ss:[esp+0x14]
 *  005948af  |. 3bfb           cmp edi,ebx
 *  005948b1  |. 77 1b          ja short taskforc.005948ce
 *  005948b3  |> e8 91350000    call taskforc.00597e49
 *  005948b8  |. 6a 16          push 0x16
 *  005948ba  |. 5e             pop esi
 *  005948bb  |. 8930           mov dword ptr ds:[eax],esi
 *  005948bd  |> 53             push ebx
 *  005948be  |. 53             push ebx
 *  005948bf  |. 53             push ebx
 *  005948c0  |. 53             push ebx
 *  005948c1  |. 53             push ebx
 *  005948c2  |. e8 7e010000    call taskforc.00594a45
 *  005948c7  |. 83c4 14        add esp,0x14
 *  005948ca  |. 8bc6           mov eax,esi
 *  005948cc  |. eb 31          jmp short taskforc.005948ff
 *  005948ce  |> 8b7424 18      mov esi,dword ptr ss:[esp+0x18]
 *  005948d2  |. 3bf3           cmp esi,ebx
 *  005948d4  |. 75 04          jnz short taskforc.005948da
 *  005948d6  |. 8819           mov byte ptr ds:[ecx],bl
 *  005948d8  |.^eb d9          jmp short taskforc.005948b3
 *  005948da  |> 8bd1           mov edx,ecx
 *  005948dc  |> 8a06           /mov al,byte ptr ds:[esi]
 *  005948de  |. 8802           |mov byte ptr ds:[edx],al
 *  005948e0  |. 42             |inc edx
 *  005948e1  |. 46             |inc esi
 *  005948e2  |. 3ac3           |cmp al,bl
 *  005948e4  |. 74 03          |je short taskforc.005948e9
 *  005948e6  |. 4f             |dec edi
 *  005948e7  |.^75 f3          \jnz short taskforc.005948dc
 *  005948e9  |> 3bfb           cmp edi,ebx ; jichi: hook here
 *  005948eb  |. 75 10          jnz short taskforc.005948fd
 *  005948ed  |. 8819           mov byte ptr ds:[ecx],bl
 *  005948ef  |. e8 55350000    call taskforc.00597e49
 *  005948f4  |. 6a 22          push 0x22
 *  005948f6  |. 59             pop ecx
 *  005948f7  |. 8908           mov dword ptr ds:[eax],ecx
 *  005948f9  |. 8bf1           mov esi,ecx
 *  005948fb  |.^eb c0          jmp short taskforc.005948bd
 *  005948fd  |> 33c0           xor eax,eax
 *  005948ff  |> 5f             pop edi
 *  00594900  |. 5e             pop esi
 *  00594901  |. 5b             pop ebx
 *  00594902  \. c3             retn
 *
 *  Use this if that hook fails, try this one for future engines:
 *  /HS0@44CADA
 */
bool InsertTaskforce2Hook()
{
  const BYTE bytes[] = {
      0x88, 0x02, // 005948de  |. 8802           |mov byte ptr ds:[edx],al
      0x42,       // 005948e0  |. 42             |inc edx
      0x46,       // 005948e1  |. 46             |inc esi
      0x3a, 0xc3, // 005948e2  |. 3ac3           |cmp al,bl
      0x74, 0x03, // 005948e4  |. 74 03          |je short taskforc.005948e9
      0x4f,       // 005948e6  |. 4f             |dec edi
      0x75, 0xf3, // 005948e7  |.^75 f3          \jnz short taskforc.005948dc
      0x3b, 0xfb  // 005948e9  |> 3bfb           cmp edi,ebx ; jichi: hook here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 2
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD3(reladdr, processStartAddress, range);
  if (!addr)
  {
    ConsoleOutput("Taskforce2: pattern not exist");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(ecx); // text in ecx
  hp.type = USING_STRING;     // 0x41
  hp.filter_fun = all_ascii_Filter;
  // GROWL_DWORD(hp.address);
  // hp.address = 0x1948e9 + processStartAddress;

  ConsoleOutput("INSERT Taskforce2");
  return NewHook(hp, "Taskforce2");
}
bool InsertTaskforce2XHook()
{
  // ちんくる★ツインクル フェスティバル！
  const BYTE bytes[] = {
      0X8A, 0X07, 0X89, 0x7d, XX, 0X84, 0XC0, 0x0F};

  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
  {
    ConsoleOutput("Taskforce2: pattern not exist");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edi);
  hp.type = USING_STRING | USING_SPLIT; // 0x41
  hp.split = regoffset(eax);
  hp.filter_fun = all_ascii_Filter;

  ConsoleOutput("INSERT Taskforce2");
  return NewHook(hp, "Taskforce2");
}
namespace
{ // unnamed
  namespace ScenarioHook
  {
    namespace Private
    {
      void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {

        int capacity = s->stack[1];      // arg 2, should always be 0x1000
        auto text = (LPCSTR)s->stack[2]; // arg 3
        if (capacity <= 0 || !text || !*text)
          return;
        *split = s->stack[2] == s->stack[12] ? Engine::ScenarioRole : Engine::OtherRole;
        // auto split = s->edx;
        // auto sig = Engine::hashThreadSignature(role, split);
        enum
        {
          sig = 0
        }; // split not used
        buffer->from(text);
      }
      void hookafter(hook_context *s, TextBuffer buffer, HookParam *)
      {
        std::string newData = buffer.strA();
        int capacity = s->stack[1]; // arg 2, should always be 0x1000
        if (newData.size() >= capacity)
          newData = newData.substr(0, capacity - 1);
        s->stack[2] = (ULONG)allocateString(newData); // arg 3
      }
    } // namespace Private

    /**
     *  Sample game: オトメスイッチ
     *
     *  Debugging method: hook to the ITH function, and then check stack
     *  strncpy is not hooked as it is also used to copy system text
     *
     *  0012D0D0   1A72224C
     *  0012D0D4   1A721FA4
     *  0012D0D8   00000000
     *  0012D0DC   0044A61A  RETURN to .0044A61A from .0058F477
     *  0012D0E0   1A72224C ; jichi: target text
     *  0012D0E4   00001000 ; jichi: this value is different for different callers
     *  0012D0E8   0D4CFA70	; jichi: source text here
     *  0012D0EC   00A53E0E  .00A53E0E
     *  0012D0F0   1A721F80
     *  0012D0F4   1AD70020
     *  0012D0F8   00000000
     *  0012D0FC   0012D138  Pointer to next SEH record
     *  0012D100   0069D878  SE handler
     *  0012D104   00000000
     *  0012D108   00451436  RETURN to .00451436 from .0044A5B0
     *  0012D10C   0D4CFAE8
     *  0012D110   0D4CFA70
     *  0012D114   0D4CF908
     *  0012D118   00000016
     *  0012D11C   00FFFFFF  .00FFFFFF
     *  0012D120   00000016
     *  0012D124   0000001F
     *  0012D128   00A53FD2  .00A53FD2
     *  0012D12C   006E3BC8  .006E3BC8
     *  0012D130   00000000
     *  0012D134   0012D10C
     *  0012D138   0012D8AC  Pointer to next SEH record
     *  0012D13C   0069D878  SE handler
     *  0012D140   00000000
     *  0012D144   004617DD  RETURN to .004617DD from .004513D0
     *  0012D148   00000000
     *  0012D14C   0D4CFAE8
     *  0012D150   00000000
     *  0012D154   00000000
     *  0012D158   006E3BC8  .006E3BC8
     *  0012D15C   00000016
     *  0012D160   0000001F
     *
     *  Caller of the strncpy function
     *  0044A5AF   CC               INT3
     *  0044A5B0   6A FF            PUSH -0x1
     *  0044A5B2   68 78D86900      PUSH .0069D878
     *  0044A5B7   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
     *  0044A5BD   50               PUSH EAX
     *  0044A5BE   53               PUSH EBX
     *  0044A5BF   55               PUSH EBP
     *  0044A5C0   57               PUSH EDI
     *  0044A5C1   A1 4C3F7F00      MOV EAX,DWORD PTR DS:[0x7F3F4C]
     *  0044A5C6   33C4             XOR EAX,ESP
     *  0044A5C8   50               PUSH EAX
     *  0044A5C9   8D4424 10        LEA EAX,DWORD PTR SS:[ESP+0x10]
     *  0044A5CD   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
     *  0044A5D3   33DB             XOR EBX,EBX
     *  0044A5D5   895C24 18        MOV DWORD PTR SS:[ESP+0x18],EBX
     *  0044A5D9   8D7E 5C          LEA EDI,DWORD PTR DS:[ESI+0x5C]
     *  0044A5DC   8D6B 14          LEA EBP,DWORD PTR DS:[EBX+0x14]
     *  0044A5DF   90               NOP
     *  0044A5E0   53               PUSH EBX
     *  0044A5E1   68 C83B6E00      PUSH .006E3BC8
     *  0044A5E6   8BCF             MOV ECX,EDI
     *  0044A5E8   E8 A376FBFF      CALL .00401C90
     *  0044A5ED   83C7 1C          ADD EDI,0x1C
     *  0044A5F0   83ED 01          SUB EBP,0x1
     *  0044A5F3  ^75 EB            JNZ SHORT .0044A5E0
     *  0044A5F5   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
     *  0044A5F9   BD 10000000      MOV EBP,0x10
     *  0044A5FE   396C24 38        CMP DWORD PTR SS:[ESP+0x38],EBP
     *  0044A602   73 04            JNB SHORT .0044A608
     *  0044A604   8D4424 24        LEA EAX,DWORD PTR SS:[ESP+0x24]
     *  0044A608   50               PUSH EAX
     *
     *  0044A609   8DBE A8020000    LEA EDI,DWORD PTR DS:[ESI+0x2A8]
     *  0044A60F   68 00100000      PUSH 0x1000
     *  0044A614   57               PUSH EDI
     *
     *  0044A615   E8 5D4E1400      CALL .0058F477  ; jichi: called here
     *  0044A61A   8BC7             MOV EAX,EDI
     *  0044A61C   83C4 0C          ADD ESP,0xC
     *  0044A61F   895E 58          MOV DWORD PTR DS:[ESI+0x58],EBX
     *  0044A622   899E A8120000    MOV DWORD PTR DS:[ESI+0x12A8],EBX
     *  0044A628   899E AC120000    MOV DWORD PTR DS:[ESI+0x12AC],EBX
     *  0044A62E   8D50 01          LEA EDX,DWORD PTR DS:[EAX+0x1]
     *  0044A631   8A08             MOV CL,BYTE PTR DS:[EAX]
     *  0044A633   83C0 01          ADD EAX,0x1
     *  0044A636   3ACB             CMP CL,BL
     *  0044A638  ^75 F7            JNZ SHORT .0044A631
     *  0044A63A   2BC2             SUB EAX,EDX
     *  0044A63C   6A FF            PUSH -0x1
     *  0044A63E   8986 B0120000    MOV DWORD PTR DS:[ESI+0x12B0],EAX
     *  0044A644   53               PUSH EBX
     *  0044A645   8D4424 28        LEA EAX,DWORD PTR SS:[ESP+0x28]
     *  0044A649   50               PUSH EAX
     *  0044A64A   8D8E 8C020000    LEA ECX,DWORD PTR DS:[ESI+0x28C]
     *  0044A650   899E B8120000    MOV DWORD PTR DS:[ESI+0x12B8],EBX
     *  0044A656   E8 0575FBFF      CALL .00401B60
     *  0044A65B   396C24 38        CMP DWORD PTR SS:[ESP+0x38],EBP
     *  0044A65F   899E C8120000    MOV DWORD PTR DS:[ESI+0x12C8],EBX
     *  0044A665   72 0D            JB SHORT .0044A674
     *  0044A667   8B4C24 24        MOV ECX,DWORD PTR SS:[ESP+0x24]
     *  0044A66B   51               PUSH ECX
     *  0044A66C   E8 C14A1400      CALL .0058F132
     *  0044A671   83C4 04          ADD ESP,0x4
     *  0044A674   8B4C24 10        MOV ECX,DWORD PTR SS:[ESP+0x10]
     *  0044A678   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
     *  0044A67F   59               POP ECX
     *  0044A680   5F               POP EDI
     *  0044A681   5D               POP EBP
     *  0044A682   5B               POP EBX
     *  0044A683   83C4 0C          ADD ESP,0xC
     *  0044A686   C2 1C00          RETN 0x1C
     *  0044A689   CC               INT3
     *
     *  This is properly the strncpy function. Capacity in arg2. Target in arg1. Source in arg3.
     *  0058F476   CC               INT3
     *  0058F477   8B4C24 04        MOV ECX,DWORD PTR SS:[ESP+0x4]
     *  0058F47B   53               PUSH EBX
     *  0058F47C   33DB             XOR EBX,EBX
     *  0058F47E   3BCB             CMP ECX,EBX
     *  0058F480   56               PUSH ESI
     *  0058F481   57               PUSH EDI
     *  0058F482   74 08            JE SHORT .0058F48C
     *  0058F484   8B7C24 14        MOV EDI,DWORD PTR SS:[ESP+0x14]
     *  0058F488   3BFB             CMP EDI,EBX
     *  0058F48A   77 1B            JA SHORT .0058F4A7
     *  0058F48C   E8 D8390000      CALL .00592E69
     *  0058F491   6A 16            PUSH 0x16
     *  0058F493   5E               POP ESI
     *  0058F494   8930             MOV DWORD PTR DS:[EAX],ESI
     *  0058F496   53               PUSH EBX
     *  0058F497   53               PUSH EBX
     *  0058F498   53               PUSH EBX
     *  0058F499   53               PUSH EBX
     *  0058F49A   53               PUSH EBX
     *  0058F49B   E8 D9010000      CALL .0058F679
     *  0058F4A0   83C4 14          ADD ESP,0x14
     *  0058F4A3   8BC6             MOV EAX,ESI
     *  0058F4A5   EB 31            JMP SHORT .0058F4D8
     *  0058F4A7   8B7424 18        MOV ESI,DWORD PTR SS:[ESP+0x18]
     *  0058F4AB   3BF3             CMP ESI,EBX
     *  0058F4AD   75 04            JNZ SHORT .0058F4B3
     *  0058F4AF   8819             MOV BYTE PTR DS:[ECX],BL
     *  0058F4B1  ^EB D9            JMP SHORT .0058F48C
     *  0058F4B3   8BD1             MOV EDX,ECX
     *
     *  Sample game: 神様（仮）-カミサマカッコカリ-路地裏繚乱編
     */

    bool attach(ULONG startAddress, ULONG stopAddress)
    {
      const uint8_t bytes[] = {
          0x8d, 0xbe, 0xa8, 0x02, 0x00, 0x00, // 0044a609   8dbe a8020000    lea edi,dword ptr ds:[esi+0x2a8]
          0x68, 0x00, 0x10, 0x00, 0x00,       // 0044a60f   68 00100000      push 0x1000
          0x57,                               // 0044a614   57               push edi
          0xe8                                // 0044a615   e8 5d4e1400      call .0058f477  ; jichi: called here
      };
      enum
      {
        addr_offset = sizeof(bytes) - 1
      };
      ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      HookParam hp;
      hp.address = addr + addr_offset;
      hp.text_fun = Private::hookBefore;
      hp.embed_fun = Private::hookafter;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
      return NewHook(hp, "EmbedTaskforce");
    }

  } // namespace ScenarioHook
} // unnamed namespace

bool Taskforce2::attach_function()
{

  bool b1 = InsertTaskforce2Hook();
  bool b2 = InsertTaskforce2XHook();
  bool b3 = ScenarioHook::attach(processStartAddress, processStopAddress);
  return b1 || b2 || b3;
}