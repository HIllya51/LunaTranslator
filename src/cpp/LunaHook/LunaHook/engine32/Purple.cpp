#include "Purple.h"

bool Purple::attach_function()
{
  // 夢幻 虚実と真実
  // 世界の果ての物語
  const DWORD funcs[] = {
      0xCCCCCCCC,
      0xec8b55,
  };
  enum
  {
    FunctionCount = sizeof(funcs) / sizeof(*funcs)
  };
  ULONG addr = MemDbg::findMultiCallerAddress((ULONG)::GetGlyphOutlineA, funcs, FunctionCount, processStartAddress, processStopAddress);

  if (!addr)
    return false;
  if (*(DWORD *)addr == 0xCCCCCCCC)
    addr += 4;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;

  return NewHook(hp, "Purple");
}

bool Purple2::attach_function()
{
  // はっぴ～ぶり～でぃんぐ    https://vndb.org/p132
  // 夏色小町
  // はぴぶり いまさら ふぁんでぃすく
  ULONG addr = MemDbg::findCallerAddress((ULONG)::TextOutA, 0x90909090, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr += 4;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.index = 0;
  hp.type = DATA_INDIRECT;

  return NewHook(hp, "Purple2");
}