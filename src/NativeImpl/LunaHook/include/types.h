#pragma once

class WinMutex // Like CMutex but works with scoped_lock
{
public:
	WinMutex(std::wstring name = L"", LPSECURITY_ATTRIBUTES sa = nullptr) : m(CreateMutexW(sa, FALSE, name.empty() ? NULL : name.c_str())) {}
	void lock()
	{
		if (m)
			WaitForSingleObject(m, INFINITE);
	}
	void unlock()
	{
		if (m)
			ReleaseMutex(m);
	}

private:
	AutoHandle<> m;
};

inline SECURITY_ATTRIBUTES allAccess = std::invoke([] // allows non-admin processes to access kernel objects made by admin processes
												   {
	static SECURITY_DESCRIPTOR sd = {};
	InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
	SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
	return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE }; });
struct HookParam;
struct hook_context
{
#ifndef _WIN64
	uintptr_t _eflags; // pushfd
	uintptr_t edi,	   // pushad
		esi,
		ebp,
		esp,
		ebx,
		edx,
		ecx, // this
		eax; // 0x28

#else
	uintptr_t r15,
		r14,
		r13,
		r12,
		r11,
		r10,
		r9,
		r8,
		rdi,
		rsi,
		rbp,
		rsp,
		rdx,
		rcx,
		rbx,
		rax;
#endif
	uintptr_t eflags; // pushaf
	union
	{
		uintptr_t stack[1]; // beginning of the runtime stack
		uintptr_t retaddr;
		BYTE base[1];
	};
	void toPCONTEXT(PCONTEXT pcontext)
	{
#ifndef _WIN64
		pcontext->Eax = eax;
		pcontext->Ecx = ecx;
		pcontext->Edx = edx;
		pcontext->Ebx = ebx;
		pcontext->Esp = esp;
		pcontext->Ebp = ebp;
		pcontext->Esi = esi;
		pcontext->Edi = edi;
		pcontext->EFlags = eflags;
#else
		pcontext->Rax = rax;
		pcontext->Rbx = rbx;
		pcontext->Rcx = rcx;
		pcontext->Rdx = rdx;
		pcontext->Rsp = rsp;
		pcontext->Rbp = rbp;
		pcontext->Rsi = rsi;
		pcontext->Rdi = rdi;
		pcontext->R8 = r8;
		pcontext->R9 = r9;
		pcontext->R10 = r10;
		pcontext->R11 = r11;
		pcontext->R12 = r12;
		pcontext->R13 = r13;
		pcontext->R14 = r14;
		pcontext->R15 = r15;
		pcontext->EFlags = eflags;
#endif
	}
	static hook_context fromPCONTEXT(PCONTEXT pcontext)
	{
		hook_context context;
#ifndef _WIN64
		context.eax = pcontext->Eax;
		context.ecx = pcontext->Ecx;
		context.edx = pcontext->Edx;
		context.ebx = pcontext->Ebx;
		context.esp = pcontext->Esp;
		context.ebp = pcontext->Ebp;
		context.esi = pcontext->Esi;
		context.edi = pcontext->Edi;
		context.eflags = pcontext->EFlags;
		context.retaddr = *(DWORD *)pcontext->Esp;
#else
		context.rax = pcontext->Rax;
		context.rbx = pcontext->Rbx;
		context.rcx = pcontext->Rcx;
		context.rdx = pcontext->Rdx;
		context.rsp = pcontext->Rsp;
		context.rbp = pcontext->Rbp;
		context.rsi = pcontext->Rsi;
		context.rdi = pcontext->Rdi;
		context.r8 = pcontext->R8;
		context.r9 = pcontext->R9;
		context.r10 = pcontext->R10;
		context.r11 = pcontext->R11;
		context.r12 = pcontext->R12;
		context.r13 = pcontext->R13;
		context.r14 = pcontext->R14;
		context.r15 = pcontext->R15;
		context.eflags = pcontext->EFlags;
		context.retaddr = *(DWORD64 *)pcontext->Rsp;
#endif
		return context;
	}
	static hook_context *fromBase(uintptr_t lpDataBase)
	{
		return (hook_context *)(lpDataBase - offsetof(hook_context, base));
	}
	constexpr uintptr_t &argof(int idx)
	{
#ifdef _WIN64
		switch (idx)
		{
		case 1:
			return rcx;
		case 2:
			return rdx;
		case 3:
			return r8;
		case 4:
			return r9;
		default:
			return stack[idx];
		}
#else
		return stack[idx];
#endif
	}
	constexpr uintptr_t &argof_thiscall(int idx = 0)
	{
#ifdef _WIN64
		return argof(idx + 1);
#else
		if (idx == 0)
		{
			return ecx;
		}
		return argof(idx);
#endif
	}
	constexpr uintptr_t &last_ret_val()
	{
#ifdef _WIN64
		return rax;
#else
		return eax;
#endif
	}
	uintptr_t &argof(int idx, const HookParam &hp);
	uintptr_t &argof(int idx, const HookParam *hp);
	uintptr_t &offset(int offset, const HookParam &hp);
	uintptr_t &offset(int offset, const HookParam *hp);
};
#define ___baseoffset (int)offsetof(hook_context, base)
#define regoffset(reg) ((int)offsetof(hook_context, reg) - ___baseoffset)
#define stackoffset(idx) ((int)offsetof(hook_context, stack[idx]) - ___baseoffset)
#define GETARG(i) (((int)(size_t)&reinterpret_cast<char const volatile &>((((hook_context *)0)->argof(i)))) - ___baseoffset)

