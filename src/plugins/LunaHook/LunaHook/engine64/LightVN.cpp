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
      if (addr == 0)
        continue;
      addr += 4;
      ConsoleOutput("LightVN %p", addr);
      HookParam hp;
      hp.address = addr;
      hp.type = CODEC_UTF16 | USING_STRING | DATA_INDIRECT;
      hp.index = 0;
      hp.offset = get_reg(regs::rcx);
      hp.filter_fun = [](void *data, size_t *len, HookParam *hp)
      {
        std::wstring s((wchar_t *)data, *len / 2);
        if (s.substr(s.size() - 2, 2) == L"\\w")
          *len -= 4;
        return true;
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
    if (addr == 0)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (addr == 0)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING;
    hp.offset = get_stack(6);
    hp.filter_fun = [](void *data, size_t *len, HookParam *hp)
    {
      if (all_ascii((wchar_t *)data, *len))
        return false;
      // 高架下に広がる[瀟洒]<しょうしゃ>な店内には、あたしたちのような学生の他に、
      auto str = std::wstring(reinterpret_cast<LPWSTR>(data), *len / 2);
      auto filterpath = {
          L".rpy", L".rpa", L".py", L".pyc", L".txt",
          L".png", L".jpg", L".bmp",
          L".mp3", L".ogg",
          L".webm", L".mp4",
          L".otf", L".ttf", L"Data/"};
      for (auto _ : filterpath)
        if (str.find(_) != str.npos)
          return false;
      str = std::regex_replace(str, std::wregex(L"\\[(.*?)\\]<(.*?)>"), L"$1");
      return write_string_overwrite(data, len, str);
    };
    return NewHook(hp, "LightVN2");
  }
}
namespace
{
  bool commonfilter(LPVOID data, size_t *size, HookParam *)
  {
    auto str = std::wstring((wchar_t *)data, *size / 2);
    std::wregex pattern(L"-{2,}");
    str = std::regex_replace(str, pattern, L"");
    str = std::regex_replace(str, std::wregex(L"\\[(.*?)\\]<(.*?)>"), L"$1");
    return write_string_overwrite(data, size, str);
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
    if (addr == 0)
      return 0;
    addr = MemDbg::findEnclosingAlignedFunction_strict(addr);
    if (addr == 0)
      return 0;
    HookParam hp;
    hp.address = addr;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    // 包含太多短句，所以无法内嵌
    hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto tu = (TextUnionW *)stack->rdx;
      auto str = std::wstring_view(tu->getText(), tu->size);
      if (startWith(str, L"\\n") && endWith(str, L"\\n"))
      {
        *split = 1;
      }
      buffer->from(str);
    };
    hp.filter_fun = commonfilter;
    hp.newlineseperator = L"\\n";
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
      if (straddr == 0)
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
        auto funcaddr = MemDbg::findEnclosingAlignedFunction_strict(leaaddr, 0x2000);
        if (funcaddr == 0)
          continue;
        HookParam hp;
        hp.address = funcaddr;
        hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
        hp.text_fun = [](hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
          // wstring=TextUnionW for msvc c++17
          auto tu=(TextUnionW *)stack->rdx;
          buffer->from(std::wstring_view(tu->getText(), tu->size));
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