#include "morning.h"

int mov_xl_exx(int reg)
{
  auto off = -1;
  reg = reg & 7;
  switch (reg)
  {
  case 3:
    off = regoffset(ebx);
    break;
  case 0:
    off = regoffset(eax);
    break;
  case 1:
    off = regoffset(ecx);
    break;
  case 2:
    off = regoffset(edx);
    break;
  case 6:
    off = regoffset(esi);
    break;
  case 7:
    off = regoffset(edi);
    break;
  }
  return off;
}

bool shiftjis81()
{
  // morning
  /*if (((unsigned __int8)*a7 < 0x81u || (unsigned __int8)*a7 > 0x9Fu)
    && ((unsigned __int8)*a7 < 0xE0u || (unsigned __int8)*a7 > 0xFCu))*/
  const BYTE bytes81[] = {
      0x8A, XX,
      0x81, XX, 0x81, 0x00, 0x00, 0x00};
  const BYTE bytes81eax[] = {
      0x8A, XX,
      XX, 0x81, 0x00, 0x00, 0x00};

  int idx = 0;
  auto succ = false;
  for (auto bs : {bytes81, bytes81eax})
  {
    for (auto addr : Util::SearchMemory(bs, idx ? 7 : 8, PAGE_EXECUTE, processStartAddress, processStopAddress))
    {

      int jumpxxop = *(((BYTE *)addr) + (idx ? 7 : 8));
      if (jumpxxop < 0x7c || jumpxxop > 0x7f)
        continue;
      auto off = mov_xl_exx(*(((BYTE *)addr) + 1));
      if (off != -1)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.offset = off;
      hp.type = USING_STRING | NO_CONTEXT;
      succ |= NewHook(hp, "shiftjis819fefc");
    }
    idx += 1;
  }

  return succ;
}

bool morning::attach_function()
{
  return shiftjis81();
}