#include "XUSE.h"

bool InsertXUSEHook2()
{
  PcHooks::hookGDIFunctions(GetCharABCWidthsA); // 神様のゲーム

  // 最果てのイマ -COMPLETE-

  BYTE bytes[] = {
      0x68, 0x34, 0x01, 0x00, 0x00
      // v39 = v16;
      // v40 = v15;  <-----  v15 ,eax
      // v41 = (const char*)operator new(0x134u);
  };
  auto succ = false;
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  for (auto addr : addrs)
  {

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = CODEC_ANSI_BE | NO_CONTEXT | USING_SPLIT;
    hp.split = 0;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->viewA();
      if (std::all_of(s.begin(), s.end(), [](char c)
                      { return c == 0 || c == ' '; }))
        buffer->clear();
    };
    succ |= NewHook(hp, "XUSE2");
  }
  return succ;
}
bool InsertXUSEHook()
{
  // 詩乃先生の誘惑授業
  // 憂ちゃんの新妻だいあり～
  BYTE bytes[] = {
      0x6a, 0x00,
      XX,
      0x6a, 0x05,
      XX,
      XX,
      0xff, 0x15, XX4,
      0x8b, 0xf0,
      0x83, 0xfe, 0xff

  };
  auto succ = false;
  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  for (auto addr : addrs)
  {

    HookParam hp;
    hp.address = addr + 7;
    hp.offset = regoffset(edi);
    hp.type = CODEC_ANSI_BE | NO_CONTEXT | USING_SPLIT;
    hp.split = stackoffset(3);
    succ |= NewHook(hp, "XUSE");
  }
  return succ;
}

bool xuse_2(DWORD addr)
{
  // 久遠の絆 -THE ORIGIN-
  // 加壳了没有导入表
  auto refs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
  if (refs.size() != 2)
    return false;
  auto a1 = MemDbg::findEnclosingAlignedFunction(refs[0]);
  auto a2 = MemDbg::findEnclosingAlignedFunction(refs[1]);
  if (a1 != a2)
    return false;
  if (!a1)
    return false;
  refs = findxref_reverse_checkcallop(a1, processStartAddress, processStopAddress, 0xe8);
  if (refs.size() != 3)
    return false;
  addr = refs[refs.size() - 1];
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(8);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_GetGlyphOutlineA | DISABLE_FONT_SWITCH; //  修改字体会卡死
  return NewHook(hp, "XUSE");
}
bool xuse_1(DWORD xaddr)
{
  auto import = Util::FindImportEntry(processStartAddress, (DWORD)IsDBCSLeadByteEx);
  if (!import)
    return xuse_2(xaddr);
  BYTE bytes[] = {
      0x51, 0x68, 0xA4, 0x03, 0x00, 0x00, 0xFF, 0x15, XX4, 0x85, 0xC0};
  *(int *)(bytes + 8) = import;
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(8);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.embed_hook_font = F_GetGlyphOutlineA | DISABLE_FONT_SWITCH; //  修改字体会卡死
  return NewHook(hp, "XUSE");
}
bool xusex()
{
  // 久遠の絆 再臨詔
  /*
  char __cdecl sub_5BC9C0(int a1, int a2, int a3, HDC a4, UINT a5, unsigned int a6, __int64 a7)
{
  if ( a6 >= 7 )
    a6 = 6;
  if ( a6 >= 4 )
    return sub_5BC590(a1, a2, a3, a4, a5, a6 - 3, a7);
  else
    return sub_5BC120(a1, a2, a3, a4, a5, a6, a7, (struct _GLYPHMETRICS *)HIDWORD(a7));
}

sub_5BC590
if ( a5 == 33167 )
  {
    v21 = GetGlyphOutlineW;
    a5 = 10084;
    GlyphOutlineW = GetGlyphOutlineW(a4, 10084, v16, (LPGLYPHMETRICS)&v24, 0, 0, (const MAT2 *)&v17);
  }
  else
  {
    v21 = GetGlyphOutlineA;
    GlyphOutlineW = GetGlyphOutlineA(a4, a5, v16, (LPGLYPHMETRICS)&v24, 0, 0, (const MAT2 *)&v17);
  }
  */

  const BYTE bytes[] = {
      0x55, 0x8b, 0xec,
      0x83, 0x7d, 0x1c, 0x07,
      0x72, 0x07,
      0xc7, 0x45, 0x1c, 0x06, 0x00, 0x00, 0x00,
      0x83, 0x7d, 0x1c, 0x04,
      0x73, 0x2c,
      0x8b, 0x45, 0x24,
      // ……
  };
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  if (xuse_1(addr))
    return true;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(5);
  hp.type = USING_CHAR | CODEC_ANSI_BE;
  return NewHook(hp, "XUSE");
}
bool XUSE::attach_function()
{
  return xusex() || InsertXUSEHook() || InsertXUSEHook2();
}