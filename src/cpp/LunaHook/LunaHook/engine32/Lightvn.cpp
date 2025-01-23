﻿#include "Lightvn.h"

// https://vndb.org/r?f=fwLight_evn-

void SpecialHookLightvnA(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
	//[Parser::ReadScriptBreak] curline:'"「次は[水縹]<みはなだ>駅、水縹駅――お出口は左側です」'

	//[PARSETOKENS] line:.始発でここまで来ているのは俺くらいなものだろう。
	//(scenario:T) (script:00.txt, lineNo:30)
	//[PARSETOKENS] line:"電車には俺のほかに数人乗っている程度。\c
	//(scenario:F) (script:00.txt, lineNo:29)
	std::string s = (char *)context->stack[1];
	// std::regex _1("\\[Parser::ReadScriptBreak\\] curline:'[\"\\.]([\\s\\S]*?)'([\\s\\S]*?)");//对于多行显示不全
	// std::regex _2("\\[PARSETOKENS\\] line:([\\s\\S]*?)\\(scenario:([\\s\\S]*?)");
	std::regex _2("\\[PARSETOKENS\\] line:[-\"\\.]+([\\s\\S]*?)\\(scenario:([\\s\\S]*?)");
	std::regex _3("\\[PARSETOKENS\\] line:([\\s\\S]*?)backlogName = '([\\s\\S]*?)'([\\s\\S]*?)");
	std::smatch match;
	std::string _;
	if (std::regex_match(s, match, _2))
	{
		_ = std::string(match[1]);
		_ = std::regex_replace(_, std::regex("\\[(.*?)\\]<(.*?)>"), "$1");
		strReplace(_, "\\c", "");
		strReplace(_, "\\w", "");
		*split = 1;
	}
	else if (std::regex_match(s, match, _3))
	{
		_ = std::string(match[2]);
		*split = 2;
	}
	buffer->from(_);
}

