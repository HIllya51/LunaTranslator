#include "lua51.h"

bool lua51::attach_function()
{
  //[180330][TOUCHABLE] 想聖天使クロスエモーション外伝5 (認証回避済)
  auto hlua51 = GetModuleHandleW(L"lua5.1.dll");
  if (hlua51 == 0)
    hlua51 = GetModuleHandleW(L"lua51.dll");
  if (hlua51 == 0)
    return false;
  auto lua_pushstring = GetProcAddress(hlua51, "lua_pushstring");
  if (lua_pushstring == 0)
    return false;
  HookParam hp;
  hp.address = (uintptr_t)lua_pushstring;
  hp.type = CODEC_UTF8 | USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto text = (char *)context->argof(2);
    *split = all_ascii(text);
    buffer->from(text);
  };
  return NewHook(hp, "lua51");
}