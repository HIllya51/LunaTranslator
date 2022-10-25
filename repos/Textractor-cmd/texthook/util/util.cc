// util/util.cc
// 8/23/2013 jichi
// Branch: ITH_Engine/engine.cpp, revision 133
// See: http://ja.wikipedia.org/wiki/プロジェクト:美少女ゲーム系/ゲームエンジン

#include "util/util.h"
#include "ithsys/ithsys.h"
#include "main.h"
#include <Psapi.h>

namespace { // unnamed

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

uint64_t SafeSearchMemory(uint64_t startAddr, uint64_t endAddr, const BYTE* bytes, short length)
{
	__try
	{
		for (int i = 0; i < endAddr - startAddr - length; ++i)
			for (int j = 0; j <= length; ++j)
				if (j == length) return startAddr + i; // not sure about this algorithm...
				else if (*((BYTE*)startAddr + i + j) != *(bytes + j) && *(bytes + j) != XX) break;
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		ConsoleOutput("Textractor: SearchMemory ERROR (Textractor will likely still work fine, but please let Artikash know if this happens a lot!)");
	}
	return 0;
}

} // namespace unnamed

namespace Util
{

// jichi 8/24/2013: binary search?
DWORD GetCodeRange(DWORD hModule,DWORD *low, DWORD *high)
{
  IMAGE_DOS_HEADER *DosHdr;
  IMAGE_NT_HEADERS *NtHdr;
  DWORD dwReadAddr;
  IMAGE_SECTION_HEADER *shdr;
  DosHdr = (IMAGE_DOS_HEADER *)hModule;
  if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic) {
    dwReadAddr = hModule + DosHdr->e_lfanew;
    NtHdr = (IMAGE_NT_HEADERS *)dwReadAddr;
    if (IMAGE_NT_SIGNATURE == NtHdr->Signature) {
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
  //WCHAR str[0x40];
  enum { reverse_length = 0x800 };
  DWORD t, l;
  DWORD mask = SigMask(sig);
  bool flag2;
  for (DWORD i = 0x1000; i < size-4; i++) {
    bool flag1 = false;
    if (*(BYTE *)(pt + i) == 0xe8) {
      flag1 = flag2 = true;
      t = *(DWORD *)(pt + i + 1);
    } else if (*(WORD *)(pt + i) == 0x15ff) {
      flag1 = true;
      flag2 = false;
      t = *(DWORD *)(pt + i + 2);
    }
    if (flag1) {
      if (flag2) {
        flag1 = (pt + i + 5 + t == fun);
        l = 5;
      } else if (t >= pt && t <= pt + size - 4) {
        flag1 = fun == *(DWORD *)t;
        l = 6;
      } else
        flag1 = false;
      if (flag1)
        //swprintf(str,L"CALL addr: 0x%.8X",pt + i);
        //OutputConsole(str);
        for (DWORD j = i; j > i - reverse_length; j--)
          if ((*(WORD *)(pt + j)) == (sig & mask))  //Fun entry 1.
            //swprintf(str,L"Entry: 0x%.8X",pt + j);
            //OutputConsole(str);
            return pt + j;
      else
        i += l;
    }
  }
  //OutputConsole(L"Find call and entry failed.");
  return 0;
}

DWORD FindCallOrJmpRel(DWORD fun, DWORD size, DWORD pt, bool jmp)
{
  BYTE sig = (jmp) ? 0xe9 : 0xe8;
  for (DWORD i = 0x1000; i < size - 4; i++)
    if (sig == *(BYTE *)(pt + i)) {
      DWORD t = *(DWORD *)(pt + i + 1);
      if(fun == pt + i + 5 + t)
        //OutputDWORD(pt + i);
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
    if (sig == *(WORD *)(pt + i)) {
      DWORD t = *(DWORD *)(pt + i + 2);
      if (t > pt && t < pt + size) {
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
  for (DWORD i = 0x1000; i < size - 4; i++) {
    if (*(BYTE *)(pt + i) == 0xe8) {
      DWORD t = *(DWORD *)(pt + i + 1) + pt + i + 5;
      if (t == fun)
        return i;
    }
    if (*(WORD *)(pt + i) == 0x15ff) {
      DWORD t = *(DWORD *)(pt + i + 2);
      if (t >= pt && t <= pt + size - 4) {
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
  //WCHAR str[0x40];
  enum { reverse_length = 0x800 };
  DWORD mask = SigMask(sig);
  for (DWORD i = 0x1000; i < size - 4; i++)
    if (*(WORD *)(pt + i) == 0x15ff) {
      DWORD t = *(DWORD *)(pt + i + 2);
      if (t >= pt && t <= pt + size - 4) {
        if (*(DWORD *)t == fun)
          //swprintf(str,L"CALL addr: 0x%.8X",pt + i);
          //OutputConsole(str);
          for (DWORD j = i ; j > i - reverse_length; j--)
            if ((*(DWORD *)(pt + j) & mask) == sig) // Fun entry 1.
              //swprintf(str,L"Entry: 0x%.8X",pt + j);
              //OutputConsole(str);
              return pt + j;

      } else
        i += 6;
    }
  //OutputConsole(L"Find call and entry failed.");
  return 0;
}

DWORD FindCallAndEntryRel(DWORD fun, DWORD size, DWORD pt, DWORD sig)
{
  //WCHAR str[0x40];
  enum { reverse_length = 0x800 };
  if (DWORD i = FindCallOrJmpRel(fun, size, pt, false)) {
    DWORD mask = SigMask(sig);
    for (DWORD j = i; j > i - reverse_length; j--)
      if (((*(DWORD *)j) & mask) == sig)  //Fun entry 1.
        //swprintf(str,L"Entry: 0x%.8X",j);
        //OutputConsole(str);
        return j;
      //OutputConsole(L"Find call and entry failed.");
  }
  return 0;
}

bool CheckFile(LPCWSTR name)
{
	WIN32_FIND_DATAW unused;
	HANDLE file = FindFirstFileW(name, &unused);
	if (file != INVALID_HANDLE_VALUE)
	{
		FindClose(file);
		return true;
	}
	wchar_t path[MAX_PATH * 2];
	wchar_t* end = path + GetModuleFileNameW(nullptr, path, MAX_PATH);
	while (*(--end) != L'\\');
	wcscpy_s(end + 1, MAX_PATH, name);
	file = FindFirstFileW(path, &unused);
	if (file != INVALID_HANDLE_VALUE)
	{
		FindClose(file);
		return true;
	}
	return false;
}

DWORD FindEntryAligned(DWORD start, DWORD back_range)
{
  start &= ~0xf;
  for (DWORD i = start, j = start - back_range; i > j; i-=0x10) {
    DWORD k = *(DWORD *)(i-4);
    if (k == 0xcccccccc
      || k == 0x90909090
      || k == 0xccccccc3
      || k == 0x909090c3
      )
      return i;
    DWORD t = k & 0xff0000ff;
    if (t == 0xcc0000c2 || t == 0x900000c2)
      return i;
    k >>= 8;
    if (k == 0xccccc3 || k == 0x9090c3)
      return i;
    t = k & 0xff;
    if (t == 0xc2)
      return i;
    k >>= 8;
    if (k == 0xccc3 || k == 0x90c3)
      return i;
    k >>= 8;
    if (k == 0xc3)
      return i;
  }
  return 0;
}

DWORD FindImportEntry(DWORD hModule, DWORD fun)
{
  IMAGE_DOS_HEADER *DosHdr;
  IMAGE_NT_HEADERS *NtHdr;
  DWORD IAT, end, pt, addr;
  DosHdr = (IMAGE_DOS_HEADER *)hModule;
  if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic) {
    NtHdr = (IMAGE_NT_HEADERS *)(hModule + DosHdr->e_lfanew);
    if (IMAGE_NT_SIGNATURE == NtHdr->Signature) {
      IAT = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].VirtualAddress;
      end = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IAT].Size;
      IAT += hModule;
      end += IAT;
      for (pt = IAT; pt < end; pt += 4) {
        addr = *(DWORD *)pt;
        if (addr == fun)
          return pt;
      }
    }
  }
  return 0;
}

// Search string in rsrc section. This section usually contains version and copyright info.
bool SearchResourceString(LPCWSTR str)
{
  DWORD hModule = (DWORD)GetModuleHandleW(nullptr);
  IMAGE_DOS_HEADER *DosHdr;
  IMAGE_NT_HEADERS *NtHdr;
  DosHdr = (IMAGE_DOS_HEADER *)hModule;
  DWORD rsrc, size;
  //__asm int 3
  if (IMAGE_DOS_SIGNATURE == DosHdr->e_magic) {
    NtHdr = (IMAGE_NT_HEADERS *)(hModule + DosHdr->e_lfanew);
    if (IMAGE_NT_SIGNATURE == NtHdr->Signature) {
      rsrc = NtHdr->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_RESOURCE].VirtualAddress;
      if (rsrc) {
        rsrc += hModule;
        if (IthGetMemoryRange((LPVOID)rsrc, &rsrc ,&size) &&
            SearchPattern(rsrc, size - 4, str, wcslen(str) << 1))
          return true;
      }
    }
  }
  return false;
}

std::pair<uint64_t, uint64_t> QueryModuleLimits(HMODULE module)
{
	uintptr_t moduleStartAddress = (uintptr_t)module + 0x1000;
	uintptr_t moduleStopAddress = moduleStartAddress;
	MEMORY_BASIC_INFORMATION info;
	do
	{
		VirtualQuery((void*)moduleStopAddress, &info, sizeof(info));
		moduleStopAddress = (uintptr_t)info.BaseAddress + info.RegionSize;
	} while (info.Protect >= PAGE_EXECUTE);
	moduleStopAddress -= info.RegionSize;
	return { moduleStartAddress, moduleStopAddress };
}

std::vector<uint64_t> SearchMemory(const void* bytes, short length, DWORD protect, uintptr_t minAddr, uintptr_t maxAddr)
{
	SYSTEM_INFO systemInfo;
	GetNativeSystemInfo(&systemInfo);
	std::vector<std::pair<uint64_t, uint64_t>> validMemory;
	for (BYTE* probe = NULL; probe < systemInfo.lpMaximumApplicationAddress;)
	{
		MEMORY_BASIC_INFORMATION info = {};
		if (!VirtualQuery(probe, &info, sizeof(info)))
		{
			probe += systemInfo.dwPageSize;
			continue;
		}
		else
		{
			if ((uint64_t)info.BaseAddress + info.RegionSize >= minAddr && info.Protect >= protect && !(info.Protect & PAGE_GUARD))
				validMemory.push_back({ (uint64_t)info.BaseAddress, info.RegionSize });
			probe += info.RegionSize;
		}
	}

	std::vector<uint64_t> ret;
	for (auto memory : validMemory)
		for (uint64_t addr = max(memory.first, minAddr); true;)
			if (addr < maxAddr && (addr = SafeSearchMemory(addr, memory.first + memory.second, (const BYTE*)bytes, length)))
				ret.push_back(addr++);
			else break;

	return ret;
}

uintptr_t FindFunction(const char* function)
{
    static HMODULE modules[300] = {};
    static auto _ = EnumProcessModules(GetCurrentProcess(), modules, sizeof(modules), DUMMY);
    for (auto module : modules) if (auto addr = GetProcAddress(module, function)) return (uintptr_t)addr;
    return 0;
}

}

// EOF
