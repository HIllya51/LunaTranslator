#include "Palette.h"

bool Palette::attach_function()
{

  BYTE sig2[] = {
      // さくらシュトラッセ
      // さくらんぼシュトラッセ
      // MERI+DIA～マリアディアナ～
      0x8b, XX,
      0x8b, XX, 0x14,
      0x03, XX,
      0x3b, XX,
      0x76, XX,
      0x83, XX, 0x10,
      0x72, XX,
      0x8b, XX,
      0x8b, XX, 0x24, 0x14,
      XX,
      0x2b, XX,
      XX,
      XX,
      0x8b, XX,
      0xe8, XX4,
      XX,
      XX,
      XX,
      0xC2, 0x08, 0x00};
  auto m = GetModuleHandle(L"system.dll");
  ULONG addr = 0;
  if (m)
  {
    // もしも明日が晴れならば
    // えむぴぃ
    auto [minAddress, maxAddress] = Util::QueryModuleLimits(m);
    addr = MemDbg::findBytes(sig2, sizeof(sig2), minAddress, maxAddress);
  }
  else
  {
    addr = MemDbg::findBytes(sig2, sizeof(sig2), processStartAddress, processStopAddress);
  }
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = all_ascii_Filter;
  ConsoleOutput("Please adjust the text display speed to maximum to remove duplicates");
  return NewHook(hp, "Palette");
}