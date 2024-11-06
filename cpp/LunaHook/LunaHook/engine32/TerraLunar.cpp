#include "TerraLunar.h"

bool TerraLunar::attach_function()
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
    hp.offset = get_reg(regs::eax);
    hp.type = USING_STRING;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      StringFilter(buffer, "[w]", 3);
    };
    succ |= NewHook(hp, "TerraLunar");
  }
  return succ;
}