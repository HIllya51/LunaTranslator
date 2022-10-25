#pragma once

// main.h
// 8/23/2013 jichi
// Branch: ITH/IHF_DLL.h, rev 66

#include "types.h"

void TextOutput(ThreadParam tp, BYTE (*buffer)[PIPE_BUFFER_SIZE], int len);
void ConsoleOutput(LPCSTR text, ...);
void NotifyHookFound(HookParam hp, wchar_t* text);
void NotifyHookRemove(uint64_t addr, LPCSTR name);
void NewHook(HookParam hp, LPCSTR name, DWORD flag = HOOK_ENGINE);
void RemoveHook(uint64_t addr, int maxOffset = 9);

inline SearchParam spDefault;

#define ITH_RAISE  (*(int*)0 = 0) // raise C000005, for debugging only
#define ITH_TRY    __try
#define ITH_EXCEPT __except(EXCEPTION_EXECUTE_HANDLER)
#define ITH_WITH_SEH(...) ITH_TRY { __VA_ARGS__; } ITH_EXCEPT {}

// EOF
