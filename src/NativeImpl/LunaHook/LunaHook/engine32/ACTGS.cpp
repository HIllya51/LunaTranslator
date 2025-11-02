#include "ACTGS.h"

bool ACTGS::attach_function()
{
  const BYTE bytes[] = {
      0x0F, 0xBE, 0xD0,
      0x83, 0xFA, 0x20,
      0x74, XX,
      0x83, 0xfa, 0x09,
      0x75, XX

  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  addr = findfuncstart(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  hp.filter_fun = all_ascii_Filter;

  return NewHook(hp, "ACTGS");
}