#include "VitaminSoft.h"

namespace
{
  bool _1()
  {
    // どうして？いじってプリンセスFinalRoad～もう！またこんなところで3～
    bool ok = false;
    for (auto addr : findiatcallormov_all((DWORD)ExtTextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
    {
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(3);
      hp.type = DATA_INDIRECT;
      hp.index = 0;
      ok |= NewHook(hp, "VitaminSoft");
    }
    return ok;
  }
  bool _2()
  {
    // ねとって女神
    // ねとって女神 NEO
    bool ok = false;
    for (auto addr : findiatcallormov_all((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
    {
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      // 真説 猟奇の檻
      // mov     eax, [esp+arg_10]
      hp.offset = (((*(DWORD *)addr) == 0x1424448b) ? stackoffset(3) : stackoffset(1));
      hp.type = USING_STRING;
      ok |= NewHook(hp, "VitaminSoft2");
    }
    return ok;
  }
}

bool VitaminSoft::attach_function()
{
  auto succ = _2() || _1();
  PcHooks::hookGDIFunctions((void *)TextOutA);
  return succ;
}