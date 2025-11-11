#include "Atelier.h"
/********************************************************************************************
AtelierKaguya hook:
  Game folder contains message.dat. Used by AtelierKaguya games.
  Usually has font caching issue with TextOutA.
  Game engine uses EBP to set up stack frame so we can easily trace back.
  Keep step out until it's in main game module. We notice that either register or
  stack contains string pointer before call instruction. But it's not quite stable.
  In-depth analysis of the called function indicates that there's a loop traverses
  the string one character by one. We can set a hook there.
  This search process is too complex so I just make use of some characteristic
  instruction(add esi,0x40) to locate the right point.
********************************************************************************************/
bool InsertAtelierHook()
{
  PcHooks::hookOtherPcFunctions(); // lstrlenA gives good hook too
  // SafeFillRange(processName, &base, &size);
  // size=size-base;
  // DWORD sig = 0x40c683; // add esi,0x40
  // i=processStartAddress+SearchPattern(processStartAddress,processStopAddress-processStartAddress,&sig,3);
  DWORD i;
  for (i = processStartAddress; i < processStopAddress - 4; i++)
  {
    DWORD sig = *(DWORD *)i & 0xffffff;
    if (0x40c683 == sig) // add esi,0x40
      break;
  }
  if (i < processStopAddress - 4)
    for (DWORD j = i - 0x200; i > j; i--)
      if (*(DWORD *)i == 0xff6acccc)
      { // find the function entry
        HookParam hp;
        hp.address = i + 2;
        hp.offset = stackoffset(2);
        hp.split = regoffset(esp);
        hp.type = USING_SPLIT;
        return NewHook(hp, "Atelier KAGUYA");
      }

  return false;
}

bool InsertAtelierKaguya2Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v22713
   * https://vndb.org/v31685
   * https://vndb.org/v37081
   */
  const BYTE bytes[] = {
      0x51,             // push ecx        << hook here
      0x50,             // push eax
      0xE8, XX4,        // call Start.exe+114307
      0x83, 0xC4, 0x08, // add esp,08
      0x85, 0xC0,       // test eax,eax
      0x78, 0xA1        // js Start.exe+48947
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Atelier KAGUYA2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING | EMBED_AFTER_OVERWRITE | EMBED_ABLE | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_TextOutA;
  hp.filter_fun = NewLineCharToSpaceA;
  ConsoleOutput("INSERT Atelier KAGUYA2");

  return NewHook(hp, "Atelier KAGUYA2");
}

bool InsertAtelierKaguya3Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v10082
   */
  const BYTE bytes[] = {
      0x55,                              // push ebp       << hook here
      0x8B, 0xEC,                        // mov ebp,esp
      0x6A, 0xFF,                        // push -01
      0x68, 0x80, 0xB9, 0x4D, 0x00,      // push Start.exe+DB980
      0x64, 0xA1, XX4,                   // mov eax,fs:[00000000]
      0x50,                              // push eax
      0x51,                              // push ecx
      0x81, 0xEC, 0xAC, 0x00, 0x00, 0x00 // sub esp,000000AC
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Atelier KAGUYA3: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = NewLineCharToSpaceA;
  ConsoleOutput("INSERT Atelier KAGUYA3");

  return NewHook(hp, "Atelier KAGUYA3");
}

bool InsertAtelierKaguya4Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v14705
   */
  const BYTE bytes[] = {
      0xE8, 0x90, 0xA8, 0xFF, 0xFF, // call Start.exe+18380
      0x89, 0x45, 0xF8,             // mov [ebp-08],eax
      0x8B, 0x4D, 0x10,             // mov ecx,[ebp+10]
      0x51,                         // push ecx
      0x8B, 0x55, 0x0C,             // mov edx,[ebp+0C]
      0x52,                         // push edx
      0x8B, 0x45, 0x08,             // mov eax,[ebp+08]
      0x50                          // push eax       << hook here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 1
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Atelier KAGUYA4: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = NewLineCharToSpaceA;
  ConsoleOutput("INSERT Atelier KAGUYA4");

  return NewHook(hp, "Atelier KAGUYA4");
}

