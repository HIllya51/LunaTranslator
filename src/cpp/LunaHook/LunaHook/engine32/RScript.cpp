#include "RScript.h"

bool RScript::attach_function()
{
  /*
  void __thiscall CSelTxtEx::SetSels(CSelTxtEx *this, char *a2)

   while ( *a2 )
  {
    if ( _ismbblead(*a2) && (v8 = _ismbbtrail(a2[1])) != 0 )
    {
      if ( *((_WORD *)this + 42) >= *((_WORD *)this + 43) )
        return;
      LOWORD(v8) = (unsigned __int8)*a2;
      LOWORD(v9) = (unsigned __int8)a2[1];
      *(_WORD *)(*((_DWORD *)this + 96) + 2 * *((unsigned __int16 *)this + 42)) = v3;
      CSelTxtEx::SetSel(this, v9 + (v8 << 8), v23, v4, v22, v21);
      a2 += 2;
    }
    else if ( *a2 == 94 )
    {
      v10 = *++a2;
      if ( !v10 )
        return;
      switch ( v10 )
      {
        case 'A':
        case 'a':
  */
  BYTE bytes[] = {
      0x80, 0x3f, 0x5e,
      0x0f, 0x85, XX4,
      0x8a, 0x47, 0x01,
      0x47, 0x84, 0xc0,
      0x0f, 0x84, XX4,
      0x0f, 0xbe, 0xc0,
      0x83, 0xc0, 0xbf,
      0x83, 0xf8, 0x32};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  auto faddr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!faddr)
    return false;
  BYTE bytes2[] = {
      0x8a, 0x07,
      0x84, 0xc0,
      0x0f, 0x84, XX4,
      0x0f, 0xbe, 0xd0,
      0x52,
      0xe8, XX4, // call    __ismbblead
      0x83, 0xc4, 0x04,
      0x85, 0xc0,
      0x74, XX,
      0x0f, 0xbe, 0x47, 0x01,
      0x50,
      0xe8, XX4, // call    __ismbbtrail
  };
  auto addrX = MemDbg::findBytes(bytes2, sizeof(bytes2), faddr, addr);
  if (!addrX)
    return false;
  auto __ismbblead = *(int *)(addrX + 2 + 2 + 6 + 3 + 1 + 1) + addrX + 2 + 2 + 6 + 3 + 1 + 5;
  auto __ismbbtrail = *(int *)(addrX + sizeof(bytes2) - 4) + addrX + sizeof(bytes2);
  ConsoleOutput("%p", __ismbblead);
  ConsoleOutput("%p", __ismbbtrail);
  HookParam hp;
  hp.address = faddr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_GetGlyphOutlineA | F_GetTextExtentPoint32A;
  hp.lineSeparator = L"^n";
  patch_fun_ptrs = {{(void *)__ismbblead, +[](BYTE b)
                                          { return b != '^'; }},
                    {(void *)__ismbbtrail, +[](BYTE b)
                                           { return b != '^'; }}};
  return NewHook(hp, "RScript");
}