#include "CodeX.h"

void CodeXFilter(TextBuffer *buffer, HookParam *)
{
  std::string result = buffer->strA();
  strReplace(result, "^n", "\n");
  if (startWith(result, "\n"))
    result = result.substr(1);

  //|晒[さら]
  result = std::regex_replace(result, std::regex("\\|(.+?)\\[(.+?)\\]"), "$1");
  buffer->from(result);
}

bool InsertCodeXHook()
{

  /*
   * Sample games:
   * https://vndb.org/v41664
   * https://vndb.org/v36122
   */
  const BYTE bytes[] = {
      0x83, 0xC4, 0x08, // add esp,08                  << hook here
      0x8D, 0x85, XX4,  // lea eax,[ebp-00000218]
      0x50,             // push eax
      0x68, XX4,        // push ???????????!.exe+10A76C
      0x85, 0xF6,       // test esi,esi
      0x74, 0x4F,       // je ???????????!.exe+2A95B
      0xFF, 0x15, XX4,  // call dword ptr [???????????!.exe+C8140]
      0x8B, 0x85, XX4   // mov eax,[ebp-00000220]      << alternative hook here
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("CodeX: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = get_reg(regs::eax);
  hp.index = 0;
  hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_OVERWRITE | NO_CONTEXT; // 无法解决中文乱码
  hp.embed_hook_font = F_GetGlyphOutlineA;
  hp.filter_fun = CodeXFilter;
  ConsoleOutput("INSERT CodeX");

  return NewHook(hp, "CodeX");
}
namespace
{
  bool hook()
  {
    // 霞外籠逗留記
    BYTE _[] = {0x90, 0x90, 0x68, 0x64, 0x7B, 0x4C, 0x00}; // aHdL db 'hd{L',0
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (addr == 0)
      return false;
    addr += 2;
    BYTE bytes[] = {0x68, XX4};
    memcpy(bytes + 1, &addr, 4);
    auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
    bool succ = false;
    for (auto adr : addrs)
    {
      adr = MemDbg::findEnclosingAlignedFunction(adr);
      if (adr == 0)
        continue;
      HookParam hp;
      hp.address = adr;
      hp.offset = get_stack(1);
      hp.type = CODEC_ANSI_BE;
      succ |= NewHook(hp, "CodeX");
    }
    return succ;
  }
}
namespace
{
  // https://vndb.org/v598
  // ANGEL BULLET
  bool hook2()
  {
    BYTE _[] = {
        0x8b, 0x44, 0x24, 0x04,
        0x81, 0xec, XX4,
        0x25, 0xff, 0xff, 0, 0,
        0x8d, 0x54, 0x24, 0,
        0x56,
        0x8b, 0xf1,
        0x50,
        0x8d, 0x4e, XX,
        0x51,
        0x68, XX4, //%s%03d
        0x52,
        0xff, 0x15, XX4, // wprintfA
    };
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_reg(regs::edx);
    hp.type = USING_STRING;
    hp.filter_fun = CodeXFilter;
    return NewHook(hp, "CodeX");
  }
}
namespace
{
  bool hook3()
  {
    BYTE _[] = {
        // if ( *(_WORD *)v38 == 8511 || (_WORD)v5 == 16161 || (_WORD)v5 == 8481 )
        0xB9, 0x3F, 0x21, 0x00, 0x00, // mov     ecx, 213Fh
        0x0F, 0xB7, 0x02,             // movzx   eax, word ptr [edx]
        0x66, 0x3B, 0xC1,             // cmp     ax, cx
        0x0F, 0x84, XX4,              // jz      loc_458294
        0xb9, 0x21, 0x3f, 0x00, 0x00, // mov     ecx, 3F21h
        0x66, 0x3B, 0xC1,
        0x0F, 0x84, XX4,
        0xb9, 0x21, 0x21, 0x00, 0x00, // mov     ecx, 2121h
        0x66, 0x3B, 0xC1,
        0x0F, 0x84, XX4};
    ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
    if (addr == 0)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_stack(1);
    hp.split = get_stack(2);
    hp.type = USING_STRING | FULL_STRING | NO_CONTEXT | USING_SPLIT | EMBED_ABLE | EMBED_AFTER_OVERWRITE;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.filter_fun = CodeXFilter;
    return NewHook(hp, "CodeX2");
  }
}
bool CodeX::attach_function()
{
  PcHooks::hookGDIFunctions(GetGlyphOutlineA); // 对于部分游戏，文本分两段显示，会吞掉后半段。故此用这个兜底
  return (hook3() | InsertCodeXHook()) || hook() || hook2();
}