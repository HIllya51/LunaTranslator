#pragma once

// util.h
// 8/23/2013 jichi

#define XX2 XX, XX   // WORD
#define XX4 XX2, XX2 // DWORD
#define XX8 XX4, XX4 // QWORD
enum : DWORD
{
  X64_MAX_REL_ADDR = 0x00300000
};
enum : DWORD
{
  MAX_REL_ADDR = 0x00300000
};

namespace
{
  static union
  {
    char text_buffer[0x1000];
    wchar_t wc_buffer[0x800];
  };
  DWORD buffer_index,
      buffer_length;
}

namespace Util
{

#ifndef _WIN64
  DWORD GetCodeRange(DWORD hModule, DWORD *low, DWORD *high);
  DWORD FindCallAndEntryBoth(DWORD fun, DWORD size, DWORD pt, DWORD sig);
  DWORD FindCallOrJmpRel(DWORD fun, DWORD size, DWORD pt, bool jmp);
  DWORD FindCallOrJmpAbs(DWORD fun, DWORD size, DWORD pt, bool jmp);
  DWORD FindCallBoth(DWORD fun, DWORD size, DWORD pt);
  DWORD FindCallAndEntryAbs(DWORD fun, DWORD size, DWORD pt, DWORD sig);
  DWORD FindCallAndEntryRel(DWORD fun, DWORD size, DWORD pt, DWORD sig);
  DWORD FindImportEntry(DWORD hModule, DWORD fun);
#endif

  bool CheckFile_exits(LPCWSTR name, bool if_exits_also_ok = false);
  bool CheckFile(LPCWSTR name);

  bool SearchResourceString(LPCWSTR str, HMODULE hModule = NULL);

  std::pair<uintptr_t, uintptr_t> QueryModuleLimits(HMODULE module, uintptr_t addition = 0x1000, DWORD protect = PAGE_EXECUTE);
  std::vector<uintptr_t> SearchMemory(const void *bytes, short length, DWORD protect = PAGE_EXECUTE, uintptr_t minAddr = 0, uintptr_t maxAddr = -1ULL);
  uintptr_t FindFunction(const char *function);

} // namespace Util

#ifndef _WIN64

std::vector<DWORD> findrelativecall(const BYTE *pattern, int length, DWORD calladdress, DWORD start, DWORD end);
uintptr_t findfuncstart(uintptr_t addr, uintptr_t range = 0x100, bool checkalign = false);
uintptr_t findiatcallormov(uintptr_t addr, DWORD hmodule, uintptr_t start, uintptr_t end, bool reverse = false, BYTE movreg = 0);
std::vector<uintptr_t> findiatcallormov_all(uintptr_t addr, DWORD hmodule, uintptr_t start, uintptr_t end, DWORD protect, BYTE movreg = 0);

#endif

uintptr_t find_pattern(const char *pattern, uintptr_t start, uintptr_t end);
uintptr_t reverseFindBytes(const BYTE *pattern, int length, uintptr_t start, uintptr_t end, int offset = 0, bool checkalign = false);

std::vector<uintptr_t> findxref_reverse(uintptr_t addr, uintptr_t from, uintptr_t to);
std::vector<uintptr_t> findxref_reverse_checkcallop(uintptr_t addr, uintptr_t from, uintptr_t to, BYTE op);

namespace Engine
{
  bool isAddressReadable(const uintptr_t *p);
  bool isAddressReadable(const char *p, size_t count = 1);
  bool isAddressReadable(const wchar_t *p, size_t count = 1);
  bool isAddressWritable(const uintptr_t *p);
  bool isAddressWritable(const char *p, size_t count = 1);
  bool isAddressWritable(const wchar_t *p, size_t count = 1);
  inline bool isAddressReadable(const void *addr) { return isAddressReadable((const uintptr_t *)addr); }
  inline bool isAddressReadable(uintptr_t addr) { return isAddressReadable((const void *)addr); }
  inline bool isAddressWritable(const void *addr) { return isAddressWritable((const uintptr_t *)addr); }
  inline bool isAddressWritable(uintptr_t addr) { return isAddressWritable((const void *)addr); }
}

struct WindowInfo
{
  HWND handle;
  std::wstring title;
};
std::vector<WindowInfo> get_proc_windows();

template <typename StringT>
auto allocateString(const StringT &s) -> typename StringT::value_type *
{
  size_t t = s.size();
  typename StringT::value_type *_data = new typename StringT::value_type[t + 1];
  memcpy(_data, s.data(), strSize(s));
  _data[t] = 0;
  return _data;
}

bool IsShiftjisWord(WORD w);
bool IsShiftjisLeadByte(BYTE b);
