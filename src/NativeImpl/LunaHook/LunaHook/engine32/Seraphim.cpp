#include "Seraphim.h"

bool Seraphim::attach_function()
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