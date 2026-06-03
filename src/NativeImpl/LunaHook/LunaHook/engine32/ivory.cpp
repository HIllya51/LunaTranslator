#include "ivory.h"

bool ivory::attach_function()
{
  // https://vndb.org/v1122
  // とらいあんぐるハート3～Sweet Songs Forever～

  const BYTE bytes[] = {
      0x56,
      0x8b, 0x74, 0x24, 0x08,
      0x57,
      0x8b, 0xf9,
      0x8a, 0x06,
      0x84, 0xc0,
      0x74, XX,
      0xa8, 0x80,
      0x74, 0x0f,
      0x6a, 0x02,
      0x56,
      0x8b, 0xcf,
      0xe8, XX4,
      0x83, 0xc6, 0x02};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->viewA();
    if (s == "\x81\x75\x81\x76")
      buffer->from("\x81\x75");
  };
  return NewHook(hp, "TH3");
}