#include "Nekotaro.h"

bool Nekotaro::attach_function()
{
  // [991217][Jam] 女の子どうし ～Girl Playing Game～ (cdi)
  const BYTE bytes[] = {
      0x3c, 0x61,
      0X72, 0X0A,
      0X3C, 0X7A,
      0X77, 0X06,
      0X24, 0XDF,
      0X88, 0X44, 0X24, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0X300);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(6);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->strA();
    strReplace(s, "@n", "\n");
    strReplace(s, "\x87\x52", "!?");
    s = re::sub(s, "@x\\d");
    s = re::sub(s, "@C\\d");
    s = re::sub(s, "@P\\d");
    s = re::sub(s, "@c\\d+");
    buffer->from(s);
  };
  return NewHook(hp, "Nekotaro");
}