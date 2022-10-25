#pragma once

#include "const.h"

class WinMutex // Like CMutex but works with scoped_lock
{
public:
	WinMutex(std::wstring name = L"", LPSECURITY_ATTRIBUTES sa = nullptr) : m(CreateMutexW(sa, FALSE, name.empty() ? NULL : name.c_str())) {}
	void lock() { if (m) WaitForSingleObject(m, INFINITE); }
	void unlock() { if (m) ReleaseMutex(m); }

private:
	AutoHandle<> m;
};

inline SECURITY_ATTRIBUTES allAccess = std::invoke([] // allows non-admin processes to access kernel objects made by admin processes
{
	static SECURITY_DESCRIPTOR sd = {};
	InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
	SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
	return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };
});

// jichi 3/7/2014: Add guessed comment
struct HookParam
{
	uint64_t address; // absolute or relative address
	int offset, // offset of the data in the memory
		index, // deref_offset1
		split, // offset of the split character
		split_index, // deref_offset2
		null_length;

	wchar_t module[MAX_MODULE_SIZE];

	char function[MAX_MODULE_SIZE];
	DWORD type; // flags
	UINT codepage; // text encoding
	short length_offset; // index of the string length
	uintptr_t padding; // padding before string
	DWORD user_value; // 7/20/2014: jichi additional parameters for PSP games

	void(*text_fun)(DWORD stack, HookParam* hp, BYTE obsoleteAlwaysZero, DWORD* data, DWORD* split, DWORD* len);
	bool(*filter_fun)(void* data, DWORD* len, HookParam* hp, BYTE obsoleteAlwaysZero); // jichi 10/24/2014: Add filter function. Return false to skip the text
	bool(*hook_fun)(DWORD stack, HookParam* hp); // jichi 10/24/2014: Add generic hook function, return false if stop execution.
	int(*length_fun)(uintptr_t stack, uintptr_t data); // data after padding added

	char name[HOOK_NAME_SIZE];
};

struct ThreadParam
{
	bool operator==(ThreadParam other) const { return processId == other.processId && addr == other.addr && ctx == other.ctx && ctx2 == other.ctx2; }
	DWORD processId;
	uint64_t addr;
	uint64_t ctx; // The context of the hook: by default the first value on stack, usually the return address
	uint64_t ctx2;  // The subcontext of the hook: 0 by default, generated in a method specific to the hook
};

struct SearchParam
{
	BYTE pattern[PATTERN_SIZE] = { x64 ? 0xcc : 0x55, x64 ? 0xcc : 0x8b, x64 ? 0x48 : 0xec, 0x89 }; // pattern in memory to search for
	int length = x64 ? 4 : 3, // length of pattern (zero means this SearchParam is invalid and the default should be used)
		offset = x64 ? 2 : 0, // offset from start of pattern to add hook
		searchTime = 30000, // ms
		maxRecords = 100000,
		codepage = SHIFT_JIS;
	uintptr_t padding = 0, // same as hook param padding
		minAddress = 0, maxAddress = (uintptr_t)-1; // hook all functions between these addresses (used only if both modules empty)
	wchar_t boundaryModule[MAX_MODULE_SIZE] = {}; // hook all functions within this module (middle priority)
	wchar_t exportModule[MAX_MODULE_SIZE] = {}; // hook the exports of this module (highest priority)
	wchar_t text[PATTERN_SIZE] = {}; // text to search for
	void(*hookPostProcessor)(HookParam&) = nullptr;
};

struct InsertHookCmd // From host
{
	InsertHookCmd(HookParam hp) : hp(hp) {}
	HostCommandType command = HOST_COMMAND_NEW_HOOK;
	HookParam hp;
};

struct RemoveHookCmd // From host
{
	RemoveHookCmd(uint64_t address) : address(address) {}
	HostCommandType command = HOST_COMMAND_REMOVE_HOOK;
	uint64_t address;
};

struct FindHookCmd // From host
{
	FindHookCmd(SearchParam sp) : sp(sp) {}
	HostCommandType command = HOST_COMMAND_FIND_HOOK;
	SearchParam sp;
};

struct ConsoleOutputNotif // From dll
{
	ConsoleOutputNotif(std::string message = "") { strncpy_s(this->message, message.c_str(), MESSAGE_SIZE - 1); }
	HostNotificationType command = HOST_NOTIFICATION_TEXT;
	char message[MESSAGE_SIZE] = {};
};

struct HookFoundNotif // From dll
{
	HookFoundNotif(HookParam hp, wchar_t* text) : hp(hp) { wcsncpy_s(this->text, text, MESSAGE_SIZE - 1); }
	HostNotificationType command = HOST_NOTIFICATION_FOUND_HOOK;
	HookParam hp;
	wchar_t text[MESSAGE_SIZE] = {}; // though type is wchar_t, may not be encoded in UTF-16 (it's just convenient to use wcs* functions)
};

struct HookRemovedNotif // From dll
{
	HookRemovedNotif(uint64_t address) : address(address) {};
	HostNotificationType command = HOST_NOTIFICATION_RMVHOOK;
	uint64_t address;
};
