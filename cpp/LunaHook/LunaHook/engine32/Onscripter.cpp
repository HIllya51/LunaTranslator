#include "Onscripter.h"

namespace
{
  // Monster Girl Quest Remastered

  bool hook2()
  {
    BYTE bytes[] = {
        0x8b, 0xbe, XX2, 0x00, 0x00,
        0x80, 0x3c, 0x07, 0x00,
        0x8d, 0x1c, 0x07,
        0x75, XX,
        0x8b, 0xce,
        0xe8, XX4};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_reg(regs::eax);
    hp.type = USING_STRING | CODEC_UTF8;
    hp.filter_fun = [](LPVOID data, size_t *size, HookParam *)
    {
      auto xx = std::string((char *)data, *size);
      static std::string last;
      if (xx == last)
        return false;
      last = xx;
      strReplace(xx, "@", "");
      strReplace(xx, "\\", "");
      strReplace(xx, "_", "\n");
      strReplace(xx, "/", "");
      // # ( ) < 代码里，但C了一会儿没遇到，不管了先
      return write_string_overwrite(data, size, xx);
    };
    return NewHook(hp, "onscripter");
  }
}
bool Onscripter::attach_function()
{
  return hook2();
}