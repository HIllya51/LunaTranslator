#include "CoffeeMaker.h"

bool CoffeeMaker_attach_function()
{
  // https://vndb.org/v4025
  // こころナビ
  const BYTE bytes[] = {
      0x81, 0xF9, 0xD4, 0x2B, 0x00, 0x00,
      0x7F, XX,
      0xB8, 0x5D, 0x41, 0x4C, 0xAE};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x10);
  if (!addr)
    return false;
  auto addrs = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
  if (addrs.size() != 1)
    return false;
  auto addr2 = addrs[0];
  addr2 = MemDbg::findEnclosingAlignedFunction(addr2, 0x40);
  if (!addr2)
    return false;
  HookParam hp;
  hp.address = addr2;
  hp.type = USING_CHAR | CODEC_ANSI_BE | NO_CONTEXT;
  hp.user_value = addr;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto a2 = context->stack[1];
    if (a2 > 0x2bd4)
      return;
    auto sub_429050 = (int(__stdcall *)(signed int a1))hp->user_value;
    static int idx = 0;
    if (idx++ % 2)
      buffer->from_t((wchar_t)sub_429050(a2));
  };

  return NewHook(hp, "CoffeeMaker");
}

bool CoffeeMaker_attach_function2()
{
  // https://vndb.org/v4025
  // こころナビ
  const BYTE bytes[] = {
      0x55, 0x8B, 0xEC, 0x57, 0x56, 0x8B, 0x75, 0x0C, 0x8B, 0x4D, 0x10, 0x8B, 0x7D, 0x08, 0x8B, 0xC1,
      0x8B, 0xD1, 0x03, 0xC6, 0x3B, 0xFE, 0x76, 0x08, 0x3B, 0xF8, 0x0F, 0x82, XX4,
      0xF7, 0xC7, 0x03, 0x00, 0x00, 0x00, 0x75, XX, 0xC1, 0xE9, 0x02, 0x83, 0xE2, 0x03, 0x83, 0xF9, 0x08};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1); // regoffset(ecx);//void *__cdecl memcpy(void *a1, const void *Src, size_t Size)
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto s = buffer->strA();
    strReplace(s, R"(\w\w\w)");
    buffer->from(s);
  };
  return NewHook(hp, "CoffeeMaker");
}

bool CoffeeMaker::attach_function()
{
  return CoffeeMaker_attach_function2() || CoffeeMaker_attach_function();
}