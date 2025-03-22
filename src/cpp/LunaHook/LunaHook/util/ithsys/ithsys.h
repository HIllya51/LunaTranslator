#pragma once

// ithsys.h
// 8/23/2013 jichi
// Branch: ITH/IHF_SYS.h, rev 111

#ifdef _MSC_VER
#pragma warning(disable : 4800) // C4800: forcing value to bool
#endif                          // _MSC_VER
// #include "ntdll/ntdll.h"
#include <Windows.h>

// jichi 10/1/2013: Return 0 if failed. So, it is ambiguous if the search pattern starts at 0
uintptr_t SearchPattern(uintptr_t base, uintptr_t base_length, LPCVOID search, uintptr_t search_length);
bool MatchPattern(uintptr_t base, LPCVOID target, uintptr_t search_length);

uintptr_t IthGetMemoryRange(LPCVOID mem, uintptr_t *base, size_t *size);

extern BYTE LeadByteTable[];

// EOF
