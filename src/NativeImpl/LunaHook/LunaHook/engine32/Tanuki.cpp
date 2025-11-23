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
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
    if (*(DWORD *)i == 0x8140)
      if (DWORD j = MemDbg::findEnclosingAlignedFunction(i, 0x400))
      { // jichi 9/14/2013: might crash the game without admin priv
        // GROWL_DWORD2(i, j);
        HookParam hp;
        hp.address = j;
        hp.offset = stackoffset(1);
        hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
        hp.embed_hook_font = F_GetGlyphOutlineA;
        return NewHook(hp, "TanukiSoft");
      }

  return false;
}
bool InsertTanukiHook2()
{
  const BYTE bytes[] = {
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
  hp.lineSeparator = L"\\n";
  return NewHook(hp, "Tanuki");
}
namespace
{
  // 現実が見えてきたので少女を愛するのを辞めました。
  // 不打补丁Tanuki找不到，打了两者都可以。
  bool t3()
  {
    const BYTE bytes[] = {
        0x83, 0xfe, 0x0d,
        0x0f, 0x84, XX4,
        0x57,
        0xe8, XX4,
        0x83, 0xc4, 0x04,
        0x85, 0xc0,
        0x0f, 0x85, XX4,
        0x33, 0xff,
        0x39, 0x7d, XX,
        0x74, XX,
        0x8a, 0x55, XX,
        0xb9, 0x00, 0x02, 0x00, 0x00,
        0x84, 0xd2,
        0xb8, 0x00, 0x23, 0x00, 0x00,
        0x0f, 0x44, 0xc1,
        0x8b, 0x8d, XX4,
        0x8a, 0x31,
        0x8b, 0xc8,
        0x81, 0xc9, 0x00, 0x14, 0x00, 0x00,
        0x84, 0xf6,
        0x0f, 0x45, 0xc8,
        0x84, 0xd2,
        0x75, XX,
        0x84, 0xf6,
        0x74, XX,
        0x8b, 0xf9,
        0x81, 0xcf, 0x00, 0x30, 0x00, 0x00,
        0xe9, XX4};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x300);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      StringReplacer(buffer, TEXTANDLEN("\x98\x87"), TEXTANDLEN("\x81\x5c\x81\x5c"));
    };
    return NewHook(hp, "Tanuki3");
  }
}
bool Tanuki::attach_function()
{
  bool b1 = InsertTanukiHook();
  bool b2 = InsertTanukiHook2();
  bool b3 = t3();
  return b1 || b2 || b3;
}
bool Tanuki_last::attach_function()
{
  bool b1 = InsertTanukiHook();
  return b1;
}