#include "Diskdream.h"

bool Diskdream::attach_function()
{
  // https://vndb.org/v3143
  // Endless Serenade
  char skip[] = "FrameSkip = ";
  ULONG addr = MemDbg::findBytes(skip, sizeof(skip), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING;
  hp.codepage = 932;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    if (!(bool)IsShiftjisLeadByte(*(BYTE *)buffer->buff))
      buffer->clear();
  };
  return NewHook(hp, "Diskdream");
}