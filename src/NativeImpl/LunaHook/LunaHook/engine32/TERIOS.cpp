#include "TERIOS.h"

bool TERIOS::attach_function()
{
  // https://vndb.org/v1722
  const BYTE bytes[] = {
      0x8b, 0xd8,
      0x80, 0xfb, 0x20,
      0x77, XX,
      0x8b, 0xc3,
      0x2c, 0x01,
      0x0f, XX, XX4,
      0x2c, 0x09,
      0x0f, XX, XX4,
      0xe9};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if (all_ascii(buffer->viewA().substr(0, 2)))
      return buffer->clear();
  };
  return NewHook(hp, "TERIOS");
}