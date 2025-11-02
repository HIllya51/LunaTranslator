#include "Rejet.h"

namespace
{ // unnamed Rejet
  /**
   *  jichi 12/22/2013: Rejet
   *  See (CaoNiMaGeBi): http://www.hongfire.com/forum/printthread.php?t=36807&pp=40&page=172
   *  See (CaoNiMaGeBi): http://tieba.baidu.com/p/2506179113
   *  Pattern: 2bce8bf8
   *      2bce      sub ecx,esi ; hook here
   *      8bf8      mov eds,eax
   *      8bd1      mov edx,ecx
   *
   *  Examples:
   *  - Type1: ドットカレシ-We're 8bit Lovers!: /HBN-4*0@A5332:DotKareshi.exe
   *    length_offset: 1
   *    off: 0xfffffff8 (-0x8)
   *    type: 1096 (0x448)
   *
   *    processStartAddress = 10e0000 (variant)
   *    hook_addr = processStartAddress + reladdr = 0xe55332
   *    01185311   . FFF0           PUSH EAX  ; beginning of a new function
   *    01185313   . 0FC111         XADD DWORD PTR DS:[ECX],EDX
   *    01185316   . 4A             DEC EDX
   *    01185317   . 85D2           TEST EDX,EDX
   *    01185319   . 0F8F 45020000  JG DotKares.01185564
   *    0118531F   . 8B08           MOV ECX,DWORD PTR DS:[EAX]
   *    01185321   . 8B11           MOV EDX,DWORD PTR DS:[ECX]
   *    01185323   . 50             PUSH EAX
   *    01185324   . 8B42 04        MOV EAX,DWORD PTR DS:[EDX+0x4]
   *    01185327   . FFD0           CALL EAX
   *    01185329   . E9 36020000    JMP DotKares.01185564
   *    0118532E   . 8B7424 20      MOV ESI,DWORD PTR SS:[ESP+0x20]
   *    01185332   . E8 99A9FBFF    CALL DotKares.0113FCD0    ; hook here
   *    01185337   . 8BF0           MOV ESI,EAX
   *    01185339   . 8D4C24 14      LEA ECX,DWORD PTR SS:[ESP+0x14]
   *    0118533D   . 3BF7           CMP ESI,EDI
   *    0118533F   . 0F84 1A020000  JE DotKares.0118555F
   *    01185345   . 51             PUSH ECX                                 ; /Arg2
   *    01185346   . 68 E4FE5501    PUSH DotKares.0155FEE4                   ; |Arg1 = 0155FEE4
   *    0118534B   . E8 1023F9FF    CALL DotKares.01117660                   ; \DotKares.00377660
   *    01185350   . 83C4 08        ADD ESP,0x8
   *    01185353   . 84C0           TEST AL,AL
   *
   *  - Type2: ドットカレシ-We're 8bit Lovers! II: /HBN-8*0@A7AF9:dotkareshi.exe
   *    off: 4294967284 (0xfffffff4 = -0xc)
   *    length_offset: 1
   *    type: 1096 (0x448)
   *
   *    processStartAddress: 0x12b0000
   *
   *    01357ad2   . fff0           push eax ; beginning of a new function
   *    01357ad4   . 0fc111         xadd dword ptr ds:[ecx],edx
   *    01357ad7   . 4a             dec edx
   *    01357ad8   . 85d2           test edx,edx
   *    01357ada   . 7f 0a          jg short dotkares.01357ae6
   *    01357adc   . 8b08           mov ecx,dword ptr ds:[eax]
   *    01357ade   . 8b11           mov edx,dword ptr ds:[ecx]
   *    01357ae0   . 50             push eax
   *    01357ae1   . 8b42 04        mov eax,dword ptr ds:[edx+0x4]
   *    01357ae4   . ffd0           call eax
   *    01357ae6   > 8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
   *    01357aea   . 33ff           xor edi,edi
   *    01357aec   . 3979 f4        cmp dword ptr ds:[ecx-0xc],edi
   *    01357aef   . 0f84 1e020000  je dotkares.01357d13
   *    01357af5   . 8b7424 20      mov esi,dword ptr ss:[esp+0x20]
   *    01357af9   . e8 7283fbff    call dotkares.0130fe70    ; jichi: hook here
   *    01357afe   . 8bf0           mov esi,eax
   *    01357b00   . 3bf7           cmp esi,edi
   *    01357b02   . 0f84 0b020000  je dotkares.01357d13
   *    01357b08   . 8d5424 14      lea edx,dword ptr ss:[esp+0x14]
   *    01357b0c   . 52             push edx                                 ; /arg2
   *    01357b0d   . 68 cc9f7501    push dotkares.01759fcc                   ; |arg1 = 01759fcc
   *    01357b12   . e8 e9f9f8ff    call dotkares.012e7500                   ; \dotkares.012c7500
   *    01357b17   . 83c4 08        add esp,0x8
   *    01357b1a   . 84c0           test al,al
   *    01357b1c   . 74 1d          je short dotkares.01357b3b
   *    01357b1e   . 8d46 64        lea eax,dword ptr ds:[esi+0x64]
   *    01357b21   . e8 bad0f8ff    call dotkares.012e4be0
   *    01357b26   . 68 28a17501    push dotkares.0175a128                   ; /arg1 = 0175a128 ascii "<br>"
   *
   *  - Type2: Tiny×MACHINEGUN: /HBN-8*0@4CEB8:TinyMachinegun.exe
   *    processStartAddress: 0x12f0000
   *    There are two possible places to hook
   *
   *    0133cea0   . fff0           push eax ; beginning of a new function
   *    0133cea2   . 0fc111         xadd dword ptr ds:[ecx],edx
   *    0133cea5   . 4a             dec edx
   *    0133cea6   . 85d2           test edx,edx
   *    0133cea8   . 7f 0a          jg short tinymach.0133ceb4
   *    0133ceaa   . 8b08           mov ecx,dword ptr ds:[eax]
   *    0133ceac   . 8b11           mov edx,dword ptr ds:[ecx]
   *    0133ceae   . 50             push eax
   *    0133ceaf   . 8b42 04        mov eax,dword ptr ds:[edx+0x4]
   *    0133ceb2   . ffd0           call eax
   *    0133ceb4   > 8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
   *    0133ceb8   . 33db           xor ebx,ebx               ; jichi: hook here
   *    0133ceba   . 3959 f4        cmp dword ptr ds:[ecx-0xc],ebx
   *    0133cebd   . 0f84 d4010000  je tinymach.0133d097
   *    0133cec3   . 8b7424 20      mov esi,dword ptr ss:[esp+0x20]
   *    0133cec7   . e8 f4f90100    call tinymach.0135c8c0     ; jichi: or hook here
   *    0133cecc   . 8bf0           mov esi,eax
   *    0133cece   . 3bf3           cmp esi,ebx
   *    0133ced0   . 0f84 c1010000  je tinymach.0133d097
   *    0133ced6   . 8d5424 14      lea edx,dword ptr ss:[esp+0x14]
   *    0133ceda   . 52             push edx                                 ; /arg2
   *    0133cedb   . 68 44847d01    push tinymach.017d8444                   ; |arg1 = 017d8444
   *    0133cee0   . e8 eb5bfdff    call tinymach.01312ad0                   ; \tinymach.011b2ad0
   *
   *  - Type 3: 剣が君: /HBN-8*0@B357D:KenGaKimi.exe
   *
   *    01113550   . fff0           push eax
   *    01113552   . 0fc111         xadd dword ptr ds:[ecx],edx
   *    01113555   . 4a             dec edx
   *    01113556   . 85d2           test edx,edx
   *    01113558   . 7f 0a          jg short kengakim.01113564
   *    0111355a   . 8b08           mov ecx,dword ptr ds:[eax]
   *    0111355c   . 8b11           mov edx,dword ptr ds:[ecx]
   *    0111355e   . 50             push eax
   *    0111355f   . 8b42 04        mov eax,dword ptr ds:[edx+0x4]
   *    01113562   . ffd0           call eax
   *    01113564     8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
   *    01113568     33ff           xor edi,edi
   *    0111356a     3979 f4        cmp dword ptr ds:[ecx-0xc],edi
   *    0111356d     0f84 09020000  je kengakim.0111377c
   *    01113573     8d5424 14      lea edx,dword ptr ss:[esp+0x14]
   *    01113577     52             push edx
   *    01113578     68 dc6a5401    push kengakim.01546adc
   *    0111357d     e8 3eaff6ff    call kengakim.0107e4c0    ; hook here
   */
  bool FindRejetHook(LPCVOID pattern, DWORD pattern_size, DWORD hook_off, DWORD hook_offset, LPCSTR hook_name = "Rejet")
  {
    // Offset to the function call from the beginning of the function
    // enum { addr_offset = 0x21 }; // Type1: hex(0x01185332-0x01185311)
    // const BYTE pattern[] = {    // Type1: Function start
    //  0xff,0xf0,      // 01185311   . fff0           push eax  ; beginning of a new function
    //  0x0f,0xc1,0x11, // 01185313   . 0fc111         xadd dword ptr ds:[ecx],edx
    //  0x4a,           // 01185316   . 4a             dec edx
    //  0x85,0xd2,      // 01185317   . 85d2           test edx,edx
    //  0x0f,0x8f       // 01185319   . 0f8f 45020000  jg DotKares.01185564
    //};
    // GROWL_DWORD(processStartAddress);
    ULONG addr = processStartAddress; //- sizeof(pattern);
    do
    {
      // addr += sizeof(pattern); // ++ so that each time return diff address
      ULONG range = min(processStopAddress - addr, MAX_REL_ADDR);
      addr = MemDbg::findBytes(pattern, pattern_size, addr, addr + range);
      if (!addr)
      {
        // ITH_MSG(L"failed");
        ConsoleOutput("Rejet: pattern not found");
        return false;
      }

      addr += hook_off;
      // GROWL_DWORD(addr);
      // GROWL_DWORD(*(DWORD *)(addr-3));
      // const BYTE hook_ins[] = {
      //   /*0x8b,*/0x74,0x24, 0x20,  //    mov esi,dword ptr ss:[esp+0x20]
      //   0xe8 //??,??,??,??, 01357af9  e8 7283fbff call DotKares.0130fe70 ; jichi: hook here
      // };
    } while (0xe8202474 != *(DWORD *)(addr - 3));

    ConsoleOutput("INSERT Rejet");
    HookParam hp;
    hp.address = addr; //- 0xf;
    hp.type = NO_CONTEXT | DATA_INDIRECT | FIXING_SPLIT;
    hp.offset = hook_offset;

    return NewHook(hp, hook_name);
  }
  bool InsertRejetHook1() // This type of hook has varied hook address
  {
    const BYTE bytes[] = {
        // Type1: Function start
        0xff, 0xf0,       // 01185311   . fff0           push eax  ; beginning of a new function
        0x0f, 0xc1, 0x11, // 01185313   . 0fc111         xadd dword ptr ds:[ecx],edx
        0x4a,             // 01185316   . 4a             dec edx
        0x85, 0xd2,       // 01185317   . 85d2           test edx,edx
        0x0f, 0x8f        // 01185319   . 0f8f 45020000  jg DotKares.01185564
    };
    // Offset to the function call from the beginning of the function
    enum
    {
      addr_offset = 0x21
    }; // Type1: hex(0x01185332-0x01185311)
    enum
    {
      hook_offset = -0x8
    }; // hook parameter
    return FindRejetHook(bytes, sizeof(bytes), addr_offset, hook_offset);
  }
  bool InsertRejetHook2() // This type of hook has static hook address
  {
    const BYTE bytes[] = {
        // Type2 Function start
        0xff, 0xf0,            //   01357ad2   fff0           push eax
        0x0f, 0xc1, 0x11,      //   01357ad4   0fc111         xadd dword ptr ds:[ecx],edx
        0x4a,                  //   01357ad7   4a             dec edx
        0x85, 0xd2,            //   01357ad8   85d2           test edx,edx
        0x7f, 0x0a,            //   01357ada   7f 0a          jg short DotKares.01357ae6
        0x8b, 0x08,            //   01357adc   8b08           mov ecx,dword ptr ds:[eax]
        0x8b, 0x11,            //   01357ade   8b11           mov edx,dword ptr ds:[ecx]
        0x50,                  //   01357ae0   50             push eax
        0x8b, 0x42, 0x04,      //   01357ae1   8b42 04        mov eax,dword ptr ds:[edx+0x4]
        0xff, 0xd0,            //   01357ae4   ffd0           call eax
        0x8b, 0x4c, 0x24, 0x14 //   01357ae6   8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
    };
    // Offset to the function call from the beginning of the function
    enum
    {
      addr_offset = 0x27
    }; // Type2: hex(0x0133CEC7-0x0133CEA0) = hex(0x01357af9-0x1357ad2)
    enum
    {
      hook_offset = -0xc
    }; // hook parameter
    return FindRejetHook(bytes, sizeof(bytes), addr_offset, hook_offset);
  }
  bool InsertRejetHook3() // jichi 12/28/2013: add for 剣が君
  {
    // The following pattern is the same as type2
    const BYTE bytes[] = {
        // Type2 Function start
        0xff, 0xf0,            //   01357ad2   fff0           push eax
        0x0f, 0xc1, 0x11,      //   01357ad4   0fc111         xadd dword ptr ds:[ecx],edx
        0x4a,                  //   01357ad7   4a             dec edx
        0x85, 0xd2,            //   01357ad8   85d2           test edx,edx
        0x7f, 0x0a,            //   01357ada   7f 0a          jg short DotKares.01357ae6
        0x8b, 0x08,            //   01357adc   8b08           mov ecx,dword ptr ds:[eax]
        0x8b, 0x11,            //   01357ade   8b11           mov edx,dword ptr ds:[ecx]
        0x50,                  //   01357ae0   50             push eax
        0x8b, 0x42, 0x04,      //   01357ae1   8b42 04        mov eax,dword ptr ds:[edx+0x4]
        0xff, 0xd0,            //   01357ae4   ffd0           call eax
        0x8b, 0x4c, 0x24, 0x14 //   01357ae6   8b4c24 14      mov ecx,dword ptr ss:[esp+0x14]
    };
    // Offset to the function call from the beginning of the function
    // enum { addr_offset = 0x27 }; // Type2: hex(0x0133CEC7-0x0133CEA0) = hex(0x01357af9-0x1357ad2)
    enum
    {
      hook_offset = -0xc
    };                                // hook parameter
    ULONG addr = processStartAddress; //- sizeof(bytes);
    while (true)
    {
      // addr += sizeof(bytes); // ++ so that each time return diff address
      ULONG range = min(processStopAddress - addr, MAX_REL_ADDR);
      addr = MemDbg::findBytes(bytes, sizeof(bytes), addr, addr + range);
      if (!addr)
      {
        // ITH_MSG(L"failed");
        ConsoleOutput("Rejet: pattern not found");
        return false;
      }
      addr += sizeof(bytes);
      // Push and call at once, i.e. push (0x68) and call (0xe8)
      // 01185345     52             push edx
      // 01185346   . 68 e4fe5501    push dotkares.0155fee4                   ; |arg1 = 0155fee4
      // 0118534b   . e8 1023f9ff    call dotkares.01117660                   ; \dotkares.00377660
      enum
      {
        start = 0x10,
        stop = 0x50
      };
      // Different from FindRejetHook
      DWORD i;
      for (i = start; i < stop; i++)
        if (*(WORD *)(addr + i - 1) == 0x6852 && *(BYTE *)(addr + i + 5) == 0xe8) // 0118534B-01185346
          break;
      if (i < stop)
      {
        addr += i;
        break;
      }
    } // while(0xe8202474 != *(DWORD *)(addr - 3));

    // GROWL_DWORD(addr - processStartAddress); // = 0xb3578 for 剣が君

    ConsoleOutput("INSERT Rejet");
    // The same as type2
    HookParam hp;
    hp.address = addr; //- 0xf;
    hp.type = NO_CONTEXT | DATA_INDIRECT | FIXING_SPLIT;
    hp.offset = hook_offset;

    return NewHook(hp, "Rejet");
  }
} // unnamed Rejet

bool InsertRejetHook()
{
  return InsertRejetHook2() || InsertRejetHook1() || InsertRejetHook3();
} // insert hook2 first, since 2's pattern seems to be more unique

bool Rejet::attach_function()
{

  return InsertRejetHook();
}