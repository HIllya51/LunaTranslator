#include "Nijyuei.h"

bool Nijyuei::attach_function()
{
  // 二重影
  BYTE bytes[] = {
      0xE8, XX4,
      0x85, 0xc0,
      0x0f, 0x85, XX4,
      0x5f, 0x5e, 0x5d, 0x5b,
      0x81, 0xC4, 0x0C, 0x01, 0x00, 0x00,
      0xC3

  };
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 5;
  hp.type = USING_STRING;
  hp.offset = regoffset(edx);
  return NewHook(hp, "Nijyuei");
}