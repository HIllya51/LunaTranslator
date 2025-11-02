#include "BGI.h"
/********************************************************************************************
BGI hook:
  Usually game folder contains BGI.*. After first run BGI.gdb appears.

  BGI engine has font caching issue so the strategy is simple.
  First find call to TextOutA or TextOutW then reverse to function entry point,
  until full text is caught.
  After 2 tries we will get to the right place. Use ESP value to split text since
  it's likely to be different for different calls.
********************************************************************************************/
namespace
{ // unnamed

  /** jichi 5/12/2014
   *  Sample game:  FORTUNE ARTERIAL, case 2 at 0x41ebd0
   *
   *  sub_41EBD0 proc near, seems to take 5 parameters
   *
   *  0041ebd0  /$ 83ec 28        sub esp,0x28 ; jichi: hook here, beginning of the function
   *  0041ebd3  |. 55             push ebp
   *  0041ebd4  |. 8b6c24 38      mov ebp,dword ptr ss:[esp+0x38]
   *  0041ebd8  |. 81fd 00ff0000  cmp ebp,0xff00
   *  0041ebde  |. 0f82 e1000000  jb bgi.0041ecc5
   *  0041ebe4  |. 81fd ffff0000  cmp ebp,0xffff
   *  0041ebea  |. 0f87 d5000000  ja bgi.0041ecc5
   *  0041ebf0  |. a1 54634900    mov eax,dword ptr ds:[0x496354]
   *  0041ebf5  |. 8bd5           mov edx,ebp
   *  0041ebf7  |. 81e2 ff000000  and edx,0xff
   *  0041ebfd  |. 53             push ebx
   *  0041ebfe  |. 4a             dec edx
   *  0041ebff  |. 33db           xor ebx,ebx
   *  0041ec01  |. 3bd0           cmp edx,eax
   *  0041ec03  |. 56             push esi
   *  0041ec04  |. 0f8d 8a000000  jge bgi.0041ec94
   *  0041ec0a  |. 57             push edi
   *  0041ec0b  |. b9 06000000    mov ecx,0x6
   *  0041ec10  |. be 5c634900    mov esi,bgi.0049635c
   *  0041ec15  |. 8d7c24 20      lea edi,dword ptr ss:[esp+0x20]
   *  0041ec19  |. f3:a5          rep movs dword ptr es:[edi],dword ptr ds>
   *  0041ec1b  |. 8b0d 58634900  mov ecx,dword ptr ds:[0x496358]
   *  0041ec21  |. 8b7424 3c      mov esi,dword ptr ss:[esp+0x3c]
   *  0041ec25  |. 8bc1           mov eax,ecx
   *  0041ec27  |. 5f             pop edi
   *  0041ec28  |. 0fafc2         imul eax,edx
   *  0041ec2b  |. 8b56 08        mov edx,dword ptr ds:[esi+0x8]
   *  0041ec2e  |. 894424 0c      mov dword ptr ss:[esp+0xc],eax
   *  0041ec32  |. 3bca           cmp ecx,edx
   *  0041ec34  |. 7e 02          jle short bgi.0041ec38
   *  0041ec36  |. 8bca           mov ecx,edx
   *  0041ec38  |> 8d4401 ff      lea eax,dword ptr ds:[ecx+eax-0x1]
   *  0041ec3c  |. 8b4c24 28      mov ecx,dword ptr ss:[esp+0x28]
   *  0041ec40  |. 894424 14      mov dword ptr ss:[esp+0x14],eax
   *  0041ec44  |. 8b46 0c        mov eax,dword ptr ds:[esi+0xc]
   *  0041ec47  |. 3bc8           cmp ecx,eax
   *  0041ec49  |. 895c24 10      mov dword ptr ss:[esp+0x10],ebx
   *  0041ec4d  |. 77 02          ja short bgi.0041ec51
   *  0041ec4f  |. 8bc1           mov eax,ecx
   *  0041ec51  |> 8d4c24 0c      lea ecx,dword ptr ss:[esp+0xc]
   *  0041ec55  |. 8d5424 1c      lea edx,dword ptr ss:[esp+0x1c]
   *  0041ec59  |. 48             dec eax
   *  0041ec5a  |. 51             push ecx
   *  0041ec5b  |. 52             push edx
   *  0041ec5c  |. 894424 20      mov dword ptr ss:[esp+0x20],eax
   *  0041ec60  |. e8 7b62feff    call bgi.00404ee0
   *  0041ec65  |. 8b4424 34      mov eax,dword ptr ss:[esp+0x34]
   *  0041ec69  |. 83c4 08        add esp,0x8
   *  0041ec6c  |. 83f8 03        cmp eax,0x3
   *  0041ec6f  |. 75 15          jnz short bgi.0041ec86
   *  0041ec71  |. 8b4424 48      mov eax,dword ptr ss:[esp+0x48]
   *  0041ec75  |. 8d4c24 1c      lea ecx,dword ptr ss:[esp+0x1c]
   *  0041ec79  |. 50             push eax
   *  0041ec7a  |. 51             push ecx
   *  0041ec7b  |. 56             push esi
   *  0041ec7c  |. e8 1fa0feff    call bgi.00408ca0
   */
  bool InsertBGI1Hook()
  {
    union
    {
      DWORD i;
      DWORD *id;
      BYTE *ib;
    };
    HookParam hp;
    for (i = processStartAddress + 0x1000; i < processStopAddress; i++)
    {
      if (ib[0] == 0x3d)
      {
        i++;
        if (id[0] == 0xffff)
        { // cmp eax,0xffff
          hp.address = SafeFindEnclosingAlignedFunction(i, 0x40);
          if (hp.address)
          {
            hp.offset = stackoffset(3);
            hp.split = regoffset(esp);
            hp.type = CODEC_ANSI_BE | USING_SPLIT;
            ConsoleOutput("INSERT BGI#1");

            // RegisterEngineType(ENGINE_BGI);
            return NewHook(hp, "BGI");
          }
        }
      }
      if (ib[0] == 0x81 && ((ib[1] & 0xf8) == 0xf8))
      {
        i += 2;
        if (id[0] == 0xffff)
        { // cmp reg,0xffff
          hp.address = SafeFindEnclosingAlignedFunction(i, 0x40);
          if (hp.address)
          {
            hp.offset = stackoffset(3);
            hp.split = regoffset(esp);
            hp.type = CODEC_ANSI_BE | USING_SPLIT;
            ConsoleOutput("INSERT BGI#2");

            // RegisterEngineType(ENGINE_BGI);
            return NewHook(hp, "BGI");
          }
        }
      }
    }
    // ConsoleOutput("Unknown BGI engine.");

    // ConsoleOutput("Probably BGI. Wait for text.");
    // SwitchTrigger(true);
    // trigger_fun=InsertBGIDynamicHook;
    ConsoleOutput("BGI: failed");
    return false;
  }

