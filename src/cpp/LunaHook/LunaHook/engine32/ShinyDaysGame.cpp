#include "ShinyDaysGame.h"

/** Game-specific engines */

// static char* ShinyDaysQueueString[0x10];
// static int ShinyDaysQueueStringLen[0x10];
// static int ShinyDaysQueueIndex, ShinyDaysQueueNext;
static void SpecialGameHookShinyDays(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  static int ShinyDaysQueueStringLen;
  LPWSTR fun_str, text_str;
  DWORD l = 0;
  auto esp_base = context->base;
  fun_str = (LPWSTR)context->stack[0x13];
  auto esi = context->stack[0x1C] + 0x3C;
  auto edi = context->stack[0x1D];
  if (esi <= edi)
  {
    auto tu = (TextUnionW *)esi;
    auto vw = tu->view();
    text_str = (LPWSTR)vw.data();
    l = vw.size() * 2;
  }
  if (::memcmp(fun_str, L"[PlayVoice]", 0x18) == 0)
  {
    buffer->from(text_buffer, ShinyDaysQueueStringLen);
  }
  else if (::memcmp(fun_str, L"[PrintText]", 0x18) == 0)
  {
    memcpy(text_buffer, text_str, l);
    ShinyDaysQueueStringLen = l;
  }
}
bool InsertShinyDaysGameHook()
{
  const BYTE bytes[] = {
      0xff, 0x83, 0x70, 0x03, 0x00, 0x00, 0x33, 0xf6,
      0xc6, 0x84, 0x24, 0x90, 0x02, 0x00, 0x00, 0x02};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + 0x8;
  hp.text_fun = SpecialGameHookShinyDays;
  hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    StringCharReplacer(buffer, TEXTANDLEN(L"\\n"), L'\n');
  };
  ConsoleOutput("INSERT ShinyDays");
  return NewHook(hp, "ShinyDays");
}

bool ShinyDaysGame::attach_function()
{

  return InsertShinyDaysGameHook();
}