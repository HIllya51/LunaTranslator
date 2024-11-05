#include "DISCOVERY.h"
namespace
{
  bool DISCOVERY1()
  {
    // https://vndb.org/v4053
    // 小雪の朱－コユキノアカ－

    BYTE sig[] = {
        /*
        if ( *(v6 - 2) != 23
          || *(v6 - 3) != sub_40C130(255, 255, 255)
          || sub_418190(*(v6 - 4), v6 - 1) != 1
          || dword_B81054 && dword_975570 )*/

        0x83, 0x7b, 0xf8, 0x17,
        0x75, XX,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0xe8};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR;
    hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto v6 = (int *)stack->ebx - 4;
      buffer->from_t<WORD>(*v6);
    };
    return NewHook(hp, "DISCOVERY");
  }
}
bool DISCOVERY::attach_function()
{
  return DISCOVERY1();
}