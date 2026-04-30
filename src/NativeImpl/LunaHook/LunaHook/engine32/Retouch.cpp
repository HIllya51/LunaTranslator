#include "Retouch.h"

// jichi 6/21/2015
namespace
{ // unnamed

  void SpecialHookRetouch1(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    buffer->from((char *)context->stack[1]);
    // 这个slit不总是管用，但这样最多也不过是把人名和文本合并（例如夏への方舟系列），改了反而会导致某些游戏炸了。
    *split = context->eax == 0 ? FIXED_SPLIT_VALUE * 2 :    // name
                 context->ebx == 0 ? FIXED_SPLIT_VALUE * 1  // scenario
                                   : FIXED_SPLIT_VALUE * 3; // other
  }

  bool InsertRetouch1Hook(HMODULE hm)
  {
    // private: bool __thiscall RetouchPrintManager::printSub(char const *,class UxPrintData &,unsigned long)	0x10050650	0x00050650	2904 (0xb58)	resident.dll	C:\Local\箱庭ロジヂ�\resident.dll	Exported Function
    const char *sig = "?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z";
    DWORD addr = (DWORD)::GetProcAddress(hm, sig);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.text_fun = SpecialHookRetouch1;
    return NewHook(hp, "Retouch1");
  }

  bool InsertRetouch2Hook(HMODULE hm)
  {
    // private: void __thiscall RetouchPrintManager::printSub(char const *,unsigned long,int &,int &)	0x10046560	0x00046560	2902 (0xb56)	resident.dll	C:\Local\箱庭ロジヂ�\resident.dll	Exported Function
    const char *sig = "?printSub@RetouchPrintManager@@AAEXPBDKAAH1@Z";
    DWORD addr = (DWORD)::GetProcAddress(hm, sig);
    if (!addr)
      return false;

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "Retouch2");
  }

  namespace HistoryHook
  {
    inline ULONG get_jmp_absaddr(ULONG inst)
    {
      return inst + 5 + *(ULONG *)(inst + 1);
    }
    bool attach(HMODULE hm) // attach scenario
    {
      auto [startAddress, stopAddress] = Util::QueryModuleLimits(hm);
      const uint8_t bytes[] = {
          0x8b, 0x44, 0x24, 0x04, // 051cf2e0   8b4424 04        mov eax,dword ptr ss:[esp+0x4]
          0x6a, 0x02,             // 051cf2e4   6a 02            push 0x2
          0x6a, 0x00,             // 051cf2e6   6a 00            push 0x0
          0x6a, 0x00,             // 051cf2e8   6a 00            push 0x0
          0x6a, 0x00,             // 051cf2ea   6a 00            push 0x0
          0x50,                   // 051cf2ec   50               push eax
          0xe8                    // 9ef8ffff      // 051cf2ed   e8 9ef8ffff      call _1locke2.051ceb90
                                  //  051cf2f2   c2 0400          retn 0x4
      };
      auto addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
      if (!addr)
        return false;
      addr += sizeof(bytes) - 1; // move to the short call instruction
      addr = get_jmp_absaddr(addr);
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(1);
      hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
      hp.embed_hook_font = F_GetGlyphOutlineA;
      return NewHook(hp, "RetouchHistory");
    }

  } // namespace HistoryHook
} // unnamed namespace
static bool old(HMODULE hm)
{
  // Pia Carrot e Youkoso!! 3
  // https://vndb.org/r12883
  // https://archive.org/download/pia-carrot-e-youkoso-3/Pia_Carrot_e_Youkoso_3.rar

  return [&]()
  {
    // 这作会把每行分开，不好内嵌。
    auto message = (DWORD)GetProcAddress(hm, "?message@FCProjectAdvSystem@@UAEXPBDH@Z");
    if (!message)
      return false;
    HookParam hp;
    hp.address = message;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    return NewHook(hp, "FCProjectAdvSystem::message");
  }() && [&]()
  {
    auto name = (DWORD)GetProcAddress(hm, "?name@FCProjectAdvSystem@@UAEXPBD0H@Z");
    if (!name)
      return false;
    HookParam hp;
    hp.address = name;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING;
    return NewHook(hp, "FCProjectAdvSystem::name");
  }();
}
bool Retouch::attach_function()
{
  bool ok = InsertRetouch1Hook(hm);
  ok = InsertRetouch2Hook(hm) || ok;
  ok = HistoryHook::attach(hm) || ok;
  return ok || old(hm);
}