  /**
   *  jichi 2/5/2014: Add an alternative BGI hook
   *
   *  Issue: This hook cannot extract character name for コトバの消えた日
   *
   *  See: http://tieba.baidu.com/p/2845113296
   *  世界と世界の真ん中で
   *  - /HSN4@349E0:sekachu.exe // Disabled BGI3, floating split char
   *  - /HS-1C:-4@68E56 // Not used, cannot detect character name
   *  - /HSC@34C80:sekachu.exe  // BGI2, extract both scenario and character names
   *
   *  [Lump of Sugar] 世界と世界の真ん中で
   *  /HSC@34C80:sekachu.exe
   *  - addr: 216192 = 0x34c80
   *  - module: 3599131534
   *  - off: 12 = 0xc
   *  - type: 65 = 0x41
   *
   *  base: 0x11a0000
   *  hook_addr = base + addr = 0x11d4c80
   *
   *  011d4c7e     cc             int3
   *  011d4c7f     cc             int3
   *  011d4c80  /$ 55             push ebp    ; jichi: hook here
   *  011d4c81  |. 8bec           mov ebp,esp
   *  011d4c83  |. 6a ff          push -0x1
   *  011d4c85  |. 68 e6592601    push sekachu.012659e6
   *  011d4c8a  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  011d4c90  |. 50             push eax
   *  011d4c91  |. 81ec 300d0000  sub esp,0xd30
   *  011d4c97  |. a1 d8c82801    mov eax,dword ptr ds:[0x128c8d8]
   *  011d4c9c  |. 33c5           xor eax,ebp
   *  011d4c9e  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
   *  011d4ca1  |. 53             push ebx
   *  011d4ca2  |. 56             push esi
   *  011d4ca3  |. 57             push edi
   *  011d4ca4  |. 50             push eax
   *  011d4ca5  |. 8d45 f4        lea eax,dword ptr ss:[ebp-0xc]
   *  011d4ca8  |. 64:a3 00000000 mov dword ptr fs:[0],eax
   *  011d4cae  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc]
   *  011d4cb1  |. 8b55 18        mov edx,dword ptr ss:[ebp+0x18]
   *  011d4cb4  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  011d4cb7  |. 8b5d 10        mov ebx,dword ptr ss:[ebp+0x10]
   *  011d4cba  |. 8b7d 38        mov edi,dword ptr ss:[ebp+0x38]
   *  011d4cbd  |. 898d d8f3ffff  mov dword ptr ss:[ebp-0xc28],ecx
   *  011d4cc3  |. 8b4d 28        mov ecx,dword ptr ss:[ebp+0x28]
   *  011d4cc6  |. 8995 9cf3ffff  mov dword ptr ss:[ebp-0xc64],edx
   *  011d4ccc  |. 51             push ecx
   *  011d4ccd  |. 8b0d 305c2901  mov ecx,dword ptr ds:[0x1295c30]
   *  011d4cd3  |. 8985 e0f3ffff  mov dword ptr ss:[ebp-0xc20],eax
   *  011d4cd9  |. 8b45 1c        mov eax,dword ptr ss:[ebp+0x1c]
   *  011d4cdc  |. 8d95 4cf4ffff  lea edx,dword ptr ss:[ebp-0xbb4]
   *  011d4ce2  |. 52             push edx
   *  011d4ce3  |. 899d 40f4ffff  mov dword ptr ss:[ebp-0xbc0],ebx
   *  011d4ce9  |. 8985 1cf4ffff  mov dword ptr ss:[ebp-0xbe4],eax
   *  011d4cef  |. 89bd f0f3ffff  mov dword ptr ss:[ebp-0xc10],edi
   *  011d4cf5  |. e8 862efdff    call sekachu.011a7b80
   *  011d4cfa  |. 33c9           xor ecx,ecx
   *  011d4cfc  |. 8985 60f3ffff  mov dword ptr ss:[ebp-0xca0],eax
   *  011d4d02  |. 3bc1           cmp eax,ecx
   *  011d4d04  |. 0f84 0f1c0000  je sekachu.011d6919
   *  011d4d0a  |. e8 31f6ffff    call sekachu.011d4340
   *  011d4d0f  |. e8 6cf8ffff    call sekachu.011d4580
   *  011d4d14  |. 8985 64f3ffff  mov dword ptr ss:[ebp-0xc9c],eax
   *  011d4d1a  |. 8a03           mov al,byte ptr ds:[ebx]
   *  011d4d1c  |. 898d 90f3ffff  mov dword ptr ss:[ebp-0xc70],ecx
   *  011d4d22  |. 898d 14f4ffff  mov dword ptr ss:[ebp-0xbec],ecx
   *  011d4d28  |. 898d 38f4ffff  mov dword ptr ss:[ebp-0xbc8],ecx
   *  011d4d2e  |. 8d71 01        lea esi,dword ptr ds:[ecx+0x1]
   *  011d4d31  |. 3c 20          cmp al,0x20                 ; jichi: pattern starts
   *  011d4d33  |. 7d 75          jge short sekachu.011d4daa
   *  011d4d35  |. 0fbec0         movsx eax,al
   *  011d4d38  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  011d4d3b  |. 83f8 06        cmp eax,0x6
   *  011d4d3e  |. 77 6a          ja short sekachu.011d4daa
   *  011d4d40  |. ff2485 38691d0>jmp dword ptr ds:[eax*4+0x11d6938]
   *
   *  蒼の彼方 体験版 (8/6/2014)
   *  01312cce     cc             int3    ; jichi: reladdr = 0x32cd0
   *  01312ccf     cc             int3
   *  01312cd0   $ 55             push ebp
   *  01312cd1   . 8bec           mov ebp,esp
   *  01312cd3   . 83e4 f8        and esp,0xfffffff8
   *  01312cd6   . 6a ff          push -0x1
   *  01312cd8   . 68 86583a01    push 蒼の彼方.013a5886
   *  01312cdd   . 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  01312ce3   . 50             push eax
   *  01312ce4   . 81ec 38090000  sub esp,0x938
   *  01312cea   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312cef   . 33c4           xor eax,esp
   *  01312cf1   . 898424 3009000>mov dword ptr ss:[esp+0x930],eax
   *  01312cf8   . 53             push ebx
   *  01312cf9   . 56             push esi
   *  01312cfa   . 57             push edi
   *  01312cfb   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312d00   . 33c4           xor eax,esp
   *  01312d02   . 50             push eax
   *  01312d03   . 8d8424 4809000>lea eax,dword ptr ss:[esp+0x948]
   *  01312d0a   . 64:a3 00000000 mov dword ptr fs:[0],eax
   *  01312d10   . 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  01312d13   . 8b7d 0c        mov edi,dword ptr ss:[ebp+0xc]
   *  01312d16   . 8b5d 30        mov ebx,dword ptr ss:[ebp+0x30]
   *  01312d19   . 898424 8800000>mov dword ptr ss:[esp+0x88],eax
   *  01312d20   . 8b45 14        mov eax,dword ptr ss:[ebp+0x14]
   *  01312d23   . 898c24 8c00000>mov dword ptr ss:[esp+0x8c],ecx
   *  01312d2a   . 8b0d a8734a01  mov ecx,dword ptr ds:[0x14a73a8]
   *  01312d30   . 894424 4c      mov dword ptr ss:[esp+0x4c],eax
   *  01312d34   . 899424 bc00000>mov dword ptr ss:[esp+0xbc],edx
   *  01312d3b   . 8b55 20        mov edx,dword ptr ss:[ebp+0x20]
   *  01312d3e   . 51             push ecx                                 ; /arg1 => 00000000
   *  01312d3f   . 8d8424 0c02000>lea eax,dword ptr ss:[esp+0x20c]         ; |
   *  01312d46   . 897c24 34      mov dword ptr ss:[esp+0x34],edi          ; |
   *  01312d4a   . 899c24 8800000>mov dword ptr ss:[esp+0x88],ebx          ; |
   *  01312d51   . e8 ca59fdff    call 蒼の彼方.012e8720                       ; \蒼の彼方.012e8720
   *  01312d56   . 33c9           xor ecx,ecx
   *  01312d58   . 898424 f400000>mov dword ptr ss:[esp+0xf4],eax
   *  01312d5f   . 3bc1           cmp eax,ecx
   *  01312d61   . 0f84 391b0000  je 蒼の彼方.013148a0
   *  01312d67   . e8 54280000    call 蒼の彼方.013155c0
   *  01312d6c   . e8 7f2a0000    call 蒼の彼方.013157f0
   *  01312d71   . 898424 f800000>mov dword ptr ss:[esp+0xf8],eax
   *  01312d78   . 8a07           mov al,byte ptr ds:[edi]
   *  01312d7a   . 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx
   *  01312d81   . 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx
   *  01312d85   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312d89   . b9 01000000    mov ecx,0x1
   *  01312d8e   . 3c 20          cmp al,0x20     ; jichi: pattern starts
   *  01312d90   . 7d 58          jge short 蒼の彼方.01312dea
   *  01312d92   . 0fbec0         movsx eax,al
   *  01312d95   . 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  01312d98   . 83f8 06        cmp eax,0x6
   *  01312d9b   . 77 4d          ja short 蒼の彼方.01312dea
   *  01312d9d   . ff2485 c448310>jmp dword ptr ds:[eax*4+0x13148c4]
   *  01312da4   > 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx          ;  case 2 of switch 01312d95
   *  01312dab   . 03f9           add edi,ecx
   *  01312dad   . eb 37          jmp short 蒼の彼方.01312de6
   *  01312daf   > 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx          ;  case 3 of switch 01312d95
   *  01312db3   . 03f9           add edi,ecx
   *  01312db5   . eb 2f          jmp short 蒼の彼方.01312de6
   *  01312db7   > ba e0103b01    mov edx,蒼の彼方.013b10e0                    ;  case 4 of switch 01312d95
   *  01312dbc   . eb 1a          jmp short 蒼の彼方.01312dd8
   *  01312dbe   > ba e4103b01    mov edx,蒼の彼方.013b10e4                    ;  case 5 of switch 01312d95
   *  01312dc3   . eb 13          jmp short 蒼の彼方.01312dd8
   *  01312dc5   > ba e8103b01    mov edx,蒼の彼方.013b10e8                    ;  case 6 of switch 01312d95
   *  01312dca   . eb 0c          jmp short 蒼の彼方.01312dd8
   *  01312dcc   > ba ec103b01    mov edx,蒼の彼方.013b10ec                    ;  case 7 of switch 01312d95
   *  01312dd1   . eb 05          jmp short 蒼の彼方.01312dd8
   *  01312dd3   > ba f0103b01    mov edx,蒼の彼方.013b10f0                    ;  case 8 of switch 01312d95
   *  01312dd8   > 8d7424 14      lea esi,dword ptr ss:[esp+0x14]
   *  01312ddc   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312de0   . e8 1b8dffff    call 蒼の彼方.0130bb00
   *  01312de5   . 47             inc edi
   *  01312de6   > 897c24 30      mov dword ptr ss:[esp+0x30],edi
   *  01312dea   > 8d8424 0802000>lea eax,dword ptr ss:[esp+0x208]         ;  default case of switch 01312d95
   *  01312df1   . e8 ba1b0000    call 蒼の彼方.013149b0
   *  01312df6   . 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
   *  01312dfa   . 8bb424 2802000>mov esi,dword ptr ss:[esp+0x228]
   *  01312e01   . 894424 5c      mov dword ptr ss:[esp+0x5c],eax
   *  01312e05   . 74 12          je short 蒼の彼方.01312e19
   *  01312e07   . 56             push esi                                 ; /arg1
   *  01312e08   . e8 c31b0000    call 蒼の彼方.013149d0                       ; \蒼の彼方.013149d0
   *  01312e0d   . 83c4 04        add esp,0x4
   *  01312e10   . 898424 c000000>mov dword ptr ss:[esp+0xc0],eax
   *  01312e17   . eb 0b          jmp short 蒼の彼方.01312e24
   *  01312e19   > c78424 c000000>mov dword ptr ss:[esp+0xc0],0x0
   *  01312e24   > 8b4b 04        mov ecx,dword ptr ds:[ebx+0x4]
   *  01312e27   . 0fafce         imul ecx,esi
   *  01312e2a   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e2f   . f7e9           imul ecx
   *  01312e31   . c1fa 05        sar edx,0x5
   *  01312e34   . 8bca           mov ecx,edx
   *  01312e36   . c1e9 1f        shr ecx,0x1f
   *  01312e39   . 03ca           add ecx,edx
   *  01312e3b   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e3f   . 85c9           test ecx,ecx
   *  01312e41   . 7f 09          jg short 蒼の彼方.01312e4c
   *  01312e43   . b9 01000000    mov ecx,0x1
   *  01312e48   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e4c   > 8b53 08        mov edx,dword ptr ds:[ebx+0x8]
   *  01312e4f   . 0fafd6         imul edx,esi
   *  01312e52   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e57   . f7ea           imul edx
   *  01312e59   . c1fa 05        sar edx,0x5
   *  01312e5c   . 8bc2           mov eax,edx
   *  01312e5e   . c1e8 1f        shr eax,0x1f
   *  01312e61   . 03c2           add eax,edx
   *  01312e63   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e67   . 85c0           test eax,eax
   *  01312e69   . 7f 09          jg short 蒼の彼方.01312e74
   *  01312e6b   . b8 01000000    mov eax,0x1
   *  01312e70   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e74   > 33d2           xor edx,edx
   *  01312e76   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e7a   . 895424 6c      mov dword ptr ss:[esp+0x6c],edx
   *  01312e7e   . 8b13           mov edx,dword ptr ds:[ebx]
   *  01312e80   . 4a             dec edx                                  ;  switch (cases 1..2)
   *  01312e81   . 74 0e          je short 蒼の彼方.01312e91
   *  01312e83   . 4a             dec edx
   *  01312e84   . 75 13          jnz short 蒼の彼方.01312e99
   *  01312e86   . 8d1409         lea edx,dword ptr ds:[ecx+ecx]           ;  case 2 of switch 01312e80
   *  01312e89   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e8d   . 03c0           add eax,eax
   *  01312e8f   . eb 04          jmp short 蒼の彼方.01312e95
   *  01312e91   > 894c24 64      mov dword ptr ss:[esp+0x64],ecx          ;  case 1 of switch 01312e80
   *  01312e95   > 894424 6c      mov dword ptr ss:[esp+0x6c],eax
   *  01312e99   > 8b9c24 3802000>mov ebx,dword ptr ss:[esp+0x238]         ;  default case of switch 01312e80
   *  01312ea0   . 8bc3           mov eax,ebx
   *  01312ea2   . e8 d98bffff    call 蒼の彼方.0130ba80
   *  01312ea7   . 8bc8           mov ecx,eax
   *  01312ea9   . 8bc3           mov eax,ebx
   *  01312eab   . e8 e08bffff    call 蒼の彼方.0130ba90
   *  01312eb0   . 6a 01          push 0x1                                 ; /arg1 = 00000001
   *  01312eb2   . 8bd0           mov edx,eax                              ; |
   *  01312eb4   . 8db424 1c01000>lea esi,dword ptr ss:[esp+0x11c]         ; |
   *  01312ebb   . e8 3056fdff    call 蒼の彼方.012e84f0                       ; \蒼の彼方.012e84f0
   *  01312ec0   . 8bc7           mov eax,edi
   *  01312ec2   . 83c4 04        add esp,0x4
   *  01312ec5   . 8d70 01        lea esi,dword ptr ds:[eax+0x1]
   *  01312ec8   > 8a08           mov cl,byte ptr ds:[eax]
   *  01312eca   . 40             inc eax
   *  01312ecb   . 84c9           test cl,cl
   *  01312ecd   .^75 f9          jnz short 蒼の彼方.01312ec8
   *  01312ecf   . 2bc6           sub eax,esi
   *  01312ed1   . 40             inc eax
   *  01312ed2   . 50             push eax
   *  01312ed3   . e8 e74c0600    call 蒼の彼方.01377bbf
   *  01312ed8   . 33f6           xor esi,esi
   *  01312eda   . 83c4 04        add esp,0x4
   *
   *  1/1/2016
   *  コドモノアソビ trial
   *
   *  00A64259   CC               INT3
   *  00A6425A   CC               INT3
   *  00A6425B   CC               INT3
   *  00A6425C   CC               INT3
   *  00A6425D   CC               INT3
   *  00A6425E   CC               INT3
   *  00A6425F   CC               INT3
   *  00A64260   55               PUSH EBP
   *  00A64261   8BEC             MOV EBP,ESP
   *  00A64263   83E4 F8          AND ESP,0xFFFFFFF8
   *  00A64266   6A FF            PUSH -0x1
   *  00A64268   68 D610B000      PUSH .00B010D6
   *  00A6426D   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
   *  00A64273   50               PUSH EAX
   *  00A64274   81EC 40090000    SUB ESP,0x940
   *  00A6427A   A1 2417B200      MOV EAX,DWORD PTR DS:[0xB21724]
   *  00A6427F   33C4             XOR EAX,ESP
   *  00A64281   898424 38090000  MOV DWORD PTR SS:[ESP+0x938],EAX
   *  00A64288   53               PUSH EBX
   *  00A64289   56               PUSH ESI
   *  00A6428A   57               PUSH EDI
   *  00A6428B   A1 2417B200      MOV EAX,DWORD PTR DS:[0xB21724]
   *  00A64290   33C4             XOR EAX,ESP
   *  00A64292   50               PUSH EAX
   *  00A64293   8D8424 50090000  LEA EAX,DWORD PTR SS:[ESP+0x950]
   *  00A6429A   64:A3 00000000   MOV DWORD PTR FS:[0],EAX
   *  00A642A0   8B45 08          MOV EAX,DWORD PTR SS:[EBP+0x8]
   *  00A642A3   8B7D 0C          MOV EDI,DWORD PTR SS:[EBP+0xC]
   *  00A642A6   8B5D 30          MOV EBX,DWORD PTR SS:[EBP+0x30]
   *  00A642A9   894424 50        MOV DWORD PTR SS:[ESP+0x50],EAX
   *  00A642AD   8B45 14          MOV EAX,DWORD PTR SS:[EBP+0x14]
   *  00A642B0   894C24 74        MOV DWORD PTR SS:[ESP+0x74],ECX
   *  00A642B4   8B0D A024B800    MOV ECX,DWORD PTR DS:[0xB824A0]
   *  00A642BA   894424 4C        MOV DWORD PTR SS:[ESP+0x4C],EAX
   *  00A642BE   899424 B8000000  MOV DWORD PTR SS:[ESP+0xB8],EDX
   *  00A642C5   8B55 20          MOV EDX,DWORD PTR SS:[EBP+0x20]
   *  00A642C8   51               PUSH ECX
   *  00A642C9   8D8424 14020000  LEA EAX,DWORD PTR SS:[ESP+0x214]
   *  00A642D0   897C24 2C        MOV DWORD PTR SS:[ESP+0x2C],EDI
   *  00A642D4   899C24 88000000  MOV DWORD PTR SS:[ESP+0x88],EBX
   *  00A642DB   E8 504CFDFF      CALL .00A38F30
   *  00A642E0   33C9             XOR ECX,ECX
   *  00A642E2   898424 F8000000  MOV DWORD PTR SS:[ESP+0xF8],EAX
   *  00A642E9   3BC1             CMP EAX,ECX
   *  00A642EB   0F84 391C0000    JE .00A65F2A
   *  00A642F1   E8 FA2A0000      CALL .00A66DF0
   *  00A642F6   E8 252D0000      CALL .00A67020
   *  00A642FB   898424 FC000000  MOV DWORD PTR SS:[ESP+0xFC],EAX
   *  00A64302   8A07             MOV AL,BYTE PTR DS:[EDI]
   *  00A64304   898C24 CC000000  MOV DWORD PTR SS:[ESP+0xCC],ECX
   *  00A6430B   894C24 30        MOV DWORD PTR SS:[ESP+0x30],ECX
   *  00A6430F   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
   *  00A64313   B9 01000000      MOV ECX,0x1
   *  00A64318   3C 20            CMP AL,0x20  ; jichi: pattern found here
   *  00A6431A   7D 58            JGE SHORT .00A64374
   *  00A6431C   0FBEC0           MOVSX EAX,AL
   *  00A6431F   83C0 FE          ADD EAX,-0x2
   *  00A64322   83F8 06          CMP EAX,0x6
   *  00A64325   77 4D            JA SHORT .00A64374
   *  00A64327   FF2485 505FA600  JMP DWORD PTR DS:[EAX*4+0xA65F50]
   *  00A6432E   898C24 CC000000  MOV DWORD PTR SS:[ESP+0xCC],ECX
   *  00A64335   03F9             ADD EDI,ECX
   *  00A64337   EB 37            JMP SHORT .00A64370
   *  00A64339   894C24 30        MOV DWORD PTR SS:[ESP+0x30],ECX
   *  00A6433D   03F9             ADD EDI,ECX
   *  00A6433F   EB 2F            JMP SHORT .00A64370
   *  00A64341   BA E0C1B000      MOV EDX,.00B0C1E0
   *  00A64346   EB 1A            JMP SHORT .00A64362
   *  00A64348   BA E4C1B000      MOV EDX,.00B0C1E4
   *  00A6434D   EB 13            JMP SHORT .00A64362
   *  00A6434F   BA E8C1B000      MOV EDX,.00B0C1E8
   *  00A64354   EB 0C            JMP SHORT .00A64362
   *  00A64356   BA ECC1B000      MOV EDX,.00B0C1EC
   *  00A6435B   EB 05            JMP SHORT .00A64362
   *  00A6435D   BA F0C1B000      MOV EDX,.00B0C1F0
   *  00A64362   8D7424 14        LEA ESI,DWORD PTR SS:[ESP+0x14]
   *  00A64366   894C24 1C        MOV DWORD PTR SS:[ESP+0x1C],ECX
   *  00A6436A   E8 A196FFFF      CALL .00A5DA10
   *  00A6436F   47               INC EDI
   *  00A64370   897C24 28        MOV DWORD PTR SS:[ESP+0x28],EDI
   *  00A64374   8D8424 10020000  LEA EAX,DWORD PTR SS:[ESP+0x210]
   *  00A6437B   E8 C01C0000      CALL .00A66040
   *  00A64380   837D 10 00       CMP DWORD PTR SS:[EBP+0x10],0x0
   *  00A64384   8BB424 30020000  MOV ESI,DWORD PTR SS:[ESP+0x230]
   *  00A6438B   894424 60        MOV DWORD PTR SS:[ESP+0x60],EAX
   *  00A6438F   74 12            JE SHORT .00A643A3
   *  00A64391   56               PUSH ESI
   *  00A64392   E8 C91C0000      CALL .00A66060
   *  00A64397   83C4 04          ADD ESP,0x4
   *  00A6439A   898424 C4000000  MOV DWORD PTR SS:[ESP+0xC4],EAX
   *  00A643A1   EB 0B            JMP SHORT .00A643AE
   *  00A643A3   C78424 C4000000 >MOV DWORD PTR SS:[ESP+0xC4],0x0
   *  00A643AE   8B4B 04          MOV ECX,DWORD PTR DS:[EBX+0x4]
   *  00A643B1   0FAFCE           IMUL ECX,ESI
   *  00A643B4   B8 1F85EB51      MOV EAX,0x51EB851F
   *  00A643B9   F7E9             IMUL ECX
   *  00A643BB   C1FA 05          SAR EDX,0x5
   *  00A643BE   8BCA             MOV ECX,EDX
   *  00A643C0   C1E9 1F          SHR ECX,0x1F
   *  00A643C3   03CA             ADD ECX,EDX
   *  00A643C5   898C24 94000000  MOV DWORD PTR SS:[ESP+0x94],ECX
   *  00A643CC   85C9             TEST ECX,ECX
   *  00A643D0   B9 01000000      MOV ECX,0x1
   *  ...
   */
  // static inline size_t _bgistrlen(LPCSTR text)
  //{
  //   size_t r = ::strlen(text);
  //   if (r >=2 && *(WORD *)(text + r - 2) == 0xa581) // remove trailing ▼ = \x81\xa5
  //     r -= 2;
  //   return r;
  // }
  //
  // static void SpecialHookBGI2(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
  //{
  //   LPCSTR text = (LPCSTR)*(DWORD *)(esp_base + hp->offset);
  //   if (text) {
  //     *data = (DWORD)text;
  //     *len = _bgistrlen(text);
  //   }
  // }
  namespace Private
  {
    enum
    {
      Type1 = 1,
      Type2,
      Type3,
      Type_BGI3
    } type_;
    int textIndex_; // the i-th of argument on the stack holding the text
    void hookBefore(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
    {
      if (type_ == Type_BGI3)
      {

        DWORD retaddr = s->stack[0]; // retaddr
        *role = Engine::ScenarioRole;
        buffer->from((LPCSTR)s->stack[textIndex_]);
        return;
      }

      static std::string data_; // persistent storage, which makes this function not thread-safe

      LPCSTR text = (LPCSTR)s->stack[textIndex_]; // arg2 or arg3
      if (!text || !*text)
        return;
      // In Type 1, split = arg8
      // In Type 2, there is no arg8. However, arg8 seems to be a good split that can differenciate choice and character name
      // DWORD split = context->args[3]; // arg4
      // DWORD split = s->stack[8]; // arg8
      // auto sig = Engine::hashThreadSignature(s->stack[0], split);
      // enum { role = Engine::UnknownRole };

      // DWORD split = s->stack[8]; // this is a good split, but usually game-specific
      DWORD retaddr = s->stack[0]; // retaddr
      //* role = Engine::OtherRole;
      switch (type_)
      {

      case Type3:
        switch (s->stack[textIndex_ + 1])
        {
        case 1:
          if (*(WORD *)(retaddr + 8) == 0xcccc) // two int3
            *role = Engine::ScenarioRole;
          break;
        case 0:
          if (s->stack[10] == 0x00ffffff && s->stack[10 - 3] == 1 ||               // for old BGI2 games
              s->stack[10] == 0 && s->stack[10 - 1] == 0 && s->stack[10 - 2] == 0) // for new BGI2 games
            *role = Engine::NameRole;
          break;
        }
        break;
      case Type2:
        switch (s->stack[textIndex_ + 1])
        {
        case 1:
          // Return address for history text
          // 012B37BA   83C4 34          ADD ESP,0x34
          // 012B37BD   837D 24 00       CMP DWORD PTR SS:[EBP+0x24],0x0
          if (*(WORD *)(retaddr + 3) != 0x7d83)
            *role = Engine::ScenarioRole;
          break;
        case 0:
          if (s->stack[12] == 0x00ffffff && s->stack[12 - 3] == 2)
            *role = Engine::NameRole;
          break;
        }
        break;
      case Type1:
        switch (s->stack[textIndex_ + 1])
        {
        case 1:
          *role = Engine::ScenarioRole;
          break;
        case 0:
          if (s->stack[12] == 0x00ffffff && s->stack[12 - 3] == 1)
            *role = Engine::NameRole;
          break;
        }
        break;
      }

      buffer->from((LPCSTR)s->stack[textIndex_]);
    }

  }

