#include "T2U.h"

bool T2U::attach_function()
{
  //(18禁ゲーム)[000128][BLUE GALE] Treating2U (bin+cue)
  HookParam hp;
  hp.address = (DWORD)TextOutA; // 这个游戏设置embed_hook_font会卡死
  hp.type = USING_STRING;
  hp.offset = stackoffset(4);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static lru_cache<std::string> cache(5);
    auto s = buffer->strA();
    if (cache.touch(s))
    {
      return buffer->clear();
    }
  };
  return NewHook(hp, "T2U");
}