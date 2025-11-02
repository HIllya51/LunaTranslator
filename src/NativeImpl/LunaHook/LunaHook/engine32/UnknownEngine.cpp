#include "UnknownEngine.h"
bool UnknownEngine::attach_function()
{
  // ABANDONER - THE SEVERED DREAMS
  // https://vndb.org/v1182
  const BYTE bytes[] = {
      0x8B, 0x44, 0x24, 0x04,
      0x85, 0xC0,
      0x75, 0x03,
      0xC2, 0x08, 0x00,
      0x33, 0xD2,
      0x8A, 0x50, 0x01,
      0x8A, 0x30,
      0x8B, 0xC2,
      0x50,
      0xE8, XX4,
      0xC2, 0x08, 0x00};
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  auto succ = false;
  for (auto addr : addrs)
  {
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.index = 0;
    hp.type = DATA_INDIRECT;
    succ |= NewHook(hp, "Unknown");
  }
  return succ;
}
