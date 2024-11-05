#include "Sceplay.h"
// https://vndb.org/v10190
// 想い出の彼方

bool Sceplay::attach_function()
{
  trigger_fun = [](LPVOID addr1, hook_stack *stack)
  {
    if (addr1 != GetGlyphOutlineA)
      return false;
    auto addr = MemDbg::findEnclosingAlignedFunction((DWORD)stack->retaddr);
    ConsoleOutput("%p", addr);
    if (!addr)
      return true;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR | CODEC_ANSI_BE;
    hp.offset = get_stack(6);
    NewHook(hp, "Sceplay");
    return true;
  };

  return true;
}