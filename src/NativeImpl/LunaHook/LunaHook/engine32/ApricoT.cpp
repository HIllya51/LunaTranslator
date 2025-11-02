#include "ApRicoT.h"

/********************************************************************************************
Apricot hook:
  Game folder contains arc.a*.
  This engine is heavily based on new DirectX interfaces.
  I can't find a good place where text is clean and not repeating.
  The game processes script encoded in UTF32-like format.
  I reversed the parsing algorithm of the game and implemented it partially.
  Only name and text data is needed.

********************************************************************************************/

/** jichi 2/15/2015: ApRicoT
 *
 *  Sample game: イセカイ・ラヴァーズ�体験版
 *  Issue of the old game is that it uses esp as split, and hence has relative address
 *
 *  00978100   5b               pop ebx
 *  00978101   83c4 2c          add esp,0x2c
 *  00978104   c2 0400          retn 0x4
 *  00978107   33c0             xor eax,eax ; jichi: hook here
 *  00978109   bb 03000000      mov ebx,0x3
 *  0097810e   895c24 30        mov dword ptr ss:[esp+0x30],ebx
 *  00978112   894424 2c        mov dword ptr ss:[esp+0x2c],eax
 *  00978116   894424 1c        mov dword ptr ss:[esp+0x1c],eax
 *  0097811a   8b4e 34          mov ecx,dword ptr ds:[esi+0x34]
 *  0097811d   3b4e 3c          cmp ecx,dword ptr ds:[esi+0x3c]
 *  00978120   894424 3c        mov dword ptr ss:[esp+0x3c],eax
 *  00978124   7e 3b            jle short .00978161
 *  00978126   8b7e 3c          mov edi,dword ptr ds:[esi+0x3c]
 *  00978129   3b7e 34          cmp edi,dword ptr ds:[esi+0x34]
 *  0097812c   76 05            jbe short .00978133
 *  0097812e   e8 01db1500      call .00ad5c34
 *  00978133   837e 38 04       cmp dword ptr ds:[esi+0x38],0x4
 *  00978137   72 05            jb short .0097813e
 *  00978139   8b46 24          mov eax,dword ptr ds:[esi+0x24]
 *  0097813c   eb 03            jmp short .00978141
 *  0097813e   8d46 24          lea eax,dword ptr ds:[esi+0x24]
 *  00978141   8b3cb8           mov edi,dword ptr ds:[eax+edi*4]
 *  00978144   016e 3c          add dword ptr ds:[esi+0x3c],ebp
 *  00978147   57               push edi
 *  00978148   55               push ebp
 *  00978149   8d4c24 20        lea ecx,dword ptr ss:[esp+0x20]
 *  0097814d   e8 de05feff      call .00958730
 *
 *  Sample stack: baseaddr = 0c90000
 *  001aec2c   ede50fbb
 *  001aec30   0886064c
 *  001aec34   08860bd0
 *  001aec38   08860620
 *  001aec3c   00000000
 *  001aec40   00000000
 *  001aec44   08860bd0
 *  001aec48   001aee18
 *  001aec4c   08860620
 *  001aec50   00000000
 *  001aec54   00cb4408  return to .00cb4408 from .00c973e0
 *  001aec58   08860bd8
 *  001aec5c   00000000
 *  001aec60   001aefd8  pointer to next seh record
 *  001aec64   00e47d88  se handler
 *  001aec68   ffffffff
 *  001aec6c   00cb9f40  return to .00cb9f40 from .00cc8030 ; jichi: split here
 */
