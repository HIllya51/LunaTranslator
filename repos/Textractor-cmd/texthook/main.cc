// main.cc
// 8/24/2013 jichi
// Branch: ITH_DLL/main.cpp, rev 128
// 8/24/2013 TODO: Clean up this file

#include "main.h"
#include "defs.h"
#include "engine/match.h"
#include "texthook.h"
#include "hookfinder.h"
#include "util.h"
#include "MinHook.h"

extern const char* PIPE_CONNECTED;
extern const char* INSERTING_HOOK;
extern const char* REMOVING_HOOK;
extern const char* HOOK_FAILED;
extern const char* TOO_MANY_HOOKS;

WinMutex viewMutex;

namespace
{
	AutoHandle<> hookPipe = INVALID_HANDLE_VALUE, mappedFile = INVALID_HANDLE_VALUE;
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
			WinMutex connectionMutex(CONNECTING_MUTEX, &allAccess);
			std::scoped_lock lock(connectionMutex);
			WaitForSingleObject(AutoHandle<>(CreateEventW(&allAccess, FALSE, FALSE, PIPE_AVAILABLE_EVENT)), INFINITE);
			hostPipe = CreateFileW(HOST_PIPE, GENERIC_READ | FILE_WRITE_ATTRIBUTES, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
			hookPipe = CreateFileW(HOOK_PIPE, GENERIC_WRITE, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr);
		}
		DWORD mode = PIPE_READMODE_MESSAGE;
		SetNamedPipeHandleState(hostPipe, &mode, NULL, NULL);

		*(DWORD*)buffer = GetCurrentProcessId();
		WriteFile(hookPipe, buffer, sizeof(DWORD), &count, nullptr);

		ConsoleOutput(PIPE_CONNECTED);
		Engine::Hijack();

		while (running && ReadFile(hostPipe, buffer, PIPE_BUFFER_SIZE, &count, nullptr))
			switch (*(HostCommandType*)buffer)
			{
			case HOST_COMMAND_NEW_HOOK:
			{
				auto info = *(InsertHookCmd*)buffer;
				static int userHooks = 0;
				NewHook(info.hp, ("UserHook" + std::to_string(userHooks += 1)).c_str(), 0);
			}
			break;
			case HOST_COMMAND_REMOVE_HOOK:
			{
				auto info = *(RemoveHookCmd*)buffer;
				RemoveHook(info.address, 0);
			}
			break;
			case HOST_COMMAND_FIND_HOOK:
			{
				auto info = *(FindHookCmd*)buffer;
				if (*info.sp.text) SearchForText(info.sp.text, info.sp.codepage);
				else SearchForHooks(info.sp);
			}
			break;
			case HOST_COMMAND_DETACH:
			{
				running = false;
			}
			break;
			}
	}

	MH_Uninitialize();
	for (auto& hook : *hooks) hook.Clear();
	FreeLibraryAndExitThread(GetModuleHandleW(ITH_DLL), 0);
}

void TextOutput(ThreadParam tp, BYTE (*buffer)[PIPE_BUFFER_SIZE], int len)
{
	if (len < 0 || len > PIPE_BUFFER_SIZE - sizeof(tp)) ConsoleOutput("Textractor: something went very wrong (invalid length %d at hook address %I64d)", len, tp.addr);
	*(ThreadParam*)buffer = tp;
	WriteFile(hookPipe, buffer, sizeof(tp) + len, DUMMY, nullptr);
}

void ConsoleOutput(LPCSTR text, ...)
{
	ConsoleOutputNotif buffer;
	va_list args;
	va_start(args, text);
	vsnprintf(buffer.message, MESSAGE_SIZE, text, args);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}

void NotifyHookFound(HookParam hp, wchar_t* text)
{
	HookFoundNotif buffer(hp, text);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}

void NotifyHookRemove(uint64_t addr, LPCSTR name)
{
	if (name) ConsoleOutput(REMOVING_HOOK, name);
	HookRemovedNotif buffer(addr);
	WriteFile(hookPipe, &buffer, sizeof(buffer), DUMMY, nullptr);
}

BOOL WINAPI DllMain(HINSTANCE hModule, DWORD fdwReason, LPVOID)
{
	switch (fdwReason) 
	{
	case DLL_PROCESS_ATTACH:
	{
		viewMutex = WinMutex(ITH_HOOKMAN_MUTEX_ + std::to_wstring(GetCurrentProcessId()), &allAccess);
		if (GetLastError() == ERROR_ALREADY_EXISTS) return FALSE;
		DisableThreadLibraryCalls(hModule);

		// jichi 9/25/2013: Interprocedural communication with vnrsrv.
		mappedFile = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, HOOK_SECTION_SIZE, (ITH_SECTION_ + std::to_wstring(GetCurrentProcessId())).c_str());
		hooks = (TextHook(*)[MAX_HOOK])MapViewOfFile(mappedFile, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, HOOK_BUFFER_SIZE);
		memset(hooks, 0, HOOK_BUFFER_SIZE);

		MH_Initialize();

		CloseHandle(CreateThread(nullptr, 0, Pipe, nullptr, 0, nullptr)); // Using std::thread here = deadlock
	} 
	break;
	case DLL_PROCESS_DETACH:
	{
		MH_Uninitialize();
		UnmapViewOfFile(hooks);
	}
	break;
	}
	return TRUE;
}

void NewHook(HookParam hp, LPCSTR lpname, DWORD flag)
{
	if (++currentHook >= MAX_HOOK) return ConsoleOutput(TOO_MANY_HOOKS);
	if (lpname && *lpname) strncpy_s(hp.name, lpname, HOOK_NAME_SIZE - 1);
	ConsoleOutput(INSERTING_HOOK, hp.name);
	RemoveHook(hp.address, 0);
	if (!(*hooks)[currentHook].Insert(hp, flag))
	{
		ConsoleOutput(HOOK_FAILED);
		(*hooks)[currentHook].Clear();
	}
}

void RemoveHook(uint64_t addr, int maxOffset)
{
	for (auto& hook : *hooks) if (abs((long long)(hook.address - addr)) <= maxOffset) return hook.Clear();
}

// EOF
