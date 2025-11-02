

namespace
{ // unnamed

  // jichi 4/19/2014: Return the integer that can mask the signature
  // Artikash 8/4/2018: change implementation
  DWORD SigMask(DWORD sig)
  {
    DWORD count = 0;
    while (sig)
    {
      sig >>= 8;
      ++count;
    }
    count -= 4;
    count = -count;
    return 0xffffffff >> (count << 3);
  }

  uint64_t SafeSearchMemory(uint64_t startAddr, uint64_t endAddr, const BYTE *bytes, short length)
  {
    __try
    {
      for (int i = 0; i < endAddr - startAddr - length; ++i)
        for (int j = 0; j <= length; ++j)
          if (j == length)
            return startAddr + i; // not sure about this algorithm...
          else if (*((BYTE *)startAddr + i + j) != *(bytes + j) && *(bytes + j) != XX)
            break;
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
      ConsoleOutput("SearchMemory ERROR");
    }
    return 0;
  }

} // namespace unnamed

namespace Util
{

#ifndef _WIN64
  // jichi 8/24/2013: binary search?
  DWORD GetCodeRange(DWORD hModule, DWORD *low, DWORD *high)
  {
    IMAGE_DOS_HEADER *DosHdr;
    IMAGE_NT_HEADERS *NtHdr;
    DWORD dwReadAddr;
    IMAGE_SECTION_HEADER *shdr;
    DosHdr = (IMAGE_DOS_HEADER *)hModule;
    if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic)
    {
      dwReadAddr = hModule + DosHdr->e_lfanew;
      NtHdr = (IMAGE_NT_HEADERS *)dwReadAddr;
      if (IMAGE_NT_SIGNATURE == NtHdr->Signature)
      {
        shdr = (PIMAGE_SECTION_HEADER)((DWORD)(&NtHdr->OptionalHeader) + NtHdr->FileHeader.SizeOfOptionalHeader);
        while ((shdr->Characteristics & IMAGE_SCN_CNT_CODE) == 0)
          shdr++;
        *low = hModule + shdr->VirtualAddress;
        *high = *low + (shdr->Misc.VirtualSize & 0xfffff000) + 0x1000;
      }
    }
    return 0;
  }

  DWORD FindCallAndEntryBoth(DWORD fun, DWORD size, DWORD pt, DWORD sig)
  {
    // WCHAR str[0x40];
    enum
    {
      reverse_length = 0x800
    };
    DWORD t, l;
    DWORD mask = SigMask(sig);
    bool flag2;
    for (DWORD i = 0x1000; i < size - 4; i++)
    {
      bool flag1 = false;
      if (*(BYTE *)(pt + i) == 0xe8)
      {
        flag1 = flag2 = true;
        t = *(DWORD *)(pt + i + 1);
      }
      else if (*(WORD *)(pt + i) == 0x15ff)
      {
        flag1 = true;
        flag2 = false;
        t = *(DWORD *)(pt + i + 2);
      }
      if (flag1)
      {
        if (flag2)
        {
          flag1 = (pt + i + 5 + t == fun);
          l = 5;
        }
        else if (t >= pt && t <= pt + size - 4)
        {
          flag1 = fun == *(DWORD *)t;
          l = 6;
        }
        else
          flag1 = false;
        if (flag1)
          // swprintf(str,L"CALL addr: 0x%.8X",pt + i);
          // OutputConsole(str);
          for (DWORD j = i; j > i - reverse_length; j--)
            if ((*(WORD *)(pt + j)) == (sig & mask)) // Fun entry 1.
              // swprintf(str,L"Entry: 0x%.8X",pt + j);
              // OutputConsole(str);
              return pt + j;
            else
              i += l;
      }
    }
    // OutputConsole(L"Find call and entry failed.");
    return 0;
  }

  DWORD FindCallOrJmpRel(DWORD fun, DWORD size, DWORD pt, bool jmp)
  {
    BYTE sig = (jmp) ? 0xe9 : 0xe8;
    for (DWORD i = 0x1000; i < size - 4; i++)
      if (sig == *(BYTE *)(pt + i))
      {
        DWORD t = *(DWORD *)(pt + i + 1);
        if (fun == pt + i + 5 + t)
          // OutputDWORD(pt + i);
          return pt + i;
        else
          i += 5;
      }
    return 0;
  }

  DWORD FindCallOrJmpAbs(DWORD fun, DWORD size, DWORD pt, bool jmp)
  {
    WORD sig = jmp ? 0x25ff : 0x15ff;
    for (DWORD i = 0x1000; i < size - 4; i++)
      if (sig == *(WORD *)(pt + i))
      {
        DWORD t = *(DWORD *)(pt + i + 2);
        if (t > pt && t < pt + size)
        {
          if (fun == *(DWORD *)t)
            return pt + i;
          else
            i += 5;
        }
      }
    return 0;
  }

  DWORD FindCallBoth(DWORD fun, DWORD size, DWORD pt)
  {
    for (DWORD i = 0x1000; i < size - 4; i++)
    {
      if (*(BYTE *)(pt + i) == 0xe8)
      {
        DWORD t = *(DWORD *)(pt + i + 1) + pt + i + 5;
        if (t == fun)
          return i;
      }
      if (*(WORD *)(pt + i) == 0x15ff)
      {
        DWORD t = *(DWORD *)(pt + i + 2);
        if (t >= pt && t <= pt + size - 4)
        {
          if (*(DWORD *)t == fun)
            return i;
          else
            i += 6;
        }
      }
    }
    return 0;
  }

  DWORD FindCallAndEntryAbs(DWORD fun, DWORD size, DWORD pt, DWORD sig)
  {
    // WCHAR str[0x40];
    enum
    {
      reverse_length = 0x800
    };
    DWORD mask = SigMask(sig);
    for (DWORD i = 0x1000; i < size - 4; i++)
      if (*(WORD *)(pt + i) == 0x15ff)
      {
        DWORD t = *(DWORD *)(pt + i + 2);
        if (t >= pt && t <= pt + size - 4)
        {
          if (*(DWORD *)t == fun)
            // swprintf(str,L"CALL addr: 0x%.8X",pt + i);
            // OutputConsole(str);
            for (DWORD j = i; j > i - reverse_length; j--)
              if ((*(DWORD *)(pt + j) & mask) == sig) // Fun entry 1.
                // swprintf(str,L"Entry: 0x%.8X",pt + j);
                // OutputConsole(str);
                return pt + j;
        }
        else
          i += 6;
      }
    // OutputConsole(L"Find call and entry failed.");
    return 0;
  }

  DWORD FindCallAndEntryRel(DWORD fun, DWORD size, DWORD pt, DWORD sig)
  {
    // WCHAR str[0x40];
    enum
    {
      reverse_length = 0x800
    };
    if (DWORD i = FindCallOrJmpRel(fun, size, pt, false))
    {
      DWORD mask = SigMask(sig);
      for (DWORD j = i; j > i - reverse_length; j--)
        if (((*(DWORD *)j) & mask) == sig) // Fun entry 1.
          // swprintf(str,L"Entry: 0x%.8X",j);
          // OutputConsole(str);
          return j;
      // OutputConsole(L"Find call and entry failed.");
    }
    return 0;
  }

  DWORD FindImportEntry(DWORD hModule, DWORD fun)
  {
    IMAGE_DOS_HEADER *DosHdr;
    IMAGE_NT_HEADERS *NtHdr;
    DWORD IAT, end, pt, addr;
    DosHdr = (IMAGE_DOS_HEADER *)hModule;
    if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic)
    {
      NtHdr = (IMAGE_NT_HEADERS *)(hModule + DosHdr->e_lfanew);
      if (IMAGE_NT_SIGNATURE == NtHdr->Signature)
      {
        IAT = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].VirtualAddress;
        end = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].Size;
        IAT += hModule;
        end += IAT;
        for (pt = IAT; pt < end; pt += 4)
        {
          addr = *(DWORD *)pt;
          if (addr == fun)
            return pt;
        }
      }
    }
    return 0;
  }
