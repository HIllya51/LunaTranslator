#include "Circus1.h"
/********************************************************************************************
CIRCUS hook:
 Game folder contains advdata folder. Used by CIRCUS games.
 Usually has font caching issues. But trace back from GetGlyphOutline gives a hook
 which generate repetition.
 If we study circus engine follow Freaka's video, we can easily discover that
 in the game main module there is a static buffer, which is filled by new text before
 it's drawing to screen. By setting a hardware breakpoint there we can locate the
 function filling the buffer. But we don't have to set hardware breakpoint to search
 the hook address if we know some characteristic instruction(cmp al,0x24) around there.
********************************************************************************************/
bool InsertCircusHook1() // jichi 10/2/2013: Change return type to bool
{
  for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
    if (*(WORD *)i == 0xa3c) // cmp al, 0xA; je
      for (DWORD j = i; j < i + 0x100; j++)
      {
        BYTE c = *(BYTE *)j;
        if (c == 0xc3)
          break;
        if (c == 0xe8)
        {
          DWORD k = *(DWORD *)(j + 1) + j + 5;
          if (k > processStartAddress && k < processStopAddress)
          {
            HookParam hp;
            hp.address = k;
            hp.offset = stackoffset(3);
            hp.split = regoffset(esp);
            hp.type = DATA_INDIRECT | USING_SPLIT;
            ConsoleOutput("INSERT CIRCUS#1");

            // RegisterEngineType(ENGINE_CIRCUS);
            return NewHook(hp, "Circus1");
          }
        }
      }
  // break;
  // ConsoleOutput("Unknown CIRCUS engine");
  return false;
}
namespace
{
  // C.D.C.D.2～シーディーシーディー2～
  // https://vndb.org/v947
  bool circus12()
  {
    BYTE sig[] = {
        0x3C, 0x24,
        0x0F, 0x85, XX4,
        0x8A, 0x47, 0x01,
        0x47,
        0x3C, 0x6E,
        0x75, XX,
        0xA0, XX4,
        0xB9, XX4,
        0x84, 0xC0,
        0x0F, 0x84, XX4,
        0x88, 0x06,
        0x8A, 0x41, 0x01,
        0x46,
        0x41,
        0x84, 0xC0,
        0x75, XX,
        0xE9, XX4,
        0x3C, 0x66,
        0x75, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x40);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "Circus1");
  }
  bool dcold_name()
  {
    BYTE sig[] = {
        0x57,
        0x6a, 0x01,
        0x68, 0x58, 0x02, 0x00, 0x00,
        0x68, 0x20, 0x03, 0x00, 0x00,
        0x6a, 0x00,
        0x6a, 0x00,
        0xe8, XX4,
        0x8b, 0x7c, 0x24, 0x1c,
        0x83, 0xc4, 0x14,
        0x80, 0x3f, 0x00,
        0x74, XX,
        0x8b, 0xc7,
        0x8d, 0x50, 0x01,
        0x8a, 0x08,
        0x40,
        0x84, 0xc9,
        0x75, XX,
        0x2b, 0xc2,
        0x6b, 0xc0, 0x1a};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(1);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS | EMBED_AFTER_NEW;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    return NewHook(hp, "dcold_name");
  }
  bool dcold_setakushi()
  {
    BYTE sig[] = {
        0X56,
        0X8B, 0X74, 0X24, 0X08,
        0X8B, 0X46, 0X04,
        0X8B, 0X56, 0X1C,
        0X8B, 0X0E,
        0X57,
        0X03, 0XD0,
        0X52,
        0X8B, 0X56, 0X18,
        0X03, 0XD1,
        0X52, 0X50, 0X51,
        0XE8, XX4,
        0X8B, 0X7C, 0X24, 0X20,
        0X83, 0XC4, 0X10,
        0X80, 0X3F, 0X40,
        0X75, XX,
        0X80, 0X7F, 0X01, 0X73,
        0X75, XX,
        0XF6, 0X46, 0X08, 0X80,
        0X74, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_STRING | FULL_STRING | NO_CONTEXT;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      static lru_cache<std::string> cache(3);
      auto s = buffer->strA();
      if (cache.touch(s))
        buffer->clear();
    };
    return NewHook(hp, "dcold_setakushi");
  }
  bool dcold_TEXT()
  {
    BYTE sig[] = {
        /*
         if ( byte_8FA790[0] == 64 && byte_8FA791 == 75 )
        dword_8FAB90 = 2;
      dword_8DBC38 = strlen(byte_8FA790);
        */
        0x80, 0x3d, XX4, 0x40,
        0x89, 0x35, XX4,
        0x75, 0x13,
        0x80, 0x3d, XX4, 0x4b,
        0x75, 0x0a,
        0xc7, 0x05, XX4, 0x02, 0x00, 0x00, 0x00,
        0xb8, XX4,
        0x8d, 0x50, 0x01,
        0xeb, XX};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    static auto byte_8FA790 = (char *)*(DWORD *)(addr + 2);
    auto byte_8FA791 = (char *)*(DWORD *)(addr + 7 + 6 + 2 + 2);
    if (byte_8FA790 + 1 != byte_8FA791)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_DYNA_SJIS;
    hp.embed_hook_font = F_GetGlyphOutlineA;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      buffer->from(byte_8FA790);
    };
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      // 看起来需要过滤@k的样子，不过c了一会儿没遇到，算了先不弄它。
      auto s = buffer->strA();
      s = re::sub(s, R"(\x81\x6f(.*?)\x81\x5e(.*?)\x81\x70)", "$2"); // ｛みす／御簾｝
      strReplace(s, "\x81\x40");
      strReplace(s, "\n");
      buffer->from(s);
    };
    hp.embed_fun = [](hook_context *context, TextBuffer buffer)
    {
      strcpy(byte_8FA790, buffer.strA().c_str());
    };
    return NewHook(hp, "dcold_TEXT");
  }
  bool dcold()
  {
    // D.C.～ダ・カーポ～　MEMORIES DISC
    auto succ = dcold_name() && dcold_TEXT();
    if (succ)
      succ |= dcold_setakushi();
    return succ;
  }
}
bool Circus1::attach_function()
{
  return (InsertCircusHook1() | circus12()) || dcold();
}

bool Circus_old::attach_function()
{
  //[041213][CIRCUS]最終試験くじら
  auto call = findiatcallormov((DWORD)GetGlyphOutlineA, processStartAddress, processStartAddress, processStopAddress);
  if (!call)
    return false;
  auto func = MemDbg::findEnclosingAlignedFunction(call);
  if (!func)
    return false;
  BYTE sig[] = {
      /*
      .text:0041D1CD                 cmp     edi, 8140h
  .text:0041D1D3                 jz      loc_41D2D9
  .text:0041D1D9                 cmp     edi, 20h ; ' '
  .text:0041D1DC                 jz      loc_41D2E1*/
      /*
      if ( v14 == 33088 )
              {
                gm.gmCellIncX = psizl.cx;
                goto LABEL_46;
              }
              if ( v14 == 32 )
                goto LABEL_46;
              if ( v43 == v14 )
                goto LABEL_44;
              sub_41DC00(0);
              v15 = pvBuffer;
              if ( GetGlyphOutlineA(hdc, v14, 6u, &gm, cjBuffer, pvBuffer, &mat2) != -1 )*/
      0x81, 0xFF, 0x40, 0x81, 0x00, 0x00,
      0x0F, 0x84, XX4,
      0x83, 0xFF, 0x20,
      0x0F, 0x84, XX4

  };
  if (!MemDbg::findBytes(sig, sizeof(sig), func, call))
    return false;
  auto refs = findxref_reverse_checkcallop(func, processStartAddress, processStopAddress, 0xe8);
  if (refs.size() == 3)
  {
    func = MemDbg::findEnclosingAlignedFunction(refs[0]);
  }
  HookParam hp;
  hp.address = func;
  hp.offset = stackoffset(4);
  hp.split = stackoffset(1);
  hp.type = USING_STRING | USING_SPLIT;
  return NewHook(hp, "Circus");
}