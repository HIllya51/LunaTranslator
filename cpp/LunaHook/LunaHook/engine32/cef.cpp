#include "cef.h"
typedef wchar_t char16;

typedef struct _cef_string_wide_t
{
	wchar_t *str;
	size_t length;
	void (*dtor)(wchar_t *str);
} cef_string_wide_t;

typedef struct _cef_string_utf8_t
{
	char *str;
	size_t length;
	void (*dtor)(char *str);
} cef_string_utf8_t;

typedef struct _cef_string_utf16_t
{
	char16 *str;
	size_t length;
	void (*dtor)(char16 *str);
} cef_string_utf16_t;
static void hook_cef_string_utf16_t(hook_context *context, HookParam *hp, TextBuffer *buff, uintptr_t *split)
{
	if (auto p = (_cef_string_utf16_t *)context->stack[1])
	{
		buff->from(p->str, p->length);

		auto s = context->ecx;
		for (int i = 0; i < 0x10; i++) // traverse pointers until a non-readable address is met
			if (s && !::IsBadReadPtr((LPCVOID)s, sizeof(DWORD)))
				s = *(DWORD *)s;
			else
				break;
		if (!s)
			s = hp->address;
		if (hp->type & USING_SPLIT)
			*split = s;
	}
}
static void hook_cef_string_wide_t(hook_context *context, HookParam *hp, TextBuffer *buff, uintptr_t *split)
{
	if (auto p = (_cef_string_wide_t *)context->stack[1])
	{
		buff->from(p->str, p->length);

		auto s = context->ecx;
		for (int i = 0; i < 0x10; i++) // traverse pointers until a non-readable address is met
			if (s && !::IsBadReadPtr((LPCVOID)s, sizeof(DWORD)))
				s = *(DWORD *)s;
			else
				break;
		if (!s)
			s = hp->address;
		if (hp->type & USING_SPLIT)
			*split = s;
	}
}
static void hook_cef_string_utf8_t(hook_context *context, HookParam *hp, TextBuffer *buff, uintptr_t *split)
{
	if (auto p = (_cef_string_utf8_t *)context->stack[1])
	{
		buff->from(p->str, p->length);
		auto s = context->ecx;
		for (int i = 0; i < 0x10; i++) // traverse pointers until a non-readable address is met
			if (s && !::IsBadReadPtr((LPCVOID)s, sizeof(DWORD)))
				s = *(DWORD *)s;
			else
				break;
		if (!s)
			s = hp->address;
		if (hp->type & USING_SPLIT)
			*split = s;
	}
}
bool InsertlibcefHook(HMODULE module)
{
	if (!module)
		return false;
	bool ret = false;

	struct libcefFunction
	{ // argument indices start from 0 for SpecialHookMonoString, otherwise 1
		const char *functionName;
		size_t textIndex;						// argument index
		short lengthIndex;						// argument index
		unsigned long hookType;					// HookParam type
		decltype(HookParam::text_fun) text_fun; // HookParam::text_fun_t
	};

	HookParam hp;
	const libcefFunction funcs[] = {
		{"cef_string_utf8_set", 1, 0, USING_STRING | CODEC_UTF8 | NO_CONTEXT, NULL}, // ok
		{"cef_string_utf8_to_utf16", 1, 0, USING_STRING | CODEC_UTF8 | NO_CONTEXT, NULL},
		{"cef_string_utf8_to_wide", 1, 0, USING_STRING | CODEC_UTF8 | NO_CONTEXT, NULL}, // ok
		{"cef_string_utf8_clear", 0, 0, USING_STRING | CODEC_UTF8 | NO_CONTEXT, hook_cef_string_utf8_t},

		{"cef_string_utf16_set", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL},		   // ok
		{"cef_string_utf16_clear", 0, 0, USING_STRING | CODEC_UTF16, hook_cef_string_utf16_t}, // ok
		{"cef_string_utf16_to_utf8", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL},	   // ok
		{"cef_string_utf16_to_wide", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL},

		{"cef_string_ascii_to_utf16", 1, 0, USING_STRING | NO_CONTEXT, NULL},
		{"cef_string_ascii_to_wide", 1, 0, USING_STRING | NO_CONTEXT, NULL},

		{"cef_string_wide_set", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL}, // ok
		{"cef_string_wide_to_utf16", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL},
		{"cef_string_wide_to_utf8", 1, 0, USING_STRING | CODEC_UTF16 | NO_CONTEXT, NULL},
		{"cef_string_wide_clear", 0, 0, USING_STRING | CODEC_UTF16, hook_cef_string_wide_t}};
	for (auto func : funcs)
	{
		if (FARPROC addr = ::GetProcAddress(module, func.functionName))
		{
			if (!addr)
				continue;
			hp.address = (DWORD)addr;
			hp.type = func.hookType;
			hp.offset = func.textIndex * 4;
			hp.length_offset = func.lengthIndex * 4;
			hp.text_fun = (decltype(hp.text_fun))func.text_fun;
			ConsoleOutput("libcef: INSERT");
			ret |= NewHook(hp, func.functionName);
		}
	}

	if (!ret)
		ConsoleOutput("libcef: failed to find function address");
	return ret;
}
namespace
{
	void ceffileter(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strW();
		if (s == *(std::wstring *)(hp->user_value))
			return buffer->clear();
		*(std::wstring *)(hp->user_value) = s;
	};
}
bool libcefhook(HMODULE module)
{
	// https://vndb.org/v12297
	// 魔降ル夜ノ凜 Animation ダウンロード版

	auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
	ConsoleOutput("check v8libcefhook %p %p", minAddress, maxAddress);
	const BYTE bytes[] = {
		0x50,
		0x51,
		0x52,
		0x57,
		0xff, 0xd6,
		0x83, 0xc4, 0x10,
		0x8b, 0x4d, XX,
		0x89, 0xc6,
		0x31, 0xe9,
		0xe8, XX4,
		0x89, 0xF0,
		0x83, 0xC4, 0x18,
		0x5e,
		0x5f,
		0x5d,
		0xc3

	};
	// 対魔忍ユキカゼ２Animation
	const BYTE bytes2[] = {
		0x51,
		0x57,
		0x52,
		0x50,
		0xff, 0xd6,
		0x83, 0xc4, 0x10,
		0x8b, 0x4d, XX,
		0x89, 0xc6,
		0x31, 0xe9,
		0xe8, XX4,
		0x89, 0xF0,
		0x83, 0xC4, 0x18,
		0x5e,
		0x5f,
		0x5b,
		0x5d,
		0xc3

	};
	bool succ = false;
	for (auto addrs : {Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE_READWRITE, minAddress, maxAddress), Util::SearchMemory(bytes2, sizeof(bytes2), PAGE_EXECUTE_READWRITE, minAddress, maxAddress)})
	{
		for (auto addr : addrs)
		{
			HookParam hp;
			hp.address = addr + 4;
			hp.offset = stackoffset(1);
			hp.filter_fun = ceffileter;
			hp.lineSeparator = L"<br>";
			hp.length_offset = 2;
			hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
			hp.user_value = (DWORD) new std::wstring;
			succ |= NewHook(hp, "libcef");
		}
	}
	return succ;
}
bool cef::attach_function()
{
	auto hm = GetModuleHandleW(L"libcef.dll");

	if (!hm)
		return false;
	// InsertlibcefHook(hm);

	return libcefhook(hm);
}