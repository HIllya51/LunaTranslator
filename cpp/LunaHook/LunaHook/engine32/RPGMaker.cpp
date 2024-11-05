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
  hp.offset=get_stack(1);
  hp.length_offset=2;
  hp.filter_fun = [](LPVOID data, size_t *size, HookParam *)
  {
    if (all_ascii((char *)data, *size))
      return false;
    std::string result = std::string((char *)data, *size);
    result = std::regex_replace(result, std::regex(R"(@c\[\](.*?)@c\[\])"), "$1");
    return write_string_overwrite(data, size, result);
  };

  return NewHook(hp, "RPGMaker");
}