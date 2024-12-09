#include "Stronger.h"
namespace
{
  // https://vndb.org/v1334
  // Pygmalion ~The Dark Romance~
  bool h1()
  {
    auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress, false, 0x3d); // mov     edi, ds:GetGlyphOutlineA
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    auto addrs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (addrs.size() != 1)
      return false;
    addr = addrs[0];
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = DATA_INDIRECT | USING_CHAR;
    return NewHook(hp, "Stronger");
  }
}
bool Stronger::attach_function()
{
  return h1();
}