  /**
   *  5/12/2014
   *  This is the caller of the ITH BGI hook, which extract text by characters
   *  and cannot be used for substition.
   *
   *  Sample game: 世界征服彼女
   *  ITH hooked function: BGI#2 0x425550, called by 0x427450
   *
   *  00427450  /$ 6a ff          push -0x1  ; jichi: function starts
   *  00427452  |. 68 78634900    push sekajyo_.00496378                   ;  se handler installation
   *  00427457  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  0042745d  |. 50             push eax
   *  0042745e  |. 64:8925 000000>mov dword ptr fs:[0],esp
   *  00427465  |. 81ec d80c0000  sub esp,0xcd8
   *  0042746b  |. 8b8424 080d000>mov eax,dword ptr ss:[esp+0xd08]
   *  00427472  |. 56             push esi
   *  00427473  |. 8d8c24 3801000>lea ecx,dword ptr ss:[esp+0x138]
   *  0042747a  |. 50             push eax
   *  0042747b  |. 51             push ecx
   *  0042747c  |. 8b0d e0464b00  mov ecx,dword ptr ds:[0x4b46e0]
   *  00427482  |. e8 f9fdfdff    call sekajyo_.00407280
   *  00427487  |. 33f6           xor esi,esi
   *  00427489  |. 898424 b800000>mov dword ptr ss:[esp+0xb8],eax
   *  00427490  |. 3bc6           cmp eax,esi
   *  00427492  |. 0f84 95140000  je sekajyo_.0042892d
   *  00427498  |. 53             push ebx
   *  00427499  |. 55             push ebp
   *  0042749a  |. 8bac24 fc0c000>mov ebp,dword ptr ss:[esp+0xcfc]
   *  004274a1  |. 57             push edi
   *  004274a2  |. 89b424 b400000>mov dword ptr ss:[esp+0xb4],esi
   *  004274a9  |. 897424 10      mov dword ptr ss:[esp+0x10],esi
   *  004274ad  |. 8a45 00        mov al,byte ptr ss:[ebp]
   *  004274b0  |. b9 01000000    mov ecx,0x1
   *  004274b5  |. 3c 20          cmp al,0x20
   *  004274b7  |. 7d 68          jge short sekajyo_.00427521
   *  004274b9  |. 0fbec0         movsx eax,al
   *  004274bc  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *
   *  Sample game: FORTUNE ARTERIAL
   *  ITH hooked function: BGI#2 sub_41EBD0, called by 0x4207e0
   *
   *  0041ebcd     90             nop
   *  0041ebce     90             nop
   *  0041ebcf     90             nop
   *  004207e0  /$ 81ec 30090000  sub esp,0x930   ; jichi: function starts
   *  004207e6  |. 8b8424 5409000>mov eax,dword ptr ss:[esp+0x954]
   *  004207ed  |. 56             push esi
   *  004207ee  |. 8d8c24 0401000>lea ecx,dword ptr ss:[esp+0x104]
   *  004207f5  |. 50             push eax
   *  004207f6  |. 51             push ecx
   *  004207f7  |. 8b0d 48634900  mov ecx,dword ptr ds:[0x496348]
   *  004207fd  |. e8 ee47feff    call bgi.00404ff0
   *  00420802  |. 33f6           xor esi,esi
   *  00420804  |. 894424 54      mov dword ptr ss:[esp+0x54],eax
   *  00420808  |. 3bc6           cmp eax,esi
   *  0042080a  |. 0f84 94080000  je bgi.004210a4
   *  00420810  |. 53             push ebx
   *  00420811  |. 55             push ebp
   *  00420812  |. 8bac24 4809000>mov ebp,dword ptr ss:[esp+0x948]
   *  00420819  |. 57             push edi
   *  0042081a  |. 897424 54      mov dword ptr ss:[esp+0x54],esi
   *  0042081e  |. 897424 10      mov dword ptr ss:[esp+0x10],esi
   *  00420822  |. 8a45 00        mov al,byte ptr ss:[ebp]
   *  00420825  |. 3c 20          cmp al,0x20
   *  00420827  |. 7d 69          jge short bgi.00420892
   *  00420829  |. 0fbec0         movsx eax,al
   *  0042082c  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  0042082f  |. 83f8 06        cmp eax,0x6
   *  00420832  |. 77 5e          ja short bgi.00420892
   *  00420834  |. ff2485 ac10420>jmp dword ptr ds:[eax*4+0x4210ac]
   *  0042083b  |> c74424 54 0100>mov dword ptr ss:[esp+0x54],0x1          ;  case 2 of switch 0042082c
   *  00420843  |. eb 45          jmp short bgi.0042088a
   *  00420845  |> 8d5424 1c      lea edx,dword ptr ss:[esp+0x1c]          ;  case 4 of switch 0042082c
   *  00420849  |. 68 0c424800    push bgi.0048420c
   *  0042084e  |. 52             push edx
   *  0042084f  |. eb 29          jmp short bgi.0042087a
   *  00420851  |> 68 08424800    push bgi.00484208                        ;  case 5 of switch 0042082c
   *  00420856  |. eb 1d          jmp short bgi.00420875
   *  00420858  |> 8d4c24 1c      lea ecx,dword ptr ss:[esp+0x1c]          ;  case 6 of switch 0042082c
   *  0042085c  |. 68 04424800    push bgi.00484204
   *  00420861  |. 51             push ecx
   *  00420862  |. eb 16          jmp short bgi.0042087a
   *  00420864  |> 8d5424 1c      lea edx,dword ptr ss:[esp+0x1c]          ;  case 7 of switch 0042082c
   *  00420868  |. 68 00424800    push bgi.00484200
   *  0042086d  |. 52             push edx
   *  0042086e  |. eb 0a          jmp short bgi.0042087a
   *  00420870  |> 68 fc414800    push bgi.004841fc                        ;  case 8 of switch 0042082c
   *  00420875  |> 8d4424 20      lea eax,dword ptr ss:[esp+0x20]
   *  00420879  |. 50             push eax
   *  0042087a  |> c74424 18 0100>mov dword ptr ss:[esp+0x18],0x1
   *  00420882  |. e8 b9a7ffff    call bgi.0041b040
   *  00420887  |. 83c4 08        add esp,0x8
   *  0042088a  |> 45             inc ebp
   *  0042088b  |. 89ac24 4c09000>mov dword ptr ss:[esp+0x94c],ebp
   *  00420892  |> 8b9c24 3001000>mov ebx,dword ptr ss:[esp+0x130]         ;  default case of switch 0042082c
   *  00420899  |. 8d8c24 1001000>lea ecx,dword ptr ss:[esp+0x110]
   *  004208a0  |. 51             push ecx
   *  004208a1  |. 895c24 70      mov dword ptr ss:[esp+0x70],ebx
   *  004208a5  |. e8 76080000    call bgi.00421120
   *  004208aa  |. 894424 34      mov dword ptr ss:[esp+0x34],eax
   *  004208ae  |. 8b8424 5409000>mov eax,dword ptr ss:[esp+0x954]
   *  004208b5  |. 83c4 04        add esp,0x4
   *  004208b8  |. 3bc6           cmp eax,esi
   *  004208ba  |. 74 0f          je short bgi.004208cb
   *  004208bc  |. 53             push ebx
   *  004208bd  |. e8 7e080000    call bgi.00421140
   */
  ULONG search1(ULONG startAddress, ULONG stopAddress)
  {
    // return 0x4207e0; // FORTUNE ARTERIAL
    // const BYTE bytes[] = {
    //   0x8a,0x45, 0x00,  // 00420822  |. 8a45 00        mov al,byte ptr ss:[ebp]
    //   0x3c, 0x20,       // 00420825  |. 3c 20          cmp al,0x20
    //   0x7d, 0x69,       // 00420827  |. 7d 69          jge short bgi.00420892
    //   0x0f,0xbe,0xc0,   // 00420829  |. 0fbec0         movsx eax,al
    //   0x83,0xc0, 0xfe,  // 0042082c  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
    //   0x83,0xf8, 0x06,  // 0042082f  |. 83f8 06        cmp eax,0x6
    //   0x77, 0x5e        // 00420832  |. 77 5e          ja short bgi.00420892
    // };
    // enum { hook_offset = 0x4207e0 - 0x420822 }; // distance to the beginning of the function

    const uint8_t bytes[] = {
        // 0fafcbf7e9c1fa058bc2c1e81f03d08bfa85ff
        0x0f, 0xaf, 0xcb, // 004208de  |. 0fafcb         imul ecx,ebx
        0xf7, 0xe9,       // 004208e1  |. f7e9           imul ecx
        0xc1, 0xfa, 0x05, // 004208e3  |. c1fa 05        sar edx,0x5
        0x8b, 0xc2,       // 004208e6  |. 8bc2           mov eax,edx
        0xc1, 0xe8, 0x1f, // 004208e8  |. c1e8 1f        shr eax,0x1f
        0x03, 0xd0,       // 004208eb  |. 03d0           add edx,eax
        0x8b, 0xfa,       // 004208ed  |. 8bfa           mov edi,edx
        0x85, 0xff,       // 004208ef  |. 85ff           test edi,edi
    };
    // enum { hook_offset = 0x4207e0 - 0x4208de }; // distance to the beginning of the function
    // ULONG range = qMin(stopAddress - startAddress, Engine::MaximumMemoryRange);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      // ConsoleOutput("BGI2: pattern not found");
      return 0;
    enum : WORD
    {
      sub_esp = 0xec81 // 004207e0  /$ 81ec 30090000
      ,
      push_ff = 0xff6a // 00427450  /$ 6a ff   push -0x1, seh handler
    };
    for (int i = 0; i < 300; i++, addr--)
      if (*(WORD *)addr == sub_esp)
      { // beginning of the function without seh

        // Sample game: 世界征服彼女 with SEH
        // 00427450  /$ 6a ff          push -0x1
        // 00427452  |. 68 78634900    push sekajyo_.00496378                   ;  se handler installation
        // 00427457  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
        // 0042745d  |. 50             push eax
        // 0042745e  |. 64:8925 000000>mov dword ptr fs:[0],esp
        // 00427465  |. 81ec d80c0000  sub esp,0xcd8
        //
        // 0x00427465 - 0x00427450 == 21
        ULONG seh_addr = addr;
        for (int j = 0; j < 40; j++, seh_addr--)
          if (*(WORD *)seh_addr == push_ff) // beginning of the function with seh
            return seh_addr;
        return addr;
      }

    return 0;
  }