#endif

  bool CheckFile(LPCWSTR name)
  {
    return CheckFile_exits(name, false);
  }
  bool CheckFile_exits(LPCWSTR name, bool if_exits_also_ok)
  {
    WIN32_FIND_DATAW unused;
    HANDLE file = FindFirstFileW(name, &unused);
    if ((file != INVALID_HANDLE_VALUE) || (if_exits_also_ok && PathFileExists(name)))
    {
      FindClose(file);
      return true;
    }
    wchar_t path[MAX_PATH * 2];
    wchar_t *end = path + GetModuleFileNameW(nullptr, path, MAX_PATH);
    while (*(--end) != L'\\')
      ;
    wcscpy_s(end + 1, MAX_PATH, name);
    file = FindFirstFileW(path, &unused);
    if ((file != INVALID_HANDLE_VALUE) || (if_exits_also_ok && PathFileExists(path)))
    {
      FindClose(file);
      return true;
    }
    return false;
  }

  // Search string in rsrc section. This section usually contains version and copyright info.
  bool SearchResourceString(LPCWSTR str, HMODULE hModule)
  {
    if (!hModule)
      hModule = GetModuleHandleW(nullptr);
    IMAGE_DOS_HEADER *DosHdr;
    IMAGE_NT_HEADERS *NtHdr;
    DosHdr = (IMAGE_DOS_HEADER *)hModule;
    uintptr_t rsrc, size;
    if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic)
    {
      NtHdr = (IMAGE_NT_HEADERS *)((uintptr_t)hModule + DosHdr->e_lfanew);
      if (IMAGE_NT_SIGNATURE == NtHdr->Signature)
      {
        rsrc = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_RESOURCE].VirtualAddress;
        if (rsrc)
        {
          rsrc += (uintptr_t)hModule;
          if (IthGetMemoryRange((LPVOID)rsrc, &rsrc, &size) &&
              SearchPattern(rsrc, size - 4, str, wcslen(str) << 1))
            return true;
        }
      }
    }
    return false;
  }

  std::pair<uintptr_t, uintptr_t> QueryModuleLimits(HMODULE module, uintptr_t addition, DWORD protect)
  {
    uintptr_t moduleStartAddress = (uintptr_t)module + addition;
    uintptr_t moduleStopAddress = moduleStartAddress;
    MEMORY_BASIC_INFORMATION info;
    do
    {
      VirtualQuery((void *)moduleStopAddress, &info, sizeof(info));
      moduleStopAddress = (uintptr_t)info.BaseAddress + info.RegionSize;
    } while (info.Protect >= protect);
    moduleStopAddress -= info.RegionSize;
    return {moduleStartAddress, moduleStopAddress};
  }

  std::vector<uintptr_t> SearchMemory(const void *bytes, short length, DWORD protect, uintptr_t minAddr, uintptr_t maxAddr)
  {
    SYSTEM_INFO systemInfo;
    GetNativeSystemInfo(&systemInfo);
    std::vector<std::pair<uintptr_t, uintptr_t>> validMemory;
    for (BYTE *probe = NULL; probe < systemInfo.lpMaximumApplicationAddress;)
    {
      MEMORY_BASIC_INFORMATION info = {};
      if (!VirtualQuery(probe, &info, sizeof(info)))
      {
        probe += systemInfo.dwPageSize;
        continue;
      }
      else
      {
        if ((uintptr_t)info.BaseAddress + info.RegionSize >= minAddr && info.Protect >= protect && !(info.Protect & PAGE_GUARD))
          validMemory.push_back({(uintptr_t)info.BaseAddress, info.RegionSize});
        probe += info.RegionSize;
      }
    }

    std::vector<uintptr_t> ret;
    for (auto memory : validMemory)
      for (uintptr_t addr = max(memory.first, minAddr); true;)
        if (addr < maxAddr && (addr = SafeSearchMemory(addr, memory.first + memory.second, (const BYTE *)bytes, length)))
          ret.push_back(addr++);
        else
          break;

    return ret;
  }

  uintptr_t FindFunction(const char *function)
  {
    static HMODULE modules[300] = {};
    static auto _ = EnumProcessModules(GetCurrentProcess(), modules, sizeof(modules), DUMMY);
    for (auto module : modules)
      if (auto addr = GetProcAddress(module, function))
        return (uintptr_t)addr;
    return 0;
  }

}

