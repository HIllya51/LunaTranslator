#include "NUGSystem.h"

bool NUGSystem::attach_function()
{
  // https://vndb.org/v1053
  // そらうた
  const BYTE bytes[] = {
      0X57,
      0X56,
      0X55,
      0X53,
      0X83, 0XEC, 0X08,
      0X8B, XX, XX, XX,
      0X88, 0X0C, XX,
      0X8B, 0XC1,
      0X25, 0X00, 0XFF, 0X00, 0X00,
      0XC1, 0XE8, 0X08,
      0X8B, 0XD1,
      0X81, 0XE2, 0X00, 0X00, 0XFF, 0X00,
      0X88, XX, 0X24, 0X01,
      0XC1, 0XEA, 0X10,
      0X88, XX, 0X24, 0X02,
      0X81, 0XE1, 0X00, 0X00, 0X00, 0XFF,
      0XC1, 0XE9, 0X18,
      0X88, XX, 0X24, 0X03};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR | CODEC_ANSI_BE;
  return NewHook(hp, "NUGSystem");
}