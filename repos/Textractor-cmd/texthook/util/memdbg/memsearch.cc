// memsearch.cc
// 4/20/2014 jichi
#include "memdbg/memsearch.h"
#include "ithsys/ithsys.h"
#include <windows.h>

// Helpers

namespace { // unnamed

enum : BYTE { byte_nop = 0x90 };
enum : BYTE { byte_int3 = 0xcc };
enum : WORD { word_2int3 = 0xcccc };

// jichi 4/19/2014: Return the integer that can mask the signature
// Artikash 8/4/2018: change implementation
DWORD sigMask(DWORD sig)
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

// Modified from ITH findCallOrJmpAbs
// Example call:
// 00449063  |. ff15 5cf05300  call dword ptr ds:[<&gdi32.getglyphoutli>; \GetGlyphOutlineA
enum : WORD {
  word_jmp = 0x25ff    // long jump
  , word_call = 0x15ff // far call
};

// Modified from ITH findCallOrJmpAbs
enum : BYTE {
  byte_jmp = 0xe9 // long call
  , byte_call = 0xe8 // near call
  , byte_push_small = 0x6a // push byte operand
  , byte_push_large = 0x68 // push operand > 0xff
};

/***
 *  Return the absolute address of op. Op takes 1 parameter.
 *  DWORD call with absolute address.
 *
 *  @param  op  first half of the operator
 *  @param  arg1  the function address
 *  @param  start address
 *  @param  stop address
 *  @param  offset  search after start address
 *  @param  range  search size
 *  @return  absolute address or 0
 */
DWORD findWordCall(WORD op, DWORD arg1, DWORD start, DWORD stop, DWORD offset, DWORD range)
{
  typedef WORD optype;
  typedef DWORD argtype;

  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(DWORD *)(start + i + sizeof(optype));
      if (t > start && t < stop) {
        if (arg1 == *(argtype *)t) // absolute address
          return start + i;
        //i += sizeof(optype) + sizeof(argtype) - 1; // == 5
      }
    }
  return 0;
}

DWORD findLastWordCall(WORD op, DWORD arg1, DWORD start, DWORD stop, DWORD offset, DWORD range)
{
  typedef WORD optype;
  typedef DWORD argtype;
  DWORD ret = 0;

  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(DWORD *)(start + i + sizeof(optype));
      if (t > start && t < stop) {
        if (arg1 == *(argtype *)t) // absolute address
          ret = start + i;
        //i += sizeof(optype) + sizeof(argtype) - 1; // == 5
      }
    }
  return ret;
}


/***
 *  Return the absolute address of op. Op takes 1 address parameter.
 *  BYTE call with relative address.
 *
 *  @param  op  first half of the operator
 *  @param  arg1  the function address
 *  @param  start address
 *  @param  offset  search after start address
 *  @param  range  search size
 *  @return  absolute address or 0
 */
DWORD findByteCall(BYTE op, DWORD arg1, DWORD start, DWORD offset, DWORD range)
{
  typedef BYTE optype;
  typedef DWORD argtype;

  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(argtype *)(start + i + sizeof(optype));
      //if (t > start && t < stop) {
      if (arg1 == t + start + i + sizeof(optype) + sizeof(argtype)) // relative address
        return start + i;
      //i += sizeof(optype) + sizeof(argtype) - 1; // == 4
      //}
    }
  return 0;
}

DWORD findLastByteCall(BYTE op, DWORD arg1, DWORD start, DWORD offset, DWORD range)
{
  typedef BYTE optype;
  typedef DWORD argtype;
  DWORD ret = 0;
  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(argtype *)(start + i + sizeof(optype));
      //if (t > start && t < stop) {
      if (arg1 == t + start + i + sizeof(optype) + sizeof(argtype)) // relative address
        ret = start + i;
      //i += sizeof(optype) + sizeof(argtype) - 1; // == 4
      //}
    }
  return ret;
}

/***
 *  Return the absolute address of op. Op takes 1 parameter.
 *
 *  @param  op  first half of the operator
 *  @param  arg1  the first operand
 *  @param  start address
 *  @param  search range
 *  @return  absolute address or 0
 */
