#include "Seraphim.h"

bool Seraphimattach_function2()
{
  // https://vndb.org/v3212
  // School Captain 2 会王をねらえ!
  PcHooks::hookGDIFunctions(GetGlyphOutlineW);
  trigger_fun = [](LPVOID addr1, hook_context *context)
  {
    if (addr1 != GetGlyphOutlineW)
      return false;
    auto addr = context->retaddr;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_UTF16;
    hp.offset = stackoffset(4);
    NewHook(hp, "Seraphim");
    return true;
  };
  return findiatcallormov((DWORD)GetGlyphOutlineW, processStartAddress, processStartAddress, processStopAddress);
}

bool Seraphimattach_function1()
{
  // Laughter Land
  auto addr = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sig[] = {0x81, 0xEC, 0xB8, 0x00, 0x00, 0x00};
  HookParam hp;
  hp.address = reverseFindBytes(sig, sizeof(sig), addr - 0x400, addr);
  hp.type = USING_STRING;
  hp.offset = stackoffset(7);
  return NewHook(hp, "Seraphim2");
}

bool Seraphim::attach_function()
{
  return Seraphimattach_function2() || Seraphimattach_function1();
}