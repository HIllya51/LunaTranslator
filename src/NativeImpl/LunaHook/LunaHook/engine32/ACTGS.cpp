#include "ACTGS.h"

static bool hook2()
{
  // きつね色の子守唄
  const BYTE bytes[] = {
      0x57,
      0xe8, XX4, // strlen
      0x59,
      0x89, 0x45, 0xfc,
      0x8b, 0x4d, 0xfc,
      0x41,
      0x51,
      0xe8, XX4, // new
      0x59,
      0x8b, 0xf0,
      0x89, 0x73, 0x08,
      0x85, 0xf6};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  addr = findfuncstart(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  return NewHook(hp, "ACTGS2");
}

bool ACTGS::attach_function()
{
  if (hook2())
    return true;
  const BYTE bytes[] = {
      0x0F, 0xBE, 0xD0,
      0x83, 0xFA, 0x20,
      0x74, XX,
      0x83, 0xfa, 0x09,
      0x75, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
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