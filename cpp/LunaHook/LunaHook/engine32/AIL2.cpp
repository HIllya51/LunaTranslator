#include "AIL2.h"
bool InsertAIL2Hook()
{
  auto findalign = [](uintptr_t addr1)
  {
    const BYTE pattern[] = {0x90, 0x90, 0x83, 0xec};
    return reverseFindBytes(pattern, sizeof(pattern), processStartAddress, addr1) + 2;
  };
  bool succ = false;
  BYTE bytes1[] = {
      //				.text:0042E5DF 3C 66                         cmp     al, 66h; 'f'
      //.text:0042E5E1 74 57                         jz      short loc_42E63A
      //.text : 0042E5E1
      //.text : 0042E5E3 3C 70                         cmp     al, 70h; 'p'
      //.text:0042E5E5 74 4C                         jz      short loc_42E633
      //.text : 0042E5E5
      //.text : 0042E5E7 3C 73                         cmp     al, 73h; 's'
      //.text:0042E5E9 74 37                         jz      short loc_42E622
      0x3c, 0x66,
      0x74, XX,
      0x3c, 0x70,
      0x74, XX,
      0x3c, 0x73,
      0x74, XX};
  auto addr1 = MemDbg::findBytes(bytes1, sizeof(bytes1), processStartAddress, processStopAddress);
  if (addr1 == 0)
    return false;
  addr1 = findalign(addr1);
  if (addr1 == 0)
    return false;
  ConsoleOutput("AIL1 %p", addr1);
  HookParam hp;
  hp.address = addr1;
  hp.codepage = 932;
  hp.offset = get_stack(3);
  hp.type = USING_STRING;
  succ |= NewHook(hp, "AIL1");

  BYTE bytes[] = {// if ( v12 != 32 && v12 != 33088 )
                  0x3d, 0x40, 0x81, 0x00, 0x00, 0x0f};

  addr1 = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (addr1 == 0)
    return succ;
  addr1 = MemDbg::findEnclosingAlignedFunction(addr1);
  if (addr1 == 0)
    return succ;
  hp = {};
  hp.address = addr1;
  hp.codepage = 932;
  hp.offset = get_stack(4);
  hp.type = USING_STRING | USING_SPLIT;
  hp.split_index = 0;
  succ |= NewHook(hp, "AIL2");

  return succ;
}
bool AIL2::attach_function()
{
  // アイル

  return InsertAIL2Hook();
}