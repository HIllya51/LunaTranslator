#include "Moonstone.h"
// https://vndb.org/v464
// あした出逢った少女

bool Moonstone::attach_function()
{
  const BYTE bytes[] = {
      /*
      .text:0042A10C loc_42A10C:                             ; CODE XREF: sub_42A010+11D↓j
  .text:0042A10C                 mov     al, [edx]
  .text:0042A10E                 inc     edi
  .text:0042A10F                 inc     edx
  .text:0042A110                 cmp     al, 81h
  .text:0042A112                 jb      short loc_42A118
  .text:0042A114                 cmp     al, 9Fh
  .text:0042A116                 jbe     short loc_42A128
  .text:0042A118
  .text:0042A118 loc_42A118:                             ; CODE XREF: sub_42A010+102↑j
  .text:0042A118                 cmp     al, 0E0h
  .text:0042A11A                 jb      short loc_42A120
  .text:0042A11C                 cmp     al, 0FCh
  .text:0042A11E                 jbe     short loc_42A128
  .text:0042A120
  .text:0042A120 loc_42A120:                             ; CODE XREF: sub_42A010+10A↑j
  .text:0042A120                 cmp     al, 5Ch ; '\'
  .text:0042A122                 jbe     short loc_42A12A
  .text:0042A124                 cmp     al, 70h ; 'p'
  .text:0042A126                 jnb     short loc_42A12A
  .text:0042A128
  .text:0042A128 loc_42A128:                             ; CODE XREF: sub_42A010+106↑j
  .text:0042A128                                         ; sub_42A010+10E↑j
  .text:0042A128                 inc     edx
  .text:0042A129                 inc     esi
  .text:0042A12A
  .text:0042A12A loc_42A12A:                             ; CODE XREF: sub_42A010+112↑j
  .text:0042A12A                                         ; sub_42A010+116↑j
  .text:0042A12A                 inc     esi
  .text:0042A12B                 cmp     esi, ecx
  .text:0042A12D                 jl      short loc_42A10C
  .text:0042A12F                 mov     [esp+108h+var_DC], edi

   do
      {
        v6 = *v2;
        ++v5;
        ++v2;
        if ( v6 >= 0x81u && v6 <= 0x9Fu || v6 >= 0xE0u && v6 <= 0xFCu || v6 > 0x5Cu && v6 < 0x70u )
        {
          ++v2;
          ++v3;
        }
        ++v3;
      }
      while ( v3 < (int)(v4 - 1) );
      v48 = v5;
      */
      0x8a, 0x02,
      0x47, 0x42,
      0x3c, 0x81, 0x72, 0x04,
      0x3c, 0x9f, 0x76, 0x10,
      0x3c, 0xe0, 0x72, 0x04,
      0x3c, 0xfc, 0x76, 0x08,
      0x3c, 0x5c, 0x76, 0x06,
      0x3c, 0x70, 0x73, 0x02,
      0x42

  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (context->edi != 0)
      return;
    buffer->from((char *)context->edx);
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    StringFilter(buffer, TEXTANDLEN("\x81\x89")); // ♂
    StringFilter(buffer, TEXTANDLEN("\x81\x6f"));
    StringFilter(buffer, TEXTANDLEN("\x81\x70")); // ｛｝ 上标·
    auto s = buffer->strA();
    if (s.size() % 2 == 1)
    {
      auto sub = s.substr(0, s.size() - 1);
      if (endWith(s, "^")) // 0x5e
      {
        sub += "\x81\x42"; // 。
      }
      else if (endWith(s, "_")) // 0x5f
      {
        sub += "\x81\x76"; // 」
      }
      else if (endWith(s, "]")) // 0x5d
      {
        ; // 、 8141 多了个]，不用补
      }
      else if (endWith(s, "b")) // 0x62
      {
        sub += "\x81\x48"; // ？
      }
      else if (endWith(s, "a")) // 0x61
      {
        sub += "\x81\x6a"; // ）
      }
      buffer->from(sub);
    }
  };

  return NewHook(hp, "Moonstone");
}