// jichi 3/7/2014: Add guessed comment

#define ALIGNPTR(Y, X) \
	union              \
	{                  \
		##Y;           \
		##X;           \
	};

enum class JITTYPE
{
	PC, // not a jit
	YUZU,
	PPSSPP,
	VITA3K,
	RPCS3,
	UNITY,
	PCSX2,
};
struct TextBuffer;
struct HookParam
{
	// address需要在host和hook之间传递，因此不能用uintptr_t
	uint64_t address; // absolute or relative address
	int offset,		  // offset of the data in the memory
		index,		  // deref_offset1
		split,		  // offset of the split character
		split_index;  // deref_offset2

	wchar_t module[MAX_MODULE_SIZE];

	char function[MAX_MODULE_SIZE];
	uint64_t type;							   // flags
	UINT codepage;							   // text encoding
	short length_offset;					   // index of the string length
	ALIGNPTR(uint64_t __1, uintptr_t padding); // padding before string
	ALIGNPTR(uint64_t __12, uintptr_t user_value);
	ALIGNPTR(uint64_t __2, void (*text_fun)(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split))
	ALIGNPTR(uint64_t __3, void (*filter_fun)(TextBuffer *buffer, HookParam *hp)); // jichi 10/24/2014: Add filter function. Return false to skip the text
	ALIGNPTR(uint64_t __7, void (*embed_fun)(hook_context *context, TextBuffer buffer, HookParam *hp));
	uint64_t embed_hook_font;
	ALIGNPTR(uint64_t __9, const wchar_t *lineSeparator);
	char name[HOOK_NAME_SIZE];
	wchar_t hookcode[HOOKCODE_LEN];
	DWORD detectedCodepage = 0;
	HookParam()
	{
		ZeroMemory(this, sizeof(HookParam));
	}
	uint32_t emu_addr;
	JITTYPE jittype;
	inline bool isAscii() { return (type & (CODEC_UTF16 | CODEC_UTF32 | CODEC_UTF8)) == 0; };
};

struct ThreadParam
{
	bool operator==(ThreadParam other) const { return processId == other.processId && addr == other.addr && ctx == other.ctx && ctx2 == other.ctx2; }
	DWORD processId;
	uint64_t addr;
	uint64_t ctx;  // The context of the hook: by default the first value on stack, usually the return address
	uint64_t ctx2; // The subcontext of the hook: 0 by default, generated in a method specific to the hook
};

