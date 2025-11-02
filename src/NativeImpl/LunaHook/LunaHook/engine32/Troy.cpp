#include "Troy.h"

bool Troy::attach_function()
{
  // Reverse desire～裏返る欲望～
  auto dll = GetModuleHandleW(L"sfe.dll");
  if (dll == 0)
    return false;
  auto [minaddr, maxaddr] = Util::QueryModuleLimits(dll);
  BYTE bytes[] = {
      0x3C, 0x82,
      XX2,
      0x80, 0xFB, 0x9F,
      XX2,
      0x80, 0xFB, 0xF1};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minaddr, maxaddr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "Troy");
}