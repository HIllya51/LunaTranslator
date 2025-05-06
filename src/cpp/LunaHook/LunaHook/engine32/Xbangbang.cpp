#include "Xbangbang.h"

bool Xbangbang::attach_function()
{
  // さわさわ絵にっき
  // さわさわ絵にっき２
  bool ok = false;
  for (auto addr : findiatcallormov_all((DWORD)GetTextExtentPoint32A, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING;
    ok |= NewHook(hp, "Xbangbang");
  }
  return ok;
}