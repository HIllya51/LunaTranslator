#include "MBLMED.h"

// jichi 3/19/2014: Insert both hooks
// void InsertLuneHook()
bool InsertMBLHook()
{
  enum : DWORD
  {
    fun = 0xec8b55
  }; // jichi 10/20/2014: mov ebp,esp, sub esp,*
  bool ret = false;
  if (DWORD c = Util::FindCallOrJmpAbs((DWORD)::ExtTextOutA, processStopAddress - processStartAddress, processStartAddress, true))
    if (DWORD addr = Util::FindCallAndEntryRel(c, processStopAddress - processStartAddress, processStartAddress, fun))
    {
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING;
      ret |= NewHook(hp, "MBL-Furigana");
    }
  if (DWORD c = Util::FindCallOrJmpAbs((DWORD)::GetGlyphOutlineA, processStopAddress - processStartAddress, processStartAddress, true))
    if (DWORD addr = Util::FindCallAndEntryRel(c, processStopAddress - processStartAddress, processStartAddress, fun))
    {
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.split = regoffset(esp);
      hp.type = CODEC_ANSI_BE | USING_SPLIT;
      ret |= NewHook(hp, "MBL");
    }
  if (!ret)
    ConsoleOutput("MBL: failed");
  return ret;
}
namespace
{
  bool h1()
  {
    // https://vndb.org/v14141
    // おねがい助けて!! 2 ～注がれ続ける精液～
    char sig[] = "\x81\x90\x82\x4f\x00\x81\x90\x82\x50\x00\x81\x90\x82\x51\x00\x81\x90\x82\x52";
    auto asc_76BAAE = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!asc_76BAAE)
      return false;
    BYTE bytes[] = {XX, XX4};
    *(int *)(bytes + 1) = asc_76BAAE; // mov     edx, offset asc_76BAAE
    auto push = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!push)
      return false;
    auto addr = findfuncstart(push);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING;
    return NewHook(hp, "MED");
  }
}
bool InsertMEDHook()
{
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
    if (*(DWORD *)i == 0x8175) // cmp *, 8175
      for (DWORD j = i, k = i + 0x100; j < k; j++)
        if (*(BYTE *)j == 0xe8)
        {
          DWORD t = j + 5 + *(DWORD *)(j + 1);
          if (t > processStartAddress && t < processStopAddress)
          {
            HookParam hp;
            hp.address = t;
            hp.offset = regoffset(eax);
            hp.type = CODEC_ANSI_BE;
            return NewHook(hp, "MED");
            // RegisterEngineType(ENGINE_MED);
          }
        }

  // ConsoleOutput("Unknown MED engine.");
  ConsoleOutput("MED: failed");
  return false;
}

bool MBLMED::attach_function()
{

  bool b1 = Util::CheckFile(L"*.mbl") && InsertMBLHook();
  bool b2 = Util::CheckFile(L"*.med") && (h1() || InsertMEDHook());
  return b1 || b2;
}