#pragma once

// texthook.h
// 8/24/2013 jichi
// Branch: IHF_DLL/IHF_CLIENT.h, rev 133
//
// 8/24/2013 TODO:
// - Clean up this file
// - Reduce global variables. Use namespaces or singleton classes instead.
#include "types.h"

// Artikash 6/17/2019 TODO: These have the wrong values on x64
/** jichi 12/24/2014
	  *  @param  addr  function address
	  *  @param  frame  real address of the function, supposed to be the same as addr
	  *  @param  stack  address of current stack - 4
	  *  @return  If success, which is reverted
  */
inline std::atomic<bool (*)(LPVOID addr, DWORD frame, DWORD stack)> trigger_fun = nullptr;

// jichi 9/25/2013: This class will be used by NtMapViewOfSectionfor
// interprocedure communication, where constructor/destructor will NOT work.

class TextHook
{
public:
	HookParam hp;
	union
	{
		uint64_t address;
		void* location;
	}; // Absolute address

	bool Insert(HookParam hp, DWORD set_flag);
	void Clear();

private:
	void Read();
	bool InsertHookCode();
	bool InsertReadCode();
	void Send(uintptr_t dwDatabase);
	int GetLength(uintptr_t base, uintptr_t in); // jichi 12/25/2013: Return 0 if failed
	int HookStrlen(BYTE* data);
	void RemoveHookCode();
	void RemoveReadCode();

	volatile DWORD useCount;
	HANDLE readerThread, readerEvent;
	bool err;
	BYTE trampoline[x64 ? 140 : 40];

};

enum { MAX_HOOK = 2500, HOOK_BUFFER_SIZE = MAX_HOOK * sizeof(TextHook), HOOK_SECTION_SIZE = HOOK_BUFFER_SIZE * 2 };

// EOF
