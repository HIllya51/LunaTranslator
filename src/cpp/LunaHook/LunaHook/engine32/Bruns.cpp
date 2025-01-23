#include "Bruns.h"

bool InsertBrunsHook()
{
  bool success = false;
  if (Util::CheckFile(L"libscr.dll"))
  {
    HookParam hp;
    hp.offset = stackoffset(1);
    hp.type = CODEC_UTF16;
    //?push_back@?$basic_string@GU?$char_traits@G@std@@V?$allocator@G@2@@std@@QAEXG@Z
    if (Util::CheckFile(L"msvcp90.dll"))
      hp.address = (DWORD)GetProcAddress(GetModuleHandleW(L"msvcp90.dll"), "?push_back@?$basic_string@GU?$char_traits@G@std@@V?$allocator@G@2@@std@@QAEXG@Z");
    else if (Util::CheckFile(L"msvcp80.dll"))
      hp.address = (DWORD)GetProcAddress(GetModuleHandleW(L"msvcp80.dll"), "?push_back@?$basic_string@GU?$char_traits@G@std@@V?$allocator@G@2@@std@@QAEXG@Z");
    else if (Util::CheckFile(L"msvcp100.dll")) // jichi 8/17/2013: MSVCRT 10.0 and 11.0
      hp.address = (DWORD)GetProcAddress(GetModuleHandleW(L"msvcp100.dll"), "?push_back@?$basic_string@GU?$char_traits@G@std@@V?$allocator@G@2@@std@@QAEXG@Z");
    else if (Util::CheckFile(L"msvcp110.dll"))
      hp.address = (DWORD)GetProcAddress(GetModuleHandleW(L"msvcp110.dll"), "?push_back@?$basic_string@GU?$char_traits@G@std@@V?$allocator@G@2@@std@@QAEXG@Z");
    if (hp.address)
    {
      ConsoleOutput("INSERT Brus#1");
      success |= NewHook(hp, "Bruns");
    }
  }
  // else
  //  jichi 12/21/2013: Keep both bruns hooks
  //  The first one does not work for games like 「オーク・キングダマモン娘繁殖�豚人王～�anymore.
  {
    union
    {
      DWORD i;
      DWORD *id;
      WORD *iw;
      BYTE *ib;
    };
    DWORD k = processStopAddress - 4;
    for (i = processStartAddress + 0x1000; i < k; i++)
    {
      if (*id != 0xff) // cmp reg,0xff
        continue;
      i += 4;
      if (*iw != 0x8f0f)
        continue; // jg
      i += 2;
      i += *id + 4;
      for (DWORD j = i + 0x40; i < j; i++)
      {
        if (*ib != 0xe8)
          continue;
        i++;
        DWORD t = i + 4 + *id;
        if (t > processStartAddress && t < processStopAddress)
        {
          i = t;
          for (j = i + 0x80; i < j; i++)
          {
            if (*ib != 0xe8)
              continue;
            i++;
            t = i + 4 + *id;
            if (t > processStartAddress && t < processStopAddress)
            {

              HookParam hp;
              hp.address = t;
              hp.offset = stackoffset(1);
              hp.type = CODEC_UTF16 | DATA_INDIRECT;
              ConsoleOutput("INSERT Brus#2");

              return NewHook(hp, "Bruns2");
            }
          }
          k = i; // Terminate outer loop.
          break; // Terminate inner loop.
        }
      }
    }
  }
  // ConsoleOutput("Unknown Bruns engine.");
  ConsoleOutput("Brus: failed");
  return success;
}

bool Bruns::attach_function()
{

  return InsertBrunsHook();
}