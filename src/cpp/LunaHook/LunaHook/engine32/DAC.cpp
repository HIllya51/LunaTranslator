#include "DAC.h"

bool DACattach_function()
{
  // https://vndb.org/v11673
  // もみえろCureTouch ～イカすマッサージ天国～
  const uint8_t bytes[] = {
      0x80, 0x3f, 0x60,
      0x75, XX,
      0x80, 0x7f, 0x01, 0x23,
      0x75, XX,
      0x6a, 0x60,
      0x6a, 0x60,
      0x57,
      0xe8, XX4};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static std::map<DWORD, std::string> mp;
    if (mp.find(context->retaddr) == mp.end())
      mp.insert({context->retaddr, ""});
    auto &&thisthread = mp.at(context->retaddr);

    std::string s = (char *)context->stack[2];
    s = strSplit(s, "\n")[0];
    if (endWith(thisthread, s))
      ;
    else
    {
      thisthread = s;
      strReplace(s, "`#`{$$lines}");
      strReplace(s, "\n");
      strReplace(s, "\r");
      buffer->from(s);
    }
  };
  return NewHook(hp, "DAC");
}
bool DACattach_function2()
{
  // 少女達のさえずり
  // https://vndb.org/v5378
  const uint8_t bytes[] = {
      0x66, 0x81, XX, 0x84, 0xaa,
      0x74, 0x07,
      0x66, 0x81, XX, 0x84, 0x9f,
      0x75, 0x0b};
  ULONG addrX = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addrX)
    return false;
  auto addr = findfuncstart(addrX);
  if (!addr)
  {
    //[120831][Exception] 白神子～しろみこ～ 初回限定版
    BYTE start2[] = {0xcc, 0x83, 0xec, XX};
    addr = reverseFindBytes(start2, sizeof(start2), addrX - 0x100, addrX);
    if (addr)
      addr += 1;
  }
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static std::map<DWORD, std::string> mp;
    if (mp.find(context->retaddr) == mp.end())
      mp.insert({context->retaddr, ""});
    auto &&thisthread = mp.at(context->retaddr);
    auto s = std::string((char *)context->stack[6]);
    if (startWith(s, thisthread))
    {
      buffer->from(s.substr(thisthread.size()));
    }
    else
    {
      buffer->from(s);
    }
    thisthread = s;
  };
  return NewHook(hp, "DAC2");
}
bool DAC::attach_function()
{
  return DACattach_function() || DACattach_function2();
}