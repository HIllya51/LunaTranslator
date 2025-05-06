#include "Bishop.h"

bool bishopmbcjmstojis()
{
  // 特別授業
  const BYTE bytes[] = {
      // unsigned int __cdecl _mbcjmstojis(unsigned int C)
      0x55, 0x8b, 0xec,
      0x8b, 0x45, 0x08,                        // mov     eax, [ebp+C]
      0x81, 0x3D, XX4, 0xA4, 0x03, 0x00, 0x00, // cmp     dword_4A1F0C, 3A4h   //if ( dword_4A1F0C == 932 )
      XX2,
      0xa9, 0x00, 0x00, 0xff, 0xff // if ( (C & 0xFFFF0000) != 0 )
  };

  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);

  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_SPLIT | USING_STRING;

  return NewHook(hp, "bishop");
}
bool Bishop::attach_function()
{

  return bishopmbcjmstojis();
}
bool embedbishop()
{
  // 黒の教室
  const BYTE bytes[] = {
      0x53,
      0x8b, 0x5c, 0x24, 0x0c,
      0x56,
      0x8b, 0xf7,
      0xe8, XX4,
      0xd9, 0xee,
      0xdd, 0x9f, XX4,
      0x8b, 0xc3,
      0xdb, 0x44, 0x24, 0x0c,
      0x8d, 0x50, 0x02,
      0xdd, 0x9f, XX4,
      0x66, 0x8b, 0x08,
      0x83, 0xc0, 0x02,
      0x66, 0x85, 0xc9};

  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE;
  hp.embed_hook_font = F_GetGlyphOutlineW;
  static std::wstring flag;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    if (buffer->buff[0] == L'\\')
    {
      flag = buffer->strW().substr(0, 2);
      buffer->size -= 4;
      memmove(buffer->buff, buffer->buff + 4, buffer->size);
    }
    else
    {
      flag.clear();
    }
  };
  hp.embed_fun = [](hook_context *context, TextBuffer buffer)
  {
    context->stack[2] = (DWORD)allocateString(flag + buffer.strW());
  };
  hp.lineSeparator = L"\\n";
  return NewHook(hp, "bishop");
}
bool Bishop2attach_function()
{

  // 三射面談～連鎖する恥辱・調教の学園～
  // 特別授業3SLG
  auto entry = Util::FindImportEntry(processStartAddress, (DWORD)GetGlyphOutlineW);
  if (entry == 0)
    return false;
  bool ok = false;
  for (auto addr : Util::SearchMemory(&entry, 4, PAGE_EXECUTE, processStartAddress, processStopAddress))
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      continue;
    auto xrefs = findxref_reverse_checkcallop(addr, max(processStartAddress, addr - 0x100000), min(processStopAddress, addr + 0x100000), 0xe8);
    for (auto addrx : xrefs)
    {
      // ConsoleOutput("xref %p",addrx);
      const BYTE aligned[] = {0xCC, 0xCC};
      auto addrx1 = reverseFindBytes(aligned, sizeof(aligned), addrx - 0x200, addrx);
      // ConsoleOutput("Aligned %p",addrx1);
      if (!addrx1)
        continue;
      addrx1 += 2;
      BYTE __1[] = {0xDC, 0x0D, XX, XX, XX, 0x00};
      auto _1 = MemDbg::findBytes(__1, 6, addrx - 0x30, addrx);
      // ConsoleOutput("sig %p",_1);
      if (_1 == 0)
        continue;
      BYTE checkthiscall[] = {0x8B, 0xF9}; // mov     edi, ecx
      auto _3 = MemDbg::findBytes(checkthiscall, 2, addrx1, addrx);
      HookParam hp;
      hp.address = addrx1;
      if (_3)
        hp.offset = stackoffset(3);
      else
        hp.offset = stackoffset(4);
      hp.type = CODEC_UTF16;

      ok = NewHook(hp, "Bishop2");
    }
  }
  return ok;
}

bool Bishop2::attach_function()
{
  return Bishop2attach_function() | embedbishop();
}