#include "mono.h"
#include "mono/monocommon.hpp"

namespace
{
  bool monobdwgc()
  {

    HMODULE module = GetModuleHandleW(L"mono-2.0-bdwgc.dll");
    if (module == 0)
      return false;
    auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
    BYTE bytes[] = {
        0x81, 0xF9, 0x80, 0x00, 0x00, 0x00,
        0x73, 0x05,
        0x49, 0x8B, 0xCC
        /*
  _BYTE *__fastcall sub_18005B290(
          _WORD *a1,
          int a2,
          __int64 a3,
          _DWORD *a4,
          __int64 (__fastcall *a5)(__int64, __int64),
          __int64 a6,
          __int64 a7)

        if ( (_DWORD)v26 )
        {
          if ( (unsigned int)v26 >= 0x80 )
          {
            if ( (unsigned int)v26 >= 0x800 )
            {
              if ( (unsigned int)v26 >= 0x10000 )
              {
                if ( (unsigned int)v26 >= 0x200000 )
                {
                  if ( (unsigned int)v26 >= 0x4000000 )
                  {
                    v17 = 6i64;
                    if ( (unsigned int)v26 >= 0x80000000 )
        */
    };
    auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, minAddress, maxAddress);
    auto suc = false;
    for (auto addr : addrs)
    {
      const BYTE align[] = {0xCC, 0xCC, 0xCC, 0xCC};
      addr = reverseFindBytes(align, sizeof(align), addr - 0x100, addr);
      if (addr == 0)
        continue;

      ConsoleOutput("monobdwgcdll %p", addr);
      HookParam hp;
      hp.address = addr + 4;
      hp.offset = get_reg(regs::rcx);
      hp.type = CODEC_UTF16 | USING_STRING;
      hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto str = std::wstring_view((LPWSTR)stack->rcx);
        *split = str.find(L"OnShowComplete") != str.npos;
        buffer->from(str);
      };
      hp.filter_fun = [](void *data, size_t *len, HookParam *hp)
      {
        std::wstring str = std::wstring((LPWSTR)data, *len / 2);
        if (str.find(L"OnShowComplete") != str.npos)
        {
          str = std::regex_replace(str, std::wregex(L"\n"), L"");
          std::wregex reg1(L"\\((.*?)\\)");
          std::wsmatch match;
          std::regex_search(str, match, reg1);
          auto result1 = match[1].str();

          std::regex_search(str, match, std::wregex(L" Text:(.*?)Next:(.*?)"));
          result1 = match[1].str();
          write_string_overwrite(data, len, result1);
        }
        return true;
      };
      suc |= NewHook(hp, "monobdwgcdll");
    }
    return suc;
  }
}
bool mono::attach_function()
{
  bool common = monocommon::hook_mono_il2cpp();
  return common;
}