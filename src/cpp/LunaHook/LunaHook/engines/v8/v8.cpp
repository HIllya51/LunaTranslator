#include "v8.h"
#include "osversion.hpp"
int makehttpgetserverinternal();
const wchar_t *LUNA_CONTENTBYPASS(const wchar_t *_);
#define MAGIC_SEND "\x01LUNAFROMJS\x01"
#define MAGIC_RECV "\x01LUNAFROMHOST\x01"
namespace
{
	constexpr auto magicsend = WIDEN(MAGIC_SEND);
	constexpr auto magicrecv = WIDEN(MAGIC_RECV);
	constexpr auto magicsend_A = MAGIC_SEND;
	constexpr auto magicrecv_A = MAGIC_RECV;
}
namespace
{
	bool useclipboard = false;
	bool usehttp = true;
	int usehttp_port = 0;
}
namespace
{

	void parsebefore(wchar_t *text, HookParam *hp, uintptr_t *split, TextBuffer *buffer)
	{
		if (startWith(text, magicsend))
		{
			text += wcslen(magicsend);
			auto spl = wcschr(text, L'\x03');
			strcpy(hp->name, wcasta(std::wstring(text, spl - text)).c_str());
			text = spl + 1;
			spl = wcschr(text, L'\x04');
			*split = std::stoi(std::wstring(text, spl - text));
			text = spl + 1;
			auto embedable = wcschr(text, L'\x02');
			auto isembedabl = std::stoi(std::wstring(text, embedable - text));
			if (isembedabl)
				hp->type |= EMBED_ABLE;
			else
				hp->type &= ~EMBED_ABLE;
			text = embedable + 1;
			buffer->from(text);
		}
	}
	std::wstring parseafter(std::wstring_view view)
	{
		std::wstring transwithfont = magicrecv;
		transwithfont += commonsharedmem->fontFamily;
		transwithfont += L'\x02';
		transwithfont += view;
		return transwithfont;
	}
}
namespace
{
	bool hookClipboard()
	{
		HookParam hp;
		hp.address = (uintptr_t)SetClipboardData;
		hp.type = USING_STRING | NO_CONTEXT | CODEC_UTF16 | EMBED_ABLE;
		hp.text_fun = [](hook_context *context, HookParam *hp, auto *buffer, uintptr_t *split)
		{
			HGLOBAL hClipboardData = (HGLOBAL)context->argof(2);
			parsebefore((wchar_t *)GlobalLock(hClipboardData), hp, split, buffer);
			GlobalUnlock(hClipboardData);
		};
		hp.embed_fun = [](hook_context *s, TextBuffer buffer)
		{
			std::wstring transwithfont = parseafter(buffer.viewW());
			HGLOBAL hClipboardData = GlobalAlloc(GMEM_MOVEABLE, transwithfont.size() * 2 + 2);
			auto pchData = (wchar_t *)GlobalLock(hClipboardData);
			wcscpy(pchData, (wchar_t *)transwithfont.c_str());
			GlobalUnlock(hClipboardData);
			s->argof(2) = (uintptr_t)hClipboardData;
		};
		return NewHook(hp, "nwjs/electron rpgmakermv/tyranoscript");
	}
}
namespace
{
	bool hook_LUNA_CONTENTBYPASS()
	{
		HookParam hp;
		hp.address = (uintptr_t)LUNA_CONTENTBYPASS;
		hp.type = USING_STRING | NO_CONTEXT | CODEC_UTF16 | EMBED_ABLE;
		hp.text_fun = [](hook_context *context, HookParam *hp, auto *buffer, uintptr_t *split)
		{
			parsebefore((wchar_t *)context->argof(1), hp, split, buffer);
		};
		hp.embed_fun = [](hook_context *s, TextBuffer buffer)
		{
			std::wstring transwithfont = parseafter(buffer.viewW());
			s->argof(1) = (uintptr_t)allocateString(transwithfont);
		};
		return NewHook(hp, "nwjs/electron rpgmakermv/tyranoscript");
	}
}
namespace v8script
{
	typedef void (*RequestInterrupt_callback)(void *, void *);
#ifndef _WIN64
#define THISCALL __thiscall
#define fnRequestInterrupt "?RequestInterrupt@Isolate@v8@@QAEXP6AXPAV12@PAX@Z1@Z"
#define fnNewFromUtf8_maybelocal "?NewFromUtf8@String@v8@@SA?AV?$MaybeLocal@VString@v8@@@2@PAVIsolate@2@PBDW4NewStringType@2@H@Z"
#define fnNewFromUtf8_local "?NewFromUtf8@String@v8@@SA?AV?$Local@VString@v8@@@2@PAVIsolate@2@PBDW4NewStringType@12@H@Z"
#define fnGetCurrentContext "?GetCurrentContext@Isolate@v8@@QAE?AV?$Local@VContext@v8@@@2@XZ"
#define fnCompile_local "?Compile@Script@v8@@SA?AV?$Local@VScript@v8@@@2@V?$Handle@VString@v8@@@2@PAVScriptOrigin@2@@Z"
#define fnCompile_local_2 "?Compile@Script@v8@@SA?AV?$Local@VScript@v8@@@2@V?$Local@VString@v8@@@2@PAVScriptOrigin@2@@Z"
#define fnCompile_local_3 "?Compile@Script@v8@@SA?AV?$Local@VScript@v8@@@2@V?$Handle@VString@v8@@@2@PAVScriptOrigin@2@PAVScriptData@2@0@Z"
#define fnRun_local "?Run@Script@v8@@QAE?AV?$Local@VValue@v8@@@2@XZ"
#define fnCompile_maylocal "?Compile@Script@v8@@SA?AV?$MaybeLocal@VScript@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VString@v8@@@2@PAVScriptOrigin@2@@Z"
#define fnRunv_maylocal "?Run@Script@v8@@QAE?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@@Z"

#else
#define THISCALL
#define fnRequestInterrupt "?RequestInterrupt@Isolate@v8@@QEAAXP6AXPEAV12@PEAX@Z1@Z"
#define fnNewFromUtf8_maybelocal "?NewFromUtf8@String@v8@@SA?AV?$MaybeLocal@VString@v8@@@2@PEAVIsolate@2@PEBDW4NewStringType@2@H@Z"
#define fnNewFromUtf8_local "?NewFromUtf8@String@v8@@SA?AV?$Local@VString@v8@@@2@PEAVIsolate@2@PEBDW4NewStringType@12@H@Z"
#define fnGetCurrentContext "?GetCurrentContext@Isolate@v8@@QEAA?AV?$Local@VContext@v8@@@2@XZ"
#define fnCompile_local "?Compile@Script@v8@@SA?AV?$Local@VScript@v8@@@2@V?$Handle@VString@v8@@@2@PEAVScriptOrigin@2@@Z"
#define fnCompile_local_2 fnCompile_local
#define fnCompile_local_3 fnCompile_local
#define fnRun_local "?Run@Script@v8@@QEAA?AV?$Local@VValue@v8@@@2@XZ"
#define fnCompile_maylocal "?Compile@Script@v8@@SA?AV?$MaybeLocal@VScript@v8@@@2@V?$Local@VContext@v8@@@2@V?$Local@VString@v8@@@2@PEAVScriptOrigin@2@@Z"
#define fnRunv_maylocal "?Run@Script@v8@@QEAA?AV?$MaybeLocal@VValue@v8@@@2@V?$Local@VContext@v8@@@2@@Z"

#endif
	typedef void *(THISCALL *GetCurrentContextt)(void *, void *);
	typedef void *(THISCALL *Run_local_t)(void *, void *);
	typedef void *(THISCALL *Run_maybelocal_t)(void *, void *, void *);
	typedef void *(THISCALL *RequestInterruptt)(void *, RequestInterrupt_callback, void *);

