#include "TerraLunar.h"
namespace
{
  bool H1()
  {
    const BYTE bytes[] = {
        // らくえん～あいかわらずなぼく。の場合～
        0x8A, 0x08,
        0x81, 0xF9, 0x9F, 0x00, 0x00, 0x00,
        0x7E};
    auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
    auto succ = false;
    for (auto addr : addrs)
    {
      HookParam hp;
      hp.address = addr;
      hp.offset = regoffset(eax);
      hp.type = USING_STRING;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        StringFilter(buffer, TEXTANDLEN("[w]"));
      };
      succ |= NewHook(hp, "TerraLunar");
    }
    return succ;
  }
  bool H2()
  {
    const BYTE bytes[] = {
        // https://vndb.org/v2416
        // ナースのお勉強 応用編～受けシチュ以外は絶対禁止！～
        0X8B, 0X4D, 0X0C, 0X0F, 0XBE, 0X51, 0X01, 0XB8, 0X00, 0X01, 0X00, 0X00};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING;
    return NewHook(hp, "AtelierD");
  }
}
bool TerraLunar::attach_function()
{

  return H2() | H1();
}