uintptr_t SafeFindEnclosingAlignedFunction(uintptr_t addr, uintptr_t range)
{
  uintptr_t r = 0;
  __try
  {
    r = MemDbg::findEnclosingAlignedFunction(addr, range); // this function might raise if failed
  }
  __except (EXCEPTION_EXECUTE_HANDLER)
  {
  }
  return r;
}

uintptr_t SafeFindBytes(LPCVOID pattern, size_t patternSize, uintptr_t lowerBound, uintptr_t upperBound)
{
  ULONG r = 0;
  __try
  {
    r = MemDbg::findBytes(pattern, patternSize, lowerBound, upperBound);
  }
  __except (EXCEPTION_EXECUTE_HANDLER)
  {
  }
  return r;
}

#ifndef _WIN64

std::vector<DWORD> findrelativecall(const BYTE *pattern, int length, DWORD calladdress, DWORD start, DWORD end)
{
  std::vector<DWORD> save;
  for (; start < end; start += 1)
  {
    DWORD addr = MemDbg::findBytes(pattern, length, start, end);
    start = addr;
    if (!addr)
      return save;

    BYTE callop = 0xE8;

    union little
    {
      DWORD _dw;
      BYTE _bytes[4];
    } relative;
    relative._dw = (calladdress - addr - length - 5);
    DWORD calladdr = addr + length;
    if (*((BYTE *)calladdr) == callop)
    {

      calladdr += 1;
      BYTE *_b = (BYTE *)calladdr;
      BYTE *_a = relative._bytes;
      /*ConsoleOutput("%p", addr);
      ConsoleOutput("%p %x", calladdress, relative._dw);
      ConsoleOutput("%02x%02x%02x%02x %02x%02x%02x%02x", _a[0], _a[1], _a[2], _a[3], _b[0], _b[1], _b[2], _b[3]);*/
      if ((_a[0] == _b[0]) && (_a[1] == _b[1]) && (_a[2] == _b[2]) && (_a[3] == _b[3]))
      {
        save.push_back(start);
      }
    }
  }
  return save;
}
uintptr_t findfuncstart(uintptr_t start, uintptr_t range, bool checkalign)
{
  if (!start)
    return 0;
  const BYTE funcstart[] = {
      0x55, 0x8b, 0xec};
  if (checkalign)
  {
    start &= ~0xf;
    for (uintptr_t i = start, j = start - range; i >= j; i -= 0x10)
    {
      if (memcmp((void *)i, funcstart, 3) == 0)
        return i;
    }
    return 0;
  }
  else
  {
    return reverseFindBytes(funcstart, sizeof(funcstart), start - range, start);
  }
}
#define buildbytes(ret)                              \
  auto entry = Util::FindImportEntry(hmodule, addr); \
  if (entry == 0)                                    \
    return ret;                                      \
  BYTE bytes[] = {XX, XX, XX4};                      \
  if (movreg)                                        \
  {                                                  \
    bytes[0] = 0x8b, bytes[1] = movreg;              \
  }                                                  \
  else                                               \
  {                                                  \
    bytes[0] = 0xff;                                 \
    bytes[1] = 0x15;                                 \
  }                                                  \
  memcpy(bytes + 2, &entry, 4);
