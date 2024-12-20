
#include "MinHook.h"
extern WinMutex viewMutex;

// - Unnamed helpers -

namespace
{ // unnamed
#ifndef _WIN64
	BYTE common_hook[] = {
		0x9c,					// pushfd
		0x60,					// pushad
		0x9c,					// pushfd ; Artikash 11/4/2018: not sure why pushfd happens twice. Anyway, after this a total of 0x28 bytes are pushed
		0x8d, 0x44, 0x24, 0x28, // lea eax,[esp+0x28]
		0x50,					// push eax ; lpDatabase
		0xb9, 0, 0, 0, 0,		// mov ecx,@this
		0xbb, 0, 0, 0, 0,		// mov ebx,@TextHook::Send
		0xff, 0xd3,				// call ebx
		0x9d,					// popfd
		0x61,					// popad
		0x9d,					// popfd
		0x68, 0, 0, 0, 0,		// push @original
		0xc3					// ret ; basically absolute jmp to @original
	};
	int this_offset = 9, send_offset = 14, original_offset = 24;
#else
	BYTE common_hook[] = {
		0x9c,		// push rflags
		0x50,		// push rax
		0x53,		// push rbx
		0x51,		// push rcx
		0x52,		// push rdx
		0x54,		// push rsp
		0x55,		// push rbp
		0x56,		// push rsi
		0x57,		// push rdi
		0x41, 0x50, // push r8
		0x41, 0x51, // push r9
		0x41, 0x52, // push r10
		0x41, 0x53, // push r11
		0x41, 0x54, // push r12
		0x41, 0x55, // push r13
		0x41, 0x56, // push r14
		0x41, 0x57, // push r15
		// https://docs.microsoft.com/en-us/cpp/build/x64-calling-convention
		// https://stackoverflow.com/questions/43358429/save-value-of-xmm-registers
		0x48, 0x83, 0xec, 0x20,							// sub rsp,0x20
		0xf3, 0x0f, 0x7f, 0x24, 0x24,					// movdqu [rsp],xmm4
		0xf3, 0x0f, 0x7f, 0x6c, 0x24, 0x10,				// movdqu [rsp+0x10],xmm5
		0x48, 0x8d, 0x94, 0x24, 0xa8, 0x00, 0x00, 0x00, // lea rdx,[rsp+0xa8]
		0x48, 0xb9, 0, 0, 0, 0, 0, 0, 0, 0,				// mov rcx,@this
		0x48, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0,				// mov rax,@TextHook::Send
		0x48, 0x89, 0xe3,								// mov rbx,rsp
		0x48, 0x83, 0xe4, 0xf0,							// and rsp,0xfffffffffffffff0 ; align stack
		0xff, 0xd0,										// call rax
		0x48, 0x89, 0xdc,								// mov rsp,rbx
		0xf3, 0x0f, 0x6f, 0x6c, 0x24, 0x10,				// movdqu xmm5,XMMWORD PTR[rsp + 0x10]
		0xf3, 0x0f, 0x6f, 0x24, 0x24,					// movdqu xmm4,XMMWORD PTR[rsp]
		0x48, 0x83, 0xc4, 0x20,							// add rsp,0x20
		0x41, 0x5f,										// pop r15
		0x41, 0x5e,										// pop r14
		0x41, 0x5d,										// pop r13
		0x41, 0x5c,										// pop r12
		0x41, 0x5b,										// pop r11
		0x41, 0x5a,										// pop r10
		0x41, 0x59,										// pop r9
		0x41, 0x58,										// pop r8
		0x5f,											// pop rdi
		0x5e,											// pop rsi
		0x5d,											// pop rbp
		0x5c,											// pop rsp
		0x5a,											// pop rdx
		0x59,											// pop rcx
		0x5b,											// pop rbx
		0x58,											// pop rax
		0x9d,											// pop rflags
		0xff, 0x25, 0x00, 0x00, 0x00, 0x00,				// jmp qword ptr [rip]
		0, 0, 0, 0, 0, 0, 0, 0							// @original
	};
	int this_offset = 50, send_offset = 60, original_offset = 126;
#endif

	// thread_local BYTE buffer[PIPE_BUFFER_SIZE];
	// thread_local will crush on windowsxp
} // unnamed namespace

