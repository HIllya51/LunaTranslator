#include "Azurite.h"
bool Azurite::attach_function()
{
  bool succ = false;
  for (auto addr : findiatcallormov_all((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
  {
    auto faddr = findfuncstart(addr, 0x280);
    if (!faddr)
      continue;

    BYTE check[] = {0x3D, 0x5C, 0x6E, 0x00, 0x00}; //  cmp     eax, 6E5Ch
    if (!MemDbg::findBytes(check, sizeof(check), addr, faddr))
      continue;
    HookParam hp;
    hp.address = faddr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT | EMBED_AFTER_NEW;
    hp.embed_hook_font = F_TextOutA;
    hp.offset = stackoffset(1);
    succ |= NewHook(hp, "Azurite");
  }

  return succ;
}