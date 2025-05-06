#include "OVERDRIVE.h"

bool OVERDRIVE::attach_function()
{
  // エーデルワイス
  const BYTE bytes[] = {
      0x56,
      0x57,
      0x8b, 0x7c, 0x24, 0x0c,
      0x32, 0xc0,
      0x85, 0xff,
      0x8b, 0xf1,
      0x0f, 0x84, XX, 0x00, 0x00, 0x00};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    StringFilter(buffer, TEXTANDLEN("\\p\\l"));
  };
  return NewHook(hp, "OVERDRIVE");
}