static void SpecialHookApRicoT(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD reg_esi = context->esi;
  DWORD base = *(DWORD *)(reg_esi + 0x24);
  DWORD index = *(DWORD *)(reg_esi + 0x3c);
  DWORD *script = (DWORD *)(base + index * 4);
  // jichi 2/14/2015
  // Change reg_esp to the return address
  // DWORD reg_esp = regof(esp, esp_base);
  //*split = reg_esp;
  //*split = regof(esp, esp_base);
  DWORD arg = context->stack[16];                                       // return address
  *split = arg > processStartAddress ? arg - processStartAddress : arg; // use relative split value
  //*split = argof(1, esp_base);
  if (script[0] == L'<')
  {
    DWORD *end;
    for (end = script; *end != L'>'; end++)
      ; // jichi 2/14/2015: i.e. = ::wcschr(script) or script
    switch (script[1])
    {
    case L'N':
      if (script[2] == L'a' && script[3] == L'm' && script[4] == L'e')
      {
        buffer_index = 0;
        for (script += 5; script < end; script++)
          if (*script > 0x20)
            wc_buffer[buffer_index++] = *script & 0xFFFF;
        buffer->from(wc_buffer, buffer_index << 1);
        // jichi 1/4/2014: The way I save subconext is not able to distinguish the split value
        // Change to shift 16
        //*split |= 1 << 31;
        *split |= 1 << 16; // jichi: differentiate name and text script
      }
      break;
    case L'T':
      if (script[2] == L'e' && script[3] == L'x' && script[4] == L't')
      {
        buffer_index = 0;
        for (script += 5; script < end; script++)
        {
          if (*script > 0x40)
          {
            while (*script == L'{')
            {
              script++;
              while (*script != L'\\')
              {
                wc_buffer[buffer_index++] = *script & 0xffff;
                script++;
              }
              while (*script++ != L'}')
                ;
            }
            wc_buffer[buffer_index++] = *script & 0xffff;
          }
        }
        buffer->from(wc_buffer, buffer_index << 1);
      }
      break;
    }
  }
}

bool InsertApRicoTHook()
{
  for (DWORD i = processStartAddress + 0x1000; i < processStopAddress - 4; i++)
    if ((*(DWORD *)i & 0xfff8fc) == 0x3cf880) // cmp reg,0x3c
      for (DWORD j = i + 3, k = i + 0x100; j < k; j++)
        if ((*(DWORD *)j & 0xffffff) == 0x4c2)
        { // retn 4
          HookParam hp;
          hp.address = j + 3;
          hp.text_fun = SpecialHookApRicoT;
          hp.type = USING_STRING | NO_CONTEXT | CODEC_UTF16;
          ConsoleOutput("INSERT ApRicoT");
          // GROWL_DWORD3(hp.address, processStartAddress, processStopAddress);

          // RegisterEngineType(ENGINE_APRICOT);
          //  jichi 2/14/2015: disable cached GDI functions
          ConsoleOutput("ApRicoT: disable GDI hooks");

          return NewHook(hp, "ApRicoT");
        }

  ConsoleOutput("ApRicoT: failed");
  return false;
}