bool InsertAtelierKaguya5Hook()
{

  /*
   * Sample games:
   * https://vndb.org/v11224
   */
  const BYTE bytes[] = {
      0xC2,
      0x04,
      0x00, // ret 0004
      0x55, // push ebp       << hook here
      0x8B,
      0xEC, // mov ebp,esp
      0x6A,
      0xFF, // push -01
      0x68,
      XX4, // push Start.exe+DA680
      0x64,
      0xA1,
      0x00,
      0x00,
      0x00,
      0x00, // mov eax,fs:[00000000]
      0x50, // push eax
      0x51, // push ecx
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Atelier KAGUYA5: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + 3;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING;
  hp.filter_fun = NewLineCharToSpaceA;
  ConsoleOutput("INSERT Atelier KAGUYA5");

  return NewHook(hp, "Atelier KAGUYA5");
}
bool InsertAtelierKaguyaX()
{
  // エロティ課 誘惑研修はじまるよ～ しごいちゃうから覚悟なさい!
  const BYTE bytes[] = {
      0x3D, 0xF0, 0x41, 0x00, 0x00,
      0x75};

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  addr = findfuncstart(addr, 0x1000);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;

  return NewHook(hp, "Atelier KAGUYA3");
}
bool Atelier::attach_function()
{

  return InsertAtelierHook() || InsertAtelierKaguya2Hook() || InsertAtelierKaguyaX() || InsertAtelierKaguya3Hook() || InsertAtelierKaguya4Hook() || InsertAtelierKaguya5Hook();
}

bool Atelier2attach_function()
{
  // https://vndb.org/v304
  // ダンジョンクルセイダーズ～TALES OF DEMON EATER～
  const BYTE bytes[] = {
      0x83, 0xFE, 0x34,
      0xF6, XX,
      0x88, XX, 0x24, 0x29,
      0x7D};

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + sizeof(bytes) - 1;
  hp.offset = stackoffset(10);
  hp.type = USING_CHAR | NO_CONTEXT;
  // NO_CONTEXT:
  // 牝奴隷 ～犯された放課後～
  // https://vndb.org/v4351会把每行单独分开。
  return NewHook(hp, "Atelier KAGUYA3");
}

bool Atelier2attach_function2()
{
  auto addr = findiatcallormov((ULONG)TextOutA, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  auto faddr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!faddr)
    return false;
  HookParam hp;
  hp.address = faddr;
  hp.offset = stackoffset(3);
  hp.type = USING_STRING; // https://vndb.org/v13691  // 肉牝R30 ～肉欲に堕ちた牝たち～
  if (addr - faddr > 0x40)
    hp.type |= DATA_INDIRECT; // https://vndb.org/v7264  // 禁断の病棟 特殊精神科医 遊佐惣介の診察記録
  return NewHook(hp, "Atelier KAGUYA2");
}
static bool h3()
{
  // 最終痴漢電車DVDエディション

  const BYTE bytes[] = {
      0xa1, XX4,
      0x53,
      0x8b, 0x5c, 0x24, 0x08,
      0x56,
      0x8b, 0xf1,
      0x57,
      0x85, 0xdb,
      0x89, 0x06,
      0x74, XX,
      0x8b, 0xc3,
      0xc1, 0xe8, 0x10,
      0x66, 0x85, 0xc0,
      0x75, XX,
      0x0f, 0xb7, 0xc3,
      0x50,
      0xe8, XX4, // CString::LoadStringA
      0xeb,XX,
      0x53,
      0xff,0x15,XX4,//lstrlenA
  };

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.offset = stackoffset(1);
  return NewHook(hp, "Atelier2_1");
}
bool Atelier2::attach_function()
{
  return h3() || Atelier2attach_function() || Atelier2attach_function2();
}