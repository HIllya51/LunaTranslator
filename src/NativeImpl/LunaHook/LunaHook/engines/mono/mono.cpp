#include "mono.h"
#include "mono/monocommon.hpp"
#if 0
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
      if (!addr)
        continue;

      ConsoleOutput("monobdwgcdll %p", addr);
      HookParam hp;
      hp.address = addr + 4;
      hp.offset = regoffset(rcx);
      hp.type = CODEC_UTF16 | USING_STRING;
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto str = std::wstring_view((LPWSTR)context->rcx);
        *split = str.find(L"OnShowComplete") != str.npos;
        buffer->from(str);
      };
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        std::wstring str = buffer->strW();
        if (str.find(L"OnShowComplete") != str.npos)
        {
          str = re::sub(str, L"\n");
          std::wregex reg1(L"\\((.*?)\\)");
          std::wsmatch match;
          std::regex_search(str, match, reg1);
          auto result1 = match[1].str();

          std::regex_search(str, match, std::wregex(L" Text:(.*?)Next:(.*?)"));
          result1 = match[1].str();
          buffer->from(result1);
        }
      };
      suc |= NewHook(hp, "monobdwgcdll");
    }
    return suc;
  }
}
#endif
#if 0
bool monobdwgc()
{

	HMODULE module = GetModuleHandleW(L"mono-2.0-bdwgc.dll");
	if (module == 0)
		return false;
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	BYTE bytes[] = {
		0x3D, 0x00, 0x00, 0x01, 0x00,
		0x73, XX,
		0xb8, 0x03, 0x00, 0x00, 0x00,
		0xEB, XX};
	auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, minAddress, maxAddress);
	auto succ = false;
	for (auto addr : addrs)
	{
		ConsoleOutput("monobdwgcdll %p", addr);
		HookParam hp;
		hp.address = (DWORD)addr;
		hp.offset = regoffset(eax);
		hp.type = CODEC_UTF16 | NO_CONTEXT;
		succ |= NewHook(hp, "monobdwgcdll");
	}
	return succ;
}
bool monodll()
{

	HMODULE module = GetModuleHandleW(L"mono.dll");
	if (module == 0)
		return false;
	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	BYTE bytes[] = {
		0x81, 0xFB, XX4,
		0x73};
	auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, minAddress, maxAddress);
	auto succ = false;
	for (auto addr : addrs)
	{
		ConsoleOutput("monodll %p", addr);
		HookParam hp;
		hp.address = (DWORD)addr;
		hp.offset = regoffset(ebx);
		hp.type = CODEC_UTF16 | NO_CONTEXT;
		succ |= NewHook(hp, "monodll");
	}
	return succ;
}

#endif
bool mono::attach_function_()
{
  return monocommon::hook_mono_il2cpp();
}