void SpecialHookLightvnW(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
	std::wstring s((wchar_t *)context->stack[1]);
	std::wregex _2(L"\\[PARSETOKENS\\] line:[-\"\\.]+([\\s\\S]*?)\\(scenario:([\\s\\S]*?)");
	std::wregex _3(L"\\[PARSETOKENS\\] line:([\\s\\S]*?)backlogName = '([\\s\\S]*?)'([\\s\\S]*?)");
	std::wsmatch match;
	std::wstring _;
	if (std::regex_match(s, match, _2))
	{
		_ = std::wstring(match[1]);
		_ = std::regex_replace(_, std::wregex(L"\\[(.*?)\\]<(.*?)>"), L"$1");
		strReplace(_, L"\\c", L"");
		strReplace(_, L"\\w", L"");
		*split = 1;
	}
	else if (std::regex_match(s, match, _3))
	{
		_ = std::wstring(match[2]);
		*split = 2;
	}
	buffer->from(_);
}
bool InsertLightvnHook()
{
	wcscpy_s(spDefault.boundaryModule, L"Engine.dll");
	/*// This hooking method also has decent results, but hooking OutputDebugString seems better
	const BYTE bytes[] = { 0x8d, 0x55, 0xfe, 0x52 };
	for (auto addr : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE_READ, (uintptr_t)GetModuleHandleW(L"Engine.dll")))
	{
		HookParam hp;
		hp.address = MemDbg::findEnclosingAlignedFunction(addr);
		hp.type = CODEC_UTF16 | USING_STRING;
		hp.offset=stackoffset(1);
		NewHook(hp, "Light.vn");
	}*/
	VirtualProtect(IsDebuggerPresent, 2, PAGE_EXECUTE_READWRITE, DUMMY);
	*(uint16_t *)IsDebuggerPresent = 0xc340; // asm for inc eax ret
	HookParam hp;
	hp.address = (uintptr_t)OutputDebugStringA;
	hp.type = CODEC_UTF8 | USING_STRING;
	hp.offset = stackoffset(1);
	hp.text_fun = SpecialHookLightvnA;
	auto succ = NewHook(hp, "OutputDebugStringA");
	hp.address = (uintptr_t)OutputDebugStringW;
	hp.type = CODEC_UTF16 | USING_STRING;
	hp.text_fun = SpecialHookLightvnW;
	succ |= NewHook(hp, "OutputDebugStringW");
	return succ;
}
namespace
{
	bool _1()
	{
		auto [minAddress, maxAddress] = Util::QueryModuleLimits(GetModuleHandle(L"Engine.dll"));
		const BYTE BYTES[] = {
			0x55, 0x8b, 0xec,
			0x83, 0xec, XX,
			0x8b, XX, 0x10,
			0x89, XX, XX,
			0x8b, XX, 0x0c,
			0x89, XX, XX,
			0x8b, XX, 0x08,
			0x89, XX, XX,
			0xc7, 0x45, XX, 0x00, 0x00, 0x00, 0x00,
			0x83, 0x7d, XX, 0x00,
			0x74, XX,
			0x8b, 0x45, XX,
			0x66, 0x8b, 0x08,
			0x66, 0x89, 0x4d, XX,
			0x8b, XX, XX,
			0x66, XX, XX,
			0x66, XX, XX, XX,
			0x66, XX, XX, XX,
			0x66, XX, XX, XX};
		auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), minAddress, maxAddress);
		if (!addr)
			return false;
		auto addrs = findxref_reverse_checkcallop(addr, minAddress, maxAddress, 0xe8);
		if (addrs.size() != 3)
			return false;
		addr = addrs[0];
		addr = findfuncstart(addr);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr;
		hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
		{
			static std::wstring last;

			auto s = buffer->strW();
			if (startWith(s, L"\"-"))
				return buffer->clear();
			if (!(startWith(s, L"\"") || startWith(s, L".") || startWith(s, L"-\".")))
				return buffer->clear();

			if (startWith(s, L"\"") || startWith(s, L"."))
				s = s.substr(1);
			else if (startWith(s, L"-\"."))
				s = s.substr(3);
			if (s == L"イン" || s == L"拡大" || s == L"アウト" || s == L"インアウト" || startWith(s, L"イン ") || startWith(s, L"拡大 ") || startWith(s, L"インアウト ") || startWith(s, L"アウト "))
				return buffer->clear();

			if (s == last)
				return buffer->clear();
			last = s;
			buffer->from(s);
		};
		hp.offset = stackoffset(1);
		hp.type = CODEC_UTF16 | USING_STRING;
		return NewHook(hp, "Light.VN");
	}
}
namespace
{
	bool veryold()
	{
		// https://vndb.org/v25877
		//  私のアリス

		/*
		Concurrency::details::_CancellationTokenRegistration *__thiscall sub_10093E10(
		Concurrency::details::_CancellationTokenRegistration *this,
		Concurrency::details::_CancellationTokenRegistration *a2)
{
  int v2; // eax
  int v4; // [esp-4h] [ebp-Ch]
  char v6; // [esp+6h] [ebp-2h] BYREF
  char v7; // [esp+7h] [ebp-1h] BYREF

  if ( this != a2 )
  {
	v4 = sub_101095C0(&v7);
	v2 = sub_101095C0(&v6);
	sub_10088180(v2, v4);
	std::wstring::assign(a2);
  }
  return this;
}
		*/
		auto [minAddress, maxAddress] = Util::QueryModuleLimits(GetModuleHandle(L"Engine.dll"));
		const BYTE BYTES[] = {
			0x55, 0x8b, 0xec,
			0x83, 0xec, 0x08,
			0x89, 0x4d, 0xf8,
			0x8b, 0x45, 0xf8,
			0x3b, 0x45, 0x08,
			0x74, XX,
			0x8d, 0x4d, 0xff,
			0x51,
			0x8b, 0x4d, 0x08,
			0xe8, XX4,
			0x50,
			0x8d, 0x55, 0xfe,
			0x52,
			0x8b, 0x4d, 0xf8,
			0xe8, XX4,
			0x50,
			0xe8, XX4,
			0x83, 0xc4, 0x08,
			0x0f, 0xb6, 0xc0,
			0x85, 0xc0,
			0x74, XX,
			0x33, 0xc9,
			0x74, XX,
			0x6a, 0x00,
			0x6a, 0x01};
		auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), minAddress, maxAddress);
		if (!addr)
			return false;
		HookParam hp;
		hp.address = addr;
		hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
		{
			if (context->stack[1] != context->THISCALLTHIS)
			{
				buffer->from(((TextUnionW *)context->stack[1])->getText());
			}
		};
		hp.type = USING_STRING | CODEC_UTF16;
		return NewHook(hp, "Light.VN");
	}
}
bool Lightvn::attach_function()
{
	return InsertLightvnHook() | (_1() || veryold());
}