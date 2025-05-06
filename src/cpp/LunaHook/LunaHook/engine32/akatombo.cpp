#include "akatombo.h"

bool akatombo::attach_function()
{
  // サキュヴァス ～堕ちた天使～
  // https://vndb.org/v7387
  BYTE bytes[] = {
      0x3C, 0x80, 0x72, XX, 0x3C, 0x9F, 0x76, XX, 0x3C, 0xE0, 0x72, XX, 0x3C, 0xEF, 0x77, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr, 0x200);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  return NewHook(hp, "akatombo");
}