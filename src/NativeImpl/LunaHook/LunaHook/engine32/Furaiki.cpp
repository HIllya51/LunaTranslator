#include "Furaiki.h"

static bool h1()
{
  BYTE bytes[] = {
      0X55,
      0X56,
      0X8B, 0XF0,
      0X33, 0XED,
      0X39, 0XAE, 0XCC, 0X08, 0X00, 0X00,
      0XC6, 0X86, 0XC9, 0X00, 0X00, 0X00, 0X01,
      0X89, 0XAE, 0XD0, 0X08, 0X00, 0X00,
      0X7E, 0X68,
      0X57,
      0X8D, 0XBE, 0XCB, 0X00, 0X00, 0X00};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.type = FULL_STRING | USING_STRING | NO_CONTEXT;
  hp.address = addr;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    int v2 = 0;
    int a1 = context->eax;
    std::string s;
    char *v4 = (char *)(a1 + 203);
    do
    {
      s += v4;
      v4 += 256;
      ++v2;
    } while (v2 < *(DWORD *)(a1 + 2252));
    buffer->from(s);
  };
  return NewHook(hp, "Furaiki");
}
bool Furaiki::attach_function()
{
  return h1();
}