bool ApRicoT::attach_function()
{

  return InsertApRicoTHook();
}
bool ApRicoTOld2()
{
  // https://vndb.org/v1285
  const uint8_t bytes[] = {
      0x33, 0xed,
      0x39, 0x6c, XX2,
      0x0f, 0x8e, XX4,
      //<==
      0x8b, 0x9c, 0x24, XX4,
      0x8d, 0x4e, 0x04,
      0x89, 0x4c, XX2,
      0xeb, 0x0b};
  ULONG addrX = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addrX)
    return false;
  HookParam hp;
  hp.address = addrX + 2 + 4 + 6;
  hp.type = USING_STRING | NO_CONTEXT;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto ret = context->retaddr;
    if (ret == 0)
      return;
    auto v7 = (DWORD *)context->esi;
    auto v34 = v7 + 1;
    std::string str;
    for (int v21 = 0; v21 < v7[5]; v21++)
    {
      auto v22 = v7[6] < 4u ? v34 : (DWORD *)*v34;
      auto v23 = v22[v21];
      v23 = _byteswap_ushort(v23);
      str += std::string((char *)&v23, 2);
    }
    if (ret > 0x10000)
    {
      static std::string lastname;
      if (str == lastname)
        return;
      lastname = str;
      buffer->from(str);
      *split = 1;
    }
    else
    {
      static lru_cache<std::string> cache(4);
      static std::string last;

      if (cache.touch(str))
      {
        last = str;
        return;
      }
      auto parse = [](std::string s)
      {
        return strReplace(s, "\x81\x40");
      };
      if (startWith(str, last))
      {
        buffer->from(parse(str.substr(last.size())));
        last = str;
      }
      else
      {
        last = str;
        buffer->from(parse(str));
      }
    }
  };
  return NewHook(hp, "ApRicoTOld2");
}
bool ApRicoTOldH()
{
  //[040130][APRICOT] Maple Colors H (bin+cue)
  const uint8_t bytes[] = {
      0x8b, 0x4c, 0x24, XX,
      0x8b, 0x44, 0x24, XX,
      0x2b, 0xc8,
      0x32, 0xdb,
      0x33, 0xff,
      0xd1, 0xf9,
      0x0f, 0x84, XX4};
  ULONG addrX = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addrX)
    return false;
  HookParam hp;
  hp.address = addrX + 8;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto ret = context->retaddr;
    if ((ret != 0) && (ret != 0x15d800))
      return;
    auto ecx = (char *)context->ecx;
    auto eax = (char *)context->eax;
    std::string str;
    for (int edi = 0; edi != (((int)(ecx - eax)) >> 1); edi++)
    {
      WORD ax = *(WORD *)(eax + edi * 2);
      if (ax == 0xa)
        continue;
      ax = _byteswap_ushort(ax);
      str += std::string((char *)&ax, 2);
    }
    static std::string name;
    if (ret == 0x15d800)
    {
      name = str;
    }
    else
    {
      auto parse = [](std::string s)
      {
        return strReplace(s, "\x81\x40");
      };
      static std::string last;
      if (last.size() && startWith(str, last))
      {
        buffer->from(parse(str.substr(last.size())));
        name = "";
      }
      else
      {
        buffer->from(name + parse(str));
      }
      last = str;
    }
  };
  return NewHook(hp, "ApRicoTOld");
}
namespace
{
  bool ayakashi()
  {
    const uint8_t bytes[] = {
        // ayakashi H
        0x8d, 0x69, 0x04,
        0xeb, 0x04,
        //
        0x8b, 0x4c, 0x24, 0x10,
        //
        0x8b, 0x51, 0x18,
        0x83, 0xfa, 0x10,
        0x72, 0x05,
        0x8b, 0x45, 0x00,
        0xeb, 0x02,
        //
        0x8b, 0xc5,
        //
        0x8a, XX, XX,
        0x8a, XX,
        0x80, XX, 0x20,
        0x80, XX, 0x5f,
        0x80, XX, 0x3b};
    ULONG addrX = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    bool isH = true;
    if (!addrX)
    {
      const uint8_t bytes2[] = {
          // ayakashi
          0xc7, 0x44, 0x24, XX, 0x01, 0x00, 0x00, 0x00,
          0x0f, 0x84, XX4,
          0x8b, 0x74, 0x24, 0x10,
          0x53,
          //
          0x8a, XX, XX,
          0x8a, XX,
          0x80, XX, 0x20,
          0x80, XX, 0x5f,
          0x80, XX, 0x3b};
      addrX = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
      isH = false;
    }
    if (!addrX)
      return false;
    addrX = MemDbg::findEnclosingAlignedFunction(addrX, 0x80);
    if (!addrX)
      return false;
    HookParam hp;
    hp.address = addrX;
    hp.type = NO_CONTEXT | USING_STRING;
    if (isH)
    {
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        buffer->from(((TextUnionA *)(context->stack[2] + 4))->view());
      };
    }
    else
    {
      hp.offset = stackoffset(2);
      hp.type |= DATA_INDIRECT;
    }
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      //{しらがみ 白神}{きくり 菊理}が顔を紅潮させて怒った。
      auto s = buffer->strA();
      s = re::sub(s, R"(\{(.*?) (.*?)\})", "$2");
      s = re::sub(s, "[\r\n]+(\x81\x40)*");
      buffer->from(s);
    };
    return NewHook(hp, "AYAKASHI");
  }
}
bool ApRicoTOld::attach_function()
{
  return ApRicoTOldH() || ApRicoTOld2() || ayakashi();
}