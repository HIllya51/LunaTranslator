#include "GSX.h"

namespace
{

  bool GSX1()
  {
    // https://vndb.org/v7585
    // PersonA ～オペラ座の怪人～ 体验版
    // http://www.mirai-soft.com/products/persona/download.html
    // https://dlsoft.dmm.co.jp/detail/stone_0015/
    ULONG addr = MemDbg::findCallerAddress((ULONG)::GetCharWidth32W, 0xec8b55, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_UTF16 | DATA_INDIRECT;
    hp.offset = stackoffset(4);
    return NewHook(hp, "GSX");
  }
  bool GSX2()
  {
    // https://vndb.org/v1930
    // 星の王女 体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0016/
    // https://vndb.org/v1931
    // 星の王女2 体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0017/
    // https://vndb.org/v2989
    // ツンデレ★Ｓ乙女 ―sweet sweet sweet―  体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0027/
    // https://vndb.org/v1952
    // 星の王女 ～宇宙意識に目覚めた義経～ 体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0023/
    // https://vndb.org/v1400
    // 仁義なき乙女 恋恋三昧 体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0032/
    // https://vndb.org/v856
    // 仁義なき乙女 体验版
    // https://dlsoft.dmm.co.jp/detail/stone_0031/
    ULONG addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, false, XX);
    if (!addr)
      addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
    if (!addr)
      return false;
    auto addr1 = findfuncstart(addr);
    auto addr2 = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr1)
      addr = addr1;
    else
      addr = addr2;
    if (!addr)
      return false;
    auto xrefs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (xrefs.size() != 2)
      return false;
    addr = xrefs[1];
    addr1 = findfuncstart(addr, 0x180);
    addr2 = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr1)
      addr = addr1;
    else
      addr = addr2;
    if (!addr)
      return false;
    ConsoleOutput("%p", addr);
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      WORD d;
      if (IsBadReadPtr((VOID *)context->stack[3], 4))
        d = *(WORD *)context->stack[4];
      else
        d = *(WORD *)context->stack[3];
      buffer->from_t(d);
    };
    return NewHook(hp, "GSX");
  }

}
bool GSX::attach_function()
{
  return GSX1() || GSX2();
}