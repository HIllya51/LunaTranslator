#include "R11.h"
// Remember 11
static void ff(TextBuffer *buffer, HookParam *)
{
  StringFilter(buffer, "%XS", 5); // remove %XS followed by 2 chars
  std::wstring str = buffer->strAW();
  std::wstring result1 = re::sub(str, L"\\{(.*?):(.*?)\\}", L"$1");
  result1 = re::sub(result1, L"\\{(.*?);(.*?)\\}", L"$1");
  result1 = re::sub(result1, L"%[A-Z]+");
  buffer->fromWA(result1);
}
static bool maintext()
{
  BYTE check[] = {
      0x8a, 0x11,
      0x83, 0xc1, 0x01,
      0x84, 0xd2,
      0x75, 0xf7,
      0x2b, 0x4c, 0x24, 0x24,
      0x03, 0xc1,
      0x80, 0x38, 0x81,
      0x75, XX,
      0x8a, 0x40, 0x01,
      0x3c, 0x75,
      0x0f, 0x84, XX4,
      0x3c, 0x77,
      0x0f, 0x84, XX4,
      0x3c, 0x69,
      0x74, XX};
  auto addr = MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | EMBED_ABLE; // 主要是可以嵌入英文
  hp.offset = stackoffset(1);
  hp.filter_fun = ff;
  hp.embed_fun = [](hook_context *s, TextBuffer buffer, HookParam *)
  {
    auto prefixappendfix = [](const std::wstring &origin, const std::wstring &newstr)
    {
      std::wstring pre = re::match(origin, LR"(((%[A-Z]+)*)(.*?))").value()[1];
      std::wstring app = re::match(origin, LR"((.*?)((%[A-Z]+)*))").value()[2];
      return pre + newstr + app;
    };

    auto data_ = buffer.strAW();
    strReplace(data_, L" ", L"　　");
    std::wstring origin = StringToWideString((char *)s->stack[1], 932).value();
    s->stack[1] = (DWORD)allocateString(WideStringToString(prefixappendfix(origin, data_), 932));
  };
  return NewHook(hp, "R11");
}
static bool sentakushi()
{
  BYTE check[] = {
      0xc1, 0xe0, 0x0c,
      0x99,
      0x81, 0xe2, 0xff, 0x0f, 0x00, 0x00,
      0x03, 0xc2,
      0x8b, 0x96, 0x10, 0x02, 0x00, 0x00,
      0xc1, 0xf8, 0x0c,
      0x2d, 0xff, 0x0f, 0x00, 0x00,
      0xc1, 0xf8, 0x0c,
      0x2b, 0xd0};
  auto addr = MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE start[] = {0xCC, 0xCC, 0x53};
  addr = reverseFindBytes(start, sizeof(start), addr - 0x100, addr, 2, true);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | FULL_STRING;
  hp.offset = stackoffset(3);
  hp.filter_fun = ff;
  return NewHook(hp, "R11");
}
bool R11::attach_function()
{
  return maintext() && sentakushi();
}