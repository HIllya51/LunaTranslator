#include "Ciel.h"

bool InsertCielHook()
{

  /*
   * Sample games:
   * https://vndb.org/r26480
   * https://vndb.org/v1648
   * https://vndb.org/v10392
   */
  const BYTE bytes[] = {
      0x50,                       // push eax               << hook here
      0xE8, XX4,                  // call FaultA.exe+81032
      0x83, 0xC4, 0x04,           // add esp,04
      0x85, 0xC0,                 // test eax,eax
      0x74, 0x32,                 // je FaultA.exe+41FA6
      0x81, 0x7C, 0x24, 0x10, XX4 // cmp [esp+10],000003FE
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edi);
  hp.type = DATA_INDIRECT | NO_CONTEXT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    if ((buffer->size) == 1)
      buffer->clear();
  };

  return NewHook(hp, "Ciel");
}
bool Ciel::attach_function()
{

  return InsertCielHook();
}