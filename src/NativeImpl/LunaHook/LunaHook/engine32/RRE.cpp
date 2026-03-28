#include "RRE.h"

static void SpecialRunrunEngine(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  // CC_UNUSED(split);
  DWORD eax = context->eax, // *(DWORD *)(esp_base - 0x8),
      edx = context->edx;   // *(DWORD *)(esp_base - 0x10);
  DWORD addr = eax + edx;   // eax + edx
  buffer->from_t(*(WORD *)(addr));
}
bool InsertRREHook()
{
  ULONG addr = MemDbg::findCallAddress((ULONG)::IsDBCSLeadByte, processStartAddress, processStopAddress);
  if (!addr)
  {
    return false;
  }
  WORD sig = 0x51c3;
  HookParam hp;
  hp.address = addr;
  hp.type = NO_CONTEXT | DATA_INDIRECT | USING_CHAR;
  if ((*(WORD *)(addr - 2) != sig))
  {
    hp.text_fun = SpecialRunrunEngine;
    return NewHook(hp, "RunrunEngine Old");
  }
  else
  {
    hp.offset = regoffset(eax);
    return NewHook(hp, "RunrunEngine");
  }
}

bool RRE::attach_function()
{

  return InsertRREHook();
}