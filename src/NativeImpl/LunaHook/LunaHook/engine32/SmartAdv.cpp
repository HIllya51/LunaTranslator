#include "SmartAdv.h"
// https://vndb.org/r6347
// VALENTINE PINK～パーフェクトエディション～

bool SmartAdv::attach_function()
{ /*
int __stdcall sub_100122D0(_DWORD *a1, int a2, int a3, int *a4, int a5)

ms_exc.registration.Next = (struct _EH3_EXCEPTION_REGISTRATION *)a2;
*/
  auto [s, e] = Util::QueryModuleLimits(GetModuleHandle(L"video.dll"));
  auto addr = findiatcallormov((DWORD)CreateFontIndirectA, (DWORD)GetModuleHandle(L"video.dll"), s, e);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | EMBED_AFTER_NEW;
  hp.embed_hook_font = F_ExtTextOutA;
  hp.offset = stackoffset(2);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    CharFilter(buffer, '\n');
  };
  return NewHook(hp, "SmartAdv");
}