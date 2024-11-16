#pragma once

inline std::atomic<bool (*)(LPVOID addr, hook_stack *stack)> trigger_fun = nullptr;

class TextHook
{
public:
	HookParam hp;
	ALIGNPTR(uint64_t address, void *location);
	uint64_t savetypeforremove;
	bool Insert(HookParam hp);
	void Clear();

private:
	void Read();
	bool InsertHookCode();
	bool InsertReadCode();
	bool InsertBreakPoint();
	bool RemoveBreakPoint();
	bool breakpointcontext(PCONTEXT);
	void Send(uintptr_t dwDatabase);
	int GetLength(hook_stack *stack, uintptr_t in); // jichi 12/25/2013: Return 0 if failed
	int HookStrlen(BYTE *data);
	void RemoveHookCode();
	void RemoveReadCode();
	bool waitfornotify(TextBuffer*, ThreadParam tp);
	void parsenewlineseperator(TextBuffer*);
	volatile DWORD useCount;
	ALIGNPTR(uint64_t __1, HANDLE readerThread);
	ALIGNPTR(uint64_t __2, HANDLE readerEvent);
	bool err;
	ALIGNPTR(BYTE __4[140], BYTE trampoline[x64 ? 140 : 40]);
	ALIGNPTR(uint64_t __3, BYTE *local_buffer);
};

enum
{
	MAX_HOOK = 2500
};

// EOF