uintptr_t findiatcallormov(uintptr_t addr, DWORD hmodule, uintptr_t start, uintptr_t end, bool reverse, BYTE movreg)
{
  buildbytes(0) if (reverse) return reverseFindBytes(bytes, sizeof(bytes), start, end);
  else return MemDbg::findBytes(bytes, sizeof(bytes), start, end);
}

std::vector<uintptr_t> findiatcallormov_all(uintptr_t addr, DWORD hmodule, uintptr_t start, uintptr_t end, DWORD protect, BYTE movreg)
{
  buildbytes({}) return Util::SearchMemory(bytes, sizeof(bytes), protect, start, end);
}
#endif

uintptr_t reverseFindBytes(const BYTE *pattern, int length, uintptr_t start, uintptr_t end, int offset, bool checkalign)
{
  for (end -= length; end >= start; end -= 1)
  {
    bool success = true;
    for (int i = 0; i < length; i++)
    {
      if (pattern[i] != *(BYTE *)(end + i) && pattern[i] != XX)
      {
        success = false;
        break;
      }
    }
    if (success)
    {
      auto ret = end + offset;

      if (checkalign && ret & 0xf)
        continue;

      return ret;
    }
    // if (memcmp(pattern, (const BYTE*)(end), length) == 0) {
    //   return end;
    // }
  }
  return 0;
}

