#include "GASTRO.h"
bool GASTRO::attach_function()
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
  if (addr == 0)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = get_stack(2);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    std::string s = buffer->strA();
    s = std::regex_replace(s, std::regex("#(.*?)#"), "");
    strReplace(s, "\\c", "");
    strReplace(s, "\\n", "");
    buffer->from(s);
  };
  return NewHook(hp, "GASTRO");
}