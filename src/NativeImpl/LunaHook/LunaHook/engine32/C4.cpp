#include "C4.h"

/********************************************************************************************
C4 hook: (Contributed by Stomp)
  Game folder contains C4.EXE or XEX.EXE.
********************************************************************************************/
bool InsertC4Hook()
{
  const BYTE bytes[] = {0x8a, 0x10, 0x40, 0x80, 0xfa, 0x5f, 0x88, 0x15};
  // enum { addr_offset = 0 };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("C4: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = DATA_INDIRECT | NO_CONTEXT;
  ConsoleOutput("INSERT C4");

  // RegisterEngineType(ENGINE_C4);
  return NewHook(hp, "C4");
}

bool C4::attach_function()
{

  return InsertC4Hook();
}