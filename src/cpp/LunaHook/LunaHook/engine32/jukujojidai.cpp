#include "jukujojidai.h"

bool jukujojidai::attach_function()
{

  const BYTE bytes[] = {
      // 撫乳～今夜、あなたのお掃除しましょうか?～
      // https://vndb.org/v15867
      0x41,
      0x83, 0xC0, 0x20,
      0x81, 0xF9, 0xC8, 0x00, 0x00, 0x00,
      0x7C};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x1000);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = CODEC_UTF16 | DATA_INDIRECT;

  return NewHook(hp, "jukujojidai");
}