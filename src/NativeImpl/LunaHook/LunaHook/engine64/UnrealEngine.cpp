#include "UnrealEngine.h"

namespace
{
  void ENTERGRAMfilter(TextBuffer *buffer, HookParam *hp)
  {
    std::wstring str = buffer->strW();
    str = re::sub(str, L"\\|(.*?)\u300a(.*?)\u300b", L"$1");
    str = re::sub(str, L"\u3000|\n");
    buffer->from(str);
  };
  bool InsertENTERGRAM()
  {
    // https://vndb.org/v40521
    //[240125][1208048][エンターグラム] すだまリレイシヨン パッケージ版 (mdf+mds)

    const BYTE BYTES[] = {
        0x48, 0x8B, 0x43, 0x38,
        0x48, 0x8D, 0x7C, 0x24, 0x30,
        0x48, 0x8B, 0x74, 0x24, 0x20,
        0x48, 0x85, 0xC0,
        0x48, 0x8B, 0xCD,
        0x48, 0x89, 0x6C, 0x24, 0x40,
        0x48, 0x0F, 0x45, 0xF8};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr + 14;
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
    hp.filter_fun = ENTERGRAMfilter;
    hp.offset = regoffset(rsi);
    hp.lineSeparator = L"\\n";
    return NewHook(hp, "UnrealEngine");
  }
  bool ue5()
  {
    // https://github.com/HIllya51/LunaTranslator/issues/1175
    const BYTE BYTES[] = {
        0x48, 0x89, 0x5C, 0x24, 0x08, 0x48, 0x89, 0x6C, 0x24, 0x10, 0x48, 0x89, 0x74, 0x24, 0x18, 0x57, 0x41, 0x56, 0x41, 0x57, 0x48, 0x83, 0xEC, 0x20, 0x48, 0x8B, 0x59, 0x10, 0x45, 0x33, 0xF6, 0x4C, 0x8B, 0xFA, 0x48, 0x8B, 0xF1, 0x48, 0x85, 0xDB, 0x74, XX, 0x8B, 0x43, 0x08, 0x85, 0xC0, 0x74, XX, 0x8D, 0x48, 0x01, 0xF0, 0x0F, 0xB1, 0x4B, 0x08, 0x74, XX, 0x85, 0xc0, 0x75, XX, 0x33, 0xdb, 0x49, 0x8b, 0x06, 0xb9, 0x40, 0x00, 0x00, 0x00};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
    hp.offset = stackoffset(5);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strW();
      static std::wstring last;
      if (startWith(s, last))
      {
        buffer->from(s.substr(last.size(), s.size() - last.size()));
      }
      last = s;
    };
    return NewHook(hp, "UnrealEngine5");
  }
  bool xxx()
  {
    // 逸剑风云决

    const BYTE BYTES[] = {
        /*
        .text:0000000143B4E330                 movzx   esi, word ptr [rcx+r15*2]
    .text:0000000143B4E335                 inc     edx
    .text:0000000143B4E337                 mov     r8d, [rsp+498h+var_458]
    .text:0000000143B4E33C                 mov     eax, esi
    .text:0000000143B4E33E                 inc     r8d
    .text:0000000143B4E341                 mov     [rsp+498h+var_474], edx
    .text:0000000143B4E345                 and     eax, 0FFFFFC00h
    .text:0000000143B4E34A                 mov     [rsp+498h+var_458], r8d
    .text:0000000143B4E34F                 inc     r15
    .text:0000000143B4E352                 cmp     eax, 0D800h
    .text:0000000143B4E357                 jnz     short loc_143B4E392
    .text:0000000143B4E359                 movsxd  r9, [rsp+498h+var_46C]
    .text:0000000143B4E35E                 cmp     r15, r9
    .text:0000000143B4E361                 jz      short loc_143B4E392
    .text:0000000143B4E363                 movzx   ecx, word ptr [rcx+r15*2]
    .text:0000000143B4E368                 mov     eax, ecx
    .text:0000000143B4E36A                 and     eax, 0FFFFFC00h
    .text:0000000143B4E36F                 cmp     eax, 0DC00h
    .text:0000000143B4E374                 jnz     short loc_143B4E392
    .text:0000000143B4E376                 add     esi, 0FFFF2809h*/
        0x42, 0x0f, 0xb7, 0x34, 0x79,
        0xff, 0xc2,
        0x44, 0x8b, 0x44, 0x24, XX,
        0x8b, 0xc6,
        0x41, 0xff, 0xc0,
        0x89, 0x54, 0x24, XX,
        0x25, 0x00, 0xfc, 0xff, 0xff,
        0x44, 0x89, 0x44, 0x24, XX,
        0x49, 0xff, 0xc7,
        0x3d, 0x00, 0xd8, 0x00, 0x00,
        0x75, XX,
        0x4c, 0x63, 0x4c, 0x24, 0x2c,
        0x4d, 0x3b, 0xf9,
        0x74, 0x2f,
        0x42, 0x0f, 0xb7, 0x0c, 0x79,
        0x8b, 0xc1,
        0x25, 0x00, 0xfc, 0xff, 0xff,
        0x3d, 0x00, 0xdc, 0x00, 0x00,
        0x75, XX,
        0x81, 0xc6, 0x09, 0x28, 0xff, 0xff};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE start[] = {
        0x48, 0x89, 0x5c, 0x24, 0x10,
        0x48, 0x89, 0x6c, 0x24, 0x18,
        0x48, 0x89, 0x74, 0x24, 0x20};
    auto func = reverseFindBytes(start, sizeof(start), addr - 0x200, addr, 0, true);
    if (!func)
      return false;
    HookParam hp;
    hp.address = func;
    hp.type = USING_STRING | CODEC_UTF16 | USING_SPLIT; // 会提取出所有TextBlock文字。怎么split都不完美，就这样吧。
    hp.offset = regoffset(rsi);
    hp.split = regoffset(rsi); // rcx
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      if (all_ascii(buffer->viewW()))
        return buffer->clear();
    };
    return NewHook(hp, "UnrealEngine");
  }
  template <int _>
  void uefilter(TextBuffer *buffer, HookParam *)
  {
    static int idx = 0;
    if (idx++ % 2 == 0)
      return buffer->clear();
    static std::wstring last;
    auto _this = buffer->strW();
    if (startWith(_this, last))
    {
      buffer->from(_this.substr(last.size()));
      last = std::move(_this);
    }
    else if (_this.size() == last.size() + 1)
    {
      buffer->clear();
    }
    else
    {
      last = std::move(_this);
    }
  }
  bool ue42_1()
  {
    const BYTE BYTES[] = {
        0x4a, 0x8d, 0x14, 0x65, 0x00, 0x00, 0x00, 0x00,
        0x48, 0x8b, 0xc8,
        0x4b, 0x8d, 0x1c, 0x36,
        0x49, 0x03, 0xd5,
        0x4c, 0x8b, 0xc3,
        0x48, 0x8b, 0xf8,
        0xe8, XX4,
        0x33, 0xc0};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE start[] = {
        0x40, 0x55,
        0x41, 0x54,
        0x41, 0x55,
        0x41, 0x56,
        0x41, 0x57};
    auto func = reverseFindBytes(start, sizeof(start), addr - 0x100, addr, 0, true);
    if (!func)
      return false;
    HookParam hp;
    hp.address = func;
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
    hp.offset = regoffset(rdx);
    hp.filter_fun = uefilter<0>;
    return NewHook(hp, "UnrealEngine4");
  }
  bool ue42_2()
  {
    const BYTE BYTES[] = {
        0x0f, 0xbe, 0x44, 0x24, 0x40,
        0x85, 0xc0,
        0x74, 0x34,
        0x8b, 0x44, 0x24, 0x3c,
        0x83, 0xe0, 0xfc,
        0x3d, 0x0c, 0x20, 0x00, 0x00,
        0x74, 0x1c,
        0x8b, 0x44, 0x24, 0x3c,
        0x2d, 0x2a, 0x20, 0x00, 0x00,
        0x83, 0xf8, 0x05,
        0x72, 0x0e,
        0x8b, 0x44, 0x24, 0x3c,
        0x2d, 0x66, 0x20, 0x00, 0x00,
        0x83, 0xf8, 0x04,
        0x73, 0x0a};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    BYTE start[] = {
        0x48, 0x89, 0x4c, 0x24, 0x08,
        0x48, 0x81, 0xec, XX4};
    auto func = reverseFindBytes(start, sizeof(start), addr - 0x400, addr, 0, true);
    if (!func)
      return false;
    HookParam hp;
    hp.address = func;
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a1 = context->rcx;
      buffer->from((PWSTR) * (uintptr_t *)(a1 + 16));
    };
    hp.filter_fun = uefilter<1>;
    return NewHook(hp, "UnrealEngine4");
  }
  bool ue42()
  {
    // Mugen Endless Runner 1.0.1.0
    return ue42_1() | ue42_2();
  }
}
bool UnrealEngine::attach_function()
{
  return ((InsertENTERGRAM() || ue5()) | xxx()) || ue42();
}
