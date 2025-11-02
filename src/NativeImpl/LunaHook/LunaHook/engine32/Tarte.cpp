#include "Tarte.h"

bool Tarte::attach_function()
{
  // ひなたぼっこ
  // ひなたると～ひなたぼっこファンディスク～
  // スクールぱにっく！
  // こいじばし  https://vndb.org/v4247
  for (auto addr : findiatcallormov_all((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    auto xrefs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
    for (auto addrx : xrefs)
    {
      auto addrx1 = MemDbg::findEnclosingAlignedFunction(addrx);
      if (!addrx1)
        continue;
      BYTE __[] = {0x3C, 0x81};
      auto _ = MemDbg::findBytes(__, 2, addrx1, addrx);
      if (_ == 0)
        continue;
      HookParam hp;
      hp.address = addrx1;
      hp.offset = stackoffset(2);
      hp.type = CODEC_ANSI_BE;
      auto succ = NewHook(hp, "Tarte");

      auto xrefs1 = findxref_reverse_checkcallop(addrx1, addrx1 - 0x1000, addrx1 + 0x1000, 0xe8);
      for (auto addrx11 : xrefs1)
      {
        auto addrx12 = MemDbg::findEnclosingAlignedFunction(addrx11);
        if (addrx11 - addrx12 < 0x30)
        {
          HookParam hp;
          hp.address = addrx12;
          hp.offset = stackoffset(5);
          hp.type = CODEC_ANSI_BE;
          succ |= NewHook(hp, "Tarte");
        }
      }
      return succ;
    }
  }
  return false;
}