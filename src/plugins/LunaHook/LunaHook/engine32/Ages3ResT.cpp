#include "Ages3ResT.h"

bool Ages3ResTHook()
{
  const BYTE bytes[] = {
      0x8d, 0x4f, XX,
      0xff, 0x15, XX4,
      XX,
      0x8d, 0x8f, XX4,
      0xff, 0x15, XX4,
      0x8d, XX, XX4,
      XX,
      0x8d, 0x8f, XX4,
      0xff, 0x15, XX4,
      0x8b, XX,
      0xff, 0x15, XX4};

  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  bool succ = false;
  for (auto addr : addrs)
  {
    ConsoleOutput("Ages3ResT %p", addr);
    if (addr == 0)
      return false;
    addr = findfuncstart(addr);
    ConsoleOutput("Ages3ResT %p", addr);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_stack(3);
    hp.type = CODEC_UTF16 | USING_STRING;
    succ |= NewHook(hp, "Ages3ResT");
  }
  return succ;
}

bool Ages3ResT::attach_function()
{
  return Ages3ResTHook();
}