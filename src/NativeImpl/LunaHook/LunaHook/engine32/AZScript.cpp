#include "AZScript.h"
// すたじおみりす
// 空の森
bool AZScript::attach_function()
{
  BYTE bytes[] = {
      0X8B, 0X44, 0X24, 0X10,
      0X56,
      0X8B, 0X74, 0X24, 0X08,
      0X6A, 0X00,
      0X50,
      0X56,
      0XE8, XX4,
      0X83, 0XC4, 0X0C,
      0X85, 0XC0,
      0X7C, XX,
      0X8B, 0X4E, XX,
      0X8D, 0X54, 0X24, 0X1C,
      0X51,
      0X52,
      0XE8, XX4,
      0X85, 0XC0,
      0X74, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(6);
  hp.type = USING_STRING;

  return NewHook(hp, "AZScript");
}