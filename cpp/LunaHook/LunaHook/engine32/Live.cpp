#include "Live.h"
bool InsertLiveDynamicHook(LPVOID addr, DWORD frame, DWORD stack)
{
  if (addr != ::GetGlyphOutlineA || !frame)
    return false;
  DWORD k = *(DWORD *)frame;
  k = *(DWORD *)(k + 4);
  if (*(BYTE *)(k - 5) != 0xe8)
    k = *(DWORD *)(frame + 4);
  DWORD j = k + *(DWORD *)(k - 4);
  if (j > processStartAddress && j < processStopAddress)
  {
    HookParam hp;
    hp.address = j;
    hp.offset = regoffset(edx);
    hp.type = CODEC_ANSI_BE;
    ConsoleOutput("INSERT DynamicLive");
    return NewHook(hp, "Live");
    // RegisterEngineType(ENGINE_LIVE);
  }
  ConsoleOutput("DynamicLive: failed");
  return true; // jichi 12/25/2013: return true
}
// void InsertLiveHook()
//{
//   ConsoleOutput("Probably Live. Wait for text.");
//   trigger_fun=InsertLiveDynamicHook;
//   SwitchTrigger(true);
// }
bool InsertLiveHook()
{
  const BYTE ins[] = {0x64, 0x89, 0x20, 0x8b, 0x45, 0x0c, 0x50};
  ULONG addr = MemDbg::findBytes(ins, sizeof(ins), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("Live: pattern not found");
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = CODEC_ANSI_BE;
  ConsoleOutput("INSERT Live");
  return NewHook(hp, "Live");
  // RegisterEngineType(ENGINE_LIVE);
  // else ConsoleOutput("Unknown Live engine");
}

bool Live::attach_function()
{

  return InsertLiveHook();
}