#include "InteractiveNovelEngine.h"
// https://vndb.org/v22940
// 俺の娘

// 其实用EasyHook出入一个C#的dll才对，但是太麻烦了，而且是.netframework2，编译都费劲
/*
struct Object *__fastcall COMString::StringInitSBytPtrPartialEx(
        struct StringObject *a1,
        char *a2,
        struct Object *a3,
        int a4,
        int a5)
*/
bool InteractiveNovelEngine::attach_function()
{
  auto [s, e] = Util::QueryModuleLimits(GetModuleHandleW(L"mscorwks.dll"));
  BYTE bytes[] = {
      0x68, 0x68, 0x01, 0x00, 0x00,
      0xb8, XX4,
      0xe8, XX4,
      0x89, 0x95, XX4,
      0x8b, 0x45, 0x08,
      0x89, 0x85, XX4,
      0x33, 0xdb,
      0x8d, 0x8d, XX4,
      0xe8, XX4,
      0x85, 0xc0,
      0x0f, 0x85, XX4,
      0x8d, 0x85, XX4,
      0x50,
      0x53,
      0x8d, 0x85, XX4,
      0x50,
      0xb8, XX4,
      0x50,
      0x8d, 0x8d, XX4,
      0xe8, XX4,
      0xff, 0x15, XX4,
      0x8b, 0xf8,
      0x8b, 0x47, 0x04,
      0xa8, 0x01};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), s, e);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING | CODEC_UTF8 | FULL_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    static lru_cache<std::string> cache(5);
    auto s = buffer->strA();
    if (all_ascii(s))
      return buffer->clear();
    if (cache.touch(s))
      return buffer->clear();
    s = re::sub(s, "owner = .*");
    s = re::sub(s, ".*[+-]\\d+");
    buffer->from(strReplace(s, "@"));
  };
  return NewHook(hp, "InteractiveNovelEngine");
}