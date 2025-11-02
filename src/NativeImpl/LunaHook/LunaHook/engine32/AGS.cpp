#include "AGS.h"

bool InsertAGSHook()
{

  const BYTE bytes1[] = {
      /*.text:0043E3A0 55                            push    ebp
  .text : 0043E3A1 8B EC                         mov     ebp, esp
  .text : 0043E3A3 83 EC 38                      sub     esp, 38h
  .text : 0043E3A6 53                            push    ebx
  .text : 0043E3A7 56                            push    esi
  .text : 0043E3A8 8B F1                         mov     esi, ecx*/
      0x55,
      0x8b, 0xec,
      0x83, 0xec, 0x38, 0x53, 0x56, 0x8b, 0xf1};

  ULONG addr = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);
  if (!addr)
  {
    return false;
  }
  const BYTE bytes2[] = {
      /*	.text:0043E95E FF 75 08                      push[ebp + arg_0]
  .text:0043E961 8B CE                         mov     ecx, esi
  .text : 0043E963 E8 38 FA FF FF                call    sub_43E3A0*/
      0xff, 0x75, 0x08,
      0x8b, 0xce};
  bool ok = false;

  auto addrs = findrelativecall(bytes2, sizeof(bytes2), addr, processStartAddress, processStopAddress);

  for (auto addr : addrs)
  {
    addr = findfuncstart(addr);
    if (!addr)
      continue;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING;
    ConsoleOutput("INSERT HOOK_AGS %p", addr);

    ok |= NewHook(hp, "HOOK_AGS");
  }

  return ok;
}

namespace
{
  bool hook2()
  {
    // 誘惑女教師～熟れた蜜の味～
    for (auto addr : findiatcallormov_all((DWORD)TextOutA, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE))
    {

      auto funcaddr = findfuncstart(addr, 0x1000);
      ConsoleOutput("funcaddr %p", funcaddr);
      if (!funcaddr)
        continue;
      BYTE sig1[] = {0x68, 0x00, 0x80, 0x00, 0x00, 0x6a, 0x00};
      BYTE sig2[] = {0x2D, 0xC0, 0x00, 0x00, 0x00, 0xC1, 0xE0, 0x08};
      BYTE sig3[] = {0x83, 0xC0, 0x80, 0xC1, 0xE0, 0x08};
      BYTE sig4[] = {0x3C, 0xA0, 0x0F, 0xB6, 0xC0};
      int found = 0;
      for (auto sigsz : std::vector<std::pair<BYTE *, int>>{{sig1, sizeof(sig1)}, {sig2, sizeof(sig2)}, {sig3, sizeof(sig3)}, {sig4, sizeof(sig4)}})
      {
        auto fd = MemDbg::findBytes(sigsz.first, sigsz.second, funcaddr, addr);
        ConsoleOutput("%p", fd);
        if (fd)
          found += 1;
      }
      if (found == 4)
      {
        HookParam hp;
        hp.address = funcaddr;
        hp.type = DATA_INDIRECT;
        hp.offset = stackoffset(1);
        hp.index = 0;
        return NewHook(hp, "AGS");
      }
    }
    return false;
  }
}

bool AGS::attach_function()
{

  return InsertAGSHook() || hook2();
}