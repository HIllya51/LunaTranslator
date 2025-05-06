#include "Retouch.h"

// jichi 6/21/2015
namespace
{ // unnamed

  void SpecialHookRetouch1(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    buffer->from((char *)context->stack[1]);
    *split =
        context->eax == 0 ? FIXED_SPLIT_VALUE * 2 : // name
            context->ebx == 0 ? FIXED_SPLIT_VALUE * 1
                              : // scenario
            context->eax;       // FIXED_SPLIT_VALUE * 3 ; // other //夏への方舟１体験版
  }

  bool InsertRetouch1Hook()
  {
    HMODULE hModule = ::GetModuleHandleA("resident.dll");
    if (!hModule)
    {
      ConsoleOutput("Retouch: failed, dll handle not loaded");
      return false;
    }
    // private: bool __thiscall RetouchPrintManager::printSub(char const *,class UxPrintData &,unsigned long)	0x10050650	0x00050650	2904 (0xb58)	resident.dll	C:\Local\箱庭ロジヂ�\resident.dll	Exported Function
    const char *sig = "?printSub@RetouchPrintManager@@AAE_NPBDAAVUxPrintData@@K@Z";
    DWORD addr = (DWORD)::GetProcAddress(hModule, sig);
    if (!addr)
    {
      ConsoleOutput("Retouch: failed, procedure not found");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.text_fun = SpecialHookRetouch1;
    ConsoleOutput("INSERT Retouch");
    return NewHook(hp, "Retouch");
  }

  bool InsertRetouch2Hook()
  {
    HMODULE hModule = ::GetModuleHandleA("resident.dll");
    if (!hModule)
    {
      ConsoleOutput("Retouch2: failed, dll handle not loaded");
      return false;
    }
    // private: void __thiscall RetouchPrintManager::printSub(char const *,unsigned long,int &,int &)	0x10046560	0x00046560	2902 (0xb56)	resident.dll	C:\Local\箱庭ロジヂ�\resident.dll	Exported Function
    const char *sig = "?printSub@RetouchPrintManager@@AAEXPBDKAAH1@Z";
    DWORD addr = (DWORD)::GetProcAddress(hModule, sig);
    if (!addr)
    {
      ConsoleOutput("Retouch2: failed, procedure not found");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    ConsoleOutput("INSERT Retouch");
    return NewHook(hp, "Retouch");
  }

  namespace HistoryHook
  {
    inline ULONG get_jmp_absaddr(ULONG inst)
    {
      return inst + 5 + *(ULONG *)(inst + 1);
    }
    bool attach() // attach scenario
    {
      if (GetModuleHandle(L"resident.dll") == 0)
        return false;
      auto [startAddress, stopAddress] = Util::QueryModuleLimits(GetModuleHandle(L"resident.dll"));
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
bool InsertRetouchHook()
{
  bool ok = InsertRetouch1Hook();
  ok = InsertRetouch2Hook() || ok;
  ok = HistoryHook::attach() || ok;
  return ok;
}
bool Retouch::attach_function()
{

  return InsertRetouchHook();
}