std::vector<uintptr_t> findxref_reverse_checkcallop(uintptr_t addr, uintptr_t from, uintptr_t to, BYTE op)
{
  // op可以为E8 call E9 jump
  // 上面的版本其实就应该checkcallop的，之前忘了，但不敢乱改破坏之前的了，不然还要重新测试。
  std::vector<uintptr_t> res;
  if (!addr)
    return res;
  uintptr_t now = to;
  while (now > from)
  {
    uintptr_t calladdr = now - 5;
    if (IsBadReadPtr((LPVOID)(calladdr + 1), 4) == 0)
    {
      int relative = *(int *)(calladdr + 1);
      if (now + relative == addr)
      {
        if (*(BYTE *)calladdr == op)
          res.push_back(calladdr);
      }
    }

    now -= 1;
  }
  return res;
}
std::vector<uintptr_t> findxref_reverse(uintptr_t addr, uintptr_t from, uintptr_t to)
{
  std::vector<uintptr_t> res;
  if (!addr)
    return res;
  uintptr_t now = to;
  while (now > from)
  {
    uintptr_t calladdr = now - 5;
    uintptr_t relative = *(int *)(calladdr + 1);
    if (now + relative == addr)
    {
      res.push_back(calladdr);
    }
    now -= 1;
  }
  return res;
}
int hexCharToValue(char c)
{
  if (c >= '0' && c <= '9')
  {
    return c - '0';
  }
  else if (c >= 'A' && c <= 'F')
  {
    return c - 'A' + 10;
  }
  else if (c >= 'a' && c <= 'f')
  {
    return c - 'a' + 10;
  }
  else if (c == '?')
  {
    return -1;
  }
  else
  {
    return -2;
  }
}
uintptr_t find_pattern(const char *pattern, uintptr_t start, uintptr_t end)
{
  std::vector<int> check;
  bool ignore = false;
  for (int i = 0; i < strlen(pattern); i++)
  {
    auto c = pattern[i];
    switch (c)
    {
    case '\n':
      ignore = false; // 注释，直到换行
    case ' ':         // 忽略空格，制表，回车
    case '\t':
      break;
    case '/': // 注释
      ignore = true;
      break;
    default:
    { //? 0-9A-Fa-f
      auto _i = hexCharToValue(c);
      if (_i == -2)
        return 0;
      check.push_back(_i);
    }
    }
  }
  if (check.size() % 2 != 0)
    return 0;
  std::vector<BYTE> _type, _pattern;
  for (int j = 0; j < check.size(); j += 2)
  {
    if (check[j] != -1 && check[j + 1] != -1)
    {
      _type.push_back(0);
      _pattern.push_back(check[j] * 0x10 + check[j + 1]);
    }
    else if (check[j] == -1 && check[j + 1] == -1)
    { //??
      _type.push_back(1);
      _pattern.push_back(0);
    }
    else if (check[j] == -1)
    { //?_
      _type.push_back(2);
      _pattern.push_back(check[j + 1]);
    }
    else
    { // _?
      _type.push_back(3);
      _pattern.push_back(check[j] * 0x10);
    }
  }
  for (uintptr_t i = start; i < end; i++)
  {
    bool succ = true;
    for (int j = 0; succ && (j < _pattern.size()); j += 1)
    {
      switch (_type[j])
      {
      case 0:
      {
        if (_pattern[j] != *(BYTE *)(i + j))
        {
          succ = false;
        }
        break;
      }
      case 1:
      {
        break;
      }
      case 2:
      {
        if (((*(BYTE *)(i + j)) & 0xf) != _pattern[j])
        {
          succ = false;
        }
        break;
      }
      case 3:
      {
        if (((*(BYTE *)(i + j)) & 0xf0) != _pattern[j])
        {
          succ = false;
        }
        break;
      }
      }
    }
    if (succ)
      return i;
  }
  return 0;
}

