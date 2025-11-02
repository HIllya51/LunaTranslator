#include "TSSystem.h"
bool TSSystem::attach_function()
{
  // D-EVE in you
  // トロピカルKISS
  const BYTE bytes[] = {
      0xB9, 0x42, 0x00, 0x00, 0x00,
      0xF3, 0xA5};
  bool ok = false;
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  for (auto addr : addrs)
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    ok |= NewHook(hp, "TSSystem");
  }
  return ok;
}
