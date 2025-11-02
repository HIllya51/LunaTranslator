#include "AGE_System.h"
namespace
{

  DWORD findx()
  {
    // 已破解
    auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, true, 0x1d); // mov     ebx, ds:GetGlyphOutlineA
    if (addr)
      return addr;
    // 未破解
    // v8 = _mbsnextc(String);
    BYTE sig[] = {
        0x8b, 0x4c, 0x24, 0x04,
        0x33, 0xd2,
        0x0f, 0xb6, 0x01,
        0xf6, 0x80, XX4, 0x04,
        0x74, 0x06,
        0xc1, 0xe0, 0x08,
        0x8b, 0xd0,
        0x41,
        0x0f, 0xb6, 0x01,
        0x03, 0xc2,
        0xc3};
    addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    auto addr2 = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (addr2.size() != 2)
      return 0;
    return addr2[1];
  }
}
bool AGE_System::attach_function()
{
  //(18禁ゲーム) [170331] [ルネ] ようこそ！ スケベエルフの森へ パッケージ版
  auto addr = findx();
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  auto addr2 = findxref_reverse_checkcallop(addr, addr - 0x1000, addr + 0x1000, 0xe8);
  if (addr2.size() != 1)
    return false;

  auto addr21 = MemDbg::findEnclosingAlignedFunction(addr2[0]);
  if (!addr21)
    return false;

  HookParam hp;
  hp.address = addr21;
  hp.offset = stackoffset(3);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | EMBED_AFTER_NEW;
  hp.embed_hook_font = F_GetGlyphOutlineA;
  return NewHook(hp, "AGE_System");
}