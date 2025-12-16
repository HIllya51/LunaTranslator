#include "lucasystem.h"

void IG64filter(TextBuffer *buffer, HookParam *)
{

  std::wstring str = buffer->strW();
  str = re::sub(str, L"\\$\\[(.*?)\\$/(.*?)\\$\\]", L"$1");

  buffer->from(re::sub(str, L"@[^@]*@"));
};
bool InsertIG64Hook2()
{
  const BYTE BYTES[] = {
      0xBA, 0x3F, 0xFF, 0x00, 0x00,
      XX, 0x8B, XX,
      0xE8, XX2, XX, 0x00};
  bool ok = false;
  auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE, processStartAddress, processStopAddress);
  std::set<uintptr_t> collect;
  for (auto addr : addrs)
  {
    BYTE check = *(BYTE *)(addr + 5 + 3 + 3);
    if (check != 0x00 &&
        check != 0x01 // Summer Pockets REFLECTION BLUE Ver1.3.2.1
    )
      continue;
    const BYTE aligned[] = {0xCC, 0xCC};
    auto addr1 = reverseFindBytes(aligned, sizeof(aligned), addr - 0x10000, addr);
    //[240830][1150510][Key] LUNARiA -Virtualized Moonchild- 多国語版 Chinese-English-Japanese DL版 (files)
    const BYTE sig2[] = {0x48, 0x89, XX, XX, XX, 0x55, 0x56, 0x57, 0x41, 0x54, 0x41, 0x55, 0x41, 0x56, 0x41, 0x57};
    auto addr2 = reverseFindBytes(sig2, sizeof(sig2), addr - 0x10000, addr);
    addr = max(addr1, addr2);
    if (!addr)
      continue;
    if (addr == addr1)
      addr += 2;
    collect.insert(addr);
  }
  for (auto addr : collect)
  {
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW; // 可以内嵌英文
    hp.filter_fun = IG64filter;
    hp.offset = regoffset(rdx); // rdx
    ok |= NewHook(hp, "LucaSystem");
  }
  return ok;
}
bool lucasystem::attach_function()
{
  return InsertIG64Hook2();
}
