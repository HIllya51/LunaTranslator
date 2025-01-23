#include "utawarerumono.h"

bool utawarerumonoh()
{
  const BYTE bytes[] = {
      0x80, XX, 0x5C,
      0x75
      //*a2 != 92 || a2[1] != 107
  };
  const BYTE bytes2[] = {
      0x80, XX, XX, XX, 0x5C,
      0x75};
  auto addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  auto addr2 = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  auto succ = false;
  for (auto addr : {addr1, addr2})
  {
    if (!addr)
      continue;
    const BYTE funcstart[] = {
        0x51, 0x53};
    addr = reverseFindBytes(funcstart, sizeof(funcstart), addr - 0x100, addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.lineSeparator = L"\\n";
    hp.offset = stackoffset(1);
    hp.type = CODEC_UTF8 | USING_STRING | NO_CONTEXT;
    ConsoleOutput("utawarerumono");
    succ |= NewHook(hp, "utawarerumono");
  }
  return succ;
}
bool utawarerumonoh2()
{
  const BYTE bytes2[] = {
      0x8b, 0xca,
      0xc1, 0xe9, 0x02,
      0xf3, 0xa5};
  auto addr2 = Util::SearchMemory(bytes2, sizeof(bytes2), PAGE_EXECUTE, processStartAddress, processStopAddress);
  auto succ = false;
  for (auto addr : addr2)
  {
    HookParam hp;
    hp.address = addr + 2;
    hp.offset = regoffset(esi);
    hp.type = CODEC_UTF8 | USING_STRING | NO_CONTEXT;
    hp.lineSeparator = L"\\n";
    ConsoleOutput("utawarerumono %p", addr);
    succ |= NewHook(hp, "utawarerumono");
  }
  return succ;
}

bool utawarerumono::attach_function()
{
  bool b1 = utawarerumonoh();
  bool b2 = utawarerumonoh2();
  return b1 || b2;
}