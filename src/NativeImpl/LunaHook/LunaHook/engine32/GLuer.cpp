#include "GLuer.h"

bool GLuer::attach_function()
{
  static bool name = false;
  bool succ = true;
  {
    BYTE bytes[] = {
        0x8b, 0x54, 0x24, 0x0c,
        0x83, 0xec, 0x18,
        0x8a, 0x02,
        0x55,
        0x84, 0xc0,
        0x8b, 0xe9,
        0x0f, 0x84, XX4,
        0x8b, 0x4c, 0x24, 0x2c,
        0x53,
        0x81, 0xe1, 0x00, 0x00, 0x00, 0xff,
        0x56};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | FULL_STRING;
    hp.offset = 0xc;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      if (s.size() > 2 && name)
      {
        name = !name;
      }
      else
        buffer->clear();
    };
    succ &= NewHook(hp, "GLuer");
  }
  {
    BYTE bytes[] = {
        0x83, 0xec, 0x20,
        0x8b, 0x44, 0x24, 0x28,
        0x53,
        0x8b, 0xd9,
        0x55,
        0x8b, 0x4c, 0x24, XX,
        0x8b, 0x6c, 0x24, XX,
        0x83, 0xc1, 0x04,
        0x56,
        0x57,
        0x89, 0x44, 0x24, XX,
        0x89, 0x4c, 0x24, XX,
        0xc7, 0x44, 0x24, 0x14, 0x20, 0x00, 0x00, 0x00};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | FULL_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      static std::string last;
      auto s = buffer->strA();
      if (last == s)
        return buffer->clear();
      last = s;
      name = true;
      s = re::sub(s, R"(\n(\x81\x40)*)");
      buffer->from(s);
    };
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      std::string s;
      int a4 = context->stack[3];
      auto v19 = (int ***)(a4 + 4);
      auto v14 = 32;
      bool v11;
      do
      {
        auto v6 = *v19;
        if (*v19)
        {
          while (1)
          {
            auto v13 = *v6;
            s += (char *)v6[2];
            if (!v13)
              break;
            v6 = (int **)v13;
          }
        }
        s += '\n';
        v11 = v14 == 1;
        v19 += 7;
        --v14;

      } while (!v11);

      buffer->from(s);
    };
    succ &= NewHook(hp, "GLuer");
  }
  return succ;
}