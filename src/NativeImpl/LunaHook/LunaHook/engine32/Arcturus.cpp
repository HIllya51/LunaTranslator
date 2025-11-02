#include "Arcturus.h"

static bool h2()
{
  // 二世の契り
  BYTE bytes2[] = {
      0x8b, 0x44, 0x24, 0x04,
      0x56,
      0x8b, 0x74, 0x24, 0x0c,
      0x8a, 0x0e,
      0x84, 0xc9,
      0x74, XX,
      XX,
      0x80, 0xf9, 0x24,
      0x75, XX,
      0x8a, 0x4e, 0x01,
      0x46,
      0x80, 0xf9, 0x6e,
      0x75, XX};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.type = USING_STRING;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    std::string s = buffer->strA();
    s = re::sub(s, R"(\x81\x6f(.*?)\x81\x5e(.*?)\x81\x70)", "$2");
    s = re::sub(s, R"(@c\d(.*?)@c)", "$1");
    s = re::sub(s, "[\r\n]+(\x81\x40)*");
    buffer->from(s);
  };
  return NewHook(hp, "Arcturus2");
}
static bool h1()
{
  // https://github.com/HIllya51/LunaTranslator/issues/1824
  // https://vndb.org/v23847
  // ときめき にゃの☆げっちゅ！
  // https://archive.org/details/tokimeki-nya-no-getchu

  // https://github.com/HIllya51/LunaTranslator/issues/1825
  // https://vndb.org/v23852
  // げっちゅ屋★げっちゅ！！
  // https://archive.org/details/getchu-yagetchu
  BYTE bytes[] = {
      0x57,
      0xe8, XX4,
      0x83, 0xc4, 0x04,
      0x85, 0xc0,
      0x75, XX,
      0x8a, 0x07,
      0x3c, 0x20,
      0x7c, XX,
      0x3c, 0x7f,
      0x7d, XX,
      0x0f, 0xbe, 0xc0,
      0x8d, 0x0c, 0x45, XX4,
      0x51,
      0xe8, XX4};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x20);
  if (!addr)
    return false;
  HookParam hp;
  hp.type = USING_STRING;
  hp.address = addr;
  hp.offset = stackoffset(3);
  return NewHook(hp, "Arcturus");
}
bool Arcturus::attach_function()
{
  if (type == 1)
    return h1();
  if (type == 2)
    return h2();
  return false;
}