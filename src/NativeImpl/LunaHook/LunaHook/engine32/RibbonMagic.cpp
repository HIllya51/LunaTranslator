#include "RibbonMagic.h"

bool RibbonMagic::attach_function()
{
  // https://vndb.org/v807
  // クレプシドラ～光と影の十字架～
  BYTE bytes2[] = {
      0x83, 0xec, XX,
      0xa1, XX4,
      0x53,
      0x89, XX, XX, XX,
      0x55,
      0x33, 0xc0,
      0x56,
      0x57,
      0x8b, 0xe9,
      0x89, XX, XX, XX,
      0x8b, XX, XX, XX,
      0x8b, XX, XX, XX,
      0xf7, 0xd8,
      0x1b, 0xc0,
      0x89, XX, XX, XX,
      0x24, 0xfc,
      0xc7, XX, XX, XX, 0x20, 0x00, 0x00, 0x00,
      0x83, 0xc0, 0x08};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static std::string last;
    auto s = buffer->strA();
    if (startWith(s, last))
      buffer->from(s.substr(last.size()));
    last = s;
  };
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    int a4 = context->stack[3];
    std::string ss;
    // for (auto i = 0; i < 2; ++i)
    {
      auto v16 = (int ***)(a4 + 4);
      auto v18 = 32;
      bool v14;
      do
      {
        auto v8 = *v16;
        if (*v16)
          while (1)
          {
            auto v17 = *v8;
            ss += (char *)(unsigned __int8 *)v8[2];
            if (*(v8[3] - 2))
            {
              ss += (char *)(unsigned __int8 *)v8[3];
            }
            if (!v17)
              break;
            v8 = (int **)v17;
          }
        v14 = v18 == 1;
        v16 += 7;
        --v18;
      } while (!v14);
    }
    buffer->from(ss);
  };

  return NewHook(hp, "clep");
}