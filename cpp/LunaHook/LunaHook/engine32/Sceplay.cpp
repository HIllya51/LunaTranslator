#include "Sceplay.h"
// https://vndb.org/v10190
// 想い出の彼方

bool Sceplay::attach_function()
{
  PcHooks::hookGDIFunctions();
  trigger_fun = [](LPVOID addr1, hook_context *context)
  {
    if (addr1 != GetGlyphOutlineA)
      return false;
    auto addr = MemDbg::findEnclosingAlignedFunction((DWORD)context->retaddr);
    ConsoleOutput("%p", addr);
    if (!addr)
      return true;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_ANSI_BE;
    hp.offset = stackoffset(6);
    NewHook(hp, "Sceplay");
    return true;
  };

  return true;
}