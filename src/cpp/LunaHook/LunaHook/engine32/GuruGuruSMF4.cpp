#include "GuruGuruSMF4.h"

bool GuruGuruSMF4::attach_function()
{

  PcHooks::hookGDIFunctions();
  // 奈落の森の花
  trigger_fun = [](LPVOID addr1, hook_context *context)
  {
    if (addr1 != GetGlyphOutlineW)
      return false;
    auto addr = MemDbg::findEnclosingAlignedFunction((DWORD)context->retaddr, 0x500);
    ConsoleOutput("%p", addr);
    if (!addr)
      return true;
    auto xrefs = findxref_reverse_checkcallop(addr, max(processStartAddress, addr - 0x100000), min(processStopAddress, addr + 0x100000), 0xe8);
    if (xrefs.size() != 1)
      return true;
    addr = xrefs[0];
    ConsoleOutput("%p", addr);
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    ConsoleOutput("%p", addr);
    if (!addr)
      return true;
    auto xrefs2 = findxref_reverse_checkcallop(addr, max(processStartAddress, addr - 0x100000), min(processStopAddress, addr + 0x100000), 0xe8);
    if (xrefs2.size() != 2)
      return true;
    addr = xrefs2[1];
    ConsoleOutput("%p", addr);
    addr = findfuncstart(addr, 0x300); // MemDbg::findEnclosingAlignedFunction(addr,0x500);
    ConsoleOutput("%p", addr);
    if (!addr)
      return true;
    HookParam hp;
    hp.address = (DWORD)addr;
    hp.offset = stackoffset(2);
    hp.type = CODEC_UTF16 | USING_STRING;

    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      auto ws = buffer->strW();

      static std::set<std::wstring> dedump;
      if (![&]()
          {
            if (endWith(ws, L"FPS"))
              return false;
            if (startWith(ws, L"ver"))
              return false;
            if (startWith(ws, L"VER"))
              return false;
            if (dedump.count(ws))
              return false;
            dedump.insert(ws);
            return true;
          }())
        buffer->clear();
    };
    NewHook(hp, "GuruGuruSMF4");
    return true;
  };

  return false;
}