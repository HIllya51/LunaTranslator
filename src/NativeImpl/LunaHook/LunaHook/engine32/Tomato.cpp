#include "Tomato.h"
bool Tomato::attach_function()
{
  // 姫武者
  bool ok = false;
  for (auto addr : findiatcallormov_all((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.type = DATA_INDIRECT;
    hp.index = 0;
    ok |= NewHook(hp, "Tomato");
  }
  return ok;
}
