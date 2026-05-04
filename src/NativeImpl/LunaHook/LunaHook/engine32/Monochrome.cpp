#include "Monochrome.h"

bool Monochrome::attach_function()
{
  // https://vndb.org/v11759
  // ラブレッスン
  auto addr = findiatcallormov((DWORD)GetTextExtentPoint32A, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static std::string last;
    auto s = buffer->strA();
    if (s == last)
    {
      buffer->clear();
    }
    last = s;
  };
  return NewHook(hp, "Monochrome");
}