#include "MixwillSoft.h"
// https://vndb.org/v10193
bool MixwillSoft::attach_function()
{
  const BYTE bytes[] = {
      /*
  .text:0042D0B5                 mov     eax, [esp+5ECh+var_5C4]
  .text:0042D0B9                 mov     [esp+5ECh+var_4], 2
  .text:0042D0C4                 test    eax, eax
  .text:0042D0C6                 jnz     short loc_42D0CD
  .text:0042D0C8                 mov     eax, offset String
  .text:0042D0CD
  .text:0042D0CD loc_42D0CD:                             ; CODE XREF: sub_42CF50+176↑j
  .text:0042D0CD                 mov     ecx, [esp+5ECh+var_5C0]
  .text:0042D0D1                 cmp     byte ptr [eax+ecx-1], 5Ch ; '\'
  .text:0042D0D6                 jnz     short loc_42D0F9
  .text:0042D0D8                 lea     eax, [ecx-1]
  .text:0042D0DB                 cmp     eax, ecx
      */
      /*
     v12 = v130;
     v177 = 2;
     if ( !v130 )
       v12 = String;
     if ( v12[v131 - 1] == 92 )
     {
       if ( v131 - 1 > v131 )
      */
      0x8B, 0x44, 0x24, 0x28,
      0xC7, 0x84, 0x24, 0xE8, 0x05, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00,
      0x85, 0xC0,
      0x75, 0x05,
      0xB8, 0x40, 0xA5, 0x59, 0x00,
      0x8B, 0x4C, 0x24, 0x2C,
      0x80, 0x7C, 0x08, 0xFF, 0x5C,
      0x75, 0x21,
      0x8D, 0x41, 0xFF,
      0x3B, 0xc1};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 4 + 11 + 2 + 2 + 5;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  // 内嵌时长度溢出会崩溃，所以不内嵌。
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if (endWith(buffer->viewA(), "/"))
    {
      buffer->size -= 1;
    }
  };
  return NewHook(hp, "MixwillSoft");
}