#include "Candy.h"

/********************************************************************************************
CandySoft hook:
  Game folder contains many *.fpk. Engine name is SystemC.
  I haven't seen this engine in other company/brand.

  AGTH /X3 will hook lstrlenA. One thread is the exactly result we want.
  But the function call is difficult to located programmatically.
  I find a equivalent points which is more easy to search.
  The script processing function needs to find 0x5B'[',
  so there should a instruction like cmp reg,5B
  Find this position and navigate to function entry.
  The first parameter is the string pointer.
  This approach works fine with game later than つよきす２学�

  But the original つよき�is quite different. I handle this case separately.

********************************************************************************************/
namespace
{
  // https://vndb.org/v23666
  //(18禁ゲーム) [180928] [INTERHEART glossy] はらかつ！3 ～子作りビジネス廃業の危機！？～ (iso+mds+rr3)
  // https://vndb.org/v47957
  //[240222][1261652][DESSERT Soft] 二股野郎とパパ活姉妹 パッケージ版 (mdf+mds)
  // https://vndb.org/v20368
  //[170224] [Sweet HEART] アイドル★クリニック 恋の薬でHな処方 (iso+mds+rr3)
  void filter(TextBuffer *buffer, HookParam *)
  {
    StringFilter(buffer, TEXTANDLEN("$L"));
    StringFilter(buffer, TEXTANDLEN("$M"));
    StringFilter(buffer, TEXTANDLEN("$S"));
    StringFilterBetween(buffer, TEXTANDLEN("["), TEXTANDLEN("]"));
    StringFilterBetween(buffer, TEXTANDLEN("&"), TEXTANDLEN(";"));
    // else
    // {
    //   v18 = *v16++;
    //   switch ( v18 )
    //   {
    //     case '$':
    //       switch ( *v16 )
    //       {
    //         case 0:
    //           goto LABEL_44;
    //         case 76:
    //           v15 = 3;
    //           break;
    //         case 77:
    //           if ( v15 < 2 )
    //             v15 = 2;
    //           break;
    //         default:
    //           if ( *v16 == 83 && !v15 )
    //             v15 = 1;
    //           break;
    //       }
    //       break;
    //     case '[':
    //       for ( i = *v16; i; i = *++v16 )
    //       {
    //         if ( i == 93 )
    //           break;
    //       }
    //       break;
    //     case '&':
    //       for ( j = *v16; j; j = *++v16 )
    //       {
    //         if ( j == 59 )
    //           break;
    //       }
    //       break;
    //     default:
    //       goto LABEL_43;
    //   }
    //   ++v16;
    // }
  }
  uintptr_t hh()
  {
    // void __usercall sub_425580(char *a1@<edx>, int a2@<ecx>, int a3)
    BYTE bytes[] = {
        0x3c, 0x24,
        0x75, XX,
        0x80, 0x7e, 0x01, 0x00,
        0x74, XX,
        0x83, XX, 0x02,
        0x83, XX, 0x02};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    addr = findfuncstart(addr, 0x400);
    return addr;
  }
}

namespace
{ // unnamed Candy

  // jichi 8/23/2013: split into two different engines
  // if (_wcsicmp(processName, L"systemc.exe")==0)
  // Process name is "SystemC.exe"
  bool InsertCandyHook1()
  {
    for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
      if ((*(DWORD *)i & 0xffffff) == 0x24f980) // cmp cl,24
        for (DWORD j = i, k = i - 0x100; j > k; j--)
          if (*(DWORD *)j == 0xc0330a8a)
          { // mov cl,[edx]; xor eax,eax
            HookParam hp;
            hp.address = j;
            hp.offset = regoffset(edx);
            hp.type = USING_STRING;
            ConsoleOutput("INSERT SystemC#1");

            // RegisterEngineType(ENGINE_CANDY);
            return NewHook(hp, "SystemC");
          }
    ConsoleOutput("CandyHook1: failed");
    return false;
  }

  uintptr_t __InsertCandyHook2()
  {
    for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
      if (*(WORD *)i == 0x5b3c ||               // cmp al,0x5b
          (*(DWORD *)i & 0xfff8fc) == 0x5bf880) // cmp reg,0x5B
        for (DWORD j = i, k = i - 0x100; j > k; j--)
          if ((*(DWORD *)j & 0xffff) == 0x8b55)
          { // push ebp, mov ebp,esp, sub esp,*
            return j;
          }
    return 0;
  }
  // jichi 8/23/2013: Process name is NOT "SystemC.exe"
  bool InsertCandyHook2()
  {
    auto addr1 = hh(); // 新版本的candy，但是有时会和旧版在同一个地址。当是同一个地址时，避让5个字节
    auto addr2 = __InsertCandyHook2();
    HookParam hp;
    hp.type = USING_STRING;
    hp.filter_fun = filter;
    if (addr2 == 0 && addr1 == 0)
      return false;
    else if (addr2 == 0 && addr1 != 0)
    {
      hp.address = addr1;
      hp.offset = regoffset(edx);
      return NewHook(hp, "SystemC");
    }
    else if (addr2 != 0 && addr1 == 0)
    {
      hp.address = addr2;
      hp.offset = stackoffset(1); // jichi: text in arg1
      return NewHook(hp, "SystemC");
    }
    else
    {
      if (addr1 == addr2)
      {
        addr1 += 5;
      }
      hp.address = addr1;
      hp.offset = regoffset(edx);
      auto succ = NewHook(hp, "SystemC");
      hp.address = addr2;
      hp.offset = stackoffset(1);
      succ |= NewHook(hp, "SystemC");
      return succ;
    }
  }