  /**
   *  jichi 2/5/2014: Add an alternative BGI hook
   *
   *  Issue: This hook cannot extract character name for コトバの消えた日
   *
   *  See: http://tieba.baidu.com/p/2845113296
   *  世界と世界の真ん中で
   *  - /HSN4@349E0:sekachu.exe // Disabled BGI3, floating split char
   *  - /HS-1C:-4@68E56 // Not used, cannot detect character name
   *  - /HSC@34C80:sekachu.exe  // BGI2, extract both scenario and character names
   *
   *  [Lump of Sugar] 世界と世界の真ん中で
   *  /HSC@34C80:sekachu.exe
   *  - addr: 216192 = 0x34c80
   *  - module: 3599131534
   *  - off: 12 = 0xc
   *  - type: 65 = 0x41
   *
   *  base: 0x11a0000
   *  hook_addr = base + addr = 0x11d4c80
   *
   *  011d4c7e     cc             int3
   *  011d4c7f     cc             int3
   *  011d4c80  /$ 55             push ebp    ; jichi: hook here
   *  011d4c81  |. 8bec           mov ebp,esp
   *  011d4c83  |. 6a ff          push -0x1
   *  011d4c85  |. 68 e6592601    push sekachu.012659e6
   *  011d4c8a  |. 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  011d4c90  |. 50             push eax
   *  011d4c91  |. 81ec 300d0000  sub esp,0xd30
   *  011d4c97  |. a1 d8c82801    mov eax,dword ptr ds:[0x128c8d8]
   *  011d4c9c  |. 33c5           xor eax,ebp
   *  011d4c9e  |. 8945 f0        mov dword ptr ss:[ebp-0x10],eax
   *  011d4ca1  |. 53             push ebx
   *  011d4ca2  |. 56             push esi
   *  011d4ca3  |. 57             push edi
   *  011d4ca4  |. 50             push eax
   *  011d4ca5  |. 8d45 f4        lea eax,dword ptr ss:[ebp-0xc]
   *  011d4ca8  |. 64:a3 00000000 mov dword ptr fs:[0],eax
   *  011d4cae  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc]
   *  011d4cb1  |. 8b55 18        mov edx,dword ptr ss:[ebp+0x18]
   *  011d4cb4  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  011d4cb7  |. 8b5d 10        mov ebx,dword ptr ss:[ebp+0x10]
   *  011d4cba  |. 8b7d 38        mov edi,dword ptr ss:[ebp+0x38]
   *  011d4cbd  |. 898d d8f3ffff  mov dword ptr ss:[ebp-0xc28],ecx
   *  011d4cc3  |. 8b4d 28        mov ecx,dword ptr ss:[ebp+0x28]
   *  011d4cc6  |. 8995 9cf3ffff  mov dword ptr ss:[ebp-0xc64],edx
   *  011d4ccc  |. 51             push ecx
   *  011d4ccd  |. 8b0d 305c2901  mov ecx,dword ptr ds:[0x1295c30]
   *  011d4cd3  |. 8985 e0f3ffff  mov dword ptr ss:[ebp-0xc20],eax
   *  011d4cd9  |. 8b45 1c        mov eax,dword ptr ss:[ebp+0x1c]
   *  011d4cdc  |. 8d95 4cf4ffff  lea edx,dword ptr ss:[ebp-0xbb4]
   *  011d4ce2  |. 52             push edx
   *  011d4ce3  |. 899d 40f4ffff  mov dword ptr ss:[ebp-0xbc0],ebx
   *  011d4ce9  |. 8985 1cf4ffff  mov dword ptr ss:[ebp-0xbe4],eax
   *  011d4cef  |. 89bd f0f3ffff  mov dword ptr ss:[ebp-0xc10],edi
   *  011d4cf5  |. e8 862efdff    call sekachu.011a7b80
   *  011d4cfa  |. 33c9           xor ecx,ecx
   *  011d4cfc  |. 8985 60f3ffff  mov dword ptr ss:[ebp-0xca0],eax
   *  011d4d02  |. 3bc1           cmp eax,ecx
   *  011d4d04  |. 0f84 0f1c0000  je sekachu.011d6919
   *  011d4d0a  |. e8 31f6ffff    call sekachu.011d4340
   *  011d4d0f  |. e8 6cf8ffff    call sekachu.011d4580
   *  011d4d14  |. 8985 64f3ffff  mov dword ptr ss:[ebp-0xc9c],eax
   *  011d4d1a  |. 8a03           mov al,byte ptr ds:[ebx]
   *  011d4d1c  |. 898d 90f3ffff  mov dword ptr ss:[ebp-0xc70],ecx
   *  011d4d22  |. 898d 14f4ffff  mov dword ptr ss:[ebp-0xbec],ecx
   *  011d4d28  |. 898d 38f4ffff  mov dword ptr ss:[ebp-0xbc8],ecx
   *  011d4d2e  |. 8d71 01        lea esi,dword ptr ds:[ecx+0x1]
   *  011d4d31  |. 3c 20          cmp al,0x20
   *  011d4d33  |. 7d 75          jge short sekachu.011d4daa
   *  011d4d35  |. 0fbec0         movsx eax,al
   *  011d4d38  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  011d4d3b  |. 83f8 06        cmp eax,0x6
   *  011d4d3e  |. 77 6a          ja short sekachu.011d4daa
   *  011d4d40  |. ff2485 38691d0>jmp dword ptr ds:[eax*4+0x11d6938]
   */
  ULONG search2(ULONG startAddress, ULONG stopAddress)
  {
    // return startAddress + 0x31850; // 世界と世界の真ん中 体験版
    const uint8_t bytes[] = {
        // 3c207d750fbec083c0fe83f806776a
        0x3c, 0x20,       // 011d4d31  |. 3c 20          cmp al,0x20
        0x7d, 0x75,       // 011d4d33  |. 7d 75          jge short sekachu.011d4daa
        0x0f, 0xbe, 0xc0, // 011d4d35  |. 0fbec0         movsx eax,al
        0x83, 0xc0, 0xfe, // 011d4d38  |. 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
        0x83, 0xf8, 0x06, // 011d4d3b  |. 83f8 06        cmp eax,0x6
        0x77, 0x6a        // 011d4d3e  |. 77 6a          ja short sekachu.011d4daa
    };
    enum
    {
      hook_offset = 0x34c80 - 0x34d31
    }; // distance to the beginning of the function
    // ULONG range = qMin(stopAddress - startAddress, Engine::MaximumMemoryRange);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      // ConsoleOutput("BGI2: pattern not found");
      return 0;

    addr += hook_offset;
    enum : uint8_t
    {
      push_ebp = 0x55
    }; // 011d4c80  /$ 55             push ebp
    if (*(uint8_t *)addr != push_ebp)
      // ConsoleOutput("BGI2: pattern found but the function offset is invalid");
      return 0;

    return addr;
  }

