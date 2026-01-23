#include "PONScripter.h"

bool InsertPONScripterHook()
{
  if (DWORD str = MemDbg::findBytes("CBString::Failure in (CBString", 30, processStartAddress, processStopAddress))
  {
    if (DWORD calledAt = MemDbg::findBytes(&str, sizeof(str), processStartAddress, processStopAddress))
    {
      DWORD funcs[] = {0xec8b55, 0xe58955};
      DWORD addr = MemDbg::findBytes(funcs, 3, calledAt - 0x100, calledAt);
      if (!addr)
        addr = MemDbg::findBytes(funcs + 1, 3, calledAt - 0x100, calledAt);
      if (addr)
      {
        HookParam hp;
        hp.address = addr;
        hp.type = USING_STRING | CODEC_UTF8 | DATA_INDIRECT;
        hp.offset = stackoffset(1);
        hp.index = 0xc;
        return NewHook(hp, "PONScripter");
      }
    }
  }
  return false;
}
void PONScripterFilter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->data);
  static std::string prevText;

  for (int i = 0; i < buffer->size; i++)
  {
    if (text[i] == '^' || text[i] == '@' || text[i] == '\\' || text[i] == '\n')
    {
      text[i] = '\0';
      buffer->size = i;
      break;
    }
  }

  if (!prevText.compare(text))
    return buffer->clear();
  prevText = text;

  StringFilter(buffer, "#", 7); // remove # followed by 6 chars
}

bool InsertPONScripterEngHook()
{

  /*
   * Sample games:
   * https://vndb.org/v24770
   */
  const BYTE bytes[] = {
      0x89, 0xD0,       // mov eax,edx
      0x8D, 0x75, 0xD8, // lea esi,[ebp-28]
      0x89, 0x55, 0xB4, // mov [ebp-4C],edx
      0x83, 0xC0, 0x01, // add eax,01
      0x89, 0x45, 0xC0  // mov [ebp-40],eax    << hook here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 3
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING | CODEC_UTF8;
  hp.filter_fun = PONScripterFilter;
  return NewHook(hp, "PONScripterEng");
}

bool InsertPONScripterJapHook()
{

  /*
   * Sample games:
   * https://vndb.org/v24770
   */
  const BYTE bytes[] = {
      0x8D, 0x87, XX4,        // lea eax,[edi+00000198]               << hook here
      0x8B, 0x0D, XX4,        // mov ecx,[ciconia_phase1.exe+3D82C0]
      0x89, 0x55, 0xB4,       // mov [ebp-4C],edx
      0xC6, 0x45, 0xAE, 0x00, // mov byte ptr [ebp-52],00
      0x89, 0x45, 0xA4,       // mov [ebp-5C],eax
      0x8B, 0x01,             // mov eax,[ecx]
      0x8B, 0x75, 0xB4        // mov esi,[ebp-4C]
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = USING_STRING | CODEC_UTF8;
  hp.filter_fun = PONScripterFilter;
  return NewHook(hp, "PONScripterJap");
}
namespace
{
  bool pons()
  {
    /*
int __thiscall sub_46A3C0(int *this, void *a2, int a3)
{
  int result; // eax
  int v4; // esi
  int v5; // [esp+12h] [ebp-26h] BYREF
  int v6; // [esp+14h] [ebp-24h] BYREF
  char v7[32]; // [esp+18h] [ebp-20h] BYREF

  result = sub_460780(this + 1, a2, a3); <--findbytes+xref
  if ( result == -1 )
  {
    sub_684AC0("CBString::Failure in concatenate", (int)&v5);
    sub_65EF20(&v6);
    sub_683500((char *)&v5 + 1);
    v4 = sub_6B17C0(8);
    sub_65EEE0(v7);
    sub_6B1F70(v4, &ZTIN7Bstrlib17CBStringExceptionE, sub_65EFD0);
  }
  return result;
}
    */
    const BYTE bytes[] = {
        0x55, 0x57, 0x56, 0x53,
        0x83, 0xec, XX,
        0x8b, 0x5c, 0x24, XX,
        0x8b, 0x7c, 0x24, XX,
        0x8b, 0x74, 0x24, XX,
        0x85, 0xdb,
        0x0f, 0x84, XX4,
        0x8b, 0x43, 0x08,
        0x85, 0xc0,
        0x89, 0x44, 0x24, 0x0c,
        0x0f, 0x84, XX4,
        0x8b, 0x43, 0x04,
        0x85, 0xc0,
        0x78, XX,
        0x8b, 0x13,
        0x39, 0xd0,
        0x7f, XX,
        0x85, 0xd2,
        0x7e, XX,
        0x85, 0xff,
        0x8d, 0x76, 0x00,
        0x74, XX,
        0x89, 0xf5,
        0xc1, 0xed, 0x1f};
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    auto addrs = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (1 != addrs.size())
      return false;
    for (addr = addrs[0]; (addrs[0] - addr < 0x30) && ((*(BYTE *)addr) != 0x55); addr -= 1)
      ;
    if (*(BYTE *)addr != 0x55)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_CHAR | CODEC_UTF8 | DATA_INDIRECT;
    return NewHook(hp, "PONScripter2");
  }
}
bool PONScripter::attach_function()
{

  bool ok = InsertPONScripterEngHook() && InsertPONScripterJapHook();
  return ok || (pons() || InsertPONScripterHook()); // If a language hook is missing, the original code is executed
}