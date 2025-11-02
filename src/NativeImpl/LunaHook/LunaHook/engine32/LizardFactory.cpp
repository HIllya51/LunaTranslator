#include "LizardFactory.h"

bool LizardFactory::attach_function()
{
  const BYTE bytes[] = {
      0x84, 0xc0,
      0x0f, 0x84, XX4,
      0x3c, 0x81,
      0x72, XX,
      0x3c, 0xa0,
      0x72, XX,
      0x3c, 0xe0,
      0x72, XX,
      0x3c, 0xff,
      0x73, XX,
      0x8b, 0x0f,
      0x8b, 0xc1,
      0xc1, 0xf8, 0x08,
      0x0f, 0xb6, 0xf0,
      0x0f, 0xb6, 0xc1,
      0xc1, 0xe0, 0x08,
      0x0b, 0xf0,
      0x83, 0xc7, 0x02,
      0xb8, 0x01, 0x00, 0x00, 0x00,
      0xeb, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x20);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | DATA_INDIRECT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static std::string last;
    auto s = buffer->strA();
    if (endWith(last, s))
      return buffer->clear();
    last = s;
    buffer->from(strReplace(strReplace(s, "\r"), "\n"));
  };
  return NewHook(hp, "LizardFactory");
}