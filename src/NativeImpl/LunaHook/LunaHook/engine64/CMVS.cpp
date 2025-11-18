#include "CMVS.h"
namespace
{
  uintptr_t getptr2()
  {
    // ハピメアFD RE.ver
    const uint8_t bytes[] = {
        0xB8, XX, 0x81, 0x00, 0x00};
    std::map<uintptr_t, int> count;
    auto addr = processStartAddress;
    while (addr)
    {
      addr = MemDbg::findBytes(bytes, sizeof(bytes), addr + 1, processStopAddress);
      if (!addr)
        continue;
      auto b = ((BYTE *)addr)[1];
      if (b != 0x4a && b != 0x45)
        continue;
      auto f = MemDbg::findEnclosingAlignedFunction(addr, 0x900);
      if (!f)
        continue;
      count[f] += 1;
    }
    auto max_it = std::max_element(count.begin(), count.end(),
                                   [](const auto &a, const auto &b)
                                   {
                                     return a.second < b.second;
                                   });

    if (max_it != count.end())
    {
      if (max_it->second == 2)
        return max_it->first;
    }
    return 0;
  }
  uintptr_t getptr()
  {
    // 有多个，但是只有最后一个是有效的
    const uint8_t bytes[] = {
        0xB8, 0x42, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX,
        0xB8, 0x76, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX,
        0xB8, 0x78, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX};
    auto addr = processStartAddress;
    std::vector<uintptr_t> already;

    while (addr)
    {
      addr = MemDbg::findBytes(bytes, sizeof(bytes), addr + 1, processStopAddress);
      if (!addr)
        continue;
      auto f = MemDbg::findEnclosingAlignedFunction(addr);
      if (!f)
        continue;
      if (std::find(already.begin(), already.end(), f) != already.end())
        continue;
      already.push_back(f);
    }
    if (already.size())
    {
      return already.back();
    }
    return 0;
  }
  bool EMbed()
  {
    auto addr = getptr();
    if (!addr)
      addr = getptr2();
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(rdx);
    hp.type = EMBED_ABLE | USING_STRING | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "EmbedCMVS");
  }

  bool CMVSh()
  {

    DWORD align = 0xCCCCCCCC;
    auto addr = MemDbg::findCallerAddress((uintptr_t)::GetGlyphOutlineA, align, processStartAddress, processStopAddress);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr + 4;
    hp.offset = regoffset(r8);
    hp.type = CODEC_ANSI_BE;

    return NewHook(hp, "CMVS");
  }
}
bool CMVS::attach_function()
{
  bool b1 = CMVSh();
  bool b2 = EMbed();
  return b1 || b2;
}