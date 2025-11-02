#include "Overflow.h"

bool InsertSekaiProject1Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v1193
   */
  const BYTE bytes[] = {
      0xCC,                   // int 3
      0x83, 0xEC, 0x10,       // sub esp,10    << hook here
      0x8B, 0x44, 0x24, 0x14, // mov eax,[esp+14]
      0x53,                   // push ebx
      0x56,                   // push esi
      0x50,                   // push eax
      0x8B, 0xD9              // mov ebx,ecx
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("SekaiProject1: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = stackoffset(1);
  hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
  ConsoleOutput("INSERT SekaiProject1");
  return NewHook(hp, "SekaiProject1");
}

bool InsertSekaiProject2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/r21174
   */
  const BYTE bytes[] = {
      0xC7, 0x45, 0xDC, 0x00, 0x00, 0x00, 0x00, // mov [ebp-24],00000000        << hook here
      0xEB, 0x09,                               // jmp "SCHOOLDAYS HQ.exe"+4C821
      0x8B, 0x45, 0xDC,                         // mov eax,[ebp-24]
      0x83, 0xC0, 0x01,                         // add eax,01
      0x89, 0x45, 0xDC                          // mov [ebp-24],eax
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("SekaiProject2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(21);
  hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
  ConsoleOutput("INSERT SekaiProject2");
  return NewHook(hp, "SekaiProject2");
}

bool InsertSekaiProject3Hook()
{

  /*
   * Sample games:
   * https://vndb.org/r39989
   */
  const BYTE bytes[] = {
      0xCC,                   // int 3
      0x8B, 0x44, 0x24, 0x04, // mov eax,[esp+04]     << hook here
      0x83, 0xEC, 0x14,       // sub esp,14
      0x55,                   // push ebp
      0x56,                   // push esi
      0x57,                   // push edi
      0x8B, 0xF9              // mov edi,ecx
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("SekaiProject3: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = stackoffset(1);
  hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
  ConsoleOutput("INSERT SekaiProject3");
  return NewHook(hp, "SekaiProject3");
}

bool Overflow::attach_function()
{
  return InsertSekaiProject1Hook() || InsertSekaiProject2Hook() || InsertSekaiProject3Hook();
}
