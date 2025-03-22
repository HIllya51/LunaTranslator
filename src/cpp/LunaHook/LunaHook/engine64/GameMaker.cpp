#include "GameMaker.h"
bool GameMaker::attach_function()
{
  /*
 sub_1414255B0("string_char_at", sub_141391150, 2i64);
.text:0000000141396346                 lea     rdx, sub_141391150
.text:000000014139634D                 lea     rcx, aStringCharAt ; "string_char_at"
.text:0000000141396354                 lea     r8d, [r9+2]
.text:0000000141396358                 call    sub_1414255B0
*/
  char func[] = "string_char_at";
  auto addr = MemDbg::findBytes(func, sizeof(func), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::find_leaorpush_addr(addr, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE target[] = {0x48, 0x8D, 0x15, XX4};
  if (memcmp((char *)addr - sizeof(target), target, 0x3) != 0)
    return false;
  auto string_char_at = addr + *(int *)((char *)addr - sizeof(target) + 3);
  /*
.text:0000000141391247                 add     rsp, 30h
.text:000000014139124B                 pop     rdi
.text:000000014139124C                 retn
  */
  const BYTE bytes[] = {
      0x48, 0x83, 0xc4, XX,
      XX,
      0xc3};
  addr = MemDbg::findBytes(bytes, sizeof(bytes), string_char_at, string_char_at + 0x100);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
  hp.offset = regoffset(rax);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    CharFilter(buffer, '$');
  };
  return NewHook(hp, "GameMaker");
}