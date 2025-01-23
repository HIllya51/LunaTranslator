#include "TYPEMOON.h"
namespace
{
  bool _h()
  {
    // TYPE-MOON 魔法使いの夜 多国語版 中文-英文-日文
    BYTE bytes[] = {
        0xBA, 0x08, 0xFF, 0x00, 0x00,
        0x41, 0xB8, 0x1C, 0x20, 0x00, 0x00,
        0x66, 0x90};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    ConsoleOutput("%p", addr);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    ConsoleOutput("%p", addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW;
    hp.offset = regoffset(r8);
    return NewHook(hp, "typemoon");
  }
}
bool TYPEMOON::attach_function()
{
  return _h();
}
