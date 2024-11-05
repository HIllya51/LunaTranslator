#include"MBLMED.h"

// jichi 3/19/2014: Insert both hooks
//void InsertLuneHook()
bool InsertMBLHook()
{
  enum : DWORD { fun = 0xec8b55 }; // jichi 10/20/2014: mov ebp,esp, sub esp,*
  bool ret = false;
  if (DWORD c = Util::FindCallOrJmpAbs((DWORD)::ExtTextOutA, processStopAddress - processStartAddress, processStartAddress, true))
    if (DWORD addr = Util::FindCallAndEntryRel(c, processStopAddress - processStartAddress, processStartAddress, fun)) {
      HookParam hp;
      hp.address = addr;
      hp.offset=get_stack(1);
      hp.type = USING_STRING;
      ConsoleOutput("INSERT MBL-Furigana");
      ret|=NewHook(hp, "MBL-Furigana");
    }
  if (DWORD c = Util::FindCallOrJmpAbs((DWORD)::GetGlyphOutlineA, processStopAddress - processStartAddress, processStartAddress, true))
    if (DWORD addr = Util::FindCallAndEntryRel(c, processStopAddress - processStartAddress, processStartAddress, fun)) {
      HookParam hp;
      hp.address = addr;
      hp.offset=get_stack(1);
      hp.split = get_reg(regs::esp);
      hp.type = CODEC_ANSI_BE|USING_SPLIT;
      ConsoleOutput("INSERT MBL");
      ret|=NewHook(hp, "MBL");
    }
  if (!ret)
    ConsoleOutput("MBL: failed");
  return ret;
}

bool InsertMEDHook()
{
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
    if (*(DWORD *)i == 0x8175) //cmp *, 8175
      for (DWORD j = i, k = i + 0x100; j < k; j++)
        if (*(BYTE *)j == 0xe8) {
          DWORD t = j + 5 + *(DWORD *)(j + 1);
          if (t > processStartAddress && t < processStopAddress) {
            HookParam hp;
            hp.address = t;
            hp.offset=get_reg(regs::eax);
            hp.type = CODEC_ANSI_BE;
            ConsoleOutput("INSERT MED");
            return NewHook(hp, "MED");
            //RegisterEngineType(ENGINE_MED);
          }
        }

  //ConsoleOutput("Unknown MED engine.");
  ConsoleOutput("MED: failed");
  return false;
}

bool MBLMED::attach_function() {
    
    bool b1=Util::CheckFile(L"*.mbl") &&InsertMBLHook();
    bool b2=Util::CheckFile(L"*.med") &&InsertMEDHook();
    return b1||b2;
} 