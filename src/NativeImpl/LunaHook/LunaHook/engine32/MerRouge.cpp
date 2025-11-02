#include "MerRouge.h"

bool MerRouge::attach_function()
{
  // https://vndb.org/v12120
  HookParam hp;
  hp.address = (DWORD)TextOutA;
  hp.offset = stackoffset(4);
  hp.type = USING_STRING; // 可以内嵌，但是需要修改TextOutA导致递归崩溃
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    static std::set<uintptr_t> addrs;
    auto addr = context->stack[4];
    if (addrs.count(addr - 4))
      return;
    addrs.insert(addr);
    buffer->from((char *)addr);
  };
  return NewHook(hp, "MerRouge");
}