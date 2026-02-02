#include "Milk.h"
/*
int __cdecl sub_40C750(char *a1, _DWORD *a2)
{
  unsigned __int16 v2; // dx
  int v3; // edi
  int result; // eax
  int v5; // eax

  HIBYTE(v2) = *a1;
  LOBYTE(v2) = a1[1];
  v3 = *a1;
  *a2 = 24 * (v2 & 0xF);
  if ( v2 < 0x8140u || v2 > 0x84FFu )
  {
    if ( v2 < 0x8740u || v2 > 0x879Fu )
    {
      if ( v2 < 0x8890u || v2 > 0x88FFu )
      {
        if ( v2 < 0x8940u || v2 > 0x9FFFu )
        {
          if ( v2 < 0xE040u || v2 > 0xEAA4u )
          {
            if ( v2 < 0xFA40u || v2 > 0xFAFCu )
            {
              if ( v2 < 0xFB40u || v2 > 0xFBFCu )
              {
                if ( v2 < 0xFC40u || v2 > 0xFC4Bu )
                {
                  if ( dword_41CABC <= 1 )
                    v5 = *((_WORD *)off_41C8B0 + v3) & 0x157;
                  else
                    v5 = _isctype(v3, 343);
                  if ( !v5 )
                  {
                    MessageBoxA(dwCallback, asc_41C6C0, 0, 0);
                    sub_402D30();
                    exit(1);
                  }
                  result = 1;
                  *a2 = 24 * (*a1 & 0xF);
                  a2[1] = 24 * (((v3 & 0xF0) - 32) >> 4);
                }
                else
                {
                  result = 2;
                  a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (((v2 & 0xFF00) - 64512) >> 8) + 520);
                }
              }
              else
              {
                result = 2;
                a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (((v2 & 0xFF00) - 64256) >> 8) + 508);
              }
            }
            else
            {
              result = 2;
              a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (((v2 & 0xFF00) - 64000) >> 8) + 496);
            }
          }
          else
          {
            result = 2;
            a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (((v2 & 0xFF00) - 57344) >> 8) + 345);
          }
        }
        else
        {
          result = 2;
          a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (((v2 & 0xFF00) - 35072) >> 8) + 69);
        }
      }
      else
      {
        result = 2;
        a2[1] = 24 * ((((v2 & 0xF0) - 144) >> 4) + 62);
      }
    }
    else
    {
      result = 2;
      a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 56);
    }
  }
  else
  {
    a2[1] = 24 * ((((v2 & 0xF0) - 64) >> 4) + 12 * (HIBYTE(v2) & 0xF));
    return 2;
  }
  return result;
}
*/
/*
text:0040C750 55                                            push    ebp
.text:0040C751 8B 6C 24 08                                   mov     ebp, [esp+4+arg_0]
.text:0040C755 33 D2                                         xor     edx, edx
.text:0040C757 56                                            push    esi
.text:0040C758 8A 45 00                                      mov     al, [ebp+0]
.text:0040C75B 8A 4D 01                                      mov     cl, [ebp+1]
.text:0040C75E 8B 74 24 10                                   mov     esi, [esp+8+arg_4]
.text:0040C762 8A F0                                         mov     dh, al
.text:0040C764 8A D1                                         mov     dl, cl
.text:0040C766 83 E1 0F                                      and     ecx, 0Fh
.text:0040C769 57                                            push    edi
.text:0040C76A 0F BE F8                                      movsx   edi, al
.text:0040C76D 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C770 8B C2                                         mov     eax, edx
.text:0040C772 C1 E1 03                                      shl     ecx, 3
.text:0040C775 66 3D 40 81                                   cmp     ax, 8140h
.text:0040C779 89 0E                                         mov     [esi], ecx
.text:0040C77B 72 36                                         jb      short loc_40C7B3
.text:0040C77D 66 3D FF 84                                   cmp     ax, 84FFh
.text:0040C781 77 30                                         ja      short loc_40C7B3
.text:0040C783 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C788 5F                                            pop     edi
.text:0040C789 8B C8                                         mov     ecx, eax
.text:0040C78B 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C790 C1 E9 08                                      shr     ecx, 8
.text:0040C793 83 E1 0F                                      and     ecx, 0Fh
.text:0040C796 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C799 C1 F8 04                                      sar     eax, 4
.text:0040C79C 8D 14 49                                      lea     edx, [ecx+ecx*2]
.text:0040C79F 8D 04 90                                      lea     eax, [eax+edx*4]
.text:0040C7A2 8D 04 40                                      lea     eax, [eax+eax*2]
.text:0040C7A5 C1 E0 03                                      shl     eax, 3
.text:0040C7A8 89 46 04                                      mov     [esi+4], eax
.text:0040C7AB 5E                                            pop     esi
.text:0040C7AC B8 02 00 00 00                                mov     eax, 2
.text:0040C7B1 5D                                            pop     ebp
.text:0040C7B2 C3                                            retn
.text:0040C7B3                               ; ---------------------------------------------------------------------------
.text:0040C7B3
.text:0040C7B3                               loc_40C7B3:                             ; CODE XREF: sub_40C750+2B↑j
.text:0040C7B3                                                                       ; sub_40C750+31↑j
.text:0040C7B3 66 3D 40 87                                   cmp     ax, 8740h
.text:0040C7B7 72 26                                         jb      short loc_40C7DF
.text:0040C7B9 66 3D 9F 87                                   cmp     ax, 879Fh
.text:0040C7BD 77 20                                         ja      short loc_40C7DF
.text:0040C7BF 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C7C4 5F                                            pop     edi
.text:0040C7C5 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C7C8 C1 F8 04                                      sar     eax, 4
.text:0040C7CB 83 C0 38                                      add     eax, 38h ; '8'
.text:0040C7CE 8D 0C 40                                      lea     ecx, [eax+eax*2]
.text:0040C7D1 B8 02 00 00 00                                mov     eax, 2
.text:0040C7D6 C1 E1 03                                      shl     ecx, 3
.text:0040C7D9 89 4E 04                                      mov     [esi+4], ecx
.text:0040C7DC 5E                                            pop     esi
.text:0040C7DD 5D                                            pop     ebp
.text:0040C7DE C3                                            retn
.text:0040C7DF                               ; ---------------------------------------------------------------------------
.text:0040C7DF
.text:0040C7DF                               loc_40C7DF:                             ; CODE XREF: sub_40C750+67↑j
.text:0040C7DF                                                                       ; sub_40C750+6D↑j
.text:0040C7DF 66 3D 90 88                                   cmp     ax, 8890h
.text:0040C7E3 72 28                                         jb      short loc_40C80D
.text:0040C7E5 66 3D FF 88                                   cmp     ax, 88FFh
.text:0040C7E9 77 22                                         ja      short loc_40C80D
.text:0040C7EB 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C7F0 5F                                            pop     edi
.text:0040C7F1 2D 90 00 00 00                                sub     eax, 90h
.text:0040C7F6 C1 F8 04                                      sar     eax, 4
.text:0040C7F9 83 C0 3E                                      add     eax, 3Eh ; '>'
.text:0040C7FC 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C7FF B8 02 00 00 00                                mov     eax, 2
.text:0040C804 C1 E2 03                                      shl     edx, 3
.text:0040C807 89 56 04                                      mov     [esi+4], edx
.text:0040C80A 5E                                            pop     esi
.text:0040C80B 5D                                            pop     ebp
.text:0040C80C C3                                            retn
.text:0040C80D                               ; ---------------------------------------------------------------------------
.text:0040C80D
.text:0040C80D                               loc_40C80D:                             ; CODE XREF: sub_40C750+93↑j
.text:0040C80D                                                                       ; sub_40C750+99↑j
.text:0040C80D 66 3D 40 89                                   cmp     ax, 8940h
.text:0040C811 72 40                                         jb      short loc_40C853
.text:0040C813 66 3D FF 9F                                   cmp     ax, 9FFFh
.text:0040C817 77 3A                                         ja      short loc_40C853
.text:0040C819 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C81E 5F                                            pop     edi
.text:0040C81F 8B C8                                         mov     ecx, eax
.text:0040C821 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C826 81 E1 00 FF 00 00                             and     ecx, 0FF00h
.text:0040C82C 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C82F 81 E9 00 89 00 00                             sub     ecx, 8900h
.text:0040C835 C1 F9 08                                      sar     ecx, 8
.text:0040C838 C1 F8 04                                      sar     eax, 4
.text:0040C83B 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C83E 8D 44 88 45                                   lea     eax, [eax+ecx*4+45h]
.text:0040C842 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C845 B8 02 00 00 00                                mov     eax, 2
.text:0040C84A C1 E2 03                                      shl     edx, 3
.text:0040C84D 89 56 04                                      mov     [esi+4], edx
.text:0040C850 5E                                            pop     esi
.text:0040C851 5D                                            pop     ebp
.text:0040C852 C3                                            retn
.text:0040C853                               ; ---------------------------------------------------------------------------
.text:0040C853
.text:0040C853                               loc_40C853:                             ; CODE XREF: sub_40C750+C1↑j
.text:0040C853                                                                       ; sub_40C750+C7↑j
.text:0040C853 66 3D 40 E0                                   cmp     ax, 0E040h
.text:0040C857 72 43                                         jb      short loc_40C89C
.text:0040C859 66 3D A4 EA                                   cmp     ax, 0EAA4h
.text:0040C85D 77 3D                                         ja      short loc_40C89C
.text:0040C85F 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C864 5F                                            pop     edi
.text:0040C865 8B C8                                         mov     ecx, eax
.text:0040C867 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C86C 81 E1 00 FF 00 00                             and     ecx, 0FF00h
.text:0040C872 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C875 81 E9 00 E0 00 00                             sub     ecx, 0E000h
.text:0040C87B C1 F9 08                                      sar     ecx, 8
.text:0040C87E C1 F8 04                                      sar     eax, 4
.text:0040C881 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C884 8D 84 88 59 01 00 00                          lea     eax, [eax+ecx*4+159h]
.text:0040C88B 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C88E B8 02 00 00 00                                mov     eax, 2
.text:0040C893 C1 E2 03                                      shl     edx, 3
.text:0040C896 89 56 04                                      mov     [esi+4], edx
.text:0040C899 5E                                            pop     esi
.text:0040C89A 5D                                            pop     ebp
.text:0040C89B C3                                            retn
.text:0040C89C                               ; ---------------------------------------------------------------------------
.text:0040C89C
.text:0040C89C                               loc_40C89C:                             ; CODE XREF: sub_40C750+107↑j
.text:0040C89C                                                                       ; sub_40C750+10D↑j
.text:0040C89C 66 3D 40 FA                                   cmp     ax, 0FA40h
.text:0040C8A0 72 43                                         jb      short loc_40C8E5
.text:0040C8A2 66 3D FC FA                                   cmp     ax, 0FAFCh
.text:0040C8A6 77 3D                                         ja      short loc_40C8E5
.text:0040C8A8 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C8AD 5F                                            pop     edi
.text:0040C8AE 8B C8                                         mov     ecx, eax
.text:0040C8B0 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C8B5 81 E1 00 FF 00 00                             and     ecx, 0FF00h
.text:0040C8BB 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C8BE 81 E9 00 FA 00 00                             sub     ecx, 0FA00h
.text:0040C8C4 C1 F9 08                                      sar     ecx, 8
.text:0040C8C7 C1 F8 04                                      sar     eax, 4
.text:0040C8CA 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C8CD 8D 84 88 F0 01 00 00                          lea     eax, [eax+ecx*4+1F0h]
.text:0040C8D4 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C8D7 B8 02 00 00 00                                mov     eax, 2
.text:0040C8DC C1 E2 03                                      shl     edx, 3
.text:0040C8DF 89 56 04                                      mov     [esi+4], edx
.text:0040C8E2 5E                                            pop     esi
.text:0040C8E3 5D                                            pop     ebp
.text:0040C8E4 C3                                            retn
.text:0040C8E5                               ; ---------------------------------------------------------------------------
.text:0040C8E5
.text:0040C8E5                               loc_40C8E5:                             ; CODE XREF: sub_40C750+150↑j
.text:0040C8E5                                                                       ; sub_40C750+156↑j
.text:0040C8E5 66 3D 40 FB                                   cmp     ax, 0FB40h
.text:0040C8E9 72 43                                         jb      short loc_40C92E
.text:0040C8EB 66 3D FC FB                                   cmp     ax, 0FBFCh
.text:0040C8EF 77 3D                                         ja      short loc_40C92E
.text:0040C8F1 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C8F6 5F                                            pop     edi
.text:0040C8F7 8B C8                                         mov     ecx, eax
.text:0040C8F9 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C8FE 81 E1 00 FF 00 00                             and     ecx, 0FF00h
.text:0040C904 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C907 81 E9 00 FB 00 00                             sub     ecx, 0FB00h
.text:0040C90D C1 F9 08                                      sar     ecx, 8
.text:0040C910 C1 F8 04                                      sar     eax, 4
.text:0040C913 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C916 8D 84 88 FC 01 00 00                          lea     eax, [eax+ecx*4+1FCh]
.text:0040C91D 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C920 B8 02 00 00 00                                mov     eax, 2
.text:0040C925 C1 E2 03                                      shl     edx, 3
.text:0040C928 89 56 04                                      mov     [esi+4], edx
.text:0040C92B 5E                                            pop     esi
.text:0040C92C 5D                                            pop     ebp
.text:0040C92D C3                                            retn
.text:0040C92E                               ; ---------------------------------------------------------------------------
.text:0040C92E
.text:0040C92E                               loc_40C92E:                             ; CODE XREF: sub_40C750+199↑j
.text:0040C92E                                                                       ; sub_40C750+19F↑j
.text:0040C92E 66 3D 40 FC                                   cmp     ax, 0FC40h
.text:0040C932 72 43                                         jb      short loc_40C977
.text:0040C934 66 3D 4B FC                                   cmp     ax, 0FC4Bh
.text:0040C938 77 3D                                         ja      short loc_40C977
.text:0040C93A 25 FF FF 00 00                                and     eax, 0FFFFh
.text:0040C93F 5F                                            pop     edi
.text:0040C940 8B C8                                         mov     ecx, eax
.text:0040C942 25 F0 00 00 00                                and     eax, 0F0h
.text:0040C947 81 E1 00 FF 00 00                             and     ecx, 0FF00h
.text:0040C94D 83 E8 40                                      sub     eax, 40h ; '@'
.text:0040C950 81 E9 00 FC 00 00                             sub     ecx, 0FC00h
.text:0040C956 C1 F9 08                                      sar     ecx, 8
.text:0040C959 C1 F8 04                                      sar     eax, 4
.text:0040C95C 8D 0C 49                                      lea     ecx, [ecx+ecx*2]
.text:0040C95F 8D 84 88 08 02 00 00                          lea     eax, [eax+ecx*4+208h]
.text:0040C966 8D 14 40                                      lea     edx, [eax+eax*2]
.text:0040C969 B8 02 00 00 00                                mov     eax, 2
.text:0040C96E C1 E2 03                                      shl     edx, 3
.text:0040C971 89 56 04                                      mov     [esi+4], edx
.text:0040C974 5E                                            pop     esi
.text:0040C975 5D                                            pop     ebp
.text:0040C976 C3                                            retn
.text:0040C977                               ; ---------------------------------------------------------------------------
.text:0040C977
.text:0040C977                               loc_40C977:                             ; CODE XREF: sub_40C750+1E2↑j
.text:0040C977                                                                       ; sub_40C750+1E8↑j
.text:0040C977 83 3D BC CA 41 00 01                          cmp     dword_41CABC, 1
.text:0040C97E 7E 10                                         jle     short loc_40C990
.text:0040C980 68 57 01 00 00                                push    157h            ; Type
.text:0040C985 57                                            push    edi             ; C
.text:0040C986 E8 74 73 00 00                                call    __isctype
.text:0040C98B 83 C4 08                                      add     esp, 8
.text:0040C98E EB 0E                                         jmp     short loc_40C99E
.text:0040C990                               ; ---------------------------------------------------------------------------
.text:0040C990
.text:0040C990                               loc_40C990:                             ; CODE XREF: sub_40C750+22E↑j
.text:0040C990 A1 B0 C8 41 00                                mov     eax, off_41C8B0
.text:0040C995 66 8B 04 78                                   mov     ax, [eax+edi*2]
.text:0040C999 25 57 01 00 00                                and     eax, 157h
.text:0040C99E
.text:0040C99E                               loc_40C99E:                             ; CODE XREF: sub_40C750+23E↑j
.text:0040C99E 85 C0                                         test    eax, eax
.text:0040C9A0 74 2C                                         jz      short loc_40C9CE
.text:0040C9A2 8A 45 00                                      mov     al, [ebp+0]
.text:0040C9A5 81 E7 F0 00 00 00                             and     edi, 0F0h
.text:0040C9AB 83 EF 20                                      sub     edi, 20h ; ' '
.text:0040C9AE 83 E0 0F                                      and     eax, 0Fh
.text:0040C9B1 C1 FF 04                                      sar     edi, 4
.text:0040C9B4 8D 0C 40                                      lea     ecx, [eax+eax*2]
.text:0040C9B7 B8 01 00 00 00                                mov     eax, 1
.text:0040C9BC 8D 14 7F                                      lea     edx, [edi+edi*2]
.text:0040C9BF 5F                                            pop     edi
.text:0040C9C0 C1 E1 03                                      shl     ecx, 3
.text:0040C9C3 C1 E2 03                                      shl     edx, 3
.text:0040C9C6 89 0E                                         mov     [esi], ecx
.text:0040C9C8 89 56 04                                      mov     [esi+4], edx
.text:0040C9CB 5E                                            pop     esi
.text:0040C9CC 5D                                            pop     ebp
.text:0040C9CD C3                                            retn
.text:0040C9CE                               ; ---------------------------------------------------------------------------
.text:0040C9CE
.text:0040C9CE                               loc_40C9CE:                             ; CODE XREF: sub_40C750+250↑j
.text:0040C9CE A1 20 F3 41 00                                mov     eax, dwCallback
.text:0040C9D3 6A 00                                         push    0               ; uType
.text:0040C9D5 6A 00                                         push    0               ; lpCaption
.text:0040C9D7 68 C0 C6 41 00                                push    offset asc_41C6C0 ; "梊婜偟側偄暥帤僐乕僪"
.text:0040C9DC 50                                            push    eax             ; hWnd
.text:0040C9DD FF 15 38 A2 41 00                             call    ds:MessageBoxA
.text:0040C9E3 E8 48 63 FF FF                                call    sub_402D30
.text:0040C9E8 6A 01                                         push    1               ; Code
.text:0040C9EA E8 B2 6F 00 00                                call    _exit
.text:0040C9EA                               sub_40C750      endp
*/
bool Milk::attach_function()
{
  const BYTE pattern[] = {

      0x66, 0x3d, 0x40, 0x87,
      0x72, XX,
      0x66, 0x3d, 0x9f, 0x87,
      0x77, XX,
      0x25, 0xf0, 0x00, 0x00, 0x00,
      0x5f,
      0x83, 0xe8, 0x40,
      0xc1, 0xf8, 0x04,
      0x83, 0xc0, 0x38,
      0x8d, 0x0c, 0x40,
      0xb8, 0x02, 0x00, 0x00, 0x00,
      0xc1, 0xe1, 0x03,
      0x89, 0x4e, 0x04,
      0x5e,
      0x5d,
      0xc3};
  auto addr = MemDbg::findBytes(pattern, sizeof(pattern), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x80);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR | DATA_INDIRECT;
  return NewHook(hp, "Milk");
}
