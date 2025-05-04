#include "ADVSystem.h"
namespace
{
  bool name()
  {
    BYTE sig[] = {
        0X53,
        0X55,
        0X8B, 0X6C, 0X24, 0X10,
        0X56,
        0X8B, 0XF0,
        0X8A, 0X1E,
        0X84, 0XDB,
        0X74, XX,
        0X57,
        0X0F, 0XB6, 0XFB,
        0X57,
        0X83, 0XC6, 0X01,
        0XE8, XX4,
        0X83, 0XC4, 0X04,
        0X85, 0XC0,
        0X75, XX,
        0XF6, 0X87, XX4, 0X04,
        0X74, XX,
        0X8A, 0XE3,
        0X83, 0XC6, 0X01,
        0X8A, 0X46, 0XFF,
        0XEB, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT | EMBED_AFTER_NEW;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "ADVSystem");
  }
  bool prolog()
  {
    BYTE sig[] = {
        0x80, 0X7E, 0X08, 0X00,
        0X8B, 0X7E, 0X0C,
        0X89, 0X06,
        0X0F, 0X85, XX4,
        0X8B, 0X4E, 0X10,
        0X8A, 0X04, 0X39,
        0X83, 0XC1, 0X01,
        0X84, 0XC0,
        0X89, 0X4E, 0X10,
        0X74, XX,
        0X3C, 0X0A,
        0X74, XX,
        0X3C, 0X0D,
        0X74, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a1 = context->esi;
      auto v5 = *(DWORD *)(a1 + 12);
      auto v6 = *(DWORD *)(a1 + 16);
      if (v6)
        return;
      buffer->from((char *)v5);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      buffer->from(strReplace(s, "\r\n", "\n"));
    };
    hp.embed_fun = [](hook_context *context, TextBuffer buffer)
    {
      auto a1 = context->esi;
      auto v5 = *(DWORD *)(a1 + 12);
      auto s = buffer.strA();
      strReplace(s, "\n", "\r\n");
      strcpy((char *)v5, s.c_str());
    };
    return NewHook(hp, "ADVSystem");
  }
  bool text()
  {
    BYTE sig[] = {
        0X83, 0XBF, 0X2C, 0X03, 0X00, 0X00, 0X00,
        0X8B, 0X8F, 0XA8, 0X02, 0X00, 0X00,
        0X8B, 0X59, 0X04,
        0X0F, 0X85, XX4,
        0X80, 0X7F, 0X30, 0X00,
        0X0F, 0X85, XX4,
        0X8B, 0X87, 0XB4, 0X02, 0X00, 0X00,
        0X8A, 0X14, 0X18,
        0X8D, 0X48, 0X01,
        0X0F, 0XB6, 0XC2,
        0X83, 0XF8, 0X24,
        0X89, 0X8F, 0XB4, 0X02, 0X00, 0X00,
        0X0F, 0X87, XX4};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto a1 = context->edi;
      auto v4 = *(DWORD *)(*(DWORD *)(a1 + 680) + 4);
      auto v5 = *(DWORD *)(a1 + 692);
      if (v5)
        return;
      buffer->from((char *)v4);
    };
    static bool hasl = false;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      strReplace(s, "\r\n", "\n");
      if (endWith(s, "$L"))
      {
        hasl = true;
        s = s.substr(0, s.size() - 2);
      }
      buffer->from(s);
    };
    hp.embed_fun = [](hook_context *context, TextBuffer buffer)
    {
      auto a1 = context->edi;
      auto v4 = *(DWORD *)(*(DWORD *)(a1 + 680) + 4);
      auto s = buffer.strA();
      if (hasl)
      {
        s += "$L";
      }
      strReplace(s, "\n", "\r\n");
      strcpy((char *)v4, s.c_str());
      hasl = false;
    };
    return NewHook(hp, "ADVSystem");
  }
}
bool ADVSystem::attach_function()
{
  // クラブ・ロマンスへようこそ
  // prolog最好转成繁体再内嵌，否则可能有些字符会导致崩溃。
  return prolog() && text() && name();
}