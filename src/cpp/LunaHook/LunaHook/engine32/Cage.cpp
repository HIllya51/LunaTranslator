#include "Cage.h"

bool Cage::attach_function()
{
  // https://vndb.org/v8381
  // 夢姿 ～ゆめのすがた～
  /*
  size_t __cdecl _mbslen(const unsigned __int8 *String)
{
const unsigned __int8 *v2; // eax
size_t i; // esi

if ( !dword_476AFC )
return strlen((const char *)String);
_lock(25);
v2 = String;
for ( i = 0; *v2; ++i )
{
if ( (byte_476C01[*v2] & 4) != 0 && !*++v2 )
break;
++v2;
}
_unlock(25);
return i;
}
  */
  /*
  .text:00451B0C                 mov     eax, [esp+8+String]
.text:00451B10                 pop     ecx
.text:00451B11                 xor     esi, esi
.text:00451B13
.text:00451B13 loc_451B13:                             ; CODE XREF: __mbslen+3D↓j
.text:00451B13                 mov     cl, [eax]
.text:00451B15                 test    cl, cl
.text:00451B17                 jz      short loc_451B2F
.text:00451B19                 movzx   ecx, cl
.text:00451B1C                 test    byte_476C01[ecx], 4
.text:00451B23                 jz      short loc_451B2B
.text:00451B25                 inc     eax
.text:00451B26                 cmp     byte ptr [eax], 0
.text:00451B29                 jz      short loc_451B2F
.text:00451B2B
.text:00451B2B loc_451B2B:                             ; CODE XREF: __mbslen+33↑j
.text:00451B2B                 inc     esi
.text:00451B2C                 inc     eax
.text:00451B2D                 jmp     short loc_451B13
  */
  BYTE check[] = {
      0x8B, 0x44, 0x24, 0x0C,
      0x59,
      0x33, 0xF6,
      0x8A, 0x08,
      0x84, 0xC9,
      0x74, 0x16,
      0x0F, 0xB6, 0xC9,
      0xF6, 0x81, XX4, 0x04,
      0x74, 0x06,
      0x40,
      0x80, 0x38, 0x00,
      0x74, 0x04,
      0x46,
      0x40,
      0xEB, 0xE4};
  auto addrx = MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress);
  if (!addrx)
    return false;
  addrx = MemDbg::findEnclosingAlignedFunction(addrx);
  if (!addrx)
    return 0;
  HookParam hp;
  hp.address = addrx;
  hp.type = USING_STRING;
  hp.offset = stackoffset(1);
  return NewHook(hp, "Cage");
}