	typedef void *(*NewFromUtf8t)(void *, void *, const char *, int, int);
	typedef void *(*Compile_local_t)(void *, void *, void *, void *, void *);
	typedef void *(*Compile_maybelocal_t)(void *, void *, void *, void *);
	RequestInterruptt RequestInterrupt;
	NewFromUtf8t NewFromUtf8 = 0, NewFromUtf8v2, NewFromUtf8v1;
	GetCurrentContextt GetCurrentContext;
	Compile_local_t Compile_local;
	Compile_maybelocal_t Compile_maybelocal;
	Run_local_t Run_local;
	Run_maybelocal_t Run_maybelocal;
	void _interrupt_function(void *isolate, void *)
	{
		void *context;
		void *v8string;
		void *script;
		void *useless;
		ConsoleOutput("isolate %p", isolate);
		GetCurrentContext(isolate, &context);
		ConsoleOutput("context %p", context);
		if (!context)
			return;
		int is_packed = 0;
		if (auto moduleFileName = getModuleFilename())
		{

			AutoHandle hFile = CreateFile(moduleFileName.value().c_str(), FILE_READ_ATTRIBUTES, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
			if (hFile)
			{
				LARGE_INTEGER fileSize;
				if (GetFileSizeEx(hFile, &fileSize))
				{
					if (fileSize.QuadPart > 1024 * 1024 * 200)
					{
						// 200mb
						is_packed = 1;
					}
				}
			}
		}

		std::string lunajspatch = LoadResData(L"lunajspatch", L"JSSOURCE");
		strReplace(lunajspatch, "IS_PACKED", std::to_string(is_packed));
		strReplace(lunajspatch, "IS_USECLIPBOARD", std::to_string(useclipboard));
		strReplace(lunajspatch, "INTERNAL_HTTP_PORT", std::to_string(usehttp_port));
		NewFromUtf8(&v8string, isolate, lunajspatch.c_str(), 1, -1);
		ConsoleOutput("v8string %p", v8string);
		if (!v8string)
			return;
		if (NewFromUtf8v1)
		{
			(Compile_local)(&script, v8string, 0, 0, 0);
			ConsoleOutput("script %p", script);
			if (!script)
				return;
			(Run_local)(script, &useless);
			ConsoleOutput("useless %p", useless);
		}
		else if (NewFromUtf8v2)
		{
			(Compile_maybelocal)(&script, context, v8string, 0);
			ConsoleOutput("script %p", script);
			if (!script)
				return;
			(Run_maybelocal)(script, &useless, context);
			ConsoleOutput("useless %p", useless);
		}
	}
	bool init_v8_functions(HMODULE hmodule)
	{
		RequestInterrupt = (decltype(RequestInterrupt))GetProcAddress(hmodule, fnRequestInterrupt);

		NewFromUtf8v2 = (decltype(NewFromUtf8))GetProcAddress(hmodule, fnNewFromUtf8_maybelocal);
		NewFromUtf8v1 = (decltype(NewFromUtf8))GetProcAddress(hmodule, fnNewFromUtf8_local);

		GetCurrentContext = (decltype(GetCurrentContext))GetProcAddress(hmodule, fnGetCurrentContext);
		if (!GetCurrentContext)
			return false;
		if (NewFromUtf8v1)
		{
			NewFromUtf8 = NewFromUtf8v1;
			Compile_local = (decltype(Compile_local))GetProcAddress(hmodule, fnCompile_local);
			if (!Compile_local)
				Compile_local = (decltype(Compile_local))GetProcAddress(hmodule, fnCompile_local_2);
			if (!Compile_local)
				Compile_local = (decltype(Compile_local))GetProcAddress(hmodule, fnCompile_local_3);
			Run_local = (decltype(Run_local))GetProcAddress(hmodule, fnRun_local);
			if (!(Run_local && Compile_local))
				return false;
		}
		else if (NewFromUtf8v2)
		{
			NewFromUtf8 = NewFromUtf8v2;
			Compile_maybelocal = (decltype(Compile_maybelocal))GetProcAddress(hmodule, fnCompile_maylocal);
			Run_maybelocal = (decltype(Run_maybelocal))GetProcAddress(hmodule, fnRunv_maylocal);
			if (!(Run_maybelocal && Compile_maybelocal))
				return false;
		}
		else
			return false;

		return true;
	}
	bool v8runscript_isolate(void *isolate)
	{
		if (!isolate)
			return false;
		if (RequestInterrupt)
			RequestInterrupt(isolate, _interrupt_function, nullptr);
		else
			_interrupt_function(isolate, nullptr);
		return true;
	}

	void v8runscript_isolate_bypass(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{

		hp->type = HOOK_EMPTY;
		hp->text_fun = nullptr;

		auto isolate = (void *)context->argof(2); // 测试正确，且和v8::Isolate::GetCurrent结果相同
		v8runscript_isolate(isolate);
	}
	void *v8getcurrisolate(HMODULE hmod)
	{
#ifndef _WIN64
#define fnGetCurrent "?GetCurrent@Isolate@v8@@SAPAV12@XZ"
#define fnTryGetCurrent "?TryGetCurrent@Isolate@v8@@SAPAV12@XZ"
#else
#define fnGetCurrent "?GetCurrent@Isolate@v8@@SAPEAV12@XZ"
#define fnTryGetCurrent "?TryGetCurrent@Isolate@v8@@SAPEAV12@XZ"
#endif
		void *GetCurrent;
		GetCurrent = GetProcAddress(hmod, fnGetCurrent);
		if (!GetCurrent)
			GetCurrent = GetProcAddress(hmod, fnTryGetCurrent);
		if (!GetCurrent)
			return 0;
		auto isolate = ((void *(*)())GetCurrent)();
		return isolate;
	}
	bool v8runscript(HMODULE _hmodule)
	{
		auto isolate = v8getcurrisolate(_hmodule);
		if (isolate)
			return v8runscript_isolate(isolate);
#ifndef _WIN64
#define fnisolategetters {"?New@Number@v8@@SA?AV?$Local@VNumber@v8@@@2@PEAVIsolate@2@N@Z", "?New@Number@v8@@SA?AV?$Local@VNumber@v8@@@2@PAVIsolate@2@N@Z", "?NewFromUtf8@String@v8@@SA?AV?$Local@VString@v8@@@2@PAVIsolate@2@PBDW4NewStringType@12@H@Z"}
#else
#define fnisolategetters {"?New@Integer@v8@@SA?AV?$Local@VInteger@v8@@@2@PEAVIsolate@2@H@Z", "?New@Number@v8@@SA?AV?$Local@VNumber@v8@@@2@PEAVIsolate@2@N@Z", "?New@Number@v8@@SA?AV?$Local@VNumber@v8@@@2@PAVIsolate@2@N@Z", "?NewFromUtf8@String@v8@@SA?AV?$Local@VString@v8@@@2@PEAVIsolate@2@PEBDW4NewStringType@12@H@Z", "?Utf8Length@String@v8@@QEBAHPEAVIsolate@2@@Z"}
#endif
		bool succ = false;
		for (auto fnisolategetter : fnisolategetters)
		{
			auto isolategetter = GetProcAddress(_hmodule, fnisolategetter);
			if (!isolategetter)
				continue;
			HookParam hp;
			hp.address = (uintptr_t)isolategetter;
			hp.text_fun = v8runscript_isolate_bypass;
			succ |= NewHook(hp, "isolategetter");
		}
		return succ;
	}
}
namespace
{
#ifndef _WIN64
#define v8StringLength "?Length@String@v8@@QBEHXZ"
#define v8StringWriteUtf8 "?WriteUtf8@String@v8@@QBEHPADHPAHH@Z"
#define v8StringUtf8Length "?Utf8Length@String@v8@@QBEHXZ"
#define v8StringWrite "?Write@String@v8@@QBEHPAGHHH@Z"
#define v8StringWriteIsolate "?Write@String@v8@@QBEHPAVIsolate@2@PAGHHH@Z"
#else
#define v8StringLength "?Length@String@v8@@QEBAHXZ"
#define v8StringWriteUtf8 "?WriteUtf8@String@v8@@QEBAHPEADHPEAHH@Z"
#define v8StringUtf8Length "?Utf8Length@String@v8@@QEBAHXZ"
#define v8StringWrite "?Write@String@v8@@QEBAHPEAGHHH@Z"
#define v8StringWriteIsolate "?Write@String@v8@@QEBAHPEAVIsolate@2@PEAGHHH@Z"
#endif
	uintptr_t WriteUtf8;
	uintptr_t Utf8Length;
	bool hookstring(HMODULE hm)
	{
		WriteUtf8 = (uintptr_t)GetProcAddress(hm, v8StringWriteUtf8);
		Utf8Length = (uintptr_t)GetProcAddress(hm, v8StringUtf8Length);
		if (WriteUtf8 == 0 || Utf8Length == 0)
			return false;

		HookParam hp;
		hp.type = USING_STRING | CODEC_UTF8;
		hp.text_fun =
			[](hook_context *context, HookParam *hp, auto *buffer, uintptr_t *split)
		{
			auto length = ((size_t(THISCALL *)(void *))Utf8Length)((void *)context->argof_thiscall(0));
			if (!length)
				return;
			auto u8str = new char[length + 1];
			int writen;
			((size_t(THISCALL *)(void *, char *, int, int *, int))WriteUtf8)((void *)context->argof_thiscall(0), u8str, length, &writen, 0);
			buffer->from(u8str, length);
		};
		hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
		{
			auto checks = {
				magicsend_A, // 防止煞笔选择这条内容
				magicrecv_A,
				R"(http://)",
				R"(https://)",
				R"(\\?\)", // 路径
			};
			if (std::any_of(checks.begin(), checks.end(), [&](auto str)
							{ return strstr((char *)buffer->buff, str) != 0; }))
			{
				return buffer->clear();
			}
		};
		bool succ = false;

		auto pv8StringLength = GetProcAddress(hm, v8StringLength);
		if (pv8StringLength)
		{

			hp.address = (uintptr_t)pv8StringLength;
			succ |= NewHook(hp, "v8::String::Length");
		}
		auto pv8StringWrite = GetProcAddress(hm, v8StringWrite);
		if (pv8StringWrite)
		{

			hp.address = (uintptr_t)pv8StringWrite;
			succ |= NewHook(hp, "v8::String::Write");
		}
		auto pv8StringWriteIsolate = GetProcAddress(hm, v8StringWriteIsolate);
		if (pv8StringWriteIsolate)
		{
			hp.address = (uintptr_t)pv8StringWriteIsolate;
			succ |= NewHook(hp, "v8::String::Write::isolate");
		}
		return succ;
	}
}
bool tryhookv8()
{
	for (const wchar_t *moduleName : {(const wchar_t *)NULL, L"node.dll", L"nw.dll"})
	{
		auto hm = GetModuleHandleW(moduleName);
		if (hm == 0)
			continue;
		auto stringsucc = hookstring(hm);
		auto funcsucc = v8script::init_v8_functions(hm);
		auto succ = stringsucc;
		if (funcsucc)
		{
			// useclipboard = !std::filesystem::exists(std::filesystem::path(getModuleFilename().value()).replace_filename("disable.clipboard"));
			// usehttp = !(GetOSVersion().IsleWinXP() || std::filesystem::exists(std::filesystem::path(getModuleFilename().value()).replace_filename("disable.http")));
			// if (usehttp)
			{
				usehttp_port = makehttpgetserverinternal();
				ConsoleOutput("%d %d", GetCurrentProcessId(), usehttp_port);
				hook_LUNA_CONTENTBYPASS();
				dont_detach = true;
			}
			// if (useclipboard)
			//{
			//	hookClipboard();
			// }
			// if (useclipboard || usehttp)
			{
				succ |= v8script::v8runscript(hm);
			}
		}
		if (stringsucc || funcsucc)
			return succ;
	}
	return false;
}