  /**
   *  Sample Game: type 3: 蒼の彼方 体験版 (8/6/2014)
   *  01312cce     cc             int3    ; jichi: reladdr = 0x32cd0
   *  01312ccf     cc             int3
   *  01312cd0   $ 55             push ebp
   *  01312cd1   . 8bec           mov ebp,esp
   *  01312cd3   . 83e4 f8        and esp,0xfffffff8
   *  01312cd6   . 6a ff          push -0x1
   *  01312cd8   . 68 86583a01    push 蒼の彼方.013a5886
   *  01312cdd   . 64:a1 00000000 mov eax,dword ptr fs:[0]
   *  01312ce3   . 50             push eax
   *  01312ce4   . 81ec 38090000  sub esp,0x938
   *  01312cea   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312cef   . 33c4           xor eax,esp
   *  01312cf1   . 898424 3009000>mov dword ptr ss:[esp+0x930],eax
   *  01312cf8   . 53             push ebx
   *  01312cf9   . 56             push esi
   *  01312cfa   . 57             push edi
   *  01312cfb   . a1 24673c01    mov eax,dword ptr ds:[0x13c6724]
   *  01312d00   . 33c4           xor eax,esp
   *  01312d02   . 50             push eax
   *  01312d03   . 8d8424 4809000>lea eax,dword ptr ss:[esp+0x948]
   *  01312d0a   . 64:a3 00000000 mov dword ptr fs:[0],eax
   *  01312d10   . 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
   *  01312d13   . 8b7d 0c        mov edi,dword ptr ss:[ebp+0xc]
   *  01312d16   . 8b5d 30        mov ebx,dword ptr ss:[ebp+0x30]
   *  01312d19   . 898424 8800000>mov dword ptr ss:[esp+0x88],eax
   *  01312d20   . 8b45 14        mov eax,dword ptr ss:[ebp+0x14]
   *  01312d23   . 898c24 8c00000>mov dword ptr ss:[esp+0x8c],ecx
   *  01312d2a   . 8b0d a8734a01  mov ecx,dword ptr ds:[0x14a73a8]
   *  01312d30   . 894424 4c      mov dword ptr ss:[esp+0x4c],eax
   *  01312d34   . 899424 bc00000>mov dword ptr ss:[esp+0xbc],edx
   *  01312d3b   . 8b55 20        mov edx,dword ptr ss:[ebp+0x20]
   *  01312d3e   . 51             push ecx                                 ; /arg1 => 00000000
   *  01312d3f   . 8d8424 0c02000>lea eax,dword ptr ss:[esp+0x20c]         ; |
   *  01312d46   . 897c24 34      mov dword ptr ss:[esp+0x34],edi          ; |
   *  01312d4a   . 899c24 8800000>mov dword ptr ss:[esp+0x88],ebx          ; |
   *  01312d51   . e8 ca59fdff    call 蒼の彼方.012e8720                       ; \蒼の彼方.012e8720
   *  01312d56   . 33c9           xor ecx,ecx
   *  01312d58   . 898424 f400000>mov dword ptr ss:[esp+0xf4],eax
   *  01312d5f   . 3bc1           cmp eax,ecx
   *  01312d61   . 0f84 391b0000  je 蒼の彼方.013148a0
   *  01312d67   . e8 54280000    call 蒼の彼方.013155c0
   *  01312d6c   . e8 7f2a0000    call 蒼の彼方.013157f0
   *  01312d71   . 898424 f800000>mov dword ptr ss:[esp+0xf8],eax
   *  01312d78   . 8a07           mov al,byte ptr ds:[edi]
   *  01312d7a   . 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx
   *  01312d81   . 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx
   *  01312d85   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312d89   . b9 01000000    mov ecx,0x1
   *  01312d8e   . 3c 20          cmp al,0x20     ; jichi: pattern starts
   *  01312d90   . 7d 58          jge short 蒼の彼方.01312dea
   *  01312d92   . 0fbec0         movsx eax,al
   *  01312d95   . 83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
   *  01312d98   . 83f8 06        cmp eax,0x6
   *  01312d9b   . 77 4d          ja short 蒼の彼方.01312dea
   *  01312d9d   . ff2485 c448310>jmp dword ptr ds:[eax*4+0x13148c4]
   *  01312da4   > 898c24 c400000>mov dword ptr ss:[esp+0xc4],ecx          ;  case 2 of switch 01312d95
   *  01312dab   . 03f9           add edi,ecx
   *  01312dad   . eb 37          jmp short 蒼の彼方.01312de6
   *  01312daf   > 894c24 2c      mov dword ptr ss:[esp+0x2c],ecx          ;  case 3 of switch 01312d95
   *  01312db3   . 03f9           add edi,ecx
   *  01312db5   . eb 2f          jmp short 蒼の彼方.01312de6
   *  01312db7   > ba e0103b01    mov edx,蒼の彼方.013b10e0                    ;  case 4 of switch 01312d95
   *  01312dbc   . eb 1a          jmp short 蒼の彼方.01312dd8
   *  01312dbe   > ba e4103b01    mov edx,蒼の彼方.013b10e4                    ;  case 5 of switch 01312d95
   *  01312dc3   . eb 13          jmp short 蒼の彼方.01312dd8
   *  01312dc5   > ba e8103b01    mov edx,蒼の彼方.013b10e8                    ;  case 6 of switch 01312d95
   *  01312dca   . eb 0c          jmp short 蒼の彼方.01312dd8
   *  01312dcc   > ba ec103b01    mov edx,蒼の彼方.013b10ec                    ;  case 7 of switch 01312d95
   *  01312dd1   . eb 05          jmp short 蒼の彼方.01312dd8
   *  01312dd3   > ba f0103b01    mov edx,蒼の彼方.013b10f0                    ;  case 8 of switch 01312d95
   *  01312dd8   > 8d7424 14      lea esi,dword ptr ss:[esp+0x14]
   *  01312ddc   . 894c24 1c      mov dword ptr ss:[esp+0x1c],ecx
   *  01312de0   . e8 1b8dffff    call 蒼の彼方.0130bb00
   *  01312de5   . 47             inc edi
   *  01312de6   > 897c24 30      mov dword ptr ss:[esp+0x30],edi
   *  01312dea   > 8d8424 0802000>lea eax,dword ptr ss:[esp+0x208]         ;  default case of switch 01312d95
   *  01312df1   . e8 ba1b0000    call 蒼の彼方.013149b0
   *  01312df6   . 837d 10 00     cmp dword ptr ss:[ebp+0x10],0x0
   *  01312dfa   . 8bb424 2802000>mov esi,dword ptr ss:[esp+0x228]
   *  01312e01   . 894424 5c      mov dword ptr ss:[esp+0x5c],eax
   *  01312e05   . 74 12          je short 蒼の彼方.01312e19
   *  01312e07   . 56             push esi                                 ; /arg1
   *  01312e08   . e8 c31b0000    call 蒼の彼方.013149d0                       ; \蒼の彼方.013149d0
   *  01312e0d   . 83c4 04        add esp,0x4
   *  01312e10   . 898424 c000000>mov dword ptr ss:[esp+0xc0],eax
   *  01312e17   . eb 0b          jmp short 蒼の彼方.01312e24
   *  01312e19   > c78424 c000000>mov dword ptr ss:[esp+0xc0],0x0
   *  01312e24   > 8b4b 04        mov ecx,dword ptr ds:[ebx+0x4]
   *  01312e27   . 0fafce         imul ecx,esi
   *  01312e2a   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e2f   . f7e9           imul ecx
   *  01312e31   . c1fa 05        sar edx,0x5
   *  01312e34   . 8bca           mov ecx,edx
   *  01312e36   . c1e9 1f        shr ecx,0x1f
   *  01312e39   . 03ca           add ecx,edx
   *  01312e3b   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e3f   . 85c9           test ecx,ecx
   *  01312e41   . 7f 09          jg short 蒼の彼方.01312e4c
   *  01312e43   . b9 01000000    mov ecx,0x1
   *  01312e48   . 894c24 70      mov dword ptr ss:[esp+0x70],ecx
   *  01312e4c   > 8b53 08        mov edx,dword ptr ds:[ebx+0x8]
   *  01312e4f   . 0fafd6         imul edx,esi
   *  01312e52   . b8 1f85eb51    mov eax,0x51eb851f
   *  01312e57   . f7ea           imul edx
   *  01312e59   . c1fa 05        sar edx,0x5
   *  01312e5c   . 8bc2           mov eax,edx
   *  01312e5e   . c1e8 1f        shr eax,0x1f
   *  01312e61   . 03c2           add eax,edx
   *  01312e63   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e67   . 85c0           test eax,eax
   *  01312e69   . 7f 09          jg short 蒼の彼方.01312e74
   *  01312e6b   . b8 01000000    mov eax,0x1
   *  01312e70   . 894424 78      mov dword ptr ss:[esp+0x78],eax
   *  01312e74   > 33d2           xor edx,edx
   *  01312e76   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e7a   . 895424 6c      mov dword ptr ss:[esp+0x6c],edx
   *  01312e7e   . 8b13           mov edx,dword ptr ds:[ebx]
   *  01312e80   . 4a             dec edx                                  ;  switch (cases 1..2)
   *  01312e81   . 74 0e          je short 蒼の彼方.01312e91
   *  01312e83   . 4a             dec edx
   *  01312e84   . 75 13          jnz short 蒼の彼方.01312e99
   *  01312e86   . 8d1409         lea edx,dword ptr ds:[ecx+ecx]           ;  case 2 of switch 01312e80
   *  01312e89   . 895424 64      mov dword ptr ss:[esp+0x64],edx
   *  01312e8d   . 03c0           add eax,eax
   *  01312e8f   . eb 04          jmp short 蒼の彼方.01312e95
   *  01312e91   > 894c24 64      mov dword ptr ss:[esp+0x64],ecx          ;  case 1 of switch 01312e80
   *  01312e95   > 894424 6c      mov dword ptr ss:[esp+0x6c],eax
   *  01312e99   > 8b9c24 3802000>mov ebx,dword ptr ss:[esp+0x238]         ;  default case of switch 01312e80
   *  01312ea0   . 8bc3           mov eax,ebx
   *  01312ea2   . e8 d98bffff    call 蒼の彼方.0130ba80
   *  01312ea7   . 8bc8           mov ecx,eax
   *  01312ea9   . 8bc3           mov eax,ebx
   *  01312eab   . e8 e08bffff    call 蒼の彼方.0130ba90
   *  01312eb0   . 6a 01          push 0x1                                 ; /arg1 = 00000001
   *  01312eb2   . 8bd0           mov edx,eax                              ; |
   *  01312eb4   . 8db424 1c01000>lea esi,dword ptr ss:[esp+0x11c]         ; |
   *  01312ebb   . e8 3056fdff    call 蒼の彼方.012e84f0                       ; \蒼の彼方.012e84f0
   *  01312ec0   . 8bc7           mov eax,edi
   *  01312ec2   . 83c4 04        add esp,0x4
   *  01312ec5   . 8d70 01        lea esi,dword ptr ds:[eax+0x1]
   *  01312ec8   > 8a08           mov cl,byte ptr ds:[eax]
   *  01312eca   . 40             inc eax
   *  01312ecb   . 84c9           test cl,cl
   *  01312ecd   .^75 f9          jnz short 蒼の彼方.01312ec8
   *  01312ecf   . 2bc6           sub eax,esi
   *  01312ed1   . 40             inc eax
   *  01312ed2   . 50             push eax
   *  01312ed3   . e8 e74c0600    call 蒼の彼方.01377bbf
   *  01312ed8   . 33f6           xor esi,esi
   *  01312eda   . 83c4 04        add esp,0x4
   */
  ULONG search3(ULONG startAddress, ULONG stopAddress)
  {
    // return startAddress + 0x31850; // 世界と世界の真ん中 体験版
    const uint8_t bytes[] = {
        // 3c207d580fbec083c0fe83f806774d
        0x3c, 0x20,       // 01312d8e   3c 20          cmp al,0x20     ; jichi: pattern starts
        0x7d, 0x58,       // 01312d90   7d 58          jge short 蒼の彼方.01312dea
        0x0f, 0xbe, 0xc0, // 01312d92   0fbec0         movsx eax,al
        0x83, 0xc0, 0xfe, // 01312d95   83c0 fe        add eax,-0x2                             ;  switch (cases 2..8)
        0x83, 0xf8, 0x06, // 01312d98   83f8 06        cmp eax,0x6
        0x77, 0x4d        // 01312d9b   77 4d          ja short 蒼の彼方.01312dea
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
    if (!addr)
      return 0;

    // distance to the beginning of the function
    static const int hook_offsets[] = {
        0x01312cd0 - 0x01312d8e // for new BGI2 game since 蒼の彼方 (2014/08), text is in arg2
        ,
        0x00a64260 - 0x00a64318 // For newer BGI2 game since コドモノアソビ (2015/11)
    };

    for (size_t i = 0; i < ARRAYSIZE(hook_offsets); i++)
    {
      int hook_offset = hook_offsets[i];

      enum : uint8_t
      {
        push_ebp = 0x55
      }; // 011d4c80  /$ 55             push ebp
      if (*(uint8_t *)(addr + hook_offset) == push_ebp)
        return addr + hook_offset;
    }
    return 0; // failed
  }
  bool search_tayutama(DWORD *funaddr, DWORD *addr)
  {
    const BYTE bytes[] = {
        // The following code does not exist in newer BGI games after BGI 1.633.0.0 (tayutama2_trial_EX)
        // 0x3c, 0x20,      // 011d4d31  |. 3c 20          cmp al,0x20
        // 0x7d, XX,        // 011d4d33  |. 7d 75          jge short sekachu.011d4daa ; jichi: 0x75 or 0x58
        0x0f, 0xbe, 0xc0, // 011d4d35  |. 0fbec0         movsx eax,al
        0x83, 0xc0, 0xfe, // 011d4d38  |. 83c0 fe        add eax,-0x2               ;  switch (cases 2..8)
        0x83, 0xf8        //, 0x06  // 011d4d3b  |. 83f8 06        cmp eax,0x6
                          // The following code does not exist in newer BGI games after 蒼の彼方
                          // 0x77, 0x6a     // 011d4d3e  |. 77 6a          ja short sekachu.011d4daa
    };

    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    *addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    // GROWL_DWORD(reladdr);
    if (!*addr)
    {
      return false;
    }

    *funaddr = MemDbg::findEnclosingAlignedFunction(*addr, 0x300); // range is around 177 ~ 190

    enum : BYTE
    {
      push_ebp = 0x55
    }; // 011d4c80  /$ 55             push ebp
    if (!*funaddr || *(BYTE *)*funaddr != push_ebp)
    {
      return false;
    }
    return true;
  }
  bool InsertBGI2Hook()
  {

    /* Artikash 6/14/2019: Ugh, what a mess I've dug up...
    At some point the beginning four bytes to search for were removed, but the difference below were not corrected? Or maybe they were?
    I don't have all these games so no way to confirm which (if any) are wrong.
    But the first difference (the important one since it's the one detecting offset=arg3, all others give new) seems to be four bytes off when hooking https://vndb.org/v8158
    ...but maybe it's not? Maybe I discovered a new difference?
    I think the safest option is to just add the new? difference as a case that detects offset=arg3 since either way one case will detect offset=arg3 correctly.
    And all the other cases fall through to offset=arg2.
    */
    ULONG addr, funaddr;
    HookParam hp;
    hp.embed_hook_font = F_TextOutA | F_TextOutW;
    if (search_tayutama(&funaddr, &addr))
    {

      switch (funaddr - addr)
      {
      // for old BGI2 game, text is arg3
      case 0x34c80 - 0x34d31: // old offset
      case 0x34c50 - 0x34d05: // correction as mentioned above
        Private::textIndex_ = 3;
        break;
      // for new BGI2 game since 蒼の彼方 (2014/08), text is in arg2
      case 0x01312cd0 - 0x01312D92:
      // For newer BGI2 game since コドモノアソビ (2015/11)
      case 0x00A64260 - 0x00A6431C:
      // For latest BGI2 game since タユタマ２(2016/05) by @mireado
      case 0x00E95290 - 0x00E95349:
      // For latest BGI2 game since 千の刃濤、桃花染の皇姫 体験版  by @mireado
      case 0x00AF5640 - 0x00AF56FF:
      // For latest BGI2 game since by BGI 1.633.0.0 @mireado
      case 0x00D8A660 - 0x00D8A73A:
        Private::textIndex_ = 2;
        break;
      // Artikash 8/1/2018: Looks like it's basically always 4*2. Remove error from default case: breaks SubaHibi HD. Will figure out how to do this properly if it becomes an issue.
      default:
        ConsoleOutput("BGI2 WARN: function-code distance unknown");
        Private::textIndex_ = 2;
        break;
      }
      Private::type_ = Private::Type3;
      addr = funaddr;
    }
    else if (addr = search3(processStartAddress, processStopAddress))
    {
      Private::type_ = Private::Type3;
      Private::textIndex_ = 2; // use arg2, name = "BGI2";
    }
    else if (addr = search2(processStartAddress, processStopAddress))
    {
      Private::type_ = Private::Type2;
      Private::textIndex_ = 3; // use arg3, name = "BGI2";
    }
    else if (addr = search1(processStartAddress, processStopAddress))
    {
      Private::type_ = Private::Type1;
      Private::textIndex_ = 3; // use arg3, name = "BGI";
    }
    if (!addr)
      return false;
    hp.address = addr;
    hp.offset = stackoffset(Private::textIndex_);
    // jichi 5/12/2014: Using split could distinguish name and choices. But the signature might become unstable
    hp.type = USING_STRING | USING_SPLIT | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;

    hp.text_fun = Private::hookBefore;
    hp.embed_fun = [](hook_context *context, TextBuffer buffer)
    {
      std::string sorigin = (char *)context->stack[Private::textIndex_];
      std::string s = buffer.strA();
      if (endWith(sorigin, "\n"))
      {
        s += '\n';
      }
      if (startWith(sorigin, "\x04"))
      {
        s = '\x04' + s;
      }
      context->stack[Private::textIndex_] = (DWORD)allocateString(s);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // It could be either <R..> or <r..>
      std::string result = buffer->strA();
      result = re::sub(result, "<r.+?>(.+?)</r>", "$1", std::regex_constants::icase);
      if (endWith(result, "\n"))
      {
        result = result.substr(0, result.size() - 1);
      }
      if (startWith(result, "\x04"))
      {
        result = result.substr(1);
      }
      buffer->from(result);
    };

    hp.split = stackoffset(8); // pseudo arg8

    // GROWL_DWORD2(hp.address, processStartAddress);

    return NewHook(hp, "EmbedBGI");
  }

} // unnamed

// jichi 5/12/2014: BGI1 and BGI2 game can co-exist, such as 世界と世界の真ん中で
// BGI1 can exist in both old and new games
// BGI2 only exist in new games
// Insert BGI2 first.
// Artikash 6/12/2019: In newer games neither exists, but WideCharToMultiByte works, so insert that if BGI2 fails.

void BGI7Filter(TextBuffer *buffer, HookParam *)
{
  CharFilter(buffer, L'\x0001');
  CharFilter(buffer, L'\x0002');
  CharFilter(buffer, L'\x0003');
  CharFilter(buffer, L'\x0004');
  CharFilter(buffer, L'\x0005');
  CharFilter(buffer, L'\x000A');
  CharFilter(buffer, L'▼');
  StringFilterBetween(buffer, TEXTANDLEN(L"<"), TEXTANDLEN(L">"));
}

void BGI56Filter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);

