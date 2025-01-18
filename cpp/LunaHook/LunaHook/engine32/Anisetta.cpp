#include "Anisetta.h"

bool Anisetta::attach_function()
{
  // https://vndb.org/v4068
  // 12+
  const BYTE bytes[] = {
      0xF7, 0xD8,
      0x1B, 0xC0,
      0x25, 0x58, 0x02, 0x00, 0x00,
      0x05, 0x90, 0x01, 0x00, 0x00};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = CODEC_ANSI_BE;
  hp.offset = stackoffset(5);

  return NewHook(hp, "Anisetta");
}