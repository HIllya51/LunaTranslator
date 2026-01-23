#include "AbogadoPowers.h"

bool AbogadoPowers::attach_function()
{
  // https://vndb.org/v509
  // D+VINE[LUV]
  const BYTE bytes[] = {
      0xa1, XX4,
      0x33, 0xc9,
      0x8a, 0x08,
      0x85, 0xc9,
      0x0f, 0x84, XX4,
      0xe8, XX4,
      0x85, 0xc0};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.user_value = *(DWORD *)(addr + 1);
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    buffer->from(*(char **)hp->user_value, 2);
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if (buffer->data[0] == '_')
      return buffer->clear();
    if (buffer->data[0] == 0)
      return buffer->clear();
  };
  return NewHook(hp, "AbogadoPowers");
}