#include "CMVS.h"
namespace
{
  bool EMbed()
  {
    // 有多个，但是只有最后一个是有效的
    const uint8_t bytes[] = {
        0xB8, 0x42, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX,
        0xB8, 0x76, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX,
        0xB8, 0x78, 0x81, 0x00, 0x00,
        0x66, XX2, 0x74, XX};
    bool res = false;
    auto addr = processStartAddress;

    std::vector<uintptr_t> already;

    while (addr)
    {
      addr = MemDbg::findBytes(bytes, sizeof(bytes), addr + 1, processStopAddress);
      if (!addr)
        continue;
      auto f = MemDbg::findEnclosingAlignedFunction(addr);
      if (f == 0)
        continue;
      if (std::find(already.begin(), already.end(), f) != already.end())
        continue;
      already.push_back(f);
    }
    if (already.size())
    {
      HookParam hp;
      hp.address = already.back();
      hp.offset = regoffset(rdx);

      hp.type = EMBED_ABLE | USING_STRING | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      res |= NewHook(hp, "EmbedCMVS");
    }
    return res;
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