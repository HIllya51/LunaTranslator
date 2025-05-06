#include "H_do_C.h"
// https://vndb.org/v565
// 夢見師
namespace
{
  bool nomal()
  {
    auto call = findiatcallormov((ULONG)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, false, XX);
    if (!call)
      return false;
    BYTE sig[] = {0xB8, 0x68, 0x24, 0x00, 0x00};
    auto addr = reverseFindBytes(sig, sizeof(sig), call - 0x100, call);
    if (!addr)
      return false;
    auto as = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (as.size() != 2)
      return false;
    auto as0 = MemDbg::findEnclosingAlignedFunction(as[0]);
    auto as1 = MemDbg::findEnclosingAlignedFunction(as[1]);
    if (as0 != as1)
      return false;
    if (!as0)
      return false;
    HookParam hp;
    hp.address = as0;
    hp.offset = stackoffset(2);
    hp.type = USING_CHAR | CODEC_ANSI_BE;
    return NewHook(hp, "H_do_C");
  }
  bool embed()
  {
    BYTE sig[] = {
        0x8a, 0x03,
        0x3c, 0x7c,
        0x0f, 0x84, XX4,
        0x3c, 0x80,
        0x72, 0x0b,
        0x83, 0xc6, 0x02,
        0x83, 0xc3, 0x02,
        0xe9, XX4,
        0x3c, 0x5c,
        0x0f, 0x85, XX4,
        0x8a, 0x43, 0x01,
        0x83, 0xc3, 0x01,
        0x83, 0xc6, 0x01,
        0x3c, 0x31};
    bool succ = false;
    for (auto addr : Util::SearchMemory(sig, sizeof(sig), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
      addr = MemDbg::findEnclosingAlignedFunction(addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = regoffset(ecx);
      hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      hp.lineSeparator = L"||";
      succ |= NewHook(hp, "H_do_C");
    }
    return succ;
  }
}
bool H_do_C::attach_function()
{
  return embed() | nomal();
}