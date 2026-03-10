#include "ANOS.h"

bool ANOS::attach_function()
{
  // あの、素晴らしい　をもう一度 for Windows

  const BYTE bytes[] = {
      0X8A, 0X01,
      0X33, 0XF6,
      0X3C, 0X81,
      0X57,
      0X89, 0X74, 0X24, XX,
      0X89, 0X74, 0X24, XX,
      0X72, XX,
      0X3C, 0X83,
      0X77, XX,
      0X25, 0XFF, 0X00, 0X00, 0X00,
      0X33, 0XD2,
      0X8A, 0X51, 0X01};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0X20);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR | DATA_INDIRECT;
  return NewHook(hp, "ANOS");
}