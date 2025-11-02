#include "GASTRO.h"
namespace
{
  void filter(TextBuffer *buffer, HookParam *hp)
  {
    std::string s = buffer->strA();
    s = re::sub(s, "#(.*?)#");
    strReplace(s, "\\c");
    buffer->from(s);
  }
}
bool GASTRO_attach_function1()
{
  // https://vndb.org/v4052
  BYTE bytes[] = {
      // char *__cdecl strncpy(char *Destination, const char *Source, size_t Count)
      0x8B, 0x4C, 0x24, 0x0C,
      0x57,
      0x85, 0xC9,
      0x74, XX,
      0x56,
      0x53,
      0x8B, 0xD9, 0x8B,
      0x74, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING;
  hp.filter_fun = filter;
  return NewHook(hp, "GASTRO");
}
bool GASTRO_attach_function2()
{
  // https://vndb.org/v15103
  BYTE bytes[] = {
      /*
    _WORD *__cdecl sub_40EC00(unsigned __int8 *a1, _WORD *a2, _WORD *a3, _WORD *a4)
  {
    unsigned __int8 v4; // al
    _WORD *result; // eax

    v4 = *a1;
    if ( (*a1 < 0x81u || v4 > 0x9Fu) && (v4 < 0xE0u || v4 > 0xFCu) )
      */
      0x8b, 0x54, 0x24, 0x04,
      0x8a, 0x02,
      0x3c, 0x81,
      0x72, XX,
      0x3c, 0x9f,
      0x76, XX,
      0x3c, 0xe0,
      0x72, XX,
      0x3c, 0xfc};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  auto addrs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
  if ((addrs.size() != 3) || ((addrs[0] = MemDbg::findEnclosingAlignedFunction(addrs[0])) == 0))
    return false;
  HookParam hp;
  hp.address = addrs[0];
  hp.offset = stackoffset(2);
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
  hp.filter_fun = filter;
  return NewHook(hp, "GASTRO");
}
bool GASTRO::attach_function()
{
  return GASTRO_attach_function2() || GASTRO_attach_function1();
}