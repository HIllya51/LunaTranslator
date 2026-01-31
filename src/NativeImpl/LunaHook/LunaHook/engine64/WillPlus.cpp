#include "WillPlus.h"
namespace
{
  std::wstring prefixappendfix(const std::wstring &origin, const std::wstring &newstr)
  {
    std::wstring pre = re::match(origin, LR"(((%[A-Z]+)*)(.*?))").value()[1];
    std::wstring app = re::match(origin, LR"((.*?)((%[A-Z]+)*))").value()[2];
    return pre + newstr + app;
  }
}
bool WillPlus::attach_function()
{
  /*
  while ( 1 )
  {
    v10 = Block;
    if ( *((_QWORD *)&v75 + 1) > 7ui64 )
      v10 = (void **)Block[0];
    v11 = sub_14000F090((__int64)v10, v75, 0i64, (__int64)L"{", 1ui64);
    if ( v11 == -1i64 )
      break;
    v12 = 0;
    v13 = Block;
    if ( *((_QWORD *)&v75 + 1) > 7ui64 )
      v13 = (void **)Block[0];
    v14 = sub_14000F090((__int64)v13, v75, 0i64, (__int64)L"}", 1ui64);
    v15 = Block;
    if ( *((_QWORD *)&v75 + 1) > 7ui64 )
      v15 = (void **)Block[0];
    v16 = sub_14000F090((__int64)v15, v75, 0i64, (__int64)L":", 1ui64);
    if ( v16 == -1i64 )
    {
      v17 = Block;
      if ( *((_QWORD *)&v75 + 1) > 7ui64 )
        v17 = (void **)Block[0];
      v16 = sub_14000F090((__int64)v17, v75, 0i64, (__int64)&unk_1403FC144, 1ui64);
      v12 = 1;
    }
  */
  const BYTE bytes[] = {
      0X48, 0X8D, 0X4D, XX,
      0X48, 0X83, 0X7D, XX, 0X07,
      0X48, 0X0F, 0X47, 0X4D, XX,
      0X48, 0XC7, 0X44, 0X24, 0X20, 0X01, 0X00, 0X00, 0X00,
      0X4C, 0X8D, 0X0D, XX4,
      0X45, 0X33, 0XC0,
      0X48, 0X8B, 0X55, XX,
      0XE8, XX4,
      0X48, 0X8B, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = CODEC_UTF16 | USING_STRING | EMBED_ABLE;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    std::wstring str = buffer->strW();
    str = re::sub(str, LR"(\\n　*)");
    std::wstring result1 = re::sub(str, L"\\{(.*?):(.*?)\\}", L"$1");
    result1 = re::sub(result1, L"\\{(.*?);(.*?)\\}", L"$1");
    result1 = re::sub(result1, L"%[A-Z]+");
    buffer->from(result1);
  };
  hp.text_fun = [](hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (s->r8 != 0x10)
      return;
    auto text = (LPWSTR)s->rdx;
    buffer->from(text);
  };
  hp.embed_fun = [](hook_context *s, TextBuffer buffer, HookParam *)
  {
    auto data_ = buffer.strW();
    std::wstring origin = (wchar_t *)s->rdx;
    s->rdx = (decltype(s->rdx))allocateString(prefixappendfix(origin, data_));
  };
  hp.embed_hook_font = F_GetGlyphOutlineW;
  return NewHook(hp, "WillPlus_2.1.0");
}
