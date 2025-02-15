#include "GROOVER.h"

bool GROOVER::attach_function()
{
  // https://vndb.org/v213
  // グリーングリーン2 恋のスペシャルサマー
  auto psnrGetString = GetProcAddress(GetModuleHandle(L"HdSnr3"), "snrGetString");
  BYTE bytes[] = {
      /*
    signed int __stdcall snrGetString(int a1, int a2, void *a3, signed int a4)
  {
    signed int v4; // ebx

    v4 = sub_10001E60(a1, a2);
    if ( a4 < v4 )
      v4 = a4;
    if ( a3 )
    {
      qmemcpy(a3, (const void *)sub_10001E10(a1, a2), v4); <---sub_10001E10返回eax
      *((_BYTE *)a3 + v4) = 0;
    }
    return v4;
  }
      */
      0x8b, 0xcb,
      0x8b, 0xf0,
      0x8b, 0xc1,
      0x8b, 0xfd,
      0xc1, 0xe9, 0x02,
      0xf3, 0xa5};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), (DWORD)psnrGetString, (DWORD)psnrGetString + 0x100);
  if (!addr)
    return addr;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | CODEC_UTF16;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (all_ascii((char *)context->eax))
      return;
    auto ws = StringToWideString((char *)context->eax, 932).value();
    *split = (endWith(ws, L"\\p\\l"));
    if (*split)
    {
      ws = ws.substr(0, ws.size() - 4);
    }
    std::wstring result;
    for (int i = 0; i < ws.size(); i++)
    {
      if (katakanaMap.find(ws[i]) != katakanaMap.end())
      {
        auto wc = katakanaMap[ws[i]];
        if (0xff9e == ws[i + 1])
        {
          wc += 1;
          i += 1;
        }
        else if (0xff9f == ws[i + 1])
        {
          wc += 2;
          i += 1;
        }
        result += wc;
      }
      else
        result += ws[i];
    }
    buffer->from(result);
  };
  return NewHook(hp, "GROOVER");
}