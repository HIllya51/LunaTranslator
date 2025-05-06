#include "AksysGames.h"

bool AksysGames::attach_function()
{

  const BYTE bytes[] = {
      /*
      v8 = *v2;
        if ( *v2 == (char)0x80 )
        {
          ++v2;
          ++v5;
          goto LABEL_26;
        }
        v9 = 0;
        v17 = v7;
        v15 = v2;
        v10 = v6;
        if ( (unsigned __int8)v8 >= 0x81u && (unsigned __int8)v8 <= 0x9Fu
          || (unsigned __int8)v8 >= 0xE0u && (unsigned __int8)v8 <= 0xFCu )
        {
      */
      /*
      .text:004BCB70                 mov     cl, [eax]
   .text:004BCB72                 cmp     cl, 80h ; '€'
   .text:004BCB75                 jz      loc_4BCC76
   .text:004BCB7B                 xor     esi, esi
   .text:004BCB7D                 mov     [ebp+var_20C], edi
   .text:004BCB83                 mov     [ebp+var_214], eax
   .text:004BCB89                 mov     ebx, edx
   .text:004BCB8B                 test    edi, edi
   .text:004BCB8D                 jz      short loc_4BCBE3
   .text:004BCB8F                 cmp     cl, 81h
   .text:004BCB92                 jb      short loc_4BCB99
   .text:004BCB94                 cmp     cl, 9Fh
   .text:004BCB97                 jbe     short loc_4BCBA3
   .text:004BCB99
   .text:004BCB99 loc_4BCB99:                             ; CODE XREF: sub_4BCB20+72↑j
   .text:004BCB99                 cmp     cl, 0E0h
   .text:004BCB9C                 jb      short loc_4BCBC3
   .text:004BCB9E                 cmp     cl, 0FCh
   .text:004BCBA1                 ja      short loc_4BCBC3
      */
      0x8a, 0x08,
      0x80, 0xf9, 0x80,
      0x0f, 0x84, XX4,
      0x33, 0xf6,
      0x89, XX, XX4,
      0x89, XX, XX4,
      0x8b, 0xda,
      0x85, 0xff,
      0x74, XX,
      0x80, 0xf9, 0x81,
      0x72, XX,
      0x80, 0xf9, 0x9f,
      0x76, XX,
      0x80, 0xf9, 0xe0,
      0x72, XX,
      0x80, 0xf9, 0xfc,
      0x77, XX};

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x100, true);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  return NewHook(hp, "AksysGames");
}