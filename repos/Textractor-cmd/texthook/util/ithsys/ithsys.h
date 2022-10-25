#pragma once

// ithsys.h
// 8/23/2013 jichi
// Branch: ITH/IHF_SYS.h, rev 111

#ifdef _MSC_VER
# pragma warning(disable:4800) // C4800: forcing value to bool
#endif // _MSC_VER
//#include "ntdll/ntdll.h"
#include <Windows.h>

// jichi 10/1/2013: Return 0 if failed. So, it is ambiguous if the search pattern starts at 0
DWORD SearchPattern(DWORD base, DWORD base_length, LPCVOID search, DWORD search_length); // KMP

DWORD IthGetMemoryRange(LPCVOID mem, DWORD *base, DWORD *size);

extern BYTE LeadByteTable[];

// EOF
