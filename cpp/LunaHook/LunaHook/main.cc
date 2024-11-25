
#include "MinHook.h"
void HIJACK();
void detachall();
std::unordered_map<uint64_t, std::pair<JITTYPE, uintptr_t>> emuaddr2jitaddr;
std::unordered_map<uintptr_t, std::pair<JITTYPE, uint64_t>> jitaddr2emuaddr;
HMODULE hLUNAHOOKDLL;
WinMutex viewMutex;
CommonSharedMem *commonsharedmem;
Synchronized<std::map<uint64_t, std::pair<std::string, HookParam>>> delayinserthook;
namespace
{
	AutoHandle<> hookPipe = INVALID_HANDLE_VALUE,
				 mappedFile = INVALID_HANDLE_VALUE,
				 mappedFile3 = INVALID_HANDLE_VALUE;
	TextHook (*hooks)[MAX_HOOK];
	int currentHook = 0;
}
DWORD WINAPI Pipe(LPVOID)
{
	for (bool running = true; running; hookPipe = INVALID_HANDLE_VALUE)
	{
		DWORD count = 0;
		BYTE buffer[PIPE_BUFFER_SIZE] = {};
		AutoHandle<> hostPipe = INVALID_HANDLE_VALUE;

		while (!hostPipe || !hookPipe)
		{
			// WinMutex connectionMutex(CONNECTING_MUTEX, &allAccess);
			// std::scoped_lock lock(connectionMutex);
			WaitForSingleObject(AutoHandle<>(CreateEventW(&allAccess, FALSE, FALSE, (std::wstring(PIPE_AVAILABLE_EVENT) + std::to_wstring(GetCurrentProcessId())).c_str())), INFINITE);
			hostPipe = CreateFileW((std::wstring(HOST_PIPE) + std::to_wstring(GetCurrentProcessId())).c_str(), GENERIC_READ | FILE_WRITE_ATTRIBUTES, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
			hookPipe = CreateFileW((std::wstring(HOOK_PIPE) + std::to_wstring(GetCurrentProcessId())).c_str(), GENERIC_WRITE, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
		}
		DWORD mode = PIPE_READMODE_MESSAGE;
		SetNamedPipeHandleState(hostPipe, &mode, NULL, NULL);

		*(DWORD *)buffer = GetCurrentProcessId();
		WriteFile(hookPipe, buffer, sizeof(DWORD), &count, nullptr);
		WORD hookversion[4] = LUNA_VERSION;
		WriteFile(hookPipe, hookversion, sizeof(hookversion), &count, nullptr);

		ConsoleOutput(PIPE_CONNECTED);
		HIJACK();
		host_connected = true;
		while (running && ReadFile(hostPipe, buffer, PIPE_BUFFER_SIZE, &count, nullptr))
			switch (*(HostCommandType *)buffer)
			{
			case HOST_COMMAND_NEW_HOOK:
			{
				auto info = *(InsertHookCmd *)buffer;
				static int userHooks = 0;
				NewHook(info.hp, ("UserHook" + std::to_string(userHooks += 1)).c_str());
			}
			break;
			case HOST_COMMAND_INSERT_PC_HOOKS:
			{
				auto info = *(InsertPCHooksCmd *)buffer;
				if (info.which == 0)
					PcHooks::hookGdiGdiplusD3dxFunctions();
				else if (info.which == 1)
					PcHooks::hookOtherPcFunctions();
			}
			break;
			case HOST_COMMAND_REMOVE_HOOK:
			{
				auto info = *(RemoveHookCmd *)buffer;
				RemoveHook(info.address, 0);
			}
			break;
			case HOST_COMMAND_FIND_HOOK:
			{
				auto info = *(FindHookCmd *)buffer;
				if (*info.sp.text)
					SearchForText(info.sp.text, info.sp.codepage);
				else
					SearchForHooks(info.sp);
			}
			break;
			case HOST_COMMAND_DETACH:
			{
				running = false;
			}
			break;
			}
	}

	if (dont_detach)
	{
		host_connected = false;
		return Pipe(0);
	}
	else
	{

		MH_Uninitialize();
		for (auto &hook : *hooks)
			hook.Clear();
		FreeLibraryAndExitThread(GetModuleHandleW(LUNA_HOOK_DLL), 0);
	}
}

void TextOutput(const ThreadParam &tp, const HookParam &hp, TextOutput_T *buffer, int len)
{
	memcpy(&buffer->tp, &tp, sizeof(tp));
	memcpy(&buffer->hp, &hp, sizeof(hp));
	WriteFile(hookPipe, buffer, sizeof(TextOutput_T) + len, DUMMY, nullptr);
}

void ConsoleOutput(LPCSTR text, ...)
{
	ConsoleOutputNotif buffer;
	va_list args;
	va_start(args, text);
	vsnprintf(buffer.message, MESSAGE_SIZE, text, args);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}

void WarningOutput(LPCSTR text, ...)
{
	WarningNotif buffer;
	va_list args;
	va_start(args, text);
	vsnprintf(buffer.message, MESSAGE_SIZE, text, args);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}
Synchronized<std::unordered_map<uintptr_t, std::wstring>> modulecache;
std::wstring &querymodule(uintptr_t addr)
{
	auto &re = modulecache.Acquire().contents;
	if (re.find(addr) != re.end())
		return re.at(addr);
	WCHAR fn[MAX_PATH];
	if (GetModuleFileNameW((HMODULE)addr, fn, MAX_PATH))
	{
		re[addr] = wcsrchr(fn, L'\\') + 1;
	}
	else
	{
		re[addr] = L"";
	}
	return re[addr];
}
void NotifyHookFound(HookParam hp, wchar_t *text)
{
	if (hp.jittype == JITTYPE::PC)
		if (!(hp.type & MODULE_OFFSET))
			if (AutoHandle<> process = OpenProcess(PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, FALSE, GetCurrentProcessId()))
				if (MEMORY_BASIC_INFORMATION info = {}; VirtualQueryEx(process, (LPCVOID)hp.address, &info, sizeof(info)))
				{
					auto mm = querymodule((uintptr_t)info.AllocationBase);
					if (mm.size())
					{
						hp.type |= MODULE_OFFSET;
						hp.address -= (uint64_t)info.AllocationBase;
						wcsncpy_s(hp.module, mm.c_str(), MAX_MODULE_SIZE - 1);
					}
				}
	HookFoundNotif buffer(hp, text);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}
void NotifyHookRemove(uint64_t addr, LPCSTR name)
{
	if (name)
		ConsoleOutput(REMOVING_HOOK, name);
	HookRemovedNotif buffer(addr);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}
void NotifyHookInserting(uint64_t addr, wchar_t hookcode[])
{
	HookInsertingNotif buffer(addr);
	wcscpy(buffer.hookcode, hookcode);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}
BOOL WINAPI DllMain(HINSTANCE hModule, DWORD fdwReason, LPVOID)
{
	switch (fdwReason)
	{
	case DLL_PROCESS_ATTACH:
	{
		hLUNAHOOKDLL = hModule;
		viewMutex = WinMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(GetCurrentProcessId()), &allAccess);
		if (GetLastError() == ERROR_ALREADY_EXISTS)
			return FALSE;
		DisableThreadLibraryCalls(hModule);

		auto createfm = [](AutoHandle<> &handle, void **ptr, DWORD sz, std::wstring &name)
		{
			handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, sz, (name).c_str());
			*ptr = MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, sz);
			memset(*ptr, 0, sz);
		};
		hooks = (decltype(hooks))new TextHook[MAX_HOOK];
		VirtualProtect((LPVOID)hooks, sizeof(TextHook) * MAX_HOOK, PAGE_EXECUTE_READWRITE, DUMMY);
		createfm(mappedFile3, (void **)&commonsharedmem, sizeof(CommonSharedMem), EMBED_SHARED_MEM + std::to_wstring(GetCurrentProcessId()));

		MH_Initialize();

		CloseHandle(CreateThread(nullptr, 0, Pipe, nullptr, 0, nullptr)); // Using std::thread here = deadlock
	}
	break;
	case DLL_PROCESS_DETACH:
	{
		MH_Uninitialize();
		detachall();
		delete[] hooks;
		UnmapViewOfFile(commonsharedmem);
	}
	break;
	}
	return TRUE;
}
int HookStrLen(HookParam *hp, BYTE *data)
{
	if (data == 0)
		return 0;

	if (hp->type & CODEC_UTF16)
		return wcsnlen((wchar_t *)data, TEXT_BUFFER_SIZE) * 2;
	else if (hp->type & CODEC_UTF32)
		return strlenEx((uint32_t *)data) * 4;
	else
		return strnlen((char *)data, TEXT_BUFFER_SIZE);
}
static std::mutex maplock;
void jitaddrclear()
{
	std::lock_guard _(maplock);
	emuaddr2jitaddr.clear();
	jitaddr2emuaddr.clear();
}
void jitaddraddr(uint64_t em_addr, uintptr_t jitaddr, JITTYPE jittype)
{
	std::lock_guard _(maplock);
	emuaddr2jitaddr[em_addr] = {jittype, jitaddr};
	jitaddr2emuaddr[jitaddr] = {jittype, em_addr};
}
bool NewHook_1(HookParam &hp, LPCSTR lpname)
{
	if (hp.emu_addr)
		ConsoleOutput("%p => %p", hp.emu_addr, hp.address);

	if (++currentHook >= MAX_HOOK)
	{
		ConsoleOutput(TOO_MANY_HOOKS);
		return false;
	}
	if (lpname && *lpname)
		strncpy_s(hp.name, lpname, HOOK_NAME_SIZE - 1);

	wcscpy_s(hp.hookcode, HOOKCODE_LEN, HookCode::Generate(hp, GetCurrentProcessId()).c_str());
	if (!(*hooks)[currentHook].Insert(hp))
	{
		ConsoleOutput(InsertHookFailed, WideStringToString(hp.hookcode).c_str());
		(*hooks)[currentHook].Clear();
		return false;
	}
	else
	{
		NotifyHookInserting(hp.address, hp.hookcode);
		return true;
	}
}
void delayinsertadd(HookParam hp, std::string name)
{
	delayinserthook->insert(std::make_pair(hp.emu_addr, std::make_pair(name, hp)));
	ConsoleOutput(INSERTING_HOOK, name.c_str(), hp.emu_addr);
}
void delayinsertNewHook(uint64_t em_address)
{
	auto &&_delayinserthook = delayinserthook.Acquire();
	if (_delayinserthook->find(em_address) == _delayinserthook->end())
		return;
	auto h = _delayinserthook->at(em_address);
	_delayinserthook->erase(em_address);
	NewHook(h.second, h.first.c_str());
}
bool NewHook(HookParam hp, LPCSTR name)
{
	if (hp.address || hp.jittype == JITTYPE::PC)
		return NewHook_1(hp, name);
	if (hp.jittype == JITTYPE::UNITY)
	{
		auto spls = strSplit(hp.unityfunctioninfo, ":");
		if (spls.size() != 5)
		{
			ConsoleOutput("invalid");
			return false;
		}
		int argcount;
		try
		{
			argcount = std::stoi(spls[4]);
		}
		catch (...)
		{
			argcount = -1;
		}
		hp.address = tryfindmonoil2cpp(spls[0].c_str(), spls[1].c_str(), spls[2].c_str(), spls[3].c_str(), argcount);

		if (!hp.address)
		{
			ConsoleOutput("not find");
			return false;
		}
		return NewHook_1(hp, name);
	}
	// 下面的是手动插入
	if (emuaddr2jitaddr.find(hp.emu_addr) == emuaddr2jitaddr.end())
	{
		delayinsertadd(hp, name);
		return true;
	}
	strcpy(hp.function, "");
	wcscpy(hp.module, L"");
	hp.type &= ~MODULE_OFFSET;

	hp.address = emuaddr2jitaddr[hp.emu_addr].second;
	hp.jittype = emuaddr2jitaddr[hp.emu_addr].first;
	return NewHook_1(hp, name);
}
void RemoveHook(uint64_t addr, int maxOffset)
{
	for (auto &hook : *hooks)
		if (abs((long long)(hook.address - addr)) <= maxOffset)
			return hook.Clear();
}
std::string LoadResData(LPCWSTR pszResID, LPCWSTR _type)
{
	HMODULE hModule = hLUNAHOOKDLL;
	HRSRC hRsrc = ::FindResourceW(hModule, pszResID, _type);
	if (!hRsrc)
		return "";
	DWORD len = SizeofResource(hModule, hRsrc);
	BYTE *lpRsrc = (BYTE *)LoadResource(hModule, hRsrc);
	if (!lpRsrc)
		return "";
	HGLOBAL m_hMem = GlobalAlloc(GMEM_FIXED, len);
	BYTE *pmem = (BYTE *)GlobalLock(m_hMem);
	memcpy(pmem, lpRsrc, len);
	auto data = std::string((char *)pmem, len);
	GlobalUnlock(m_hMem);
	GlobalFree(m_hMem);
	FreeResource(lpRsrc);
	return data;
}

