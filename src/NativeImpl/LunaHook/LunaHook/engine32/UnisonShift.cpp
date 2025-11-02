#include "UnisonShift.h"

bool InsertUnisonShiftHook()
{
  BYTE bytes[] = {
      0x83, 0xec, 0x14,
      0x8b, 0x44, 0x24, 0x10,
      0x53,
      0x55,
      0x8b, 0x6c, 0x24, 0x20

  };
  auto addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (addr1 == 0)
    return false;
  ConsoleOutput("UnisonShift %p", addr1);
  HookParam hp;
  hp.address = addr1;
  hp.offset = stackoffset(3);
  return NewHook(hp, "UnisonShift");
}
bool UnisonShift::attach_function()
{
  return InsertUnisonShiftHook();
}

bool InsertUnisonShift2Hook()
{
  BYTE bytes[] = {
      // 80 FB A0                      cmp     bl, 0A0h
      0x80, 0xfb, 0xa0};
  auto addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (addr1 == 0)
    return false;
  ConsoleOutput("UnisonShift2 %p", addr1);
  BYTE start[] = {0x83, 0xEC, 0x08};
  addr1 = reverseFindBytes(start, sizeof(start), addr1 - 0x100, addr1);
  if (addr1 == 0)
    return false;
  HookParam hp;
  hp.address = addr1;
  hp.offset = regoffset(eax);
  hp.type = DATA_INDIRECT;
  hp.index = 0;
  return NewHook(hp, "UnisonShift2");
}
bool InsertUnisonShift3Hook()
{

  BYTE bytes2[] = {
      0x80, 0xF9, XX};
  auto addrs = Util::SearchMemory(bytes2, sizeof(bytes2), PAGE_EXECUTE, processStartAddress, processStopAddress);
  BYTE moveaxoffset[] = {0xb8, XX, XX, XX, 0x00};
  auto succ = false;
  for (auto addr : addrs)
  {
    ConsoleOutput("UnisonShift3 %p", addr);
    addr = (DWORD)((BYTE *)addr - 5);
    int x = -1;
    for (int i = 0; i < 0x20; i++)
    {
      if (*((BYTE *)addr - i) == 0xb8 && *((BYTE *)(addr) + 4 - i) == 0)
      {
        x = i;
        break;
      }
    }
    if (x == -1)
      continue;
    ConsoleOutput("UnisonShift3 found %p", addr - x);
    addr = (DWORD)((BYTE *)addr + 1 - x);
    auto raddr = *(int *)addr;
    ConsoleOutput("UnisonShift3 raddr %p", raddr);
    HookParam hp;
    hp.address = raddr;
    hp.type = DIRECT_READ;
    succ |= NewHook(hp, "UnisonShift3");
  }

  return succ;
}
namespace
{
  // https://vndb.org/v7123
  // 凌辱人妻温泉

  bool _056()
  {
    BYTE bytes[] = {
        0x83, 0xc4, 0x0c,
        0x83, 0xc1, 0x1e,
        0x80, 0xfb, 0x81,
        0x89, XX, XX4,
        0x0f, 0x85, XX4,
        0x8a, 0x44, 0x24, 0x08,
        0x3c, 0x76,
        0x74, 0x08,
        0x3c, 0x78,
        0x0f, 0x85, XX4};
    auto addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (addr1 == 0)
      return false;
    BYTE start[] = {0x83, 0xEC, 0x08};
    addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
    if (addr1 == 0)
      return false;
    HookParam hp;
    hp.address = addr1;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      auto xx = buffer->strA();
      static std::string last;
      if (xx == last)
        return buffer->clear();
      last = std::move(xx);
    };
    return NewHook(hp, "_056");
  }
}

bool UnisonShift2::attach_function()
{
  bool b1 = InsertUnisonShift2Hook();
  bool b2 = InsertUnisonShift3Hook();
  auto __ = _056();
  return b1 || b2 || __;
}