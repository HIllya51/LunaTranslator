#include "Tanuki.h"

/** jichi 9/14/2013
 *  TanukiSoft (*.tac)
 *
 *  Seems to be broken for new games in 2012 such like となり�
 *
 *  微少女: /HSN4@004983E0
 *  This is the same hook as ITH
 *  - addr: 4817888 (0x4983e0)
 *  - text_fun: 0x0
 *  - off: 4
 *  - type: 1025 (0x401)
 *
 *  隣り�ぷ�さ� /HSN-8@200FE7:TONARINO.EXE
 *  - addr: 2101223 (0x200fe7)
 *  - module: 2343491905 (0x8baed941)
 *  - off: 4294967284 = 0xfffffff4 = -0xc
 *  - type: 1089 (0x441)
 */
bool InsertTanukiHook()
{
  ConsoleOutput("trying TanukiSoft");
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
    if (*(DWORD *)i == 0x8140)
      if (DWORD j = SafeFindEnclosingAlignedFunction(i, 0x400))
      { // jichi 9/14/2013: might crash the game without admin priv
        // GROWL_DWORD2(i, j);
        HookParam hp;
        hp.address = j;
        hp.offset = stackoffset(1);
        hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
        hp.embed_hook_font = F_GetGlyphOutlineA;
        ConsoleOutput("INSERT TanukiSoft");
        return NewHook(hp, "TanukiSoft");
      }

  // ConsoleOutput("Unknown TanukiSoft engine.");
  ConsoleOutput("TanukiSoft: failed");
  return false;
}
bool InsertTanukiHook2()
{
  const BYTE bytes[] = {
      // 0x55,0x8b,0xec,0x53,0x8b,0x5d,0x08,0x56,0x8b,0xf1,0x85,0xdb  string too long hook。但是这个会把所有字符串全提出来
      XX, 0x9F, 0x88, 0x00, 0x00,
      0x66};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x1000);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  ConsoleOutput("Tanuki %p", addr);
  return NewHook(hp, "Tanuki");
}
bool Tanuki::attach_function()
{

  bool b1 = InsertTanukiHook();
  bool b2 = InsertTanukiHook2();
  return b1 || b2;
}
bool Tanuki_last::attach_function()
{

  bool b1 = InsertTanukiHook();
  return b1;
}