#include "MarineHeart.h"

/**
 *  jichi 4/19/2014: Marine Heart
 *  See: http://blgames.proboards.com/post/1984
 *       http://www.yaoiotaku.com/forums/threads/11440-huge-bl-game-torrent
 *
 *  Issue: The extracted text someitems has limited repetition
 *  TODO: It might be better to use FindCallAndEntryAbs for gdi32.CreateFontA?
 *        See how FindCallAndEntryAbs is used in Majiro.
 *
 *  妖恋愛奭�神サマ�堕し方/HS4*0@40D160
 *  - addr: 4247904 = 0x40d160
 *  - off: 4
 *  - type: 9
 *
 *  Function starts
 *  0040d160  /$ 55                 push ebp    ; jichi: hook here
 *  0040d161  |. 8bec               mov ebp,esp
 *  0040d163  |. 83c4 90            add esp,-0x70
 *  0040d166  |. 33c0               xor eax,eax
 *  0040d168  |. 53                 push ebx
 *  0040d169  |. 56                 push esi
 *  0040d16a  |. 57                 push edi
 *  0040d16b  |. 8b75 08            mov esi,dword ptr ss:[ebp+0x8]
 *  0040d16e  |. c745 cc 281e4800   mov dword ptr ss:[ebp-0x34],saisys.00481>
 *  0040d175  |. 8965 d0            mov dword ptr ss:[ebp-0x30],esp
 *  0040d178  |. c745 c8 d0d14700   mov dword ptr ss:[ebp-0x38],<jmp.&cp3245>
 *  0040d17f  |. 66:c745 d4 0000    mov word ptr ss:[ebp-0x2c],0x0
 *  0040d185  |. 8945 e0            mov dword ptr ss:[ebp-0x20],eax
 *  0040d188  |. 64:8b15 00000000   mov edx,dword ptr fs:[0]
 *  0040d18f  |. 8955 c4            mov dword ptr ss:[ebp-0x3c],edx
 *  0040d192  |. 8d4d c4            lea ecx,dword ptr ss:[ebp-0x3c]
 *  0040d195  |. 64:890d 00000000   mov dword ptr fs:[0],ecx
 *  0040d19c  |. 8b05 741c4800      mov eax,dword ptr ds:[0x481c74]
 *  0040d1a2  |. 8945 bc            mov dword ptr ss:[ebp-0x44],eax
 *  0040d1a5  |. 8b05 781c4800      mov eax,dword ptr ds:[0x481c78]
 *  0040d1ab  |. 8945 c0            mov dword ptr ss:[ebp-0x40],eax
 *  0040d1ae  |. 8d46 24            lea eax,dword ptr ds:[esi+0x24]
 *  0040d1b1  |. 8b56 14            mov edx,dword ptr ds:[esi+0x14]
 *  0040d1b4  |. 8955 bc            mov dword ptr ss:[ebp-0x44],edx
 *  0040d1b7  |. 8b10               mov edx,dword ptr ds:[eax]
 *  0040d1b9  |. 85d2               test edx,edx
 *  0040d1bb  |. 74 04              je short saisys.0040d1c1
 *  0040d1bd  |. 8b08               mov ecx,dword ptr ds:[eax]
 *  0040d1bf  |. eb 05              jmp short saisys.0040d1c6
 *  0040d1c1  |> b9 9b1c4800        mov ecx,saisys.00481c9b
 *  0040d1c6  |> 51                 push ecx                                 ; /facename
 *  0040d1c7  |. 6a 01              push 0x1                                 ; |pitchandfamily = fixed_pitch|ff_dontcare
 *  0040d1c9  |. 6a 03              push 0x3                                 ; |quality = 3.
 *  0040d1cb  |. 6a 00              push 0x0                                 ; |clipprecision = clip_default_precis
 *  0040d1cd  |. 6a 00              push 0x0                                 ; |outputprecision = out_default_precis
 *  0040d1cf  |. 68 80000000        push 0x80                                ; |charset = 128.
 *  0040d1d4  |. 6a 00              push 0x0                                 ; |strikeout = false
 *  0040d1d6  |. 6a 00              push 0x0                                 ; |underline = false
 *  0040d1d8  |. 6a 00              push 0x0                                 ; |italic = false
 *  0040d1da  |. 68 90010000        push 0x190                               ; |weight = fw_normal
 *  0040d1df  |. 6a 00              push 0x0                                 ; |orientation = 0x0
 *  0040d1e1  |. 6a 00              push 0x0                                 ; |escapement = 0x0
 *  0040d1e3  |. 6a 00              push 0x0                                 ; |width = 0x0
 *  0040d1e5  |. 8b46 04            mov eax,dword ptr ds:[esi+0x4]           ; |
 *  0040d1e8  |. 50                 push eax                                 ; |height
 *  0040d1e9  |. e8 00fa0600        call <jmp.&gdi32.CreateFontA>            ; \createfonta
 *  0040d1ee  |. 8945 b8            mov dword ptr ss:[ebp-0x48],eax
 *  0040d1f1  |. 8b55 b8            mov edx,dword ptr ss:[ebp-0x48]
 *  0040d1f4  |. 85d2               test edx,edx
 *  0040d1f6  |. 75 14              jnz short saisys.0040d20c
 */
