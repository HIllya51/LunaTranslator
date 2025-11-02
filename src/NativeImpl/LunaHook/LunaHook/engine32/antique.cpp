#include "antique.h"

bool antique::attach_function()
{
  // https://vndb.org/v3122
  // あそび塾
  const BYTE bytes[] = {
      /*
      .text:00409809                 mov     eax, dword_43E5B4
  .text:0040980E                 cmp     byte ptr [eax], 81h
  .text:00409811                 jnz     short loc_409856
  .text:00409813                 mov     al, [eax+1]
  .text:00409816                 cmp     al, 41h ; 'A'
  .text:00409818                 jl      short loc_409856
  .text:0040981A                 cmp     al, 44h ; 'D'
  .text:0040981C                 jg      short loc_409856
      */
      /*
       if ( *(_BYTE *)dword_43E5B4 == 0x81 && (v14 = *(_BYTE *)(dword_43E5B4 + 1), v14 >= 65) && v14 <= 68 )
      */
      0x80, 0x38, 0x81,
      0x75, XX,
      0x8a, 0x40, 0x01,
      0x3c, 0x41,
      0x7c, XX,
      0x3c, 0x44,
      0x7f, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | DATA_INDIRECT | USING_SPLIT | SPLIT_INDIRECT;
  hp.offset = stackoffset(1);
  hp.split = stackoffset(3);
  hp.filter_fun = [](TextBuffer *buffer, auto *)
  {
    static int i = 0;
    if (i++ % 2)
      return buffer->clear();
    StringFilter(buffer, TEXTANDLEN("\\n"));
  };
  hp.embed_hook_font = F_GetGlyphOutlineA;
  return NewHook(hp, "antique");
}