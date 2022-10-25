// ithsys.cc
// 8/21/2013 jichi
// Branch: ITH_SYS/SYS.cpp, rev 126
//
// 8/24/2013 TODO:
// - Clean up the code
// - Move my old create remote thread for ITH2 here

#include "ithsys/ithsys.h"
#include "const.h"

/**
*  Return the address of the first matched pattern.
*  Artikash 7/14/2018: changed implementation, hopefully it behaves the same
*  Return 0 if failed. The return result is ambiguous if the pattern address is 0.
*
*  @param  startAddress  search start address
*  @param  range  search range
*  @param  pattern  array of bytes to match
*  @param  patternSize  size of the pattern array
*  @return  relative offset from the startAddress
*/
DWORD SearchPattern(DWORD base, DWORD base_length, LPCVOID search, DWORD search_length)
{
	// Artikash 7/14/2018: not sure, but I think this could throw read access violation if I dont subtract search_length
	for (int i = 0; i < base_length - search_length; ++i)
		for (int j = 0; j <= search_length; ++j)
			if (j == search_length) return i; // not sure about this algorithm...
			else if (*((BYTE*)base + i + j) != *((BYTE*)search + j) && *((BYTE*)search + j) != XX) break;
		//if (memcmp((void*)(base + i), search, search_length) == 0)
			//return i;

	return 0;
}

DWORD IthGetMemoryRange(LPCVOID mem, DWORD *base, DWORD *size)
{
	MEMORY_BASIC_INFORMATION info = {};
	VirtualQuery(mem, &info, sizeof(info));
	if (base)
		*base = (DWORD)info.BaseAddress;
	if (size)
		*size = info.RegionSize;
	return info.Protect > PAGE_NOACCESS;
}

// jichi 6/12/2015: https://en.wikipedia.org/wiki/Shift_JIS
// Leading table for SHIFT-JIS encoding
BYTE LeadByteTable[0x100] = {
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
  2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
  2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,
  2,2,2,2,2,2,2,2,2,2,2,2,2,1,1,1
};

// EOF