// - TextHook methods -

uintptr_t getasbaddr(const HookParam &hp)
{
	auto address = hp.address;
	if (hp.type & MODULE_OFFSET)
	{
		if (hp.type & FUNCTION_OFFSET)
		{
			FARPROC function = NULL;
			try
			{
				auto ordinal = std::stoi(hp.function);
				function = GetProcAddress(GetModuleHandleW(hp.module), (LPCSTR)(uintptr_t)ordinal);
			}
			catch (...)
			{
				function = GetProcAddress(GetModuleHandleW(hp.module), hp.function);
			}
			if (function)
				address += (uint64_t)function;
			else
				return ConsoleOutput(TR[FUNC_MISSING]), 0;
		}
		else
		{
			if (HMODULE moduleBase = GetModuleHandleW(hp.module))
				address += (uint64_t)moduleBase;
			else
				return ConsoleOutput(TR[MODULE_MISSING]), 0;
		}
	}
	return address;
}
bool TextHook::Insert(HookParam hp)
{

	auto addr = getasbaddr(hp);
	if (!addr)
		return false;

	RemoveHook(addr, 0);
	ConsoleOutput(TR[INSERTING_HOOK], hp.name, addr);
	local_buffer = new BYTE[PIPE_BUFFER_SIZE];
	{
		std::scoped_lock lock(viewMutex);
		this->hp = hp;
		address = addr;
	}
	savetypeforremove = hp.type;
	if (hp.type & DIRECT_READ)
		return InsertReadCode();
	if (hp.type & BREAK_POINT)
	{
		if (InsertBreakPoint())
			return true;
		if (safeautoleaveveh)
			return InsertBreakPoint(); // 搜索特殊码后，不会释放，导致virtualprotect查询失败，重试。
		return false;
	}
	return InsertHookCode();
}
uintptr_t win64find0000(uintptr_t addr)
{
	uintptr_t r = 0;
	__try
	{
		addr &= ~0xf;
		for (uintptr_t i = addr, j = addr - 0x10000; i > j; i -= 0x10)
		{
			DWORD k = *(DWORD *)(i - 4);
			if (k == 0x00000000)
				return i;
		}
		return 0;
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
	}
	return r;
}
Synchronized<std::unordered_map<uintptr_t, uintptr_t>> retaddr2relative; // 很奇怪，这个放到函数里用static在xp上会报错。
uintptr_t queryrelativeret(HookParam &hp, uintptr_t retaddr)
{
	// 不需要区分是相对于哪个module的偏移，只需要得到偏移就可以了，用来确保重启程序后ret值恒定
	auto &re = retaddr2relative.Acquire().contents;
	if (re.find(retaddr) != re.end())
		return re.at(retaddr);
	uintptr_t relative = retaddr;
	if (hp.jittype == JITTYPE::UNITY)
	{
#ifndef _WIN64
		relative = retaddr - SafeFindEnclosingAlignedFunction(retaddr, 0x10000);
#else
		relative = retaddr - win64find0000(retaddr);
#endif
	}
	else
	{
		if (MEMORY_BASIC_INFORMATION info = {}; VirtualQuery((LPCVOID)retaddr, &info, sizeof(info)))
			relative -= (uintptr_t)info.AllocationBase;
	}
	re.insert(std::make_pair(retaddr, relative));
	return relative;
}

