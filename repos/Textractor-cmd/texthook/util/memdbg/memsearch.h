#ifndef _MEMDBG_MEMSEARCH_H
#define _MEMDBG_MEMSEARCH_H

// memsearch.h
// 4/20/2014 jichi

#include "memdbg/memdbg.h"
#ifndef MEMDBG_NO_STL
# include <functional>
#endif // MEMDBG_NO_STL

MEMDBG_BEGIN_NAMESPACE

/// Estimated maximum size of the caller function, the same as ITH FindCallAndEntryAbs
enum { MaximumFunctionSize = 0x800 };

/// Offset added to the beginning of the searched address
enum { MemoryPaddingOffset = 0x1000 };

enum { MemoryAlignedStep = 0x10 };

#ifndef MEMDBG_NO_STL
///  Iterate address and return false if abort iteration.
typedef std::function<bool (dword_t)> address_fun_t;
typedef std::function<bool (dword_t, dword_t)> address2_fun_t;

/**
 *  Iterate all call and caller addresses
 *  @param  fun  the first parameter is the address of the caller, and the second parameter is the address of the call itself
 *  @return  false if return early, and true if iterate all elements
 */
bool iterCallerAddress(const address2_fun_t &fun, dword_t funcAddr, dword_t funcInst, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
bool iterCallerAddressAfterInt3(const address2_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
bool iterUniqueCallerAddress(const address_fun_t &fun, dword_t funcAddr, dword_t funcInst, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
bool iterUniqueCallerAddressAfterInt3(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);

/**
 *  Iterate all call and caller addresses
 *  @param  fun  the parameter is the address of the call
 *  @return  false if return early, and true if iterate all elements
 */
bool iterFarCallAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
bool iterNearCallAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
bool iterLongJumpAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
bool iterShortJumpAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);

bool iterAlignedNearCallerAddress(const address_fun_t &fun, dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);

bool iterFindBytes(const address_fun_t &fun, const void *pattern, dword_t patternSize, dword_t lowerBound, dword_t upperBound);
bool iterMatchBytes(const address_fun_t &fun, const void *pattern, dword_t patternSize, dword_t lowerBound, dword_t upperBound);
#endif // MEMDBG_NO_STL

/**
 *  Return the absolute address of the far caller function
 *  The same as ITH FindCallAndEntryAbs().
 *
 *  @param  funcAddr  callee function address
 *  @param  funcInst  the machine code where the caller function starts
 *  @param  lowerBound  the lower memory address to search
 *  @param  upperBound  the upper memory address to search
 *  @param* callerSearchSize  the maximum size of caller
 *  @return  the caller absolute address if succeed or 0 if fail
 *
 *  Example funcInst:
 *  0x55: push ebp
 *  0x81,0xec: sub esp XXOO (0xec81)
 *  0x83,0xec: sub esp XXOO (0xec83)
 */
dword_t findCallerAddress(dword_t funcAddr, dword_t funcInst, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
dword_t findCallerAddressAfterInt3(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
dword_t findLastCallerAddress(dword_t funcAddr, dword_t funcInst, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
dword_t findLastCallerAddressAfterInt3(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);

dword_t findMultiCallerAddress(dword_t funcAddr, const dword_t funcInsts[], dword_t funcInstCount, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);

dword_t findAlignedNearCallerAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);
dword_t findLastAlignedNearCallerAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t callerSearchSize = MaximumFunctionSize, dword_t offset = MemoryPaddingOffset);

/**
 *  Return the absolute address of the long jump (not short jump) instruction address.
 *  The same as ITH FindCallOrJmpAbs(false).
 *
 *  @param  funcAddr  callee function address
 *  @param  lowerBound  the lower memory address to search
 *  @param  upperBound  the upper memory address to search
 *  @param* offset  the relative address to search from  the lowerBound
 *  @param* range  the relative size to search, use lowerBound - upperBound when zero
 *  @return  the call instruction address if succeed or 0 if fail
 */
dword_t findLongJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
dword_t findShortJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
dword_t findLastLongJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
dword_t findLastShortJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);

/**
 *  Return the absolute address of the far call (inter-module) instruction address.
 *  The same as ITH FindCallOrJmpAbs(true).
 *
 *  @param  funcAddr  callee function address
 *  @param  lowerBound  the lower memory address to search
 *  @param  upperBound  the upper memory address to search
 *  @param* offset  the relative address to search from  the lowerBound
 *  @param* range  the relative size to search, use lowerBound - upperBound when zero
 *  @return  the call instruction address if succeed or 0 if fail
 */
dword_t findFarCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
dword_t findLastFarCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);

///  Near call (intra-module)
dword_t findNearCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);
dword_t findLastNearCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0);

///  Default to far call, for backward compatibility
inline dword_t findCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0)
{ return findFarCallAddress(funcAddr, lowerBound, upperBound, offset, range); }
inline dword_t findLastCallAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0)
{ return findLastFarCallAddress(funcAddr, lowerBound, upperBound, offset, range); }

