#include "BunBun.h"

bool BunBun::attach_function()
{
  // 保健室～マジカルピュアレッスン♪～
  // https://vndb.org/v351
  /*
  .text:00406AA0 ; int __cdecl sub_406AA0(__int16)
  .text:00406AA0 sub_406AA0      proc near               ; CODE XREF: sub_406B30+23↓p
  .text:00406AA0
  .text:00406AA0 arg_0           = dword ptr  4
  .text:00406AA0
  .text:00406AA0                 mov     ecx, [esp+arg_0]
  .text:00406AA4                 xor     eax, eax
  .text:00406AA6                 mov     al, ch
  .text:00406AA8                 and     ecx, 0FFh
  .text:00406AAE                 cmp     eax, 81h
  .text:00406AB3                 jb      short loc_406AC3
  .text:00406AB5                 cmp     eax, 9Fh
  .text:00406ABA                 ja      short loc_406AC3
  .text:00406ABC                 sub     eax, 81h
  .text:00406AC1                 jmp     short loc_406AD6
  .text:00406AC3 ; ---------------------------------------------------------------------------
  .text:00406AC3
  .text:00406AC3 loc_406AC3:                             ; CODE XREF: sub_406AA0+13↑j
  .text:00406AC3                                         ; sub_406AA0+1A↑j
  .text:00406AC3                 cmp     eax, 0E0h
  .text:00406AC8                 jb      short loc_406AD6
  .text:00406ACA                 cmp     eax, 0EFh
  .text:00406ACF                 ja      short loc_406AD6
  .text:00406AD1                 sub     eax, 0C1h
  .text:00406AD6
  .text:00406AD6 loc_406AD6:                             ; CODE XREF: sub_406AA0+21↑j
  .text:00406AD6                                         ; sub_406AA0+28↑j ...
  .text:00406AD6                 shl     eax, 1
  .text:00406AD8                 cmp     ecx, 40h ; '@'
  .text:00406ADB                 jb      short loc_406AF0
  .text:00406ADD                 cmp     ecx, 7Eh ; '~'
  .text:00406AE0                 ja      short loc_406AF0
  .text:00406AE2                 sub     ecx, 40h ; '@'
  .text:00406AE5                 shl     eax, 8
  .text:00406AE8                 lea     eax, [eax+ecx+2121h]
  .text:00406AEF                 retn
  .text:00406AF0 ; ---------------------------------------------------------------------------
  .text:00406AF0
  .text:00406AF0 loc_406AF0:                             ; CODE XREF: sub_406AA0+3B↑j
  .text:00406AF0                                         ; sub_406AA0+40↑j
  .text:00406AF0                 cmp     ecx, 80h ; '€'
  .text:00406AF6                 jb      short loc_406B0E
  .text:00406AF8                 cmp     ecx, 9Eh
  .text:00406AFE                 ja      short loc_406B0E
  .text:00406B00                 sub     ecx, 41h ; 'A'
  .text:00406B03                 shl     eax, 8
  .text:00406B06                 lea     eax, [eax+ecx+2121h]
  .text:00406B0D                 retn
  .text:00406B0E ; ---------------------------------------------------------------------------
  .text:00406B0E
  .text:00406B0E loc_406B0E:                             ; CODE XREF: sub_406AA0+56↑j
  .text:00406B0E                                         ; sub_406AA0+5E↑j
  .text:00406B0E                 cmp     ecx, 9Fh
  .text:00406B14                 jb      short loc_406B25
  .text:00406B16                 cmp     ecx, 0FCh
  .text:00406B1C                 ja      short loc_406B25
  .text:00406B1E                 sub     ecx, 9Fh
  .text:00406B24                 inc     eax
  .text:00406B25
  .text:00406B25 loc_406B25:                             ; CODE XREF: sub_406AA0+74↑j
  .text:00406B25                                         ; sub_406AA0+7C↑j
  .text:00406B25                 shl     eax, 8
  .text:00406B28                 lea     eax, [eax+ecx+2121h]
  .text:00406B2F                 retn
  .text:00406B2F sub_406AA0      endp

  int __cdecl sub_406AA0(__int16 a1)
  {
    int v1; // eax
    int v2; // ecx
    int v3; // eax

    v1 = HIBYTE(a1);
    v2 = (unsigned __int8)a1;
    if ( HIBYTE(a1) < 0x81u || HIBYTE(a1) > 0x9Fu )
    {
      if ( HIBYTE(a1) >= 0xE0u && HIBYTE(a1) <= 0xEFu )
        v1 = HIBYTE(a1) - 193;
    }
    else
    {
      v1 = HIBYTE(a1) - 129;
    }
    v3 = 2 * v1;
    if ( (unsigned __int8)a1 >= 0x40u && (unsigned __int8)a1 <= 0x7Eu )
      return (v3 << 8) + (unsigned __int8)a1 - 64 + 8481;
    if ( (unsigned __int8)a1 >= 0x80u && (unsigned __int8)a1 <= 0x9Eu )
      return (v3 << 8) + (unsigned __int8)a1 - 65 + 8481;
    if ( (unsigned __int8)a1 >= 0x9Fu && (unsigned __int8)a1 <= 0xFCu )
    {
      v2 = (unsigned __int8)a1 - 159;
      ++v3;
    }
    return (v3 << 8) + v2 + 8481;
  }
  */
  const BYTE bytes[] = {
      0x8b, 0x4c, 0x24, 0x04,
      0x33, 0xc0,
      0x8a, 0xc5,
      0x81, 0xe1, 0xff, 0x00, 0x00, 0x00,
      0x3d, 0x81, 0x00, 0x00, 0x00,
      0x72, XX,
      0x3d, 0x9f, 0x00, 0x00, 0x00,
      0x77, XX,
      0x2d, 0x81, 0x00, 0x00, 0x00,
      0xeb, XX,
      0x3d, 0xe0, 0x00, 0x00, 0x00,
      0x72, XX,
      0x3d, 0xef, 0x00, 0x00, 0x00,
      0x77, XX,
      0x2d, 0xc1, 0x00, 0x00, 0x00

  };
  // enum { addr_offset = 0 };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR | CODEC_ANSI_BE;
  return NewHook(hp, "BunBun");
}