#include "Broccoli.h"

bool Broccoli::attach_function()
{
  char check[] = "KaraokeMesPutCt %d, MojiCt %d";
  if (!MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress))
    return false;

  const BYTE bytes[] = {
      0x8b, 0x0d, XX4,
      0x89, 0x44, 0x24, XX,
      0xa1, XX4,
      0x89, 0x4c, 0x24, XX,
      0x89, 0x44, 0x24, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + sizeof(bytes) - 8;
  hp.offset = regoffset(ecx);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if (buffer->viewA() == "\\")
      return buffer->clear();
  };
  return NewHook(hp, "Broccoli");
}