///  Default to long jump, for backward compatibility
inline dword_t findJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0)
{ return findLongJumpAddress(funcAddr, lowerBound, upperBound, offset, range); }
inline dword_t findLastJumpAddress(dword_t funcAddr, dword_t lowerBound, dword_t upperBound, dword_t offset = MemoryPaddingOffset, dword_t range = 0)
{ return findLastLongJumpAddress(funcAddr, lowerBound, upperBound, offset, range); }

///  Push value >= 0xff
dword_t findPushDwordAddress(dword_t value, dword_t lowerBound, dword_t upperBound);

///  Push value <= 0xff
dword_t findPushByteAddress(byte_t value, dword_t lowerBound, dword_t upperBound);

///  Default to push DWORD
inline dword_t findPushAddress(dword_t value, dword_t lowerBound, dword_t upperBound)
{ return findPushDwordAddress(value, lowerBound, upperBound); }

/**
 *  Return the enclosing function address outside the given address.
 *  The same as ITH FindEntryAligned().
 *  "Aligned" here means the function must be after in3 (0xcc) or nop (0x90).
 *
 *  If the function does NOT exist, this function might raise without admin privilege.
 *  It is safer to wrap this function within SEH.
 *
 *  @param  addr  address within th function
 *  @param  searchSize  max backward search size
 *  @return  beginning address of the function
 *  @exception  illegal memory access
 */
dword_t findEnclosingAlignedFunction(dword_t addr, dword_t searchSize = MaximumFunctionSize);
dword_t findEnclosingFunctionBeforeDword(dword_t sig, dword_t addr, dword_t searchSize = MaximumFunctionSize, dword_t step = MemoryAlignedStep);
dword_t findEnclosingFunctionAfterDword(dword_t sig, dword_t addr, dword_t searchSize = MaximumFunctionSize, dword_t step = MemoryAlignedStep);
dword_t findEnclosingFunctionAfterInt3(dword_t addr, dword_t searchSize = MaximumFunctionSize, dword_t step = MemoryAlignedStep);
dword_t findEnclosingFunctionAfterNop(dword_t addr, dword_t searchSize = MaximumFunctionSize, dword_t step = MemoryAlignedStep);

/**
 *  Return the address of the first matched pattern.
 *  Return 0 if failed. The return result is ambiguous if the pattern address is 0.
 *  This function simpily traverse all bytes in memory range and would raise
 *  if no access to the region.
 *
 *  @param  pattern  array of bytes to match
 *  @param  patternSize  size of the pattern array
 *  @param  lowerBound  search start address
 *  @param  upperBound  search stop address
 *  @return  absolute address
 *  @exception  illegal memory access
 */
dword_t findBytes(const void *pattern, dword_t patternSize, dword_t lowerBound, dword_t upperBound);

// User space: 0 - 2G (0 - 0x7ffeffff)
// Kernel space: 2G - 4G  (0x80000000 - 0xffffffff)
//
// http://msdn.microsoft.com/en-us/library/windows/hardware/ff560042%28v=vs.85%29.aspx
// http://codesequoia.wordpress.com/2008/11/28/understand-process-address-space-usage/
// http://stackoverflow.com/questions/17244912/open-process-with-debug-privileges-and-read-write-memory
enum MemoryRange : dword_t {
  UserMemoryStartAddress = 0, UserMemoryStopAddress = 0x7ffeffff
  , KernelMemoryStartAddress = 0x80000000, KernelMemoryStopAddress = 0xffffffff
  , MappedMemoryStartAddress = 0x01000000

  , MemoryStartAddress = UserMemoryStartAddress, MemoryStopAddress = UserMemoryStopAddress
};

#if 0 // not used
/**
 *  Traverse memory continues pages and return the address of the first matched pattern.
 *
 *  @param  pattern  array of bytes to match
 *  @param  patternSize  size of the pattern array
 *  @param  lowerBound  search start address
 *  @param  upperBound  search stop address
 *  @param* search  search all pages (SearchAll) or stop on first illegal access (SearchFirst)
 *  @return  absolute address
 */
enum SearchType : byte_t { SearchAll = 0 , SearchFirst };

dword_t findBytesInPages(const void *pattern, dword_t patternSize,
    dword_t lowerBound = MemoryStartAddress, dword_t upperBound = MemoryStopAddress,
    SearchType search = SearchAll);
dword_t matchBytesInPages(const void *pattern, dword_t patternSize,
    dword_t lowerBound = MemoryStartAddress, dword_t upperBound = MemoryStopAddress,
    byte_t wildcard = WidecardByte, SearchType search = SearchAll);

#endif // 0

MEMDBG_END_NAMESPACE

#endif // _MEMDBG_MEMSEARCH_H
