#pragma once

// util.h
// 8/23/2013 jichi

namespace Util {

bool unloadCurrentModule();

DWORD GetCodeRange(DWORD hModule,DWORD *low, DWORD *high);
DWORD FindCallAndEntryBoth(DWORD fun, DWORD size, DWORD pt, DWORD sig);
DWORD FindCallOrJmpRel(DWORD fun, DWORD size, DWORD pt, bool jmp);
DWORD FindCallOrJmpAbs(DWORD fun, DWORD size, DWORD pt, bool jmp);
DWORD FindCallBoth(DWORD fun, DWORD size, DWORD pt);
DWORD FindCallAndEntryAbs(DWORD fun, DWORD size, DWORD pt, DWORD sig);
DWORD FindCallAndEntryRel(DWORD fun, DWORD size, DWORD pt, DWORD sig);
DWORD FindEntryAligned(DWORD start, DWORD back_range);
DWORD FindImportEntry(DWORD hModule, DWORD fun);
bool CheckFile(LPCWSTR name);

bool SearchResourceString(LPCWSTR str);

std::pair<uint64_t, uint64_t> QueryModuleLimits(HMODULE module);
std::vector<uint64_t> SearchMemory(const void* bytes, short length, DWORD protect = PAGE_EXECUTE, uintptr_t minAddr = 0, uintptr_t maxAddr = -1ULL);
uintptr_t FindFunction(const char* function);

} // namespace Util

// EOF
