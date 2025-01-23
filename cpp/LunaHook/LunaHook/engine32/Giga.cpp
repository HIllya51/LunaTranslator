#include "Giga.h"

bool Giga::attach_function()
{

  const BYTE bytes[] = {
      // ショコラ ~maid cafe curio Re-order~
      // https://vndb.org/v682
      0xe8, XX4,
      0x83, 0xC4, 0x10,
      0xB8, 0x01, 0x00, 0x00, 0x00,
      0x81, 0xC4, 0x00, 0x10, 0x00, 0x00,
      0xC3};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(4);
  hp.type = USING_STRING;

  return NewHook(hp, "Giga");
}