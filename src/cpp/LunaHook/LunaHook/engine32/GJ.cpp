#include "GJ.h"

bool GJ::attach_function()
{
  // int sscanf(const char *const Buffer, const char *const Format, ...)
  //->
  // int __cdecl _scanner(int (__cdecl *a1)(int), void (__cdecl *a2)(int, int), int a3, char *a4, int a5)
  BYTE bytes[] = {
      0x80, 0x7d, 0xe7, 0x25,
      0x75, 0x0f,
      0x8a, 0x17,
      0x47,
      0x88, 0x55, 0xe7,
      0x80, 0xfa, 0x25,
      0x0f, 0x85, XX4};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = findfuncstart(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    std::string s = *(char **)context->stack[3];
    if (!startWith(s, "name ") && !startWith(s, "main "))
      return;
    *split = s[0];
    s = s.substr(5);
    strReplace(s, "@n");
    buffer->from(s);
  };
  return NewHook(hp, "GJ");
}