#include "lucasystem.h"

bool IG64filter(void *data, size_t *size, HookParam *)
{

  auto text = reinterpret_cast<LPWSTR>(data);
  std::wstring str = std::wstring(text, *size / 2);
  std::wregex reg1(L"\\$\\[(.*?)\\$/(.*?)\\$\\]");
  std::wstring result1 = std::regex_replace(str, reg1, L"$1");

  std::wregex reg2(L"@[^@]*@");
  std::wstring result2 = std::regex_replace(result1, reg2, L"");
  write_string_overwrite(text, size, result2);
  return true;
};
bool InsertIG64Hook2()
{
  const BYTE BYTES[] = {
      0xBA, 0x3F, 0xFF, 0x00, 0x00,
      XX, 0x8B, XX,
      0xE8, XX2, 0x00, 0x00};
  bool ok = false;
  auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE, processStartAddress, processStopAddress);
  std::set<uintptr_t> collect;
  for (auto addr : addrs)
  {
    ConsoleOutput("%p", addr);
    const BYTE aligned[] = {0xCC, 0xCC};
    auto addr1 = reverseFindBytes(aligned, sizeof(aligned), addr - 0x10000, addr);
    //[240830][1150510][Key] LUNARiA -Virtualized Moonchild- 多国語版 Chinese-English-Japanese DL版 (files)
    const BYTE sig2[] = {0x48, 0x89, XX, XX, XX, 0x55, 0x56, 0x57, 0x41, 0x54, 0x41, 0x55, 0x41, 0x56, 0x41, 0x57};
    auto addr2 = reverseFindBytes(sig2, sizeof(sig2), addr - 0x10000, addr);
    ConsoleOutput("%p %p", addr1, addr2);
    addr = max(addr1, addr2);
    if (addr == 0)
      continue;
    if (addr == addr1)
      addr += 2;
    collect.insert(addr);
  }
  for (auto addr : collect)
  {
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE |  EMBED_AFTER_NEW; // 可以内嵌英文
    hp.filter_fun = IG64filter;
    hp.offset = get_reg(regs::rdx); // rdx
    ok |= NewHook(hp, "IG642");
  }
  return ok;
}
bool lucasystem::attach_function()
{
  return InsertIG64Hook2();
}
