#include "TAKUYO.h"

bool TAKUYO::attach_function()
{
  BYTE sig[] = {
      0X66, 0X83, 0X3D, XX4, 0X00,
      0X74, XX,
      0X8B, 0X0D, XX4,
      0X8B, 0X15, XX4,
      0xb8, XX4,
      0x66, 0x29, 0x50, 0xfe,
      0x66, 0x29, 0x08,
      0x83, 0xc0, 0x0c,
      0x66, 0x83, 0x78, 0x02, 0x00,
      0x75, XX,
      0x56,
      0xe8, XX4,
      0x83, 0xc4, 0x04,
      0X66, 0X83, 0X3D, XX4, 0X00,
      0X74, XX,
      0X8B, 0X0D, XX4,
      0X8B, 0X15, XX4,
      0xb8, XX4,
      0x66, 0x01, 0x50, 0xfe,
      0x66, 0x01, 0x08,
      0x83, 0xc0, 0x0c,
      0x66, 0x83, 0x78, 0x02, 0x00,
      0x75, XX};
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | USING_SPLIT;
  hp.offset = stackoffset(2); // 其实可以内嵌，但是字体渲染有问题
  hp.split = stackoffset(1);
  return NewHook(hp, "TAKUYO");
}