bool Engine::isAddressReadable(const uintptr_t *p)
{
  return p && !::IsBadReadPtr(p, sizeof(*p));
}

bool Engine::isAddressReadable(const char *p, size_t count)
{
  return p && count && !::IsBadReadPtr(p, sizeof(*p) * count);
}

bool Engine::isAddressReadable(const wchar_t *p, size_t count)
{
  return p && count && !::IsBadReadPtr(p, sizeof(*p) * count);
}

bool Engine::isAddressWritable(const uintptr_t *p)
{
  return p && !::IsBadWritePtr((LPVOID)p, sizeof(*p));
}

bool Engine::isAddressWritable(const char *p, size_t count)
{
  return p && count && !::IsBadWritePtr((LPVOID)p, sizeof(*p) * count);
}

bool Engine::isAddressWritable(const wchar_t *p, size_t count)
{
  return p && count && !::IsBadWritePtr((LPVOID)p, sizeof(*p) * count);
}

BOOL CALLBACK EnumWindowsProc(HWND hwnd, LPARAM lParam)
{
  auto *hwnds = reinterpret_cast<std::vector<HWND> *>(lParam);
  DWORD processId;
  if (GetWindowThreadProcessId(hwnd, &processId) && (processId == GetCurrentProcessId()))
    hwnds->push_back(hwnd);
  return TRUE;
}
std::vector<WindowInfo> get_proc_windows()
{
  std::vector<HWND> hwnds;
  std::vector<WindowInfo> windows;
  EnumWindows(EnumWindowsProc, reinterpret_cast<LPARAM>(&hwnds));
  for (auto hwnd : hwnds)
  {
    if (!(IsWindow(hwnd) && IsWindowEnabled(hwnd) & IsWindowVisible(hwnd)))
      continue;
    WindowInfo windowInfo;
    windowInfo.handle = hwnd;
    auto length = GetWindowTextLengthW(hwnd);
    auto title = std::vector<WCHAR>(length + 1);
    GetWindowTextW(hwnd, title.data(), title.size());
    windowInfo.title = title.data();
    windows.emplace_back(windowInfo);
  }
  return windows;
}

bool IsShiftjisWord(WORD w)
{
  auto l = w & 0xff;
  auto h = (w >> 8) & 0xff;
  if (!(((l <= 0x9f) && (l >= 0x81)) || ((l <= 0xEF) && (l >= 0xE0))))
    return false;
  return ((h >= 0x40) && (h <= 0x7e)) || ((h >= 0x80) && (h <= 0xFC));
}

bool IsShiftjisLeadByte(BYTE l)
{
  // 为避免转区影响
  //  0xf0-0xfc是古早非标准兼容编码范围
  return ((l <= 0x9f) && (l >= 0x81)) || ((l <= 0xfc) && (l >= 0xE0));
}