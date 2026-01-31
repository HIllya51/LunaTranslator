#include "THLabyrinth3.h"

bool THLabyrinth3::attach_function()
{
  HookParam hp;
  hp.address = 0x26908A0 + processStartAddress;
  hp.offset = regoffset(rdx);
  hp.split = regoffset(rdx);
  hp.type = CODEC_UTF16 | USING_STRING | USING_SPLIT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static lru_cache<std::wstring> last(10);
    auto s = buffer->strW();
    if (all_ascii(s))
      return buffer->clear();
    if (last.touch(s))
      return buffer->clear();
    buffer->from(s);
  };
  return NewHook(hp, "THLabyrinth3");
}