uintptr_t jitgetaddr(hook_context *context, HookParam *hp, bool offset)
{
	int off;
	if (offset)
		off = hp->offset;
	else
		off = hp->split;
	switch (hp->jittype)
	{
#ifdef _WIN64
	case JITTYPE::RPCS3:
		return RPCS3::emu_arg(context)[off];
	case JITTYPE::VITA3K:
		return VITA3K::emu_arg(context)[off];
	case JITTYPE::YUZU:
		return YUZU::emu_arg(context, hp->emu_addr)[off];
#endif
	case JITTYPE::PPSSPP:
		return PPSSPP::emu_arg(context)[off];
	default:
		return 0;
	}
}
bool checklengthembedable(const HookParam &hp, size_t size)
{
	size_t len;
	if (hp.type & CODEC_UTF16)
		len = 2;
	else if (hp.type & CODEC_UTF32)
		len = 4;
	else
	{
		len = 2;
	}
	return size > len;
}
void commonfilter(TextBuffer *buffer, HookParam *hp)
{

	if (hp->type & CODEC_UTF16)
		;
	else if (hp->type & CODEC_UTF32)
		;
	else if (hp->type & CODEC_UTF8)
		;
	else
	{
		if (buffer->size == 2)
		{
			StringFilter(buffer, "\x81\xa4", 2);
			StringFilter(buffer, "\x81\xa5", 2);
		}
	}
}
void TextHook::Send(uintptr_t lpDataBase)
{
	Send(hook_context::fromBase(lpDataBase));
}
void TextHook::Send(hook_context *context)
{
	auto buffer = (TextOutput_T *)local_buffer;
	TextBuffer buff{buffer->data, 0};
	_InterlockedIncrement((long *)&useCount);
	__try
	{

		if (auto current_trigger_fun = trigger_fun.exchange(nullptr))
			if (!current_trigger_fun(location, context))
				trigger_fun = current_trigger_fun;

		if (hp.type & HOOK_RETURN)
		{
			hp.type &= ~HOOK_RETURN;
			hp.address = context->retaddr;
			strcat(hp.name, "_Return");
			hp.emu_addr = 0;
			// 清除module
			hp.type &= ~MODULE_OFFSET;
			hp.type &= ~FUNCTION_OFFSET;
			strcpy(hp.function, "");
			wcscpy(hp.module, L"");

			NewHook(hp, hp.name);
			hp.type |= HOOK_EMPTY;
			__leave;
		}
		if (hp.type & HOOK_EMPTY)
			__leave; // jichi 10/24/2014: dummy hook only for dynamic hook

		uintptr_t lpSplit = 0,
				  lpRetn = context->retaddr,
				  *plpdatain = (uintptr_t *)(context->base + hp.offset),
				  lpDataIn = *plpdatain;

		if (hp.jittype != JITTYPE::PC && hp.jittype != JITTYPE::UNITY)
		{
			lpDataIn = jitgetaddr(context, &hp, true);
			plpdatain = &lpDataIn;
		}
		else if (hp.jittype == JITTYPE::UNITY || hp.type & CSHARP_STRING)
		{
			plpdatain = &context->argof(hp.offset);
			lpDataIn = *plpdatain;
		}

		if (hp.text_fun)
		{
			hp.text_fun(context, &hp, &buff, &lpSplit);
		}
		else if (hp.type & CSHARP_STRING)
		{
			if (auto sw = commonsolvemonostring(lpDataIn))
				buff.from(sw.value());
		}
		else
		{
			if (hp.type & FIXING_SPLIT)
				lpSplit = FIXED_SPLIT_VALUE; // fuse all threads, and prevent floating
			else if (hp.type & USING_SPLIT)
			{
				if (hp.jittype != JITTYPE::PC && hp.jittype != JITTYPE::UNITY)
					lpSplit = jitgetaddr(context, &hp, false);
				else
					lpSplit = *(uintptr_t *)(context->base + hp.split);
				if (hp.type & SPLIT_INDIRECT)
					lpSplit = *(uintptr_t *)(lpSplit + hp.split_index);
			}
			if (hp.type & DATA_INDIRECT)
			{
				plpdatain = (uintptr_t *)(lpDataIn + hp.index);
				lpDataIn = *plpdatain;
			}
			lpDataIn += hp.padding;
			buff.size = GetLength(context, lpDataIn);
		}

		if (buff.size <= 0)
			__leave;
		if (buff.size > TEXT_BUFFER_SIZE)
		{
			ConsoleOutput(TR[InvalidLength], buff.size, hp.name);
			buff.size = TEXT_BUFFER_SIZE;
		}
		if (hp.type & USING_CHAR || (!hp.text_fun && !(hp.type & USING_STRING)))
		{
			if (hp.text_fun)
				lpDataIn = *(uint32_t *)buff.buff;
			if (hp.type & CODEC_UTF32 || hp.type & CODEC_UTF8)
			{
				*(uint32_t *)buff.buff = lpDataIn & 0xffffffff;
			}
			else
			{ // CHAR_LITTEL_ENDIAN,CODEC_ANSI_BE,CODEC_UTF16
				lpDataIn &= 0xffff;
				if ((hp.type & CODEC_ANSI_BE) && (lpDataIn >> 8))
					lpDataIn = _byteswap_ushort(lpDataIn & 0xffff);
				if (buff.size == 1)
					lpDataIn &= 0xff;
				*(WORD *)buff.buff = lpDataIn & 0xffff;
			}
		}
		else if ((!hp.text_fun) && (!(hp.type & CSHARP_STRING)))
		{
			if (lpDataIn == 0)
				__leave;
			::memcpy(buff.buff, (void *)lpDataIn, buff.size);
		}
		commonfilter(&buff, &hp);
		if (buff.size <= 0)
			__leave;
		if (hp.filter_fun)
		{
			hp.filter_fun(&buff, &hp);
			if (buff.size <= 0)
				__leave;
		}

		if (hp.type & (NO_CONTEXT | FIXING_SPLIT))
			lpRetn = 0;

		buffer->type = hp.type;

		lpRetn = queryrelativeret(hp, lpRetn);
		ThreadParam tp{GetCurrentProcessId(), address, lpRetn, lpSplit};

		parsenewlineseperator(&buff);

		bool canembed;
		if (hp.type & EMBED_ABLE)
		{
			if (!checklengthembedable(hp, buff.size))
			{
				buffer->type &= (~EMBED_ABLE);
				canembed = false;
			}
			else if (checktranslatedok(buff))
			{
				buffer->type &= (~EMBED_ABLE);
				canembed = true;
			}
			else
			{
				canembed = true;
			}
		}

		TextOutput(tp, hp, buffer, buff.size);

		if (canembed && (check_embed_able(tp)))
		{
			auto size_origin = buff.size;
			auto zeros = 1;
			if (hp.type & CODEC_UTF16)
				zeros = 2;
			else if (hp.type & CODEC_UTF32)
				zeros = 4;
			if (waitfornotify(&buff, tp))
			{
				if (hp.type & EMBED_AFTER_NEW)
				{
					auto size = max(size_origin, buff.size + zeros);
					auto _ = new char[size];
					memcpy(_, buff.buff, buff.size);
					memset(_ + buff.size, 0, size - buff.size);
					*(uintptr_t *)plpdatain = (uintptr_t)_;
				}
				else if (hp.type & EMBED_AFTER_OVERWRITE)
				{
					memcpy((void *)lpDataIn, buff.buff, buff.size);
					memset((char *)lpDataIn + buff.size, 0, max(size_origin, zeros));
				}
				else if (hp.embed_fun)
					hp.embed_fun(context, buff);
				else if (hp.type & CSHARP_STRING)
				{
					unity_ui_string_embed_fun(context->argof(hp.offset), buff);
				}
			}
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		if (!err && !(hp.type & KNOWN_UNSTABLE))
		{
			err = true;
			ConsoleOutput(TR[SEND_ERROR], hp.name);
		}
	}

	_InterlockedDecrement((long *)&useCount);
}
bool TextHook::breakpointcontext(PCONTEXT pcontext)
{
	hook_context context = hook_context::fromPCONTEXT(pcontext);
	Send(&context);
	context.toPCONTEXT(pcontext);
	return true;
}
bool TextHook::InsertBreakPoint()
{
	// MH_CreateHook 64位unity/yuzu-emu经常 MH_ERROR_MEMORY_ALLOC
	return add_veh_hook(location, std::bind(&TextHook::breakpointcontext, this, std::placeholders::_1));
}
bool TextHook::RemoveBreakPoint()
{
	return remove_veh_hook(location);
}
bool TextHook::InsertHookCode()
{

	VirtualProtect(location, 10, PAGE_EXECUTE_READWRITE, DUMMY);
	void *original;
	MH_STATUS error;
	while ((error = MH_CreateHook(location, trampoline, &original)) != MH_OK)
		if (error == MH_ERROR_ALREADY_CREATED)
			RemoveHook(address);
		else
			return ConsoleOutput(MH_StatusToString(error)), false;

	*(TextHook **)(common_hook + this_offset) = this;
	*(void(TextHook::**)(uintptr_t))(common_hook + send_offset) = &TextHook::Send;
	*(void **)(common_hook + original_offset) = original;
	memcpy(trampoline, common_hook, sizeof(common_hook));
	return MH_EnableHook(location) == MH_OK;
}

void TextHook::Read()
{
	// BYTE(*buffer)[PIPE_BUFFER_SIZE] = &::buffer, *pbData = *buffer + sizeof(ThreadParam);
	auto buffer = (TextOutput_T *)local_buffer;
	auto pbData = buffer->data;
	buffer->type = hp.type;
	TextBuffer buff{pbData, 1};
	__try
	{
		if (hp.text_fun)
		{
			while ((!(hp.type & HOOK_EMPTY)) && (WaitForSingleObject(readerEvent, 500) == WAIT_TIMEOUT))
				hp.text_fun(0, &hp, 0, 0);
		}
		else
		{

			while (WaitForSingleObject(readerEvent, 500) == WAIT_TIMEOUT)
			{
				if (!location)
					continue;
				int currentLen = HookStrlen((BYTE *)location);
				bool changed = memcmp(pbData, location, buff.size) != 0;
				if (changed || (currentLen != buff.size))
				{
					buff.size = min(currentLen, TEXT_BUFFER_SIZE);
					memcpy(pbData, location, buff.size);
					if (hp.filter_fun)
					{
						hp.filter_fun(&buff, &hp);
						if (buff.size <= 0)
							continue;
					}
					TextOutput({GetCurrentProcessId(), address, 0, 0}, hp, buffer, buff.size);
					buff.size = min(currentLen, TEXT_BUFFER_SIZE);
					memcpy(pbData, location, buff.size);
				}
			}
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		ConsoleOutput(TR[READ_ERROR], hp.name);
		Clear();
	}
}

bool TextHook::InsertReadCode()
{
	readerThread = CreateThread(nullptr, 0, [](void *This)
								{ ((TextHook*)This)->Read(); return 0UL; }, this, 0, nullptr);
	readerEvent = CreateEventW(nullptr, FALSE, FALSE, NULL);
	return true;
}

void TextHook::RemoveHookCode()
{
	MH_DisableHook(location);
	while (useCount != 0)
		;
	MH_RemoveHook(location);
}

void TextHook::RemoveReadCode()
{
	SetEvent(readerEvent);
	if (GetThreadId(readerThread) != GetCurrentThreadId())
		WaitForSingleObject(readerThread, 1000);
	CloseHandle(readerEvent);
	CloseHandle(readerThread);
}

void TextHook::Clear()
{
	if (address == 0)
		return;
	if (savetypeforremove & DIRECT_READ)
		RemoveReadCode();
	else if (savetypeforremove & BREAK_POINT)
		RemoveBreakPoint();
	else
		RemoveHookCode();
	NotifyHookRemove(address, hp.name);
	std::scoped_lock lock(viewMutex);
	memset(&hp, 0, sizeof(HookParam));
	address = 0;
	if (local_buffer)
		delete[] local_buffer;
}

int TextHook::GetLength(hook_context *context, uintptr_t in)
{
	int len;
	if (hp.type & USING_STRING)
	{
		if (hp.length_offset)
		{
			len = *((uintptr_t *)context->base + hp.length_offset);
			if (len >= 0)
			{
				if (hp.type & CODEC_UTF16)
					len <<= 1;
				else if (hp.type & CODEC_UTF32)
					len <<= 2;
			}
			else if (len != -1)
			{
			}
			else
			{ // len==-1
				len = HookStrlen((BYTE *)in);
			}
		}
		else
		{
			len = HookStrlen((BYTE *)in);
		}
	}
	else
	{
		if (hp.type & CODEC_UTF16)
			len = 2;
		else if (hp.type & CODEC_UTF32)
			len = 4;
		else if (hp.type & CODEC_UTF8)
			len = utf8charlen((char *)&in);
		else
		{ // CODEC_ANSI_BE,CHAR_LITTLE_ENDIAN
			if (hp.type & CODEC_ANSI_BE)
				in >>= 8;
			len = !!IsDBCSLeadByteEx(hp.codepage, in & 0xff) + 1;
		}
	}
	return max(0, len);
}

int TextHook::HookStrlen(BYTE *data)
{
	return HookStrLen(&hp, data);
}

// EOF