//DWORD findByteOp1(BYTE op, DWORD arg1, DWORD start, DWORD size, DWORD offset)
//{
//  typedef BYTE optype;
//  typedef DWORD argtype;
//
//  for (DWORD i = offset; i < size - sizeof(argtype); i++)
//    if (op == *(optype *)(start + i)) {
//      DWORD t = *(DWORD *)(start + i + sizeof(optype));
//      if (t == arg1) {
//        return start + i;
//      else
//        i += sizeof(optype) + sizeof(argtype) - 1; // == 4
//      }
//    }
//  return 0;
//}

} // namespace unnamed

MEMDBG_BEGIN_NAMESPACE

DWORD findLongJumpAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findWordCall(word_jmp, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findShortJumpAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findByteCall(byte_jmp, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findFarCallAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findWordCall(word_call, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findNearCallAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findByteCall(byte_call, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findLastLongJumpAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findLastWordCall(word_jmp, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findLastShortJumpAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findLastByteCall(byte_jmp, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findLastFarCallAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findLastWordCall(word_call, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findLastNearCallAddress(DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return findLastByteCall(byte_call, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

DWORD findPushDwordAddress(DWORD value, DWORD lowerBound, DWORD upperBound)
{
  //value = _byteswap_ulong(value); // swap to bigendian
  const BYTE *p = (BYTE *)&value;
  const BYTE bytes[] = {byte_push_large, p[0], p[1], p[2], p[3]};
  return findBytes(bytes, sizeof(bytes), lowerBound, upperBound);
}

DWORD findPushByteAddress(BYTE value, DWORD lowerBound, DWORD upperBound)
{
  const BYTE bytes[] = {byte_push_small, value};
  return findBytes(bytes, sizeof(bytes), lowerBound, upperBound);
}

DWORD findCallerAddress(DWORD funcAddr, DWORD sig, DWORD lowerBound, DWORD upperBound, DWORD reverseLength, DWORD offset)
{
  enum { PatternSize = 4 };
  const DWORD size = upperBound - lowerBound - PatternSize;
  const DWORD fun = (DWORD)funcAddr;
  // Example function call:
  // 00449063  |. ff15 5cf05300  call dword ptr ds:[<&gdi32.getglyphoutli>; \GetGlyphOutlineA
  //WCHAR str[0x40];
  const DWORD mask = sigMask(sig);
  for (DWORD i = offset; i < size; i++)
    if (*(WORD *)(lowerBound + i) == word_call) {
      DWORD t = *(DWORD *)(lowerBound + i + 2); // 2 = sizeof(word)
      if (t >= lowerBound && t <= upperBound - PatternSize) {
        if (*(DWORD *)t == fun)
          //swprintf(str,L"CALL addr: 0x%.8X",lowerBound + i);
          //OutputConsole(str);
          for (DWORD j = i ; j > i - reverseLength; j--)
            if ((*(DWORD *)(lowerBound + j) & mask) == sig) // Fun entry 1.
              //swprintf(str,L"Entry: 0x%.8X",lowerBound + j);
              //OutputConsole(str);
              return lowerBound + j;

      } else
        i += 6;
    }
  //OutputConsole(L"Find call and entry failed.");
  return 0;
}

#ifndef MEMDBG_NO_STL

bool iterFindBytes(const address_fun_t &fun, const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound)
{
  for (DWORD addr = lowerBound; addr < upperBound - patternSize; addr += patternSize) {
    addr = findBytes(pattern, patternSize, addr, upperBound);
    if (!addr || !fun(addr))
      return false;
  }
  return true;
}

bool iterMatchBytes(const address_fun_t &fun, const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound)
{
  for (DWORD addr = lowerBound; addr < upperBound - patternSize; addr += patternSize) { ;
    addr = findBytes(pattern, patternSize, addr, upperBound);
    if (!addr || !fun(addr))
      return false;
  }
  return true;
}

bool iterWordCall(const address_fun_t &callback, WORD op, DWORD arg1, DWORD start, DWORD stop, DWORD offset, DWORD range)
{
  typedef WORD optype;
  typedef DWORD argtype;

  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(DWORD *)(start + i + sizeof(optype));
      if (t > start && t < stop) {
        if (arg1 == *(argtype *)t // absolute address
            && !callback(start + i))
          return false;
        //i += sizeof(optype) + sizeof(argtype) - 1; // == 5
      }
    }
  return true;
}

bool iterByteCall(const address_fun_t &callback, BYTE op, DWORD arg1, DWORD start, DWORD offset, DWORD range)
{
  typedef BYTE optype;
  typedef DWORD argtype;

  for (DWORD i = offset; i < offset + range - sizeof(argtype); i++)
    if (op == *(optype *)(start + i)) {
      DWORD t = *(argtype *)(start + i + sizeof(optype));
      //if (t > start && t < stop) {
      if (arg1 == t + start + i + sizeof(optype) + sizeof(argtype) // relative address
          && !callback(start + i))
        return false;
      //i += sizeof(optype) + sizeof(argtype) - 1; // == 4
      //}
    }
  return true;
}

bool iterCallerAddress(const address2_fun_t &callback, DWORD funcAddr, DWORD sig, DWORD lowerBound, DWORD upperBound, DWORD reverseLength, DWORD offset)
{
  enum { PatternSize = 4 };
  const DWORD size = upperBound - lowerBound - PatternSize;
  const DWORD fun = (DWORD)funcAddr;
  // Example function call:
  // 00449063  |. ff15 5cf05300  call dword ptr ds:[<&gdi32.getglyphoutli>; \GetGlyphOutlineA
  //WCHAR str[0x40];
  const DWORD mask = sigMask(sig);
  for (DWORD i = offset; i < size; i++)
    if (*(WORD *)(lowerBound + i) == word_call) {
      DWORD t = *(DWORD *)(lowerBound + i + 2); // 2 = sizeof(word)
      if (t >= lowerBound && t <= upperBound - PatternSize) {
        if (*(DWORD *)t == fun)
          //swprintf(str,L"CALL addr: 0x%.8X",lowerBound + i);
          //OutputConsole(str);
          for (DWORD j = i ; j > i - reverseLength; j--)
            if ((*(DWORD *)(lowerBound + j) & mask) == sig) {
              if (!callback(lowerBound + j, lowerBound + i))
                return false;
              break;
            }

      } else
        i += 6;
    }
  //OutputConsole(L"Find call and entry failed.");
  return true;
}

bool iterCallerAddressAfterInt3(const address2_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  auto callback = [&fun](dword_t addr, dword_t call) -> bool {
    while (byte_int3 == *(BYTE *)++addr); // skip leading int3
    return fun(addr, call);
  };
  return iterCallerAddress(callback, funcAddr, word_2int3, lowerBound, upperBound, callerSearchSize, offset);
}

bool iterUniqueCallerAddress(const address_fun_t &fun, dword_t funcAddr, dword_t funcInst, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  dword_t prevAddr = 0;
  auto callback = [&fun, &prevAddr](dword_t addr, dword_t) -> bool {
    if (prevAddr == addr)
      return true;
    prevAddr = addr;
    return fun(addr);
  };
  return iterCallerAddress(callback, funcAddr, funcInst, lowerBound, upperBound, callerSearchSize, offset);
}

bool iterUniqueCallerAddressAfterInt3(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  auto callback = [&fun](dword_t addr) -> bool {
    while (byte_int3 == *(BYTE *)++addr); // skip leading int3
    return fun(addr);
  };
  return iterUniqueCallerAddress(callback, funcAddr, word_2int3, lowerBound, upperBound, callerSearchSize, offset);
}

bool iterLongJumpAddress(const address_fun_t &fun, DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return iterWordCall(fun, word_jmp, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

bool iterShortJumpAddress(const address_fun_t &fun, DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return iterByteCall(fun, byte_jmp, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

bool iterFarCallAddress(const address_fun_t &fun, DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return iterWordCall(fun, word_call, funcAddr, lowerBound, upperBound, offset, range ? range : (upperBound - lowerBound - offset)); }

bool iterNearCallAddress(const address_fun_t &fun, DWORD funcAddr, DWORD lowerBound, DWORD upperBound, DWORD offset, DWORD range)
{ return iterByteCall(fun, byte_call, funcAddr, lowerBound, offset, range ? range : (upperBound - lowerBound - offset)); }

bool iterAlignedNearCallerAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  dword_t prevAddr = 0;
  auto callback = [&fun, &prevAddr, callerSearchSize](dword_t addr) -> bool {
    if ((addr = findEnclosingAlignedFunction(addr, callerSearchSize))
        && prevAddr != addr) {
      prevAddr = addr;
      return fun(addr);
    }
    return true;
  };
  return iterNearCallAddress(callback, funcAddr, lowerBound, upperBound, offset);
}

#endif // MEMDBG_NO_STL

DWORD findMultiCallerAddress(DWORD funcAddr, const DWORD sigs[], DWORD sigCount, DWORD lowerBound, DWORD upperBound, DWORD reverseLength, DWORD offset)
{
  enum { PatternSize = 4 };
  const DWORD size = upperBound - lowerBound - PatternSize;
  const DWORD fun = (DWORD)funcAddr;
  // Example function call:
  // 00449063  |. ff15 5cf05300  call dword ptr ds:[<&gdi32.getglyphoutli>; \GetGlyphOutlineA
  //WCHAR str[0x40];

  enum { MaxSigCount = 0x10 }; // mast be larger than maximum sigCount
  DWORD masks[MaxSigCount];
  for (DWORD k = 0; k < sigCount; k++)
    masks[k] = sigMask(sigs[k]);

  for (DWORD i = offset; i < size; i++)
    if (*(WORD *)(lowerBound + i) == word_call) {
      DWORD t = *(DWORD *)(lowerBound + i + 2); // 2 = sizeof(word)
      if (t >= lowerBound && t <= upperBound - PatternSize) {
        if (*(DWORD *)t == fun)
          //swprintf(str,L"CALL addr: 0x%.8X",lowerBound + i);
          //OutputConsole(str);
          for (DWORD j = i ; j > i - reverseLength; j--) {
            DWORD ret = lowerBound + j,
                  inst = *(DWORD *)ret;
            for (DWORD k = 0; k < sigCount; k++)
              if ((inst & masks[k]) == sigs[k]) // Fun entry 1.
                //swprintf(str,L"Entry: 0x%.8X",lowerBound + j);
                //OutputConsole(str);
                return ret;
          }

      } else
        i += 6;
    }
  //OutputConsole(L"Find call and entry failed.");
  return 0;
}

DWORD findLastCallerAddress(DWORD funcAddr, DWORD sig, DWORD lowerBound, DWORD upperBound, DWORD reverseLength, DWORD offset)
{
  enum { PatternSize = 4 };
  const DWORD size = upperBound - lowerBound - PatternSize;
  const DWORD fun = (DWORD)funcAddr;
  //WCHAR str[0x40];
  DWORD ret = 0;
  const DWORD mask = sigMask(sig);
  for (DWORD i = offset; i < size; i++)
    if (*(WORD *)(lowerBound + i) == word_call) {
      DWORD t = *(DWORD *)(lowerBound + i + 2);
      if (t >= lowerBound && t <= upperBound - PatternSize) {
        if (*(DWORD *)t == fun)
          //swprintf(str,L"CALL addr: 0x%.8X",lowerBound + i);
          //OutputConsole(str);
          for (DWORD j = i ; j > i - reverseLength; j--)
            if ((*(DWORD *)(lowerBound + j) & mask) == sig) { // Fun entry 1.
              //swprintf(str,L"Entry: 0x%.8X",lowerBound + j);
              //OutputConsole(str);
              ret = lowerBound + j;
              break;
            }

      } else
        i += 6;
    }
  //OutputConsole(L"Find call and entry failed.");
  return ret;
}

DWORD findCallerAddressAfterInt3(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  DWORD addr = findCallerAddress(funcAddr, word_2int3, lowerBound, upperBound, callerSearchSize, offset);
  if (addr)
    while (byte_int3 == *(BYTE *)++addr);
  return addr;
}

DWORD findLastCallerAddressAfterInt3(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  DWORD addr = findLastCallerAddress(funcAddr, word_2int3, lowerBound, upperBound, callerSearchSize, offset);
  if (addr)
    while (byte_int3 == *(BYTE *)++addr);
  return addr;
}

DWORD findAlignedNearCallerAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  if (DWORD addr = findNearCallAddress(funcAddr, lowerBound, upperBound, offset))
    return findEnclosingAlignedFunction(addr, callerSearchSize);
  return 0;
}

DWORD findLastAlignedNearCallerAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize, dword_t offset)
{
  if (DWORD addr = findLastCallerAddressAfterInt3(funcAddr, lowerBound, upperBound, callerSearchSize, offset))
    return findEnclosingAlignedFunction(addr, callerSearchSize);
  return 0;
}

DWORD findEnclosingAlignedFunction(DWORD start, DWORD back_range)
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

DWORD findEnclosingFunctionAfterDword(DWORD sig, DWORD start, DWORD back_range, DWORD step)
{
  start &= ~0xf;
  for (DWORD i = start, j = start - back_range; i > j; i-=step) { // 0x10 is aligned
    DWORD k = *(DWORD *)(i-4); // 4 = sizeof(DWORD)
    if (k == sig)
      return i;
  }
  return 0;
}

DWORD findEnclosingFunctionBeforeDword(DWORD sig, DWORD start, DWORD back_range,DWORD step)
{
  DWORD addr = findEnclosingFunctionAfterDword(sig, start, back_range, step);
  if (addr)
    addr -= sizeof(DWORD);
  return addr;
}

DWORD findEnclosingFunctionAfterInt3(DWORD start, DWORD back_range, DWORD step)
{ return findEnclosingFunctionAfterDword(0xcccccccc, start, back_range, step); }

DWORD findEnclosingFunctionAfterNop(DWORD start, DWORD back_range, DWORD step)
{ return findEnclosingFunctionAfterDword(0x90909090,start, back_range, step); }

DWORD findBytes(const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound)
{
  DWORD reladdr = SearchPattern(lowerBound, upperBound - lowerBound, pattern, patternSize);
  return reladdr ? lowerBound + reladdr : 0;
}

//DWORD reverseFindBytes(const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound)
//{
//  DWORD reladdr = reverseSearchPattern(lowerBound, upperBound - lowerBound, pattern, patternSize);
//  return reladdr ? lowerBound + reladdr : 0;
//}

#if 0 // not used
DWORD findBytesInPages(const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound, SearchType search)
{
  //enum { MinPageSize = 4 * 1024 }; // 4k
  DWORD ret = 0;
  DWORD start = lowerBound,
        stop = start;
  MEMORY_BASIC_INFORMATION mbi = {};

  //lowerBound = 0x10000000;
  //upperBound = 0x14000000;
  //SIZE_T ok = ::VirtualQuery((LPCVOID)lowerBound, &mbi, sizeof(mbi));
  //ITH_GROWL_DWORD7(1, start, stop, mbi.RegionSize, mbi.Protect, mbi.Type, mbi.State);
  //return findBytes(pattern, patternSize, lowerBound, upperBound, wildcard);
  while (stop < upperBound) {
    SIZE_T ok = ::VirtualQuery((LPCVOID)start, &mbi, sizeof(mbi));
    if (!mbi.RegionSize)
      break;
    // Only visit readable and committed region
    // Protect could be zero if not allowed to query
    if (!ok || !mbi.Protect || mbi.Protect&PAGE_NOACCESS) {
      if (stop > start && (ret = findBytes(pattern, patternSize, lowerBound, upperBound)))
        return ret;
      if (search != SearchAll)
        return 0;
      stop += mbi.RegionSize;
      start = stop;
    } else
      stop += mbi.RegionSize;
  }
  if (stop > start)
    ret = findBytes(pattern, patternSize, start, min(upperBound, stop));
  return ret;
}

DWORD matchBytesInPages(const void *pattern, DWORD patternSize, DWORD lowerBound, DWORD upperBound, BYTE wildcard, SearchType search)
{
  //enum { MinPageSize = 4 * 1024 }; // 4k
  DWORD ret = 0;
  DWORD start = lowerBound,
        stop = start;
  MEMORY_BASIC_INFORMATION mbi = {};

  //lowerBound = 0x10000000;
  //upperBound = 0x14000000;
  //SIZE_T ok = ::VirtualQuery((LPCVOID)lowerBound, &mbi, sizeof(mbi));
  //ITH_GROWL_DWORD7(1, start, stop, mbi.RegionSize, mbi.Protect, mbi.Type, mbi.State);
  //return findBytes(pattern, patternSize, lowerBound, upperBound, wildcard);
  while (stop < upperBound) {
    SIZE_T ok = ::VirtualQuery((LPCVOID)start, &mbi, sizeof(mbi));
    if (!mbi.RegionSize)
      break;
    // Only visit readable and committed region
    // Protect could be zero if not allowed to query
    if (!ok || !mbi.Protect || mbi.Protect&PAGE_NOACCESS) {
      if (stop > start && (ret = findBytes(pattern, patternSize, lowerBound, upperBound, wildcard)))
        return ret;
      if (search != SearchAll)
        return 0;
      stop += mbi.RegionSize;
      start = stop;
    } else
      stop += mbi.RegionSize;
  }
  if (stop > start)
    ret = findBytes(pattern, patternSize, start, min(upperBound, stop), wildcard);
  return ret;
}

#endif // 0

MEMDBG_END_NAMESPACE

// EOF
