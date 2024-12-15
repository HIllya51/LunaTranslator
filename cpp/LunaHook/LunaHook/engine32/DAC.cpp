#include "DAC.h"

bool DAC::attach_function()
{ // https://vndb.org/v11673
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
  hp.user_value = (DWORD) new std::map<DWORD, std::string>;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto mp = ((std::map<DWORD, std::string> *)hp->user_value);
    if (mp->find(context->retaddr) == mp->end())
      mp->insert({context->retaddr, ""});
    auto &&thisthread = mp->at(context->retaddr);

    std::string s = (char *)context->stack[2];
    s = strSplit(s, "\n")[0];
    if (endWith(thisthread, s))
      ;
    else
    {
      thisthread = s;
      strReplace(s, "`#`{$$lines}", "");
      strReplace(s, "\n", "");
      strReplace(s, "\r", "");
      buffer->from(s);
    }
  };
  return NewHook(hp, "DAC");
}