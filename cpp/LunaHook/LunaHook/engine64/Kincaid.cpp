#include "Kincaid.h"
namespace
{
  bool _1()
  {
    //     .text:0000000140230D80                 mov     rsi, rax
    // .text:0000000140230D83                 mov     edx, 1
    // .text:0000000140230D88                 mov     rcx, rdi
    // .text:0000000140230D8B                 call    sub_1402B35B0
    // .text:0000000140230D90                 lea     ebx, [rax-1]
    // .text:0000000140230D93                 mov     edx, 2
    // .text:0000000140230D98                 mov     rcx, rdi
    // .text:0000000140230D9B                 call    sub_1402B35B0
    BYTE b1[] = {
        0x48, 0x8b, 0xf0,
        0xba, 0x01, 0x00, 0x00, 0x00,
        0x48, 0x8b, 0xcf,
        0xe8, XX4,
        0x8d, 0x58, 0xff,
        0xba, 0x02, 0x00, 0x00, 0x00,
        0x48, 0x8b, 0xcf,
        0xe8, XX4};
    auto addr = MemDbg::findBytes(b1, sizeof(b1), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF8;
    hp.offset = regoffset(rax);
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      if (context->retaddr == (DWORD)-1)
      {
        buffer->from((char *)context->rax);
      }
    };
    return NewHook(hp, "Kincaid");
  }
}
bool Kincaid::attach_function()
{
  return _1();
}