bool InsertMarineHeartHook()
{
  // FIXME: Why this does not work?!
  // jichi 6/3/2014: CreateFontA is only called once in this function
  //  0040d160  /$ 55                 push ebp    ; jichi: hook here
  //  0040d161  |. 8bec               mov ebp,esp
  // ULONG addr = Util::FindCallAndEntryAbs((DWORD)CreateFontA, processStopAddress - processStartAddress, processStartAddress, 0xec8b);

  const BYTE bytes[] = {
      0x51,                         // 0040d1c6  |> 51                 push ecx                        ; /facename
      0x6a, 0x01,                   // 0040d1c7  |. 6a 01              push 0x1                        ; |pitchandfamily = fixed_pitch|ff_dontcare
      0x6a, 0x03,                   // 0040d1c9  |. 6a 03              push 0x3                        ; |quality = 3.
      0x6a, 0x00,                   // 0040d1cb  |. 6a 00              push 0x0                        ; |clipprecision = clip_default_precis
      0x6a, 0x00,                   // 0040d1cd  |. 6a 00              push 0x0                        ; |outputprecision = out_default_precis
      0x68, 0x80, 0x00, 0x00, 0x00, // 0040d1cf  |. 68 80000000        push 0x80                       ; |charset = 128.
      0x6a, 0x00,                   // 0040d1d4  |. 6a 00              push 0x0                        ; |strikeout = false
      0x6a, 0x00,                   // 0040d1d6  |. 6a 00              push 0x0                        ; |underline = false
      0x6a, 0x00,                   // 0040d1d8  |. 6a 00              push 0x0                        ; |italic = false
      0x68, 0x90, 0x01, 0x00, 0x00, // 0040d1da  |. 68 90010000        push 0x190                      ; |weight = fw_normal
      0x6a, 0x00,                   // 0040d1df  |. 6a 00              push 0x0                        ; |orientation = 0x0
      0x6a, 0x00,                   // 0040d1e1  |. 6a 00              push 0x0                        ; |escapement = 0x0
      0x6a, 0x00,                   // 0040d1e3  |. 6a 00              push 0x0                        ; |width = 0x0 0x8b,0x46, 0x04,
      0x8b, 0x46, 0x04,             // 0040d1e5  |. 8b46 04            mov eax,dword ptr ds:[esi+0x4]  ; |
      0x50,                         // 0040d1e8  |. 50                 push eax                        ; |height
      0xe8                          //, 0x00,0xfa,0x06,0x00   // 0040d1e9  |. e8 00fa0600        call <jmp.&gdi32.CreateFontA>   ; \createfonta
  };
  enum
  {
    addr_offset = 0x0040d160 - 0x0040d1c6
  }; // distance to the beginning of the function
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(reladdr);
  if (!addr)
  {
    ConsoleOutput("MarineHeart: pattern not found");
    return false;
  }

  addr += addr_offset;
  // addr = 0x40d160;
  // GROWL_DWORD(addr);
  enum : BYTE
  {
    push_ebp = 0x55
  }; // 011d4c80  /$ 55             push ebp
  if (*(BYTE *)addr != push_ebp)
  {
    ConsoleOutput("MarineHeart: pattern found but the function offset is invalid");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | DATA_INDIRECT; // = 9

  ConsoleOutput("INSERT MarineHeart");
  return NewHook(hp, "MarineHeart");
}

bool MarineHeart::attach_function()
{

  return InsertMarineHeartHook();
}