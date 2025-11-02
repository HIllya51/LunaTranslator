#include "AniSeed.h"

bool AniSeed::attach_function()
{
  // 花譜 ～この調べが君に届きますように～
  // https://vndb.org/v3521

  auto addr = findiatcallormov((DWORD)::TextOutA, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  auto faddr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!faddr)
    return false;
  BYTE check[] = {
      0x8a, 0x01,
      0xa8, 0x80,
      0x74, XX,
      0x3c, 0xa0,
      0x73, XX,
      0x25, 0xff, 0x00, 0x00, 0x00,
      0x2d, 0x80, 0x00, 0x00, 0x00,
      0x33, 0xd2,
      0x8a, 0x51, 0x01,
      0x8a, 0xf0};
  if (!MemDbg::findBytes(check, sizeof(check), faddr, addr))
    return false;
  HookParam hp;
  hp.address = faddr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR | DATA_INDIRECT;
  hp.codepage = SHIFT_JIS;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static bool lastisleftkuohao = false;
    auto s = buffer->viewA();
    if (s == "\x81\x75")
      lastisleftkuohao = true;
    else
    {
      if (lastisleftkuohao && s == "\x81\x76")
        buffer->clear();
      lastisleftkuohao = false;
    }
  };

  return NewHook(hp, "AniSeed");
}