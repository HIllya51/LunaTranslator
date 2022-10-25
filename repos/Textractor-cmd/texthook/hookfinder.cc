#include "hookfinder.h"
#include "defs.h"
#include "main.h"
#include "util.h"
#include "MinHook.h"

extern const char* HOOK_SEARCH_STARTING;
extern const char* HOOK_SEARCH_INITIALIZING;
extern const char* HOOK_SEARCH_INITIALIZED;
extern const char* MAKE_GAME_PROCESS_TEXT;
extern const char* HOOK_SEARCH_FINISHED;
extern const char* OUT_OF_RECORDS_RETRY;
extern const char* NOT_ENOUGH_TEXT;
extern const char* COULD_NOT_FIND;

namespace
{
	SearchParam sp;

	constexpr int MAX_STRING_SIZE = 500, CACHE_SIZE = 749993, GOOD_PAGE = -1;
	struct HookRecord
	{
		uint64_t address = 0;
		uintptr_t padding = 0;
		int offset = 0;
		char text[MAX_STRING_SIZE] = {};
	};
	std::unique_ptr<HookRecord[]> records;
	long recordsAvailable;
	uint64_t signatureCache[CACHE_SIZE] = {};
	long sumCache[CACHE_SIZE] = {};
	uintptr_t pageCache[CACHE_SIZE] = {};

#ifndef _WIN64
	BYTE trampoline[] =
	{
		0x9c, // pushfd
		0x60, // pushad
		0x68, 0,0,0,0, // push @addr ; after this a total of 0x28 bytes are pushed
		0x8d, 0x44, 0x24, 0x28, // lea eax,[esp+0x28]
		0x50, // push eax ; stack
		0xbb, 0,0,0,0, // mov ebx,@Send
		0xff, 0xd3, // call ebx
		0x83, 0xc4, 0x08, // add esp, 0x8 ; doesn't matter which register
		0x61, // popad
		0x9d,  // popfd
		0x68, 0,0,0,0, // push @original
		0xc3  // ret ; basically absolute jmp to @original
	};
	constexpr int addr_offset = 3, send_offset = 13, original_offset = 25, registers = 8;
#else
	BYTE trampoline[] = {
		0x9c, // push rflags
		0x50, // push rax
		0x53, // push rbx
		0x51, // push rcx
		0x52, // push rdx
		0x54, // push rsp
		0x55, // push rbp
		0x56, // push rsi
		0x57, // push rdi
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
		0x48, 0x83, 0xec, 0x20, // sub rsp,0x20
		0xf3, 0x0f, 0x7f, 0x24, 0x24, // movdqu [rsp],xmm4
		0xf3, 0x0f, 0x7f, 0x6c, 0x24, 0x10, // movdqu [rsp+0x10],xmm5
		0x48, 0x8d, 0x8c, 0x24, 0xa8, 0x00, 0x00, 0x00, // lea rcx,[rsp+0xa8]
		0x48, 0xba, 0,0,0,0,0,0,0,0, // mov rcx,@addr
		0x48, 0xb8, 0,0,0,0,0,0,0,0, // mov rax,@Send
		0x48, 0x89, 0xe3, // mov rbx,rsp
		0x48, 0x83, 0xe4, 0xf0, // and rsp,0xfffffffffffffff0 ; align stack
		0xff, 0xd0, // call rax
		0x48, 0x89, 0xdc, // mov rsp,rbx
		0xf3, 0x0f, 0x6f, 0x6c, 0x24, 0x10, // movdqu xmm5,XMMWORD PTR[rsp + 0x10]
		0xf3, 0x0f, 0x6f, 0x24, 0x24, // movdqu xmm4,XMMWORD PTR[rsp]
		0x48, 0x83, 0xc4, 0x20, // add rsp,0x20
		0x41, 0x5f, // pop r15
		0x41, 0x5e, // pop r14
		0x41, 0x5d, // pop r13
		0x41, 0x5c, // pop r12
		0x41, 0x5b, // pop r11
		0x41, 0x5a, // pop r10
		0x41, 0x59, // pop r9
		0x41, 0x58, // pop r8
		0x5f, // pop rdi
		0x5e, // pop rsi
		0x5d, // pop rbp
		0x5c, // pop rsp
		0x5a, // pop rdx
		0x59, // pop rcx
		0x5b, // pop rbx
		0x58, // pop rax
		0x9d, // pop rflags
		0xff, 0x25, 0x00, 0x00, 0x00, 0x00, // jmp qword ptr [rip]
		0,0,0,0,0,0,0,0 // @original
	};
	constexpr int addr_offset = 50, send_offset = 60, original_offset = 126, registers = 16;
#endif
}

bool IsBadReadPtr(void* data)
{
	if (data > records.get() && data < records.get() + sp.maxRecords) return true;
	uintptr_t BAD_PAGE = (uintptr_t)data >> 12;
	auto& cacheEntry = pageCache[BAD_PAGE % CACHE_SIZE];
	if (cacheEntry == BAD_PAGE) return true;
	if (cacheEntry == GOOD_PAGE) return false;

	__try
	{
		volatile char _ = *(char*)data;
		cacheEntry = GOOD_PAGE;
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		if (GetExceptionCode() == EXCEPTION_GUARD_PAGE)
		{
			MEMORY_BASIC_INFORMATION info;
			VirtualQuery(data, &info, sizeof(info));
			VirtualProtect(data, 1, info.Protect | PAGE_GUARD, DUMMY);
		}
		cacheEntry = BAD_PAGE;
	}
	return cacheEntry == BAD_PAGE;
}

void Send(char** stack, uintptr_t address)
{
	// it is unsafe to call ANY external functions from this, as they may have been hooked (if called the hook would call this function making an infinite loop)
	// the exceptions are compiler intrinsics like _InterlockedDecrement
	if (recordsAvailable <= 0) return;
	for (int i = -registers; i < 10; ++i) for (auto padding : { uintptr_t{}, sp.padding })
	{
		char* str = stack[i] + padding;
		if (IsBadReadPtr(str) || IsBadReadPtr(str + MAX_STRING_SIZE)) continue;
		__try
		{
			int length = 0, sum = 0;
			for (; (str[length] || str[length + 1]) && length < MAX_STRING_SIZE; length += 2) sum += *(uint16_t*)(str + length);
			if (length > STRING && length < MAX_STRING_SIZE - 1)
			{
				// many duplicate results with same address, offset, and third/fourth character will be found: filter them out
				uint64_t signature = ((uint64_t)i << 56) | ((uint64_t)(str[2] + str[3]) << 48) | address;
				if (signatureCache[signature % CACHE_SIZE] == signature) continue;
				signatureCache[signature % CACHE_SIZE] = signature;
				// if there are huge amount of strings that are the same, it's probably garbage: filter them out
				// can't store all the strings, so use sum as heuristic instead
				if (_InterlockedIncrement(sumCache + (sum % CACHE_SIZE)) > 25) continue;
				long n = sp.maxRecords - _InterlockedDecrement(&recordsAvailable);
				if (n < sp.maxRecords)
				{
					records[n].address = address;
					records[n].padding = padding;
					records[n].offset = i * sizeof(char*);
					for (int j = 0; j < length; ++j) records[n].text[j] = str[j];
					records[n].text[length] = 0;
				}
				if (n == sp.maxRecords)
				{
					spDefault.maxRecords = sp.maxRecords * 2;
					ConsoleOutput(OUT_OF_RECORDS_RETRY);
				}
			}
		}
		__except (EXCEPTION_EXECUTE_HANDLER) {}
	}
}

std::vector<uint64_t> GetFunctions(uintptr_t module)
{
	if (!module) return {};
	IMAGE_DOS_HEADER* dosHeader = (IMAGE_DOS_HEADER*)module;
	if (dosHeader->e_magic != IMAGE_DOS_SIGNATURE) return {};
	IMAGE_NT_HEADERS* ntHeader = (IMAGE_NT_HEADERS*)(module + dosHeader->e_lfanew);
	if (ntHeader->Signature != IMAGE_NT_SIGNATURE) return {};
	DWORD exportAddress = ntHeader->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
	if (!exportAddress) return {};
	IMAGE_EXPORT_DIRECTORY* exportDirectory = (IMAGE_EXPORT_DIRECTORY*)(module + exportAddress);
	std::vector<uint64_t> functions;
	for (int i = 0; i < exportDirectory->NumberOfNames; ++i)
		//char* funcName = (char*)(module + *(DWORD*)(module + exportDirectory->AddressOfNames + i * sizeof(DWORD)));
		functions.push_back(module + *(DWORD*)(module + exportDirectory->AddressOfFunctions +
			sizeof(DWORD) * *(WORD*)(module + exportDirectory->AddressOfNameOrdinals + i * sizeof(WORD))));
	return functions;
}

void SearchForHooks(SearchParam spUser)
{
	std::thread([=]
	{
		static std::mutex m;
		std::scoped_lock lock(m);
		*(void**)(trampoline + send_offset) = Send;

		sp = spUser.length == 0 ? spDefault : spUser;

		ConsoleOutput(HOOK_SEARCH_INITIALIZING, 0.);
		do
			try { records = std::make_unique<HookRecord[]>(recordsAvailable = sp.maxRecords); }
			catch (std::bad_alloc) { ConsoleOutput("Textractor: SearchForHooks ERROR: out of memory, retrying to allocate %d", sp.maxRecords /= 2); }
		while (!records && sp.maxRecords);

		std::vector<uint64_t> addresses;
		if (*sp.boundaryModule) std::tie(sp.minAddress, sp.maxAddress) = Util::QueryModuleLimits(GetModuleHandleW(sp.boundaryModule));
		if (*sp.exportModule) addresses = GetFunctions((uintptr_t)GetModuleHandleW(sp.exportModule));
		else for (auto& addr : addresses = Util::SearchMemory(sp.pattern, sp.length, PAGE_EXECUTE, sp.minAddress, sp.maxAddress)) addr += sp.offset;

		auto limits = Util::QueryModuleLimits(GetModuleHandleW(ITH_DLL));
		addresses.erase(std::remove_if(addresses.begin(), addresses.end(), [&](uint64_t addr) { return addr > limits.first && addr < limits.second; }), addresses.end());

		auto trampolines = (decltype(trampoline)*)VirtualAlloc(NULL, sizeof(trampoline) * addresses.size(), MEM_COMMIT, PAGE_READWRITE);
		VirtualProtect(trampolines, addresses.size() * sizeof(trampoline), PAGE_EXECUTE_READWRITE, DUMMY);
		for (int i = 0; i < addresses.size(); ++i)
		{
			void* original;
			MH_CreateHook((void*)addresses[i], trampolines[i], &original);
			MH_QueueEnableHook((void*)addresses[i]);
			memcpy(trampolines[i], trampoline, sizeof(trampoline));
			*(uintptr_t*)(trampolines[i] + addr_offset) = addresses[i];
			*(void**)(trampolines[i] + original_offset) = original;
			if (i % 2500 == 0) ConsoleOutput(HOOK_SEARCH_INITIALIZING, 1 + 98. * i / addresses.size());
		}
		ConsoleOutput(HOOK_SEARCH_INITIALIZED, addresses.size());
		MH_ApplyQueued();
		ConsoleOutput(HOOK_SEARCH_STARTING);
		ConsoleOutput(MAKE_GAME_PROCESS_TEXT, sp.searchTime / 1000);
		Sleep(sp.searchTime);
		for (auto addr : addresses) MH_QueueDisableHook((void*)addr);
		MH_ApplyQueued();
		Sleep(1000);
		for (auto addr : addresses) MH_RemoveHook((void*)addr);
		ConsoleOutput(HOOK_SEARCH_FINISHED, sp.maxRecords - recordsAvailable);
		for (int i = 0, results = 0; i < sp.maxRecords; ++i)
		{
			if (!records[i].address) continue;
			if (++results % 100'000 == 0) ConsoleOutput("Textractor: %d results processed", results);
			HookParam hp = {};
			hp.offset = records[i].offset;
			hp.type = USING_UNICODE | USING_STRING;
			hp.address = records[i].address;
			hp.padding = records[i].padding;
			hp.codepage = sp.codepage;
			if (sp.hookPostProcessor) sp.hookPostProcessor(hp);
			NotifyHookFound(hp, (wchar_t*)records[i].text);
		}
		records.reset();
		VirtualFree(trampolines, 0, MEM_RELEASE);
		for (int i = 0; i < CACHE_SIZE; ++i) signatureCache[i] = sumCache[i] = 0;
	}).detach();
}

void SearchForText(wchar_t* text, UINT codepage)
{
	bool found = false;
	char utf8Text[PATTERN_SIZE * 4] = {};
	WideCharToMultiByte(CP_UTF8, 0, text, PATTERN_SIZE, utf8Text, PATTERN_SIZE * 4, nullptr, nullptr);
	char codepageText[PATTERN_SIZE * 4] = {};
	WideCharToMultiByte(codepage, 0, text, PATTERN_SIZE, codepageText, PATTERN_SIZE * 4, nullptr, nullptr);
	if (strlen(utf8Text) < 4 || strlen(codepageText) < 4 || wcslen(text) < 4) return ConsoleOutput(NOT_ENOUGH_TEXT);
	ConsoleOutput(HOOK_SEARCH_STARTING);
	auto GenerateHooks = [&](std::vector<uint64_t> addresses, HookParamType type)
	{
		for (auto addr : addresses)
		{
			if (abs((long long)(utf8Text - addr)) < 20000) continue; // don't add read code if text is on this thread's stack
			found = true;
			HookParam hp = {};
			hp.type = DIRECT_READ | type;
			hp.address = addr;
			hp.codepage = codepage;
			NewHook(hp, "Search", 0);
		}
	};
	GenerateHooks(Util::SearchMemory(utf8Text, strlen(utf8Text), PAGE_READWRITE), USING_UTF8);
	GenerateHooks(Util::SearchMemory(codepageText, strlen(codepageText), PAGE_READWRITE), USING_STRING);
	GenerateHooks(Util::SearchMemory(text, wcslen(text) * sizeof(wchar_t), PAGE_READWRITE), USING_UNICODE);
	if (!found) ConsoleOutput(COULD_NOT_FIND);
}
