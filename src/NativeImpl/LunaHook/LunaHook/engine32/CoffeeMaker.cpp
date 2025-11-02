#include "CoffeeMaker.h"

bool CoffeeMaker_attach_function()
{
  // https://vndb.org/v4025
  // みになびVGA
  auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, true, 0x1d); // mov     ebx, ds:GetGlyphOutlineA
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_CHAR | DATA_INDIRECT;
  hp.offset = stackoffset(3);
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
  return CoffeeMaker_attach_function2() | CoffeeMaker_attach_function();
}