struct SearchParam
{
	BYTE pattern[PATTERN_SIZE] = {x64 ? 0xcc : 0x55, x64 ? 0xcc : 0x8b, x64 ? 0x48 : 0xec, 0x89}; // pattern in memory to search for
	int address_method = 0;
	int search_method = 0;
	int length = x64 ? 4 : 3, // length of pattern (zero means this SearchParam is invalid and the default should be used)
		offset = x64 ? 2 : 0, // offset from start of pattern to add hook
		searchTime = 30000,	  // ms
		maxRecords = 100000,
		codepage = SHIFT_JIS;
	// uintptr_t padding = 0, // same as hook param padding
	//	minAddress = 0, maxAddress = (uintptr_t)-1; // hook all functions between these addresses (used only if both modules empty)
	ALIGNPTR(uint64_t __1, intptr_t padding = 0);
	ALIGNPTR(uint64_t __2, uintptr_t minAddress = 0);
	ALIGNPTR(uint64_t __3, uintptr_t maxAddress = (uintptr_t)-1);
	wchar_t boundaryModule[MAX_MODULE_SIZE] = {}; // hook all functions within this module (middle priority)
	wchar_t exportModule[MAX_MODULE_SIZE] = {};	  // hook the exports of this module (highest priority)
	wchar_t text[PATTERN_SIZE] = {};			  // text to search for
	bool isjithook;
	wchar_t sharememname[64] = {0};
	ALIGNPTR(uint64_t __4, size_t sharememsize = 0);
};
enum SUPPORT_LANG;
enum LANG_STRINGS_HOOK;

struct TextOutput_T
{
	ThreadParam tp;
	HookParam hp;
	uint64_t type;
	BYTE data[0];
};

enum
{
	TEXT_BUFFER_SIZE = PIPE_BUFFER_SIZE - sizeof(TextOutput_T)
};

struct TextBuffer
{
	BYTE *const data;
	size_t size;
	template <typename CharT>
	void from(const CharT *c)
	{
		if (!c)
			return;
		size = strlenEx(c) * sizeof(CharT);
		if (size)
			strncpyEx((CharT *)data, c, TEXT_BUFFER_SIZE);
	}
	template <typename StringT, typename = std::enable_if_t<!std::is_pointer_v<StringT>>>
	void from(const StringT &c)
	{
		size = min(TEXT_BUFFER_SIZE, strSize(c));
		if (size)
			memcpy(data, c.data(), size);
	}
	template <typename AddrT>
	void from(const AddrT ptr, size_t t)
	{
		size = min(TEXT_BUFFER_SIZE, t);
		if (size && ptr)
			memcpy(data, (void *)ptr, size);
	}
	template <typename T>
	void from_t(const T tm)
	{
		size = sizeof(T);
		*(T *)data = tm;
	}
	std::string_view viewA()
	{
		return std::string_view((char *)data, size);
	}
	std::wstring_view viewW()
	{
		return std::wstring_view((wchar_t *)data, size / 2);
	}
	std::u32string_view viewU()
	{
		return std::u32string_view((char32_t *)data, size / 4);
	}
	std::string strA()
	{
		return std::string((char *)data, size);
	}
	std::u32string strU()
	{
		return std::u32string((char32_t *)data, size / sizeof(char32_t));
	}
	std::wstring strW()
	{
		return std::wstring((wchar_t *)data, size / 2);
	}
	std::wstring strAW(UINT cp = 932)
	{
		return StringToWideString(viewA(), cp).value_or(L"");
	}
	void fromWA(const std::wstring &ws, UINT cp = 932)
	{
		from(WideStringToString(ws, cp));
	}
	void clear()
	{
		size = 0;
	}
};
enum class Displaymode
{
	TRANS,
	ORI_TRANS,
	TRANS_ORI
};
struct CommonSharedMem
{
	float FontSizeRelative = 1.;
	UINT32 waittime;
	Displaymode displaymode;
	uint64_t hash;
	wchar_t text[1000];
	bool fontCharSetEnabled;
	UINT8 fontCharSet;
	wchar_t fontFamily[100];
	UINT codepage;
	bool fastskipignore;
	bool clearText;
	bool tryvehhook = false;
	struct
	{
		bool use;
		ThreadParam tp;
	} embedtps[32];
};