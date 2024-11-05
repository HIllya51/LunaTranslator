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
  hp.offset = get_reg(regs::rdx);
  hp.filter_fun = [](void *data, size_t *size, HookParam *)
  {
    auto s = std::string((char *)data, *size);
    if (startWith(s, "Characters/"))
      return false;
    if (startWith(s, "Pictures/"))
      return false;
    if (startWith(s, "Graphics/"))
      return false;
    s = std::regex_replace(s, std::regex("<.*?>"), "");
    s = std::regex_replace(s, std::regex(R"(\\tg\[(.*?)\])"), "$1\n"); // 人名
    s = std::regex_replace(s, std::regex(R"(\\\w+\[\d+\])"), "");
    strReplace(s, "\\|", "");
    return write_string_overwrite((char *)data, size, s);
  };
  hp.address = (uintptr_t)onigenc_get_right_adjust_char_head_with_prev; // 这个比较纯粹，但有时候会缺
  succ |= NewHook(hp, "MKXPZ");
  hp.address = (uintptr_t)onigenc_get_prev_char_head;
  succ |= NewHook(hp, "MKXPZ");
  return succ;
}