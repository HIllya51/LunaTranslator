#include "mirage.h"

bool mirage::attach_function()
{
  //[031219][mirage] そこに海があって
  ULONG addr = MemDbg::findCallerAddress((DWORD)TextOutA, 0x90909090, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 4;
  hp.offset = stackoffset(1);
  hp.type = DATA_INDIRECT | USING_CHAR;
  return NewHook(hp, "mirage");
}