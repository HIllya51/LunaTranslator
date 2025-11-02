#include "Interheart.h"

bool Interheart::attach_function()
{
  // 人妻スイミング倶楽部
  // https://vndb.org/v18049
  const BYTE bytes[] = {
      0x50,
      0x8d, 0x4d, XX,
      // here
      0xe8, XX4,
      0x68, XX4, // push    offset asc_956B20               ; "$L"
      0x8d, 0x4d, XX,
      0xe8};
  bool ok = false;
  for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress))
  {
    auto asc_956B20_addr_addr = addr + 1 + 3 + 5 + 1;
    auto asc_956B20_addr = *(int *)asc_956B20_addr_addr;
    char *asc_956B20 = (char *)asc_956B20_addr;
    if (asc_956B20[0] == '$' && asc_956B20[1] == 'L')
    {
      HookParam hp;
      hp.address = addr + 1 + 3;
      hp.offset = regoffset(edx);
      hp.type = USING_STRING | NO_CONTEXT;
      ok |= NewHook(hp, "Interheart");
    }
  }

  return ok;
}