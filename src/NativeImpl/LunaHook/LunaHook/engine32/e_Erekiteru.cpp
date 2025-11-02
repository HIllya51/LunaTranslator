#include "e_Erekiteru.h"

bool e_Erekiteru::attach_function()
{
  // https://vndb.org/v15578
  // 水素～1/2の奇蹟～
  const uint8_t bytes[] = {
      0x3C, 0x20,
      0x72, 0x04,
      0x3C, 0x7E,
      0x76, 0x15,
      0x3C, 0xA1,
      0x72, 0x04,
      0x3C, 0xDF,
      0x76, 0x0D};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  BYTE bs[] = {0x8B, 0x85, XX4};
  BYTE bs2[] = {0x8A, 0x44, 0x29, XX};
  auto addr1 = MemDbg::findBytes(bs, sizeof(bs), addr, addr + 0x100);
  if (!addr1)
    return false;
  auto addr2 = MemDbg::findBytes(bs2, sizeof(bs2), addr, addr + 0x100);
  if (!addr2)
    return false;
  auto lengthoffset = *(int *)(addr1 + 2);
  auto stroffset = *(BYTE *)(addr2 + 3);
  HookParam hp;
  hp.address = addr;
  hp.user_value = (DWORD) new std::pair<int, int>{lengthoffset, stroffset};
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto _ = reinterpret_cast<std::pair<int, int> *>(hp->user_value);
    auto lengthoffset = _->first;
    auto stroffset = _->second;
    static int lastlength = 0;
    static int lastslen = 0;
    auto thislength = *(DWORD *)(context->ecx + lengthoffset);
    auto slen = strlen((char *)context->ecx + stroffset);
    if ((lastslen != 0) && (lastslen != slen) && (thislength == slen))
      return;
    lastslen = slen;
    if (lastlength == thislength)
      return;
    if (lastlength > thislength)
      lastlength = 0;
    buffer->from((char *)context->ecx + stroffset + lastlength,
                 thislength - lastlength);
    lastlength = thislength;
  };
  hp.filter_fun = NewLineCharToSpaceA;
  hp.type = USING_STRING;
  return NewHook(hp, "e_Erekiteru");
}