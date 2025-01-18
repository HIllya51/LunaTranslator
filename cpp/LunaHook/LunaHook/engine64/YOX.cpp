#include "YOX.h"
bool YOX::attach_function()
{
  const BYTE BYTES[] = {
      0x48, 0x8B, 0x0F,
      0x48, 0x8d, 0x54, 0x24, 0x50};
  auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE_READ, processStartAddress, processStopAddress);
  ConsoleOutput("%p %p", processStartAddress, processStopAddress);
  for (auto addr : addrs)
  {
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING;
    hp.offset = stackoffset(26);
    ConsoleOutput("yox64 %p", addr);
    return NewHook(hp, "yox64");
  }
  ConsoleOutput("yox64 failed");
  return false;
}