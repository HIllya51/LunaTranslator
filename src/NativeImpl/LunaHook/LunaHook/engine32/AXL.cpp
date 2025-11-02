#include "AXL.h"
bool InsertAXLHook()
{
  // キミの声がきこえる

  BYTE bytes[] = {
      0x0f, 0x95, 0xc2, 0x33, 0xc0, 0xB9, 0x41, 0x00, 0x00, 0x00};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  addr = findfuncstart(addr, 0x1000);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(4);
  hp.type = USING_STRING;

  return NewHook(hp, "AXL");
}
namespace
{
  bool hook2()
  {
    // 剣乙女ノア
    // Maria～天使のキスと悪魔の花嫁～
    BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0x56,
        0x8b, 0xf0,
        0x3b, 0x9e, 0x8c, 0xf8, 0x00, 0x00,
        0x57};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.split = regoffset(eax);
    hp.type = USING_SPLIT;

    return NewHook(hp, "TAILWIND");
  }
}
bool AXL::attach_function()
{

  return InsertAXLHook() || hook2();
}