  if (text[0] == '@')
  {
    buffer->size -= 1;
    ::memmove(text, text + 1, buffer->size);
  }
}

bool InsertBGI4Hook_1()
{
  /*
    int __cdecl sub_4A3AD0(LPSTR lpMultiByteStr, LPCWCH lpWideCharStr, int a3)
{
  int v3; // edi
  UINT v4; // esi
  int v5; // ebx
  CHAR *v6; // ecx

  v3 = 0;
  v4 = sub_4A37B0();
  if ( a3 )
  {
    if ( a3 == 1 )
      v4 = 65001;
  }
  else
  {
    v4 = 932;
  }
  v5 = WideCharToMultiByte(v4, 0, lpWideCharStr, -1, 0, 0, 0, 0);
  if ( v5 >= 1 )
  {
    v6 = lpMultiByteStr;
    if ( !lpMultiByteStr )
    {
      v3 = unknown_libname_1(v5 + 1);
      v6 = (CHAR *)v3;
    }
    WideCharToMultiByte(v4, 0, lpWideCharStr, -1, v6, v5, 0, 0);
  }
  return v3;
}*/
  const BYTE bytes[] = {
      0xBE, 0xE9, 0xFD, 0x00, 0x00, // cp=65001
      0xeb, XX,
      0xBE, 0xA4, 0x03, 0x00, 0x00 // cp=932
  };
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = CODEC_UTF16 | USING_STRING;
  hp.filter_fun = BGI7Filter;
  hp.offset = GETARG(2);
  ConsoleOutput("BGI4");

  return NewHook(hp, "BGI4");
}

