#include "Hug.h"
bool Hug::attach_function()
{
  char sig[] = "\x83\x74\x83\x48\x83\x93\x83\x67\x83\x6E\x83\x93\x83\x68\x83\x8B\x92\x6C\x82\xAA\x88\xD9\x8F\xED\x82\xC5\x82\xB7\x0A";
  auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    int x = context->stack[1];
    int y = context->stack[2];
    if (x != 0x37 && x != 0x3c)
      return;
    std::string text = (char *)context->stack[3];
    *split = x;
    static std::map<std::pair<int, int>, std::string> lasts;
    auto p = std::make_pair(x, y);
    if (!lasts.count(p))
      lasts[p] = "";
    auto &thislast = lasts[p];

    auto parse = [](std::string s)
    {
      return strReplace(s, "\x81\x40");
    };
    if (thislast.size() && startWith(text, thislast))
    {
      buffer->from(parse(text.substr(thislast.size())));
    }
    else
    {
      buffer->from(parse(text));
    }
    thislast = text;
  };
  return NewHook(hp, "Hug");
}