void context_get(hook_stack *stack, PCONTEXT context)
{
#ifndef _WIN64
	stack->eax = context->Eax;
	stack->ecx = context->Ecx;
	stack->edx = context->Edx;
	stack->ebx = context->Ebx;
	stack->esp = context->Esp;
	stack->ebp = context->Ebp;
	stack->esi = context->Esi;
	stack->edi = context->Edi;
	stack->eflags = context->EFlags;
	stack->retaddr = *(DWORD *)context->Esp;
#else
	stack->rax = context->Rax;
	stack->rbx = context->Rbx;
	stack->rcx = context->Rcx;
	stack->rdx = context->Rdx;
	stack->rsp = context->Rsp;
	stack->rbp = context->Rbp;
	stack->rsi = context->Rsi;
	stack->rdi = context->Rdi;
	stack->r8 = context->R8;
	stack->r9 = context->R9;
	stack->r10 = context->R10;
	stack->r11 = context->R11;
	stack->r12 = context->R12;
	stack->r13 = context->R13;
	stack->r14 = context->R14;
	stack->r15 = context->R15;
	stack->eflags = context->EFlags;
	stack->retaddr = *(DWORD64 *)context->Rsp;
#endif
}
void context_set(hook_stack *stack, PCONTEXT context)
{
#ifndef _WIN64
	context->Eax = stack->eax;
	context->Ecx = stack->ecx;
	context->Edx = stack->edx;
	context->Ebx = stack->ebx;
	context->Esp = stack->esp;
	context->Ebp = stack->ebp;
	context->Esi = stack->esi;
	context->Edi = stack->edi;
	context->EFlags = stack->eflags;
#else
	context->Rax = stack->rax;
	context->Rbx = stack->rbx;
	context->Rcx = stack->rcx;
	context->Rdx = stack->rdx;
	context->Rsp = stack->rsp;
	context->Rbp = stack->rbp;
	context->Rsi = stack->rsi;
	context->Rdi = stack->rdi;
	context->R8 = stack->r8;
	context->R9 = stack->r9;
	context->R10 = stack->r10;
	context->R11 = stack->r11;
	context->R12 = stack->r12;
	context->R13 = stack->r13;
	context->R14 = stack->r14;
	context->R15 = stack->r15;
	context->EFlags = stack->eflags;
#endif
}