bool InsertBGI4Hook_2()
{
  /*
    if ( *(unsigned __int8 *)v1 == 239 )
    {
      v12 = *((unsigned __int8 *)v1 + 1) | 0xEF00;
      goto LABEL_16;
    }
    if ( *(unsigned __int8 *)v1 == 255 )
    {
      v12 = *((unsigned __int8 *)v1 + 1) | 0xF000;
.text:004863E0                 movzx   eax, byte ptr [ecx]
.text:004863E3                 or      eax, 0F000h
.text:004863E8                 jmp     short loc_4863F2
.text:004863EA ; ---------------------------------------------------------------------------
.text:004863EA
.text:004863EA loc_4863EA:                             ; CODE XREF: sub_486310+BB↑j
.text:004863EA                 movzx   eax, byte ptr [ecx]
.text:004863ED                 or      eax, 0EF00h*/
  const BYTE bytes[] = {
      0x0F, 0xB6, 0x01,
      0x0D, 0x00, 0xF0, 0x00, 0x00,
      0xeb, XX,
      0x0F, 0xB6, 0x01,
      0x0D, 0x00, 0xEF, 0x00, 0x00};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  auto addrs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
  if (1 != addrs.size())
    return false;
  HookParam hp;
  hp.address = addrs[0] + 5;
  hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW;
  hp.embed_hook_font = F_TextOutW | F_GetTextExtentPoint32W;
  hp.filter_fun = BGI7Filter;
  hp.offset = regoffset(eax);
  return NewHook(hp, "BGI");
}
bool InsertBGI4Hook()
{
  return InsertBGI4Hook_2() || InsertBGI4Hook_1();
}
namespace
{
  bool veryold()
  {
    // 紅月－くれないつき－
    // あの街の恋の詩
    // H2O -FOOTPRINTS IN THE SAND-

    auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
    if (!addr) // 銀行淫～堕ちゆく女達～ //mov     ebp, ds:GetGlyphOutlineA
      addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, false, XX);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    auto xrefs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
    if (xrefs.size() != 1)
      return false;
    auto xrefaddr = xrefs[0];
    auto funcstart = MemDbg::findEnclosingAlignedFunction(xrefaddr);
    if (funcstart == 0)
      return false;
    BYTE sig[] = {0x81, XX, 0x00, 0x01, 0x00, 0x00}; // cmp     ebx, 100h
    if (MemDbg::findBytes(sig, sizeof(sig), xrefaddr - 0x40, xrefaddr) == 0)
      return false;
    HookParam hp;
    hp.address = funcstart;
    hp.offset = stackoffset(2);
    hp.split = stackoffset(1);
    hp.type = CODEC_ANSI_BE | USING_SPLIT;

    return NewHook(hp, "BGI5");
  }
}
bool BGI::attach_function()
{
  if (InsertBGI4Hook())
    return true;
  return InsertBGI2Hook() || (PcHooks::hookOtherPcFunctions(), InsertBGI1Hook()) || veryold();
}