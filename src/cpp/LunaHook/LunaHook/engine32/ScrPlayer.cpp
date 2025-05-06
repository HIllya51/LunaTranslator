#include "ScrPlayer.h"

bool ScrPlayer_attach_function1()
{
  auto func = MemDbg::findCallerAddress((ULONG)GetGlyphOutlineA, 0x90909090, processStartAddress, processStopAddress);
  if (func == 0)
    return false;
  func += 4;
  BYTE check[] = {
      0x83, 0xf8, 0x20,
      0x74, XX,
      0x3d, 0x40, 0x81, 0x00, 0x00,
      0x74, XX};
  auto addr = MemDbg::findBytes(check, sizeof(check), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  if (addr != func)
    return false;
  HookParam hp;
  hp.address = func;
  hp.offset = stackoffset(5);
  // 会把多行分开导致翻译不对。
  hp.type = USING_STRING; //|EMBED_ABLE|EMBED_AFTER_NEW|EMBED_DYNA_SJIS;
  // hp.embed_hook_font=F_GetGlyphOutlineA;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    static int idx = 0;
    if (idx % 2)
      buffer->clear();
    idx += 1; // 这个函数总是连续被调用两次，一个绘制上层文字，一个绘制阴影。
  };
  return NewHook(hp, "ScrPlayer");
}

bool ScrPlayer_attach_function2()
{
  // https://vndb.org/v7056
  // Rendezvous ～ランデブー～
  //  _DWORD *__stdcall sub_41DC10(
  //        _DWORD *a1,
  //        int a2,
  //        int a3,
  //        int a4,
  //        int a5,
  //        unsigned __int8 *a6, <---
  //        int a7,
  //        int a8,
  //        int a9,
  //        char a10,
  //        int a11)
  BYTE bs[] = {
      0x51,
      0x56,
      0x8b, 0x74, 0x24, 0x20,
      0x8a, 0x06,
      0x84, 0xc0,
      0x89, 0x4c, 0x24, 0x04,
      0x0f, 0x84, XX4};
  auto addr = MemDbg::findBytes(bs, sizeof(bs), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(6);
  hp.type = USING_STRING; // 有内部的multibyte函数使得无法内嵌显示中文字符
  return NewHook(hp, "ScrPlayer2");
}
bool ScrPlayer::attach_function()
{
  return ScrPlayer_attach_function1() || ScrPlayer_attach_function2();
}