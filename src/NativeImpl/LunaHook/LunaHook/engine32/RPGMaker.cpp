#include "RPGMaker.h"
// https://www.dlsite.com/maniax/work/=/product_id/RJ01240121.html
// ネクロマリア

bool RPGMaker::attach_function()
{
  BYTE bytes2[] = {
      0x81, 0xf9, 0xff, 0xff, 0xff, 0x7f,
      XX2,
      0xb9, 0xff, 0xff, 0xff, 0x7f,
      XX2,
      0x8b, 0xc2,
      0xd1, 0xe8,
      0x89, 0x45, 0x0c,
      0xb8, 0xff, 0xff, 0xff, 0x7f,
      0x2b, 0x45, 0x0c,
      0x3b, 0xd0,
      XX2,
      0xb9, 0xff, 0xff, 0xff, 0x7f};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | CODEC_UTF8;
  hp.offset = stackoffset(1);
  hp.length_offset = 2;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    std::string result = buffer->strA();
    if (all_ascii(result))
      return buffer->clear();
    buffer->from(re::sub(result, R"(@c\[\](.*?)@c\[\])", "$1"));
  };

  return NewHook(hp, "RPGMaker");
}