  /** jichi 10/2/2013: CHECKPOINT
   *
   *  [5/31/2013] 恋もHもお勉強も、おまかせ�お姉ちも�部
   *  base = 0xf20000
   *  + シナリオ: /HSN-4@104A48:ANEBU.EXE
   *    - off: 4294967288 = 0xfffffff8 = -8
   ,    - type: 1025 = 0x401
   *  + 選択肢: /HSN-4@104FDD:ANEBU.EXE
   *    - off: 4294967288 = 0xfffffff8 = -8
   *    - type: 1089 = 0x441
   */
  // bool InsertCandyHook3()
  //{
  //   return false; // CHECKPOINT
  //   const BYTE ins[] = {
  //     0x83,0xc4, 0x0c, // add esp,0xc ; hook here
  //     0x0f,0xb6,0xc0,  // movzx eax,al
  //     0x85,0xc0,       // test eax,eax
  //     0x75, 0x0e       // jnz XXOO ; it must be 0xe, or there will be duplication
  //   };
  //   enum { addr_offset = 0 };
  //   ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  //   ULONG reladdr = SearchPattern(processStartAddress, range, ins, sizeof(ins));
  //   reladdr = 0x104a48;
  //   GROWL_DWORD(processStartAddress);
  //   //GROWL_DWORD3(reladdr, processStartAddress, range);
  //   if (!reladdr)
  //     return false;
  //
  //   HookParam hp;
  //   hp.address = processStartAddress + reladdr + addr_offset;
  //   hp.offset=regoffset(eax);
  //   hp.type = USING_STRING|NO_CONTEXT;
  //   NewHook(hp, "Candy");
  //   return true;
  // }

} // unnamed Candy

namespace
{
  bool candy3()
  {
    // お母さんは俺専用！～あなたの初めてを…母さんが貰ってア・ゲ・ル～
    // 茉莉子さん家の性事情 ~伯母さんは僕のモノ~
    const BYTE bytes[] = {
        0x24, // XX||XX2
        0x75};
    for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE))
    {
      ConsoleOutput("%x", addr);
      if ((*(BYTE *)(addr - 1) == 0x3c) || ((*(BYTE *)(addr - 2) == 0x83) && (*(BYTE *)(addr - 1) == 0xf9)))
      {
        addr = MemDbg::findEnclosingAlignedFunction(addr);
        if (!addr)
          continue;
        ConsoleOutput("!%x", addr);
        HookParam hp;
        hp.type = USING_STRING;
        if (*(BYTE *)addr == 0x55)
          hp.offset = stackoffset(1);
        else if (*(BYTE *)addr == 0x56)
          hp.offset = regoffset(eax);
        else
          continue;
        hp.address = addr;

        return NewHook(hp, "candy3");
      }
    }
    return false;
  }
  bool InsertCandyHook3()
  {

    /*
     * Sample games:
     * https://vndb.org/v24878
     */
    const BYTE bytes[] = {
        0xCC,                               // int 3
        0x55,                               // push ebp        << hook here
        0x8B, 0xEC,                         // mov ebp,esp
        0x6A, 0xFF,                         // push -01
        0x68, XX4,                          // push iinari-omnibus.exe+C4366
        0x64, 0xA1, 0x00, 0x00, 0x00, 0x00, // mov eax,fs:[00000000]
        0x50,                               // push eax
        0x83, 0xEC, 0x74,                   // sub esp,74
        0x53,                               // push ebx
        0x56,                               // push esi
        0x57                                // push edi
    };

    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 1;
    hp.offset = stackoffset(4);
    hp.type = USING_STRING | CODEC_UTF16;
    ConsoleOutput("INSERT SystemC#3");

    return NewHook(hp, "SystemC#3");
  }
}
// jichi 10/2/2013: Add new candy hook
bool InsertCandyHook()
{

  // if (0 == _wcsicmp(processName, L"systemc.exe"))
  if (Util::CheckFile(L"SystemC.exe"))
    return InsertCandyHook1() || candy3();
  else
  {
    // return InsertCandyHook2();
    bool b2 = InsertCandyHook2();
    b2 |= InsertCandyHook3();
    return b2;
  }
}
namespace
{
  bool willowsoft()
  {
    const BYTE bytes[] = {
        // https://vndb.org/v5761
        // まません

        0xA1, XX4,
        0x89, 0x45, 0xF8,
        0x83, 0x7D, 0xF8, 0x10,
        0x74, XX,
        0x83, 0x7D, 0xF8, 0x18,
        0x74, XX,
        0x83, 0x7D, 0xF8, 0x20,
        0x74, XX};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x20);
    if (!addr)
      return false;
    HookParam hp;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING;
    hp.address = addr;
    return NewHook(hp, "WillowSoft");
  }
}
bool Candy::attach_function()
{
  auto b1 = InsertCandyHook();
  if (b1)
    PcHooks::hookOtherPcFunctions();
  else
  {
    b1 = b1 || willowsoft();
    if (!b1)
      PcHooks::hookOtherPcFunctions();
  }
  return b1;
}

bool WillowSoft::attach_function()
{
  // お母さんがいっぱい!!限定ママBOX
  const BYTE bytes[] = {
      0xF7, 0xC2, 0x00, 0x00, 0xFF, 0x00,
      XX2,
      0xF7, 0xC2, 0x00, 0x00, 0x00, 0xFF,
      XX2};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;

  HookParam hp;
  hp.type = USING_STRING;
  hp.offset = stackoffset(2);
  hp.type |= DATA_INDIRECT;
  hp.index = 0;
  hp.address = addr;
  return NewHook(hp, "WillowSoft");
}