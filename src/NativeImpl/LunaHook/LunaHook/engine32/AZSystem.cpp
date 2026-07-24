#include "AZSystem.h"
// Triptych
// https://vndb.org/v537
bool AZSystem::attach_function()
{
  BYTE bytes[] = {
      0x8a, 0x1f,
      0x8a, 0xc3,
      0x34, 0x20,
      0x04, 0x5f,
      0x3c, 0x3b,
      0x77, 0x15,
      0x66, 0x8b, 0x17,
      0x8b, XX, XX, XX,
      0xb9, 0x02, 0x00, 0x00, 0x00,
      0x66, 0x89, 0x54, 0x24, 0x10,
      0x03, 0xf9};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edi);
  hp.type = USING_STRING;
  return NewHook(hp, "AZSystem");
}