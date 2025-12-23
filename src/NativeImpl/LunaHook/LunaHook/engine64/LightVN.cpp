#include "LightVN.h"
namespace
{
  bool _1()
  {
    // void __fastcall sub_1404B7960(void **Src)
    // HQ-1C*0@4B7960:LightApp.exe
    const BYTE BYTES[] = {
        0x90,
        XX4,
        XX4,
        0x48, 0x8b, 0xce,
        0xe8, XX4,
        0x90,
        0x48, 0x8b, XX2,
        0x48, 0x83, 0xfa, 0x08,
        0x72, 0x36,
        0x48, 0x8D, 0x14, 0x55, 0x02, 0x00, 0x00, 0x00,
        0x48, 0x8b, XX2,
        0x48, 0x8b, 0xc1,
        0x48, 0x81, 0xFA, 0x00, 0x10, 0x00, 0x00,
        0x72, 0x19,
        0x48, 0x83, 0xC2, 0x27,
        0x48, 0x8b, XX2,
        0x48, 0x2b, 0xc1,
        0x48, 0x83, 0xC0, 0xF8,
        0x48, 0x83, 0xF8, 0x1F,
        0x0f, 0x87, XX4,
        0xe8, XX4

    };
    auto suc = false;
    auto addrs = Util::SearchMemory(BYTES, sizeof(BYTES), PAGE_EXECUTE, processStartAddress, processStopAddress);
    for (auto addr : addrs)
    {
      ConsoleOutput("LightVN %p", addr);
      const BYTE aligned[] = {0xCC, 0xCC, 0xCC, 0xCC};
      addr = reverseFindBytes(aligned, sizeof(aligned), addr - 0x100, addr);
      if (!addr)
        continue;
      addr += 4;
      ConsoleOutput("LightVN %p", addr);
      HookParam hp;
      hp.address = addr;
      hp.type = CODEC_UTF16 | USING_STRING | DATA_INDIRECT;
      hp.index = 0;
      hp.offset = regoffset(rcx);
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        auto s = buffer->viewW();
        if (s.substr(s.size() - 2, 2) == L"\\w")
          buffer->size -= 4;
      };
      suc |= NewHook(hp, "LightVN");
    }
    return suc;
  }
  bool _2()
  {
    // 有太多乱的输出了，而且基本不需要它，所以先放到后面。

    BYTE sig[] = {
        0x48, XX, 0xFE, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F,
        0x48, 0x3B, 0xC3,
        0x76, XX,
        0x48, XX, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x7F};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING;
    hp.offset = stackoffset(6);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // 高架下に広がる[瀟洒]<しょうしゃ>な店内には、あたしたちのような学生の他に、
      auto str = buffer->strW();
      if (all_ascii(str))
        return buffer->clear();
      auto filterpath = {
          L".rpy", L".rpa", L".py", L".pyc", L".txt",
          L".png", L".jpg", L".bmp",
          L".mp3", L".ogg",
          L".webm", L".mp4",
          L".otf", L".ttf", L"Data/"};
      for (auto _ : filterpath)
        if (str.find(_) != str.npos)
          return buffer->clear();
      str = re::sub(str, L"\\[(.*?)\\]<(.*?)>", L"$1");
      buffer->from(str);
    };
    return NewHook(hp, "LightVN2");
  }
}
namespace
{
  void commonfilter(TextBuffer *buffer, HookParam *)
  {
    auto str = buffer->strW();
    str = re::sub(str, L"-{2,}");
    str = re::sub(str, L"\\[(.*?)\\]<(.*?)>", L"$1");
    strReplace(str, L"\n");
    strReplace(str, L"\\n");
    buffer->from(str);
  }
  bool lightvnparsestring()
  {
    BYTE sig[] = {
        0x4c, 0x8b, 0x47, 0x10,
        0x48, 0x83, 0x7f, 0x18, 0x08,
        0x72, 0x03,
        0x48, 0x8b, 0x3f,
        0x48, 0x8b, 0xd7,
        0x48, 0x8b, 0xcb,
        0xe8};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (!addr)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    // 包含太多短句，所以无法内嵌
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto tu = (TextUnionW *)context->rdx;
      auto str = tu->view();
      if (startWith(str, L"\\n") && endWith(str, L"\\n"))
      {
        *split = 1;
      }
      buffer->from(str);
    };
    hp.filter_fun = commonfilter;
    hp.lineSeparator = L"\\n";
    return NewHook(hp, "Light.VN.16");
  }

  bool xreflightvnparsestring()
  {
    // ver16 是上面的xref
    // ver12 找不到上面的函数
    auto checkstrings = {
        L"backlog voice already exists at line: {}",
        L"attempting to log to backlog when backlog showing"}; //. likely you faded it out."};
    auto succ = false;
    for (auto str : checkstrings)
    {
      auto straddr = MemDbg::findBytes(str, wcslen(str) * 2, processStartAddress, processStopAddress);
      if (!straddr)
        continue;
      // 140CADC30
      // 48 8D 0D C5 94 AB 00
      // 1401F4764
      BYTE lea[] = {0x48, 0x8d, XX};
      for (auto leaaddr : Util::SearchMemory(lea, sizeof(lea), PAGE_EXECUTE, processStartAddress, processStopAddress))
      {
        auto refaddr = (*(DWORD *)(leaaddr + 3)) + leaaddr + 7;
        if (refaddr != straddr)
          continue;
        BYTE sig[] = {0x55, 0x41, XX, 0x41, XX, 0x41, XX, 0x41, XX}; // カタネガイ -Trial Edition-
        auto funcaddr = MemDbg::findEnclosingAlignedFunction_strict(leaaddr, 0x2000);
        if (!funcaddr)
          continue;
        auto funcaddr2 = reverseFindBytes(sig, sizeof(sig), leaaddr - 0x2000, leaaddr, 0, true);
        if (funcaddr2 > funcaddr)
          funcaddr = funcaddr2;
        HookParam hp;
        hp.address = funcaddr;
        hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
          // wstring=TextUnionW for msvc c++17
          auto tu = (TextUnionW *)context->rdx;
          buffer->from(tu->view());
        };
        hp.filter_fun = commonfilter;
        succ |= NewHook(hp, "Light.VN.12");
      }
    }
    return succ;
  }
}
bool LightVN::attach_function()
{
  bool ok = _1();
  ok |= lightvnparsestring();
  ok |= xreflightvnparsestring();
  return ok || _2();
}