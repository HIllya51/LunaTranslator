
#include "MinHook.h"
#include "veh_hook.h"
#define HOOK_SEARCH_UNSAFE 0
namespace
{
	SearchParam sp;

	constexpr int MAX_STRING_SIZE = 500, CACHE_SIZE = 749993, GOOD_PAGE = -1;
	struct HookRecord
	{
		uint64_t address = 0;
		uint64_t em_addr = 0;
		intptr_t padding = 0;
		int offset = 0;
		JITTYPE jittype;
		char text[MAX_STRING_SIZE] = {};
		bool csstring;
	};
	std::unique_ptr<HookRecord[]> records;
	long recordsAvailable;
	uint64_t signatureCache[CACHE_SIZE] = {};
	long sumCache[CACHE_SIZE] = {};
	uintptr_t pageCache[CACHE_SIZE] = {};
	std::unordered_map<uintptr_t, std::string> remapunityjit;
#ifndef _WIN64
	BYTE trampoline[] =
		{
			0x9c,					// pushfd
			0x60,					// pushad
			0x68, 0, 0, 0, 0,		// push @addr ; after this a total of 0x28 bytes are pushed
			0x8d, 0x44, 0x24, 0x28, // lea eax,[esp+0x28]
			0x50,					// push eax ; stack
			0xbb, 0, 0, 0, 0,		// mov ebx,@Send
			0xff, 0xd3,				// call ebx
			0x83, 0xc4, 0x08,		// add esp, 0x8 ; doesn't matter which register
			0x61,					// popad
			0x9d,					// popfd
			0x68, 0, 0, 0, 0,		// push @original
			0xc3					// ret ; basically absolute jmp to @original
	};
	constexpr int addr_offset = 3, send_offset = 13, original_offset = 25, registers = 8;
#else
	BYTE trampoline[] = {
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
		0x48, 0x8d, 0x8c, 0x24, 0xa8, 0x00, 0x00, 0x00, // lea rcx,[rsp+0xa8]
		0x48, 0xba, 0, 0, 0, 0, 0, 0, 0, 0,				// mov rcx,@addr
		0x48, 0xb8, 0, 0, 0, 0, 0, 0, 0, 0,				// mov rax,@Send
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
	constexpr int addr_offset = 50, send_offset = 60, original_offset = 126, registers = 16;
#endif
}
bool IsBadReadPtr(void *data)
{
	if (data > records.get() && data < records.get() + sp.maxRecords)
		return true;
	uintptr_t BAD_PAGE = (uintptr_t)data >> 12;
	auto &cacheEntry = pageCache[BAD_PAGE % CACHE_SIZE];
	if (cacheEntry == BAD_PAGE)
		return true;
	if (cacheEntry == GOOD_PAGE)
		return false;

	__try
	{
		volatile char _ = *(char *)data;
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
namespace
{
	bool maybeWideCharja(WORD w)
	{
		return (0x3040 <= w && w <= 0x309F) || (0x30A0 <= w && w <= 0x30FF) || (0x4E00 <= w && w <= 0x9FFF) || (0x3000 <= w && w <= 0x303F);
	}
	bool maybeWideStringja(char *str)
	{
		auto w = *(WORD *)str;
		return maybeWideCharja(w);
	}
	bool maybeAnsitringja(char *str)
	{
		return IsDBCSLeadByteEx(932, *str) && (str[1] != 0);
	}
	bool maybeIsJa(char *str)
	{
		return maybeAnsitringja(str) || maybeWideStringja(str);
	}
}
void DoSend(int i, uintptr_t address, char *str, intptr_t padding, JITTYPE jittype = JITTYPE::PC, uint64_t em_addr = 0, bool csstring = false)
{
	str += padding;
	if (IsBadReadPtr(str) || IsBadReadPtr(str + MAX_STRING_SIZE))
		return;
	__try
	{
		int length = 0, sum = 0;
		for (; *(uint16_t *)(str + length) && length < MAX_STRING_SIZE; length += sizeof(uint16_t))
			sum += *(uint16_t *)(str + length);
#if HOOK_SEARCH_UNSAFE
		if (((length > STRING) || maybeIsJa(str)) && length < MAX_STRING_SIZE - 1)
#else
		if (length > STRING && length < MAX_STRING_SIZE - 1)
#endif
		{
			// many duplicate results with same address, offset, and third/fourth character will be found: filter them out
			uint64_t signature = ((uint64_t)i << 56) | ((uint64_t)(str[2] + str[3]) << 48) | address;
#if HOOK_SEARCH_UNSAFE
#else
			if (signatureCache[signature % CACHE_SIZE] == signature)
				return;
			signatureCache[signature % CACHE_SIZE] = signature;
#endif
			// if there are huge amount of strings that are the same, it's probably garbage: filter them out
			// can't store all the strings, so use sum as heuristic instead
			if (_InterlockedIncrement(sumCache + (sum % CACHE_SIZE)) > 25)
				return;
			long n = sp.maxRecords - _InterlockedDecrement(&recordsAvailable);
			if (n < sp.maxRecords)
			{
				records[n].jittype = jittype;
				records[n].padding = padding;
				records[n].csstring = csstring;
				if (csstring)
				{
					records[n].address = address;
					records[n].offset = i;
				}
				else if (jittype == JITTYPE::PC)
				{
					records[n].address = address;
					records[n].offset = i * sizeof(char *);
				}
				else
				{
					records[n].em_addr = em_addr;
					records[n].offset = i;
				}

				for (int j = 0; j < length; ++j)
					records[n].text[j] = str[j];
				records[n].text[length] = 0;
			}
			if (n == sp.maxRecords)
			{
				spDefault.maxRecords = sp.maxRecords * 2;
				ConsoleOutput(TR[OUT_OF_RECORDS_RETRY]);
			}
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
	}
}
void Send(char **strs, uintptr_t address)
{
	// it is unsafe to call ANY external functions from this, as they may have been hooked (if called the hook would call this function making an infinite loop)
	// the exceptions are compiler intrinsics like _InterlockedDecrement
	if (recordsAvailable <= 0)
		return;
	for (int i = -registers; i < 10; ++i)
	{
		DoSend(i, address, strs[i], 0);
		if (sp.padding)
			DoSend(i, address, strs[i], sp.padding);
	}
}
template <JITTYPE t>
void SendCSharpString(char **strs, uintptr_t address)
{
	// it is unsafe to call ANY external functions from this, as they may have been hooked (if called the hook would call this function making an infinite loop)
	// the exceptions are compiler intrinsics like _InterlockedDecrement
	if (recordsAvailable <= 0)
		return;
	for (int i = 0; i < 10; ++i)
	{
		__try
		{
			DoSend(i, address, (char *)commonsolvemonostring(hook_context::fromBase((uintptr_t)strs)->argof(i)).value().data(), 0, t, 0, true);
		}
		__except (EXCEPTION_EXECUTE_HANDLER)
		{
		}
	}
}
void SafeSendJitVeh(hook_context *context, uintptr_t address, uint64_t em_addr, JITTYPE jittype, intptr_t padding)
{
	__try
	{
		for (int i = 0; i < 16; i++)
		{
			char *str = 0;
			switch (jittype)
			{
#ifdef _WIN64
			case JITTYPE::YUZU:
				str = (char *)YUZU::emu_arg(context, em_addr)[i];
				break;
			case JITTYPE::VITA3K:
				str = (char *)VITA3K::emu_arg(context)[i];
				break;
			case JITTYPE::PCSX2:
				str = (char *)PCSX2Types::argsof(i);
				break;
			case JITTYPE::RPCS3:
				str = (char *)RPCS3::emu_arg(context)[i];
				break;
#endif
			case JITTYPE::PPSSPP:
				str = (char *)PPSSPP::emu_arg(context)[i];
				break;
			default:
				return;
			}
			DoSend(i, address, str, 0, jittype, em_addr);
			if (padding)
				DoSend(i, address, str, padding, jittype, em_addr);
		}
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
	}
}
bool safeleave = false;
std::unordered_map<uintptr_t, uint64_t> addresscalledtime;
bool SendJitVeh(PCONTEXT pcontext, uintptr_t address, uint64_t em_addr, JITTYPE jittype, intptr_t padding)
{
	if (safeleave)
		return false;
	if (!addresscalledtime.count(address))
		addresscalledtime[address] = 0;
	auto tm = GetTickCount64();
	if (tm - addresscalledtime[address] < 100)
		return false;
	addresscalledtime[address] = tm;
	hook_context context = hook_context::fromPCONTEXT(pcontext);
	SafeSendJitVeh(&context, address, em_addr, jittype, padding);
	return true;
}
std::vector<uintptr_t> GetFunctions(uintptr_t module)
{
	if (!module)
		return {};
	IMAGE_DOS_HEADER *dosHeader = (IMAGE_DOS_HEADER *)module;
	if (dosHeader->e_magic != IMAGE_DOS_SIGNATURE)
		return {};
	IMAGE_NT_HEADERS *ntHeader = (IMAGE_NT_HEADERS *)(module + dosHeader->e_lfanew);
	if (ntHeader->Signature != IMAGE_NT_SIGNATURE)
		return {};
	DWORD exportAddress = ntHeader->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_EXPORT].VirtualAddress;
	if (!exportAddress)
		return {};
	IMAGE_EXPORT_DIRECTORY *exportDirectory = (IMAGE_EXPORT_DIRECTORY *)(module + exportAddress);
	std::vector<uintptr_t> functions;
	for (int i = 0; i < exportDirectory->NumberOfNames; ++i)
		// char* funcName = (char*)(module + *(DWORD*)(module + exportDirectory->AddressOfNames + i * sizeof(DWORD)));
		functions.push_back(module + *(DWORD *)(module + exportDirectory->AddressOfFunctions +
												sizeof(DWORD) * *(WORD *)(module + exportDirectory->AddressOfNameOrdinals + i * sizeof(WORD))));
	return functions;
}
void mergevector(std::vector<uintptr_t> &v1, const std::vector<uintptr_t> &v2)
{
	for (auto addr : v2)
	{
		auto it = std::find(v1.begin(), v1.end(), addr);
		if (it == v1.end())
		{
			v1.push_back(addr);
		}
	}
}
void SearchForHooks_Return()
{
	ConsoleOutput(TR[HOOK_SEARCH_FINISHED], sp.maxRecords - recordsAvailable);
	for (int i = 0, results = 0; i < sp.maxRecords; ++i)
	{
		HookParam hp;
		hp.codepage = sp.codepage;
		hp.jittype = records[i].jittype;
		hp.padding = records[i].padding;
		hp.offset = records[i].offset;
		if (records[i].csstring)
		{
			if (!records[i].address)
				continue;
			hp.type = CODEC_UTF16 | USING_STRING | CSHARP_STRING;
			hp.address = records[i].address;
			if (hp.jittype == JITTYPE::UNITY)
			{
				strncpy(hp.function, remapunityjit[hp.address].c_str(), sizeof(hp.function));
			}
		}
		else if (records[i].jittype == JITTYPE::PC)
		{
			if (!records[i].address)
				continue;
			hp.type = CODEC_UTF16 | USING_STRING;
			hp.address = records[i].address;
		}
		else
		{
			if (!records[i].em_addr)
				continue;
			hp.emu_addr = records[i].em_addr;
			hp.type = CODEC_UTF16 | USING_STRING | BREAK_POINT | NO_CONTEXT;
		}
		NotifyHookFound(hp, (wchar_t *)records[i].text);
		if (++results % 100'000 == 0)
			ConsoleOutput(TR[ResultsNum], results);
	}
	records.reset();
	for (int i = 0; i < CACHE_SIZE; ++i)
		signatureCache[i] = sumCache[i] = 0;
}
void initrecords()
{
	do
		try
		{
			records = std::make_unique<HookRecord[]>(recordsAvailable = sp.maxRecords);
		}
		catch (std::bad_alloc)
		{
			ConsoleOutput(TR[SearchForHooks_ERROR], sp.maxRecords /= 2);
		}
	while (!records && sp.maxRecords);
}
void inlinehookpipeline(std::vector<uintptr_t> &addresses)
{
	auto trampolines = (decltype(trampoline) *)VirtualAlloc(NULL, sizeof(trampoline) * addresses.size(), MEM_COMMIT, PAGE_READWRITE);
	VirtualProtect(trampolines, addresses.size() * sizeof(trampoline), PAGE_EXECUTE_READWRITE, DUMMY);
	std::vector<uintptr_t> mherroridx;
	for (int i = 0; i < addresses.size(); ++i)
	{
		void *original;
		// 避免MH_RemoveHook时移除原本已有hook
		if (MH_CreateHook((void *)addresses[i], trampolines[i], &original) != MH_OK)
		{
			mherroridx.push_back(i);
		}
		MH_QueueEnableHook((void *)addresses[i]);
		memcpy(trampolines[i], trampoline, sizeof(trampoline));
		*(uintptr_t *)(trampolines[i] + addr_offset) = addresses[i];
		*(void **)(trampolines[i] + original_offset) = original;
		if (i % 2500 == 0)
			ConsoleOutput(TR[HOOK_SEARCH_INITIALIZING], 1 + 98. * i / addresses.size());
	}
	// 避免MH_RemoveHook时移除原本已有hook
	for (int i = 0; i < mherroridx.size(); i++)
	{
		auto reverseidx = mherroridx[mherroridx.size() - 1 - i];
		addresses.erase(addresses.begin() + reverseidx);
	}

	ConsoleOutput(TR[HOOK_SEARCH_INITIALIZED], addresses.size());
	MH_ApplyQueued();
	ConsoleOutput(TR[HOOK_SEARCH_STARTING]);
	ConsoleOutput(TR[MAKE_GAME_PROCESS_TEXT], sp.searchTime / 1000);
	Sleep(sp.searchTime);
	for (auto addr : addresses)
		MH_QueueDisableHook((void *)addr);
	MH_ApplyQueued();
	Sleep(1000);
	for (auto addr : addresses)
		MH_RemoveHook((void *)addr);
	VirtualFree(trampolines, 0, MEM_RELEASE);
}
uintptr_t getasbaddr(const HookParam &hp);

void _SearchForHooks(SearchParam spUser)
{
	static std::mutex m;
	std::scoped_lock lock(m);
	ConsoleOutput(TR[HOOK_SEARCH_INITIALIZING], 0.);

	sp = spUser.length == 0 ? spDefault : spUser;
	sp.codepage = spUser.codepage;
	initrecords();
	if ((!sp.isjithook) || (jittypedefault == JITTYPE::PC))
	{
		*(void **)(trampoline + send_offset) = Send;
		std::vector<uintptr_t> addresses;
		if (*sp.boundaryModule)
		{
			auto [minaddr, maxaddr] = Util::QueryModuleLimits(GetModuleHandleW(sp.boundaryModule));
			if (sp.address_method == 0)
			{
				sp.minAddress = min(max(minaddr, sp.minAddress), maxaddr);
				sp.maxAddress = max(min(maxaddr, sp.maxAddress), minaddr);
			}
			else if (sp.address_method == 1)
			{
				auto maxoff = maxaddr - minaddr;
				sp.minAddress = minaddr + min(sp.minAddress, maxoff);
				sp.maxAddress = minaddr + min(sp.maxAddress, maxoff);
			}
			// std::tie(sp.minAddress, sp.maxAddress) = Util::QueryModuleLimits(GetModuleHandleW(sp.boundaryModule));
		}
		if (*sp.exportModule)
			addresses = GetFunctions((uintptr_t)GetModuleHandleW(sp.exportModule));
		if (*sp.boundaryModule)
		{
			auto _addresses = GetFunctions((uintptr_t)GetModuleHandleW(sp.boundaryModule));
			mergevector(addresses, _addresses);
		}
		std::vector<uintptr_t> addresses1;
		if (sp.search_method == 0)
		{
			for (auto &addr : addresses1 = Util::SearchMemory(sp.pattern, sp.length, PAGE_EXECUTE, sp.minAddress, sp.maxAddress))
				addr += sp.offset;
		}
		else if (sp.search_method == 1)
		{
			auto checklength = 3;
			auto checker = [checklength](DWORD k)
			{
				if (k == 0xcccccccc || k == 0x90909090 || k == 0xccccccc3 || k == 0x909090c3)
					return true;
				DWORD t = k & 0xff0000ff;
				if (t == 0xcc0000c2 || t == 0x900000c2)
					return true;
				if (checklength == 4)
					return false;
				k >>= 8;
				if (k == 0xccccc3 || k == 0x9090c3)
					return true;
				if (checklength == 3)
					return false;
				// t = k & 0xff;
				// if (t == 0xc2)
				// return true;
				k >>= 8;
				if (k == 0xccc3 || k == 0x90c3)
					return true;
				if (checklength == 2)
					return false;
				k >>= 8;
				if (k == 0xc3)
					return true;
				return false;
			};
			for (uintptr_t addr = sp.minAddress & ~0xf; addr < sp.maxAddress; addr += 0x10)
			{
				if (IsBadReadPtr((void *)(addr - 0x10), 0x110))
				{
					addr += 0x100 - 0x10;
					continue;
				}
				auto need = checker(*(DWORD *)(addr - 4));
				if (need)
					addresses1.push_back(addr);
			}
		}
		else if (sp.search_method == 2)
		{
			for (uintptr_t addr = sp.minAddress; addr < sp.maxAddress; addr++)
			{
				if (IsBadReadPtr((void *)addr, 0x100))
				{
					addr += 0x100 - 1;
					continue;
				}
				if (((*(BYTE *)addr) == 0xe8))
				{
					auto off = *(DWORD *)(addr + 1);
					auto funcaddr = addr + 5 + off;
					if (sp.minAddress < funcaddr && sp.maxAddress > funcaddr)
					{
						auto it = std::find(addresses1.begin(), addresses1.end(), funcaddr);
						addresses1.push_back(funcaddr);
					}
				}
			}
		}
		else if (sp.search_method == 3)
		{
			AutoHandle fm = OpenFileMappingW(FILE_MAP_READ | FILE_MAP_WRITE, FALSE, sp.sharememname);
			auto ptr = (LPWSTR)MapViewOfFile(fm, FILE_MAP_READ | FILE_MAP_WRITE, 0, 0, sp.sharememsize);
			for (auto line : strSplit(ptr, L"\n"))
			{
				if (!line.size())
					continue;
				if (startWith(line, L"//"))
					continue;
				auto spls = strSplit(line, L"\t");
				if (spls.size() > 3)
				{
					line = spls[2];
				}
				try
				{
					std::wsmatch match;
					if (!std::regex_match(line, match, std::wregex(L"^([[:xdigit:]]+)(:.+?)?(:.+)?")))
						continue;
					HookParam hp;
					hp.address = std::stoull(match[1], nullptr, 16);
					if (match[2].matched)
					{
						hp.type |= MODULE_OFFSET;
						wcsncpy_s(hp.module, match[2].str().erase(0, 1).c_str(), MAX_MODULE_SIZE - 1);
					}
					if (match[3].matched)
					{
						hp.type |= FUNCTION_OFFSET;
						std::wstring func = match[3];
						strncpy_s(hp.function, wcasta(func).erase(0, 1).c_str(), MAX_MODULE_SIZE - 1);
					}
					addresses1.push_back(getasbaddr(hp));
				}
				catch (...)
				{
				}
			}
			UnmapViewOfFile(ptr);
		}
		mergevector(addresses, addresses1);

		auto limits = Util::QueryModuleLimits(GetModuleHandleW(LUNA_HOOK_DLL));
		addresses.erase(std::remove_if(addresses.begin(), addresses.end(), [&](auto addr)
									   { return addr > limits.first && addr < limits.second; }),
						addresses.end());

		inlinehookpipeline(addresses);
	}
	else if (jittypedefault == JITTYPE::UNITY)
	{
		auto methods = loop_all_methods(false);
		try
		{
			*(void **)(trampoline + send_offset) = SendCSharpString<JITTYPE::PC>;
			std::vector<uintptr_t> addrs;
			for (auto [_, addr] : std::get<il2cpploopinfo>(methods))
				addrs.push_back(addr);
			inlinehookpipeline(addrs);
		}
		catch (std::bad_variant_access const &ex)
		{

			*(void **)(trampoline + send_offset) = SendCSharpString<JITTYPE::UNITY>;
			auto functions = std::get<monoloopinfo>(methods);
			std::vector<uintptr_t> addrs;
			for (auto [addr, func] : functions)
			{
				addrs.push_back(addr);
				remapunityjit[addr] = func;
			}
			inlinehookpipeline(addrs);
		}
	}
	else
	{

		uintptr_t minemaddr = -1, maxemaddr = 0;

		ConsoleOutput(TR[HOOK_SEARCH_INITIALIZED], jitaddr2emuaddr.size());

		for (auto addr : jitaddr2emuaddr)
		{
			minemaddr = min(minemaddr, addr.second.second);
			maxemaddr = max(maxemaddr, addr.second.second);
		}
		ConsoleOutput("%p %p", minemaddr, maxemaddr);
		ConsoleOutput("%p %p", sp.minAddress, sp.maxAddress);
		if (sp.searchTime == 0 || sp.maxAddress == 0)
		{
			auto f = fopen("JIT_ADDR_MAP_DUMP.txt", "w");
			std::stringstream cache;
			cache << std::hex;
			for (auto addr : jitaddr2emuaddr)
			{
				cache << addr.second.second << " => " << addr.first << "\n";
			}
			fprintf(f, cache.str().c_str());
			fclose(f);
			return;
		}
		safeleave = false;
		std::vector<newFuncType> funcs;
		std::vector<void *> successaddr;
		for (auto addr : jitaddr2emuaddr)
		{
			// ConsoleOutput("%llx => %p", addr.second.second ,addr.first);
			if (addr.second.second > sp.maxAddress || addr.second.second < sp.minAddress)
				continue;

			funcs.push_back(std::bind(SendJitVeh, std::placeholders::_1, addr.first, addr.second.second, addr.second.first, sp.padding));
			successaddr.push_back((void *)addr.first);
		}
		successaddr = add_veh_hook(successaddr, funcs);
		ConsoleOutput(TR[HOOK_SEARCH_INITIALIZED], successaddr.size());
		if (successaddr.size() == 0)
			return;
		ConsoleOutput(TR[MAKE_GAME_PROCESS_TEXT], sp.searchTime / 1000);
		Sleep(sp.searchTime);
		// remove_veh_hook(successaddr);
		// remove_veh_hook还是有问题，容易崩
		safeleave = true;
	}
	SearchForHooks_Return();
}
void SearchForHooks(SearchParam spUser)
{
	std::thread(_SearchForHooks, spUser)
		.detach();
}

void SearchForText(wchar_t *text, UINT codepage)
{
	bool found = false;
	char utf8Text[PATTERN_SIZE * 4] = {};
	WideCharToMultiByte(CP_UTF8, 0, text, PATTERN_SIZE, utf8Text, PATTERN_SIZE * 4, nullptr, nullptr);
	char codepageText[PATTERN_SIZE * 4] = {};
	if (codepage != CP_UTF8)
		WideCharToMultiByte(codepage, 0, text, PATTERN_SIZE, codepageText, PATTERN_SIZE * 4, nullptr, nullptr);

	if (strlen(utf8Text) < 4 || ((codepage != CP_UTF8) && (strlen(codepageText) < 4)) || wcslen(text) < 3)
		return ConsoleOutput(TR[NOT_ENOUGH_TEXT]);
	ConsoleOutput(TR[HOOK_SEARCH_STARTING]);
	auto GenerateHooks = [&](uintptr_t minaddr, std::vector<uintptr_t> addresses, HookParamType type)
	{
		for (auto addr : addresses)
		{
			if (abs((long long)(utf8Text - addr)) < 20000)
				continue; // don't add read code if text is on this thread's stack
			found = true;
			HookParam hp;
			hp.type = DIRECT_READ | type;
			hp.address = addr;
			hp.codepage = codepage;
			if (jittypedefault == JITTYPE::PCSX2)
			{
				hp.emu_addr = addr - minaddr;
				hp.jittype = JITTYPE::PCSX2;
			}
			NewHook(hp, "Search");
		}
	};
	uintptr_t minaddr = 0;
#ifdef _WIN64
	if ((jittypedefault == JITTYPE::PCSX2))
	{
		minaddr = (uintptr_t)PCSX2Types::eeMem->Main;
	}
#endif
	GenerateHooks(minaddr, Util::SearchMemory(utf8Text, strlen(utf8Text), PAGE_READWRITE, minaddr), CODEC_UTF8);
	if (codepage != CP_UTF8)
		GenerateHooks(minaddr, Util::SearchMemory(codepageText, strlen(codepageText), PAGE_READWRITE, minaddr), USING_STRING);
	GenerateHooks(minaddr, Util::SearchMemory(text, wcslen(text) * sizeof(wchar_t), PAGE_READWRITE, minaddr), CODEC_UTF16);
	if (!found)
		ConsoleOutput(TR[COULD_NOT_FIND]);
}
