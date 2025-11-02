#include "Yatagarasu.h"

bool Yatagarasu::attach_function()
{
  // テンタクルロード －我が手に堕ちよ勇壮なる乙女－
  const char left[] = "<%";
  const char right[] = "<voice";
  auto addr1 = MemDbg::findBytes(left, sizeof(left), processStartAddress, processStopAddress);
  auto addr2 = MemDbg::findBytes(right, sizeof(right), processStartAddress, processStopAddress);
  if (!addr1 || !addr2)
    return false;
  addr1 = MemDbg::findPushAddress(addr1, processStartAddress, processStopAddress);
  addr2 = MemDbg::findPushAddress(addr2, processStartAddress, processStopAddress);
  if (!addr1 || !addr2)
    return false;
  addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
  addr2 = MemDbg::findEnclosingAlignedFunction(addr2);
  ConsoleOutput("%p %p", addr1, addr2);
    return false;
  if (addr1 != addr2)
    return false;
  HookParam hp;
  hp.address = addr1;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING | NO_CONTEXT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto text = buffer->strAW();
    text = re::sub(text, L"<%.*?>");
    text = re::sub(text, L"<voice.*?>");
    text = re::sub(text, L"<\\w+>");
    buffer->fromWA(text);
  };
  return NewHook(hp, "Yatagarasu");
}