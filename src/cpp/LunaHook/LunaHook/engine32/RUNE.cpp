#include "RUNE.h"

bool RUNE1()
{
  const BYTE bytes[] = {
      // 恋する妹はせつなくてお兄ちゃんを想うとすぐＨしちゃうの  （Ver.1.02）
      // Ricotte～アルペンブルの歌姫～
      // 初恋
      // 思春期
      // Fifth
      // unsigned __int8 *__cdecl _mbsinc(const unsigned __int8 *Ptr)
      0x8B, 0x44, 0x24, 0x04,
      0x0F, 0xB6, 0x08,
      0x8A, 0x89, XX4,
      0x80, 0xE1, 0x04,
      0x40,
      0x84, 0xC9,
      0x74, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "RUNE");
}
bool RUNE2()
{
  // ANGEL CORE
  auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sig1[] = {0x81, 0xe1, 0x01, 0x00, 0x00, 0x80, XX2, 0x49, 0x83, 0xc9, 0xfe, 0x41};
  auto _ = MemDbg::findBytes(sig1, sizeof(sig1), addr, addr + 0x100);
  if (_ == 0)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "RUNE");
}
bool RUNE3()
{
  // 雪のち、ふるるっ！～ところにより、恋もよう～
  const BYTE bytes[] = {
      0x6a, 0x05, 0x6a, 0x01};
  for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE_READWRITE))
  {
    auto start = MemDbg::findEnclosingAlignedFunction(addr);
    if (start == 0)
      continue;
    BYTE sig1[] = {0x6a, 0x00, 0x6a, 0x01, 0x50};
    BYTE sig2[] = {0x6a, 0x34, 0xe8};
    BYTE sig3[] = {0xc1, 0xe2, 0x10, 0x0b, 0xc2};
    bool ok = true;
    for (auto p : std::vector<std::pair<BYTE *, int>>{{sig1, sizeof(sig1)}, {sig2, sizeof(sig2)}, {sig3, sizeof(sig3)}})
    {
      auto _ = MemDbg::findBytes(p.first, p.second, start, addr);

      if (_ == 0)
        ok = ok & false;
    }

    if (ok)
    {
      HookParam hp;
      hp.address = start;
      hp.offset = stackoffset(1);
      hp.type = CODEC_ANSI_BE;
      return NewHook(hp, "RUNE");
    }
  }

  return false;
}
bool RUNE::attach_function()
{
  return RUNE1() || RUNE2() || RUNE3();
}
