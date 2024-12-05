#ifndef __LUNA_PSPUILTS_H
#define __LUNA_PSPUILTS_H
namespace ppsspp
{

  struct emfuncinfo
  {
    uint64_t type;
    int offset;
    int padding;
    decltype(HookParam::text_fun)  hookfunc;
    decltype(HookParam::filter_fun) filterfun;
    const char *_id;
  };

}

bool InsertPPSSPPcommonhooks();

#ifndef _WIN64
namespace
{
  int PPSSPP_VERSION[4] = {0, 9, 8, 0}; // 0.9.8 by default

  enum : DWORD
  {
    PPSSPP_MEMORY_SEARCH_STEP_98 = 0x01000000,
    PPSSPP_MEMORY_SEARCH_STEP_99 = 0x00050000
    //, step = 0x1000 // step  must be at least 0x1000 (offset in SearchPattern)
    //, step = 0x00010000 // crash otoboku PSP on 0.9.9 since 5pb is wrongly inserted
  };

  ULONG SafeMatchBytesInPSPMemory(LPCVOID pattern, DWORD patternSize, DWORD start = MemDbg::MappedMemoryStartAddress, DWORD stop = MemDbg::MemoryStopAddress)
  {

    ULONG step = PPSSPP_VERSION[1] == 9 && PPSSPP_VERSION[2] == 8 ? PPSSPP_MEMORY_SEARCH_STEP_98 : PPSSPP_MEMORY_SEARCH_STEP_99;
    return _SafeMatchBytesInMappedMemory(pattern, patternSize, XX, start, stop, step);
  }

  ULONG SafeMatchBytesInPS2Memory(LPCVOID pattern, DWORD patternSize)
  {
    // PCSX2 memory range
    // ds: begin from 0x20000000
    // cs: begin from 0x30000000
    enum : ULONG
    {
      // start = MemDbg::MappedMemoryStartAddress // 0x01000000
      start = 0x30000000 // larger than PSP to skip the garbage memory
      ,
      stop = 0x40000000 // larger than PSP as PS2 has larger memory
      ,
      step = 0x00010000 // smaller than PPS
      //, step = 0x00050000 // the same as PPS
      //, step = 0x1000 // step  must be at least 0x1000 (offset in SearchPattern)
    };
    return _SafeMatchBytesInMappedMemory(pattern, patternSize, XX, start, stop, step);
  }
}
#endif

#endif