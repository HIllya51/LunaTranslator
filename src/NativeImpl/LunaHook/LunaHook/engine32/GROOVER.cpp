#include "GROOVER.h"

bool GreenGreen3_textonly()
{
  // https://vndb.org/v214
  // グリーングリーン3 ハローグッバイ
  // sprintf(v15, "%s\\p\\l", v11);
  char pl[] = "%s\\p\\l";
  ULONG addr = MemDbg::findBytes(pl, sizeof(pl) - 1, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findBytes("\xe8", 1, addr, addr + 0x10);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING | NO_CONTEXT | EMBED_ABLE | EMBED_AFTER_NEW; // 中文不可
  return NewHook(hp, "GROOVER");
}
bool GreenGreen3_all()
{
  BYTE bytes[] = {
      /*
  if ( !*((_BYTE *)v6 + v4) )
        break;
      v7 = (void **)v55[0];
      if ( v56 < 0x10 )
        v7 = v55;
      v8 = *((_BYTE *)v7 + v4);
      v9 = (char *)v7 + v4;
      v10 = 0;
      if ( v8 != 92 )
        goto LABEL_22;
      do
      {
        v11 = v9[1];
        if ( v11 == 108 || v11 == 112 )
        {
          v9 += 2;
          v10 += 2;
        }
        else if ( v11 == 119 )
      */
      0x8a, 0x14, 0x30,
      0x03, 0xc6,
      0x33, 0xc9,
      0x80, 0xfa, 0x5c,
      0x75, XX,
      0x8a, 0x50, 0x01,
      0x80, 0xfa, 0x6c,
      0x74, XX,
      0x80, 0xfa, 0x70,
      0x74, XX,
      0x80, 0xfa, 0x77,
      0x75, XX};
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (context->esi)
      return;
    buffer->from((char *)context->eax);
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    StringFilter(buffer, TEXTANDLEN("\\p\\l"));
  };
  return NewHook(hp, "GROOVER");
}
bool GreenGreen3()
{
  return GreenGreen3_all() && GreenGreen3_textonly();
}
bool GreenGreen2()
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
    return false;
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
      if (katakanaMap.count(ws[i]))
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

bool GROOVER::attach_function()
{
  if (GetModuleHandle(L"HdSnr3.dll") && GetModuleHandle(L"RoFAS.dll") && GetModuleHandle(L"RoSnd.dll"))
  {
    return GreenGreen2();
  }
  else
  {
    return GreenGreen3();
  }
}