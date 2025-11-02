#include "Jisatu101.h"

bool Jisatu101::attach_function()
{
  const BYTE bytes[] = {
      // ジサツのための１０１の方法
      // https://vndb.org/v6475
      0x8b, 0x44, 0x24, 0x10,
      0x66, 0x0f, 0xb6, 0x08,
      0x66, 0x0f, 0xb6, 0x50, 0x01,

      0xC1, 0xE1, 0x08,
      0x03, 0xCA,
      0x66, 0x81, 0xF9, 0x0A, 0x0D,
      0x74};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(4);
  hp.type = DATA_INDIRECT;
  hp.index = 0;
  return NewHook(hp, "Jisatu101");
}