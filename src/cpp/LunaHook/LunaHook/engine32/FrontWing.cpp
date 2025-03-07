#include "FrontWing.h"

bool FrontWing::attach_function()
{
  const BYTE bytes[] = {
      // v55 = (int)(__CFADD__(v54 * v13, 0x80000000) + v54 * v13 + 0x80000000 + 0x80000000) >> 1;
      0x05, 0x00, 0x00, 0x00, 0x80, 0x15, 0x00, 0x00, 0x00, 0x80, 0xD1, 0xF8, 0x85, 0xC0};

  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  return NewHook(hp, "FrontWing");
}

bool FrontWing2_attach_function()
{
  const BYTE bytes[] = {
      0x68, 0xb4, 0x00, 0x00, 0x00,
      0x6a, 0x00,
      0x8b, 0x55, 0x08,
      0x81, 0xc2, XX4,
      0x52,
      0xe8, XX4,
      0x83, 0xc4, 0x0c,
      0x68, 0xb3, 0x00, 0x00, 0x00,
      0x8b, 0x45, 0x08,
      0x8b, 0x88, XX4,
      0x03, 0x4d, 0xfc,
      0x51,
      0x8b, 0x55, 0x08,
      0x81, 0xc2, XX4,
      0x52,
      0xe8, XX4};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + sizeof(bytes) - 5;
  hp.offset = regoffset(ecx);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto __ = strSplit(buffer->strA(), "\n");
    std::string s;
    for (auto i = 0; (i < __.size()) && (__[i].size() > 1); i++)
    {
      s += __[i];
    }
    auto ws = StringToWideString(s, 932).value();
    strReplace(ws, L"\r");
    ws = re::sub(ws, LR"([\w\d]*\\[\w\d]*\\[\w\d_]*)");
    ws = re::sub(ws, LR"(\[rb,(.*?),(.*?)\])", L"$1");
    ws = re::sub(ws, L",(.*?),(.*?)", L"$1$2");
    buffer->fromWA(ws);
  };
  return NewHook(hp, "FrontWing");
}
bool FrontWing2_attach_function2()
{
  const BYTE bytes[] = {
      0x8b, 0x55, 0xf8,
      0x03, 0x55, 0x10,
      0x03, 0x55, XX,
      0x8b, 0x45, 0x0c,
      0x0f, 0xbe, 0x0c, 0x10,
      0x83, 0xf9, 0x0d,
      0x75, XX,
      0x8b, 0x55, 0xf8,
      0x03, 0x55, 0x10,
      0x03, 0x55, XX,
      0x8b, 0x45, 0x0c,
      0x0f, 0xbe, 0x4c, 0x10, 0x01,
      0x83, 0xf9, 0x0a,
      0x75, XX,
      0x8b, 0x55, 0xf8,
      0x03, 0x55, 0x10,
      0x03, 0x55, XX,
      0x8b, 0x45, 0x0c,
      0x0f, 0xbe, 0x4c, 0x10, 0x02,
      0x83, 0xf9, 0x0d,
      0x75, XX,
      0x8b, 0x55, 0xf8,
      0x03, 0x55, 0x10,
      0x03, 0x55, XX,
      0x8b, 0x45, 0x0c,
      0x0f, 0xbe, 0x4c, 0x10, 0x03,
      0x83, 0xf9, 0x0a,
      0x74, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto xx = buffer->viewA();
    static std::string last;
    if (xx == last)
      return buffer->clear();
    last = xx;
  };
  return NewHook(hp, "FrontWing");
}
bool FrontWing2::attach_function()
{
  return FrontWing2_attach_function() || FrontWing2_attach_function2();
}