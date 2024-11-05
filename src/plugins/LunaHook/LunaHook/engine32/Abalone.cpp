#include "Abalone.h"

bool AbaloneHook()
{
  BYTE bytes[] = {
      0x8B, 0x44, 0x24, XX,
      0x80, 0x38, 0x00,
      0x74};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("AbaloneHook %p", addr);
  if (addr == 0)
    return false;
  HookParam hp;
  hp.address = addr + 4;
  hp.offset = get_reg(regs::eax);
  hp.type = DATA_INDIRECT;
  hp.index = 0;
  return NewHook(hp, "AbaloneHook");
}
bool Abalone::attach_function()
{
  return AbaloneHook();
}