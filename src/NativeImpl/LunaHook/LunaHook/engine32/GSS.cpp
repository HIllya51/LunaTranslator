#include "GSS.h"

namespace
{

  bool InsertGssHooks()
  {
    const BYTE s[] = {0x8B, 0x54, 0x24, 0x0C, 0x53, 0x55, 0x56, 0x8B, 0x74, 0x24,
                      0x1C, 0x57, 0x66, 0x8B, 0x3D, XX4, 0x0F, 0xB7, 0xC7, 0x8D, 0x0C};
    ULONG addr = MemDbg::findBytes(s, sizeof(s), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | FULL_STRING;
    hp.offset = stackoffset(2);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      s = re::sub(s, R"(\\n)", "\n");
      buffer->from(s);
    };
    return NewHook(hp, "GSS_Layout");
  }
}

bool GSS::attach_function()
{
  return InsertGssHooks();
}
