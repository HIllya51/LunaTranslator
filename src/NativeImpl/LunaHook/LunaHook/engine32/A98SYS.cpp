#include "A98SYS.h"

bool A98SYS::attach_function()
{
  // https://vndb.org/v6447
  // Rainy Blue ～6月の雨～

  auto addrs = findiatcallormov_all((DWORD)::ExtTextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE);
  if (addrs.size() != 2)
    return false;
  auto addr = addrs[1];
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  auto addrs1 = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
  if (!addrs1.size())
    return false;
  addr = addrs1[0];
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_ExtTextOutA;

  return NewHook(hp, "A98SYS");
}