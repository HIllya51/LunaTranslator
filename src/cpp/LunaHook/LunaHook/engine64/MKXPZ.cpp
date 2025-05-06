#include "MKXPZ.h"

bool MKXPZ::attach_function()
{
  auto hmod = GetModuleHandle(L"x64-msvcrt-ruby310.dll");
  if (!hmod)
    return false;

  auto onigenc_get_right_adjust_char_head_with_prev = GetProcAddress(hmod, "onigenc_get_right_adjust_char_head_with_prev");
  auto onigenc_get_prev_char_head = GetProcAddress(hmod, "onigenc_get_prev_char_head");
  bool succ = false;
  HookParam hp;
  hp.type = CODEC_UTF8 | USING_STRING | FULL_STRING;
  hp.offset = regoffset(rdx);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    auto s = buffer->strA();
    if (startWith(s, "Characters/"))
      return buffer->clear();
    if (startWith(s, "Pictures/"))
      return buffer->clear();
    if (startWith(s, "Graphics/"))
      return buffer->clear();
    s = re::sub(s, "<.*?>");
    s = re::sub(s, R"(\\tg\[(.*?)\])", "$1\n"); // 人名
    s = re::sub(s, R"(\\\w+\[\d+\])");
    strReplace(s, "\\|");
    buffer->from(s);
  };
  hp.address = (uintptr_t)onigenc_get_right_adjust_char_head_with_prev; // 这个比较纯粹，但有时候会缺
  succ |= NewHook(hp, "MKXPZ");
  hp.address = (uintptr_t)onigenc_get_prev_char_head;
  succ |= NewHook(hp, "MKXPZ");
  return succ;
}