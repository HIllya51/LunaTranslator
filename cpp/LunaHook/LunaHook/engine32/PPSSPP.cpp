
#include"PPSSPP.h"

#include"ppsspp/psputils.hpp"
#if 0
namespace { // unnamed

inline bool _bandaigarbage_ch(char c)
{
  return c == ' ' || c == '/' || c == '#' || c == '.' || c == ':'
      || c >= '0' && c <= '9'
      || c >= 'A' && c <= 'z'; // also ignore ASCII 91-96: [ \ ] ^ _ `
}

// Remove trailing /L/P or #n garbage
size_t _bandaistrlen(LPCSTR text)
{
  size_t len = ::strlen(text);
  size_t ret = len;
  while (len && _bandaigarbage_ch(text[len - 1])) {
    len--;
    if (text[len] == '/' || text[len] == '#') // in case trim UTF-8 trailing bytes
      ret = len;
  }
  return ret;
}

// Trim leading garbage
LPCSTR _bandailtrim(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  if (p)
    for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
      if (!_bandaigarbage_ch(*p))
        return p;
  return nullptr;
}
} // unnamed namespae



static void SpecialPSPHookBandai(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);

  if (*text) {
    //lasttext = text;
    text = _bandailtrim(text);
    *data = (DWORD)text;
    *len = _bandaistrlen(text);

    // Issue: The split value will create lots of threads for Shining Hearts
    //*split = regof(ecx, esp_base); // works for Shool Rumble, but mix character name for Shining Hearts
    *split = context->edi; // works for Shining Hearts to split character name
  }
}

// 7/22/2014 jichi: This engine works for multiple game?
// It is also observed in Broccoli game ぁ�の�リンスさまっ.
bool InsertBandaiPSPHook()
{
  ConsoleOutput("BANDAI PSP: enter");

  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 13400560   77 0f            ja short 13400571
    0xc7,0x05, XX8,                 // 13400562   c705 a8aa1001 cc>mov dword ptr ds:[0x110aaa8],0x883decc
    0xe9, XX4,                      // 1340056c  -e9 93fa54f0      jmp 03950004
    0x8b,0x35, XX4,                 // 13400571   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
    0x81,0xc6, 0x01,0x00,0x00,0x00, // 13400577   81c6 01000000    add esi,0x1
    0x8b,0x05, XX4,                 // 1340057d   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13400583   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8, XX4,            // 13400589   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
    0x8b,0x2d, XX4,                 // 13400590   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
    0x8d,0x6d, 0x01,                // 13400596   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
    0x81,0xff, 0x00,0x00,0x00,0x00  // 13400599   81ff 00000000    cmp edi,0x0
  };
  enum { memory_offset = 3 };  // 13400589   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = 0x13400589 - 0x13400560 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("BANDAI PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    //hp.offset=regoffset(eax);
    hp.text_fun = SpecialPSPHookBandai;
    ConsoleOutput("BANDAI PSP: INSERT");
    succ|=NewHook(hp, "BANDAI PSP");
  }

  ConsoleOutput("BANDAI PSP: leave");
  return succ;
}


/** 7/29/2014 jichi Otomate PPSSPP 0.9.9
 *  Sample game: Amnesia Crowd
 *  Sample game: Amnesia Later
 *
 *  006db4af   cc               int3
 *  006db4b0   8b15 b8ebaf00    mov edx,dword ptr ds:[0xafebb8]          ; ppssppwi.01134988
 *  006db4b6   56               push esi
 *  006db4b7   8b42 10          mov eax,dword ptr ds:[edx+0x10]
 *  006db4ba   25 ffffff3f      and eax,0x3fffffff
 *  006db4bf   0305 94411301    add eax,dword ptr ds:[0x1134194]
 *  006db4c5   8d70 01          lea esi,dword ptr ds:[eax+0x1]
 *  006db4c8   8a08             mov cl,byte ptr ds:[eax] ; jichi: hook here, get text in [eax]
 *  006db4ca   40               inc eax
 *  006db4cb   84c9             test cl,cl
 *  006db4cd  ^75 f9            jnz short ppssppwi.006db4c8
 *  006db4cf   2bc6             sub eax,esi
 *  006db4d1   8942 08          mov dword ptr ds:[edx+0x8],eax
 *  006db4d4   5e               pop esi
 *  006db4d5   8d0485 07000000  lea eax,dword ptr ds:[eax*4+0x7]
 *  006db4dc   c3               retn
 *  006db4dd   cc               int3
 */
static void SpecialPPSSPPHookOtomate(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  // 006db4b7   8b42 10          mov eax,dword ptr ds:[edx+0x10] ; jichi: hook here
  // 006db4ba   25 ffffff3f      and eax,0x3fffffff
  // 006db4bf   0305 94411301    add eax,dword ptr ds:[0x1134194]; jichi: ds offset
  // 006db4c5   8d70 01          lea esi,dword ptr ds:[eax+0x1]
  DWORD edx = context->edx;
  DWORD eax = *(DWORD *)(edx + 0x10);
  eax &= 0x3fffffff;
  eax += *(DWORD *)hp->user_value;

  //DWORD eax = regof(eax, esp_base);
  LPCSTR text = LPCSTR(eax);
  if (*text) {
    text = _bandailtrim(text); // the same as bandai PSP
    *data = (DWORD)text;
    *len = _bandaistrlen(text);

    *split = context->ecx; // the same as Otomate PSP hook
    //DWORD ecx = regof(ecx, esp_base); // the same as Otomate PSP hook
    //*split = ecx ? ecx : (FIXED_SPLIT_VALUE << 2);
    //*split = ecx & 0xffffff00; // skip cl which is used
  }
}
bool InsertOtomatePPSSPPHook()
{
  ConsoleOutput("Otomate PPSSPP: enter");
  const BYTE bytes[] =  {
    0x8b,0x15, XX4,             // 006db4b0   8b15 b8ebaf00    mov edx,dword ptr ds:[0xafebb8]          ; ppssppwi.01134988
    0x56,                       // 006db4b6   56               push esi
    0x8b,0x42, 0x10,            // 006db4b7   8b42 10          mov eax,dword ptr ds:[edx+0x10] ; jichi: hook here
    0x25, 0xff,0xff,0xff,0x3f,  // 006db4ba   25 ffffff3f      and eax,0x3fffffff
    0x03,0x05, XX4,             // 006db4bf   0305 94411301    add eax,dword ptr ds:[0x1134194]; jichi: ds offset
    0x8d,0x70, 0x01,            // 006db4c5   8d70 01          lea esi,dword ptr ds:[eax+0x1]
    0x8a,0x08,                  // 006db4c8   8a08             mov cl,byte ptr ds:[eax] ; jichi: hook here
    0x40,                       // 006db4ca   40               inc eax
    0x84,0xc9,                  // 006db4cb   84c9             test cl,cl
    0x75, 0xf9,                 // 006db4cd  ^75 f9            jnz short ppssppwi.006db4c8
    0x2b,0xc6,                  // 006db4cf   2bc6             sub eax,esi
    0x89,0x42, 0x08,            // 006db4d1   8942 08          mov dword ptr ds:[edx+0x8],eax
    0x5e,                       // 006db4d4   5e               pop esi
    0x8d,0x04,0x85, 0x07,0x00,0x00,0x00  // 006db4d5   8d0485 07000000  lea eax,dword ptr ds:[eax*4+0x7]
  };
  //enum { addr_offset = 0x006db4c8 - 0x006db4b0 };
  enum { addr_offset = 0x006db4b7 - 0x006db4b0 };
  enum { ds_offset = 0x006db4bf - 0x006db4b0 + 2 };
  auto succ=false;
  DWORD addr = SafeFindBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("Otomate PPSSPP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(addr + ds_offset); // this is the address after ds:[]
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPPSSPPHookOtomate;
    ConsoleOutput("Otomate PPSSPP: INSERT");
    succ|=NewHook(hp, "Otomate PPSSPP");
  }

  ConsoleOutput("Otomate PPSSPP: leave");
  return succ;
}

/** jichi 7/12/2014 PPSSPP
 *  Tested with PPSSPP 0.9.8.
 */
void SpecialPSPHook(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD offset = *(DWORD *)(context->base + hp->offset);
  LPCSTR text = LPCSTR(offset + hp->user_value);
  static LPCSTR lasttext;
  if (*text) {
    *data = (DWORD)text;
    // I only considered SHIFT-JIS/UTF-8 case
    if (hp->length_offset == 1)
      *len = 1; // only read 1 byte
    else if (hp->length_offset)
      *len = *(DWORD *)(context->base + hp->length_offset);
    else
      *len = ::strlen(text); // should only be applied to hp->type|USING_STRING
    if (hp->type & USING_SPLIT) {
      if (hp->type & FIXING_SPLIT)
        *split = FIXED_SPLIT_VALUE;
      else
        *split = *(DWORD *)(context->base + hp->split);
    }
  }
}


/** 8/9/2014 jichi imageepoch.co.jp PSP engine, 0.9.8, 0.9.9
 *  Sample game: Sol Trigger (0.9.8, 0.9.9)
 *
 *  Though Imageepoch1 also exists, it cannot find scenario text.
 *
 *  FIXED memory addresses (different from Imageepoch1): two matches, UTF-8
 *
 *  Debug method: find current text and add breakpoint.
 *
 *  There a couple of good functions. The first one is used.
 *  There is only one text threads. But it cannot extract character names.
 *
 *  135fd497   cc               int3
 *  135fd498   77 0f            ja short 135fd4a9
 *  135fd49a   c705 a8aa1001 20>mov dword ptr ds:[0x110aaa8],0x8952d20
 *  135fd4a4  -e9 5b2b2ef0      jmp 038e0004
 *  135fd4a9   8b35 dca71001    mov esi,dword ptr ds:[0x110a7dc]
 *  135fd4af   81c6 04000000    add esi,0x4
 *  135fd4b5   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  135fd4bb   81e0 ffffff3f    and eax,0x3fffffff
 *  135fd4c1   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000]   ; jichi: hook here
 *  135fd4c8   813d 68a71001 00>cmp dword ptr ds:[0x110a768],0x0
 *  135fd4d2   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  135fd4d8   c705 aca71001 23>mov dword ptr ds:[0x110a7ac],0x23434623
 *  135fd4e2   c705 b0a71001 30>mov dword ptr ds:[0x110a7b0],0x30303030
 *  135fd4ec   8935 b4a71001    mov dword ptr ds:[0x110a7b4],esi
 *  135fd4f2   c705 b8a71001 00>mov dword ptr ds:[0x110a7b8],0x0
 *  135fd4fc   0f85 16000000    jnz 135fd518
 *  135fd502   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  135fd509   e9 22000000      jmp 135fd530
 *  135fd50e   01642d 95        add dword ptr ss:[ebp+ebp-0x6b],esp
 *  135fd512   08e9             or cl,ch
 *  135fd514   0b2b             or ebp,dword ptr ds:[ebx]
 *  135fd516   2e:f0:832d c4aa1>lock sub dword ptr cs:[0x110aac4],0x8    ; lock prefix
 *  135fd51f   c705 a8aa1001 40>mov dword ptr ds:[0x110aaa8],0x8952d40
 *  135fd529  -e9 f52a2ef0      jmp 038e0023
 *  135fd52e   90               nop
 *  135fd52f   cc               int3
 */
bool InsertImageepoch2PSPHook()
{
  ConsoleOutput("Imageepoch2 PSP: enter");

  const BYTE bytes[] =  {
                                         // 135fd497   cc               int3
    0x77, 0x0f,                          // 135fd498   77 0f            ja short 135fd4a9
    0xc7,0x05, XX8,                      // 135fd49a   c705 a8aa1001 20>mov dword ptr ds:[0x110aaa8],0x8952d20
    0xe9, XX4,                           // 135fd4a4  -e9 5b2b2ef0      jmp 038e0004
    0x8b,0x35, XX4,                      // 135fd4a9   8b35 dca71001    mov esi,dword ptr ds:[0x110a7dc]
    0x81,0xc6, 0x04,0x00,0x00,0x00,      // 135fd4af   81c6 04000000    add esi,0x4
    0x8b,0x05, XX4,                      // 135fd4b5   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f,      // 135fd4bb   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8, XX4,                 // 135fd4c1   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000]   ; jichi: hook here
    0x81,0x3d, XX4, 0x00,0x00,0x00,0x00, // 135fd4c8   813d 68a71001 00>cmp dword ptr ds:[0x110a768],0x0
    0x89,0x3d, XX4,                      // 135fd4d2   893d 78a71001    mov dword ptr ds:[0x110a778],edi
    0xc7,0x05, XX8,                      // 135fd4d8   c705 aca71001 23>mov dword ptr ds:[0x110a7ac],0x23434623
    0xc7,0x05, XX8,                      // 135fd4e2   c705 b0a71001 30>mov dword ptr ds:[0x110a7b0],0x30303030
    0x89,0x35, XX4,                      // 135fd4ec   8935 b4a71001    mov dword ptr ds:[0x110a7b4],esi
    0xc7,0x05, XX4, 0x00,0x00,0x00,0x00, // 135fd4f2   c705 b8a71001 00>mov dword ptr ds:[0x110a7b8],0x0
    0x0f,0x85 //, XX4,                   // 135fd4fc   0f85 16000000    jnz 135fd518
  };
  enum { memory_offset = 3 }; // 1346d381   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = 0x135fd4c1 - 0x135fd498 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Imageepoch2 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT; // UTF-8, though
    hp.offset=regoffset(eax);
    hp.split = regoffset(ecx);
    hp.text_fun = SpecialPSPHook;
    ConsoleOutput("Imageepoch2 PSP: INSERT");
    succ|=NewHook(hp, "Imageepoch2 PSP");
  }

  ConsoleOutput("Imageepoch2 PSP: leave");
  return succ;
}

/** 7/22/2014 jichi BANDAI PSP engine, 0.9.8 only
 *  Replaced by Otomate PPSSPP on 0.9.9.
 *  Sample game: School Rumble PSP 姉さん事件で�(SHIFT-JIS)
 *  See: http://sakuradite.com/topic/333
 *
 *  Sample game: 寮�のサクリファイス work on 0.9.8, not 0.9.9
 *
 *
 *  Sample game: Shining Hearts (UTF-8)
 *  See: http://sakuradite.com/topic/346
 *
 *  The encoding could be either UTF-8 or SHIFT-JIS
 *
 *  Debug method: breakpoint the memory address
 *  There are two matched memory address to the current text
 *
 *  Only one function is accessing the text address.
 *
 *  Character name:
 *
 *  1346c122   cc               int3
 *  1346c123   cc               int3
 *  1346c124   77 0f            ja short 1346c135
 *  1346c126   c705 a8aa1001 a4>mov dword ptr ds:[0x110aaa8],0x882f2a4
 *  1346c130  -e9 cf3e2cf0      jmp 03730004
 *  1346c135   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  1346c13b   81e0 ffffff3f    and eax,0x3fffffff
 *  1346c141   8bb0 14004007    mov esi,dword ptr ds:[eax+0x7400014]
 *  1346c147   8b3d 70a71001    mov edi,dword ptr ds:[0x110a770]
 *  1346c14d   c1e7 02          shl edi,0x2
 *  1346c150   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  1346c156   81e0 ffffff3f    and eax,0x3fffffff
 *  1346c15c   8ba8 18004007    mov ebp,dword ptr ds:[eax+0x7400018]
 *  1346c162   03fe             add edi,esi
 *  1346c164   8bc7             mov eax,edi
 *  1346c166   81e0 ffffff3f    and eax,0x3fffffff
 *  1346c16c   0fb790 02004007  movzx edx,word ptr ds:[eax+0x7400002]
 *  1346c173   8bc2             mov eax,edx
 *  1346c175   8bd5             mov edx,ebp
 *  1346c177   03d0             add edx,eax
 *  1346c179   8bc2             mov eax,edx
 *  1346c17b   81e0 ffffff3f    and eax,0x3fffffff
 *  1346c181   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  1346c188   8bcf             mov ecx,edi
 *  1346c18a   81e7 ff000000    and edi,0xff
 *  1346c190   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  1346c196   8b35 b8a71001    mov esi,dword ptr ds:[0x110a7b8]
 *  1346c19c   81c6 bc82ffff    add esi,0xffff82bc
 *  1346c1a2   81ff 00000000    cmp edi,0x0
 *  1346c1a8   893d 70a71001    mov dword ptr ds:[0x110a770],edi
 *  1346c1ae   8915 78a71001    mov dword ptr ds:[0x110a778],edx
 *  1346c1b4   892d 7ca71001    mov dword ptr ds:[0x110a77c],ebp
 *  1346c1ba   890d 80a71001    mov dword ptr ds:[0x110a780],ecx
 *  1346c1c0   8935 84a71001    mov dword ptr ds:[0x110a784],esi
 *  1346c1c6   0f85 16000000    jnz 1346c1e2
 *  1346c1cc   832d c4aa1001 0b sub dword ptr ds:[0x110aac4],0xb
 *  1346c1d3   e9 3c050000      jmp 1346c714
 *  1346c1d8   014cf3 82        add dword ptr ds:[ebx+esi*8-0x7e],ecx
 *  1346c1dc   08e9             or cl,ch
 *  1346c1de   41               inc ecx
 *  1346c1df   3e:2c f0         sub al,0xf0                              ; superfluous prefix
 *  1346c1e2   832d c4aa1001 0b sub dword ptr ds:[0x110aac4],0xb
 *  1346c1e9   e9 0e000000      jmp 1346c1fc
 *  1346c1ee   01d0             add eax,edx
 *  1346c1f0   f2:              prefix repne:                            ; superfluous prefix
 *  1346c1f1   8208 e9          or byte ptr ds:[eax],0xffffffe9
 *  1346c1f4   2b3e             sub edi,dword ptr ds:[esi]
 *  1346c1f6   2c f0            sub al,0xf0
 *  1346c1f8   90               nop
 *  1346c1f9   cc               int3
 *  1346c1fa   cc               int3
 *  1346c1fb   cc               int3
 *
 *  Scenario:
 *
 *  1340055d   cc               int3
 *  1340055e   cc               int3
 *  1340055f   cc               int3
 *  13400560   77 0f            ja short 13400571
 *  13400562   c705 a8aa1001 cc>mov dword ptr ds:[0x110aaa8],0x883decc
 *  1340056c  -e9 93fa54f0      jmp 03950004
 *  13400571   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13400577   81c6 01000000    add esi,0x1
 *  1340057d   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13400583   81e0 ffffff3f    and eax,0x3fffffff
 *  13400589   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  13400590   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
 *  13400596   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  13400599   81ff 00000000    cmp edi,0x0
 *  1340059f   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  134005a5   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  134005ab   892d 78a71001    mov dword ptr ds:[0x110a778],ebp
 *  134005b1   0f84 16000000    je 134005cd
 *  134005b7   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  134005be   e9 21000000      jmp 134005e4
 *  134005c3   01d0             add eax,edx
 *  134005c5   de83 08e956fa    fiadd word ptr ds:[ebx+0xfa56e908]
 *  134005cb   54               push esp
 *  134005cc   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x4    ; lock prefix
 *  134005d4   e9 7f000000      jmp 13400658
 *  134005d9   01dc             add esp,ebx
 *  134005db   de83 08e940fa    fiadd word ptr ds:[ebx+0xfa40e908]
 *  134005e1   54               push esp
 *  134005e2   f0:90            lock nop                                 ; lock prefix is not allowed
 *  134005e4   77 0f            ja short 134005f5
 *  134005e6   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x883ded0
 *  134005f0  -e9 0ffa54f0      jmp 03950004
 *  134005f5   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  134005fb   81e0 ffffff3f    and eax,0x3fffffff
 *  13400601   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000]
 *  13400608   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
 *  1340060e   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13400611   81fe 00000000    cmp esi,0x0
 *  13400617   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  1340061d   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  13400623   0f84 16000000    je 1340063f
 *  13400629   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13400630  ^e9 afffffff      jmp 134005e4
 *  13400635   01d0             add eax,edx
 *  13400637   de83 08e9e4f9    fiadd word ptr ds:[ebx+0xf9e4e908]
 *  1340063d   54               push esp
 *  1340063e   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x3    ; lock prefix
 *  13400646   e9 0d000000      jmp 13400658
 *  1340064b   01dc             add esp,ebx
 *  1340064d   de83 08e9cef9    fiadd word ptr ds:[ebx+0xf9cee908]
 *  13400653   54               push esp
 *  13400654   f0:90            lock nop                                 ; lock prefix is not allowed
 *  13400656   cc               int3
 *  13400657   cc               int3
 */
bool InsertBandaiNamePSPHook()
{
  ConsoleOutput("BANDAI Name PSP: enter");

  const BYTE bytes[] =  {
    //0xcc,                         // 1346c122   cc               int3
    //0xcc,                         // 1346c123   cc               int3
    0x77, 0x0f,                     // 1346c124   77 0f            ja short 1346c135
    0xc7,0x05, XX8,                 // 1346c126   c705 a8aa1001 a4>mov dword ptr ds:[0x110aaa8],0x882f2a4
    0xe9, XX4,                      // 1346c130  -e9 cf3e2cf0      jmp 03730004
    0x8b,0x05, XX4,                 // 1346c135   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346c13b   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb0, XX4,                 // 1346c141   8bb0 14004007    mov esi,dword ptr ds:[eax+0x7400014]
    0x8b,0x3d, XX4,                 // 1346c147   8b3d 70a71001    mov edi,dword ptr ds:[0x110a770]
    0xc1,0xe7, 0x02,                // 1346c14d   c1e7 02          shl edi,0x2
    0x8b,0x05, XX4,                 // 1346c150   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346c156   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xa8, XX4,                 // 1346c15c   8ba8 18004007    mov ebp,dword ptr ds:[eax+0x7400018]
    0x03,0xfe,                      // 1346c162   03fe             add edi,esi
    0x8b,0xc7,                      // 1346c164   8bc7             mov eax,edi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346c166   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb7,0x90, XX4,            // 1346c16c   0fb790 02004007  movzx edx,word ptr ds:[eax+0x7400002]
    0x8b,0xc2,                      // 1346c173   8bc2             mov eax,edx
    0x8b,0xd5,                      // 1346c175   8bd5             mov edx,ebp
    0x03,0xd0,                      // 1346c177   03d0             add edx,eax
    0x8b,0xc2,                      // 1346c179   8bc2             mov eax,edx
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346c17b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8 //, XX4          // 1346c181   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
  };
  enum { memory_offset = 3 };  // 1346c181   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = sizeof(bytes) - memory_offset };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("BANDAI Name PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    hp.offset=regoffset(eax);
    hp.split = regoffset(ebx);
    hp.text_fun = SpecialPSPHook;
    ConsoleOutput("BANDAI Name PSP: INSERT");
    succ|=NewHook(hp, "BANDAI Name PSP");
  }

  ConsoleOutput("BANDAI Name PSP: leave");
  return succ;
}

/** 7/26/2014 jichi Otomate PSP engine, 0.9.8 only, 0.9.9 not work
 *  Replaced by Otomate PPSSPP on 0.9.9.
 *
 *  Sample game: クロノスタシア
 *  Sample game: フォトカ�(repetition)
 *
 *  Not work on 0.9.9: Amnesia Crowd
 *
 *  The instruction pattern also exist in 0.9.9. But the function is not called.
 *
 *  Memory address is FIXED.
 *  Debug method: breakpoint the memory address
 *
 *  The memory access of the function below is weird that the accessed value is 2 bytes after the real text.
 *
 *  PPSSPP 0.9.8, クロノスタシア
 *  13c00fe1   cc               int3
 *  13c00fe2   cc               int3
 *  13c00fe3   cc               int3
 *  13c00fe4   77 0f            ja short 13c00ff5
 *  13c00fe6   c705 a8aa1001 30>mov dword ptr ds:[0x110aaa8],0x884b330
 *  13c00ff0  -e9 0ff0edf2      jmp 06ae0004
 *  13c00ff5   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13c00ffb   81e0 ffffff3f    and eax,0x3fffffff
 *  13c01001   0fbeb0 0000c007  movsx esi,byte ptr ds:[eax+0x7c00000] ; jichi: hook here
 *  13c01008   81fe 00000000    cmp esi,0x0 ; jichi: hook here, get the esi value
 *  13c0100e   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  13c01014   0f84 25000000    je 13c0103f
 *  13c0101a   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13c01020   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  13c01023   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13c01029   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13c01030  ^e9 afffffff      jmp 13c00fe4
 *  13c01035   0130             add dword ptr ds:[eax],esi
 *  13c01037   b3 84            mov bl,0x84
 *  13c01039   08e9             or cl,ch
 *  13c0103b   e4 ef            in al,0xef                               ; i/o command
 *  13c0103d   ed               in eax,dx                                ; i/o command
 *  13c0103e   f2:              prefix repne:                            ; superfluous prefix
 *  13c0103f   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13c01046   e9 0d000000      jmp 13c01058
 *  13c0104b   013cb3           add dword ptr ds:[ebx+esi*4],edi
 *  13c0104e   8408             test byte ptr ds:[eax],cl
 *  13c01050  -e9 ceefedf2      jmp 06ae0023
 *  13c01055   90               nop
 *  13c01056   cc               int3
 *  13c01057   cc               int3
 */
// TODO: is reverse_strlen a better choice?
// Read text from esi
static void SpecialPSPHookOtomate(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  //static uniquemap uniq;
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value - 2); // -2 to read 1 word more from previous location
  if (*text) {
    *split = context->ecx; // this would cause lots of texts, but it works for all games
    //*split = regof(ecx, esp_base) & 0xff00; // only use higher bits
    *data = (DWORD)text;
    size_t sz = ::strlen(text);
    *len = sz == 3 ? 3 : 1; // handling the last two bytes
  }
}

bool InsertOtomatePSPHook()
{
  ConsoleOutput("Otomate PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 13c00fe4   77 0f            ja short 13c00ff5
    0xc7,0x05, XX8,                 // 13c00fe6   c705 a8aa1001 30>mov dword ptr ds:[0x110aaa8],0x884b330
    0xe9, XX4,                      // 13c00ff0  -e9 0ff0edf2      jmp 06ae0004
    0x8b,0x05, XX4,                 // 13c00ff5   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13c00ffb   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 13c01001   0fbeb0 0000c007  movsx esi,byte ptr ds:[eax+0x7c00000] ; jichi: hook here
    0x81,0xfe, 0x00,0x00,0x00,0x00, // 13c01008   81fe 00000000    cmp esi,0x0
    0x89,0x35, XX4,                 // 13c0100e   8935 80a71001    mov dword ptr ds:[0x110a780],esi
    0x0f,0x84, 0x25,0x00,0x00,0x00, // 13c01014   0f84 25000000    je 13c0103f
    0x8b,0x35, XX4,                 // 13c0101a   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
    0x8d,0x76, 0x01,                // 13c01020   8d76 01          lea esi,dword ptr ds:[esi+0x1]
    0x89,0x35, XX4,                 // 13c01023   8935 78a71001    mov dword ptr ds:[0x110a778],esi
    0x83,0x2d, XX4, 0x03            // 13c01029   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
  };
  enum { memory_offset = 3 };
  //enum { addr_offset = 0x13c01008 - 0x13c00fe4 };
  enum { addr_offset = 0x13c01001- 0x13c00fe4 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("Otomate PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookOtomate;
    ConsoleOutput("Otomate PSP: INSERT");
    succ|=NewHook(hp, "Otomate PSP");
  }

  ConsoleOutput("Otomate PSP: leave");
  return succ;
}

/** 7/27/2014 jichi Intense.jp PSP engine, 0.9.8, 0.9.9,
 *  Though Otomate can work, it cannot work line by line.
 *
 *  Sample game: 寮�のサクリファイス work on 0.9.8 & 0.9.9
 *  This hook is only for intro graphic painting
 *
 *  Memory address is FIXED.
 *  Debug method: predict and breakpoint the memory address
 *
 *  There are two matches in the memory, and only one function accessing them.
 *  The memory is accessed by words.
 *
 *  The memory and hooked function is as follows.
 *
 *  09dfee77  88 c3 82 a2 95 a3 82 cc 89 9c 92 ea 82 c5 81 41  暗い淵の奥底で� *  09dfee87  92 e1 82 ad 81 41 8f ac 82 b3 82 ad 81 41 8b bf  低く、小さく〟�
 *  09dfee97  82 ad 81 42 2a 70 0a 82 b1 82 ea 82 cd 81 41 8c  く�p.これは、�
 *  09dfeea7  db 93 ae 81 63 81 48 2a 70 0a 82 c6 82 e0 82 b7  �動…p.ともす
 *  09dfeeb7  82 ea 82 ce 95 b7 82 ab 93 a6 82 b5 82 c4 82 b5  れ�聞き送�て� *  09dfeec7  82 dc 82 a2 82 bb 82 a4 82 c8 81 41 2a 70 0a 8f  まぁ�ぁ��p.・
 *  09dfeed7  ac 82 b3 82 ad 81 41 8e e3 81 58 82 b5 82 ad 81  �さく、弱、�く�
 *  09dfeee7  41 95 73 8a 6d 82 a9 82 c8 89 b9 81 42 00 00 00  a不確かな音�..
 *  09dfeef7  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *  09dfee07  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
 *
 *  13472227   90               nop
 *  13472228   77 0f            ja short 13472239
 *  1347222a   c705 a8aa1001 20>mov dword ptr ds:[0x110aaa8],0x884ce20
 *  13472234  -e9 cbdd16f0      jmp 035e0004
 *  13472239   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  1347223f   81e0 ffffff3f    and eax,0x3fffffff
 *  13472245   8bb0 30004007    mov esi,dword ptr ds:[eax+0x7400030]
 *  1347224b   8b3d 84a71001    mov edi,dword ptr ds:[0x110a784]
 *  13472251   81c7 01000000    add edi,0x1
 *  13472257   8bee             mov ebp,esi
 *  13472259   032d 84a71001    add ebp,dword ptr ds:[0x110a784]
 *  1347225f   8bc5             mov eax,ebp
 *  13472261   81e0 ffffff3f    and eax,0x3fffffff
 *  13472267   0fbe90 00004007  movsx edx,byte ptr ds:[eax+0x7400000]   ; jichi: hook here
 *  1347226e   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  13472274   81e0 ffffff3f    and eax,0x3fffffff
 *  1347227a   89b8 38004007    mov dword ptr ds:[eax+0x7400038],edi
 *  13472280   8bea             mov ebp,edx
 *  13472282   81e5 ff000000    and ebp,0xff
 *  13472288   81fa 0a000000    cmp edx,0xa
 *  1347228e   c705 70a71001 0a>mov dword ptr ds:[0x110a770],0xa
 *  13472298   8915 74a71001    mov dword ptr ds:[0x110a774],edx
 *  1347229e   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  134722a4   892d 7ca71001    mov dword ptr ds:[0x110a77c],ebp
 *  134722aa   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  134722b0   0f85 16000000    jnz 134722cc
 *  134722b6   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  134722bd   e9 02680000      jmp 13478ac4
 *  134722c2   01ec             add esp,ebp
 *  134722c4   ce               into
 *  134722c5   8408             test byte ptr ds:[eax],cl
 *  134722c7  -e9 57dd16f0      jmp 035e0023
 *  134722cc   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  134722d3   e9 0c000000      jmp 134722e4
 *  134722d8   0140 ce          add dword ptr ds:[eax-0x32],eax
 *  134722db   8408             test byte ptr ds:[eax],cl
 *  134722dd  -e9 41dd16f0      jmp 035e0023
 *  134722e2   90               nop
 *  134722e3   cc               int3
 */
// Read text from esi
static void SpecialPSPHookIntense(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  DWORD text = eax + hp->user_value;
  if (BYTE c = *(BYTE *)text) { // unsigned char
    *data = text;
    *len = ::LeadByteTable[c]; // 1 or 2
    //*split = regof(ecx, esp_base); // cause scenario text to split
    //*split = regof(edx, esp_base); // cause scenario text to split

    //*split = regof(ebx, esp_base); // works, but floating value
    *split = FIXED_SPLIT_VALUE * 3;
  }
}
bool InsertIntensePSPHook()
{
  ConsoleOutput("Intense PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 13472228   77 0f            ja short 13472239
    0xc7,0x05, XX8,                 // 1347222a   c705 a8aa1001 20>mov dword ptr ds:[0x110aaa8],0x884ce20
    0xe9, XX4,                      // 13472234  -e9 cbdd16f0      jmp 035e0004
    0x8b,0x05, XX4,                 // 13472239   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1347223f   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb0, XX4,                 // 13472245   8bb0 30004007    mov esi,dword ptr ds:[eax+0x7400030]
    0x8b,0x3d, XX4,                 // 1347224b   8b3d 84a71001    mov edi,dword ptr ds:[0x110a784]
    0x81,0xc7, 0x01,0x00,0x00,0x00, // 13472251   81c7 01000000    add edi,0x1
    0x8b,0xee,                      // 13472257   8bee             mov ebp,esi
    0x03,0x2d, XX4,                 // 13472259   032d 84a71001    add ebp,dword ptr ds:[0x110a784]
    0x8b,0xc5,                      // 1347225f   8bc5             mov eax,ebp
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13472261   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0x90, XX4,            // 13472267   0fbe90 00004007  movsx edx,byte ptr ds:[eax+0x7400000]   ; jichi: hook here
    0x8b,0x05, XX4,                 // 1347226e   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f  // 13472274   81e0 ffffff3f    and eax,0x3fffffff
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x13472267 - 0x13472228 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Intense PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookIntense;
    ConsoleOutput("Intense PSP: INSERT");
    succ|=NewHook(hp, "Intense PSP");
  }

  ConsoleOutput("Intense PSP: leave");
  return succ;
}

/** 7/26/2014 jichi Broccoli PSP engine, 0.9.8, 0.9.9
 *  Sample game: 明治東亰恋伽 (works on both 0.9.8, 0.9.9)
 *
 *  Memory address is FIXED.
 *  Debug method: breakpoint the memory address
 *
 *  The data is in (WORD)dl in bytes.
 *
 *  There are two text threads.
 *  Only one is correct.
 *
 *  13d26cab   cc               int3
 *  13d26cac   77 0f            ja short 13d26cbd
 *  13d26cae   c705 a8aa1001 24>mov dword ptr ds:[0x110aaa8],0x886a724
 *  13d26cb8  -e9 4793ccef      jmp 039f0004
 *  13d26cbd   8b35 dca71001    mov esi,dword ptr ds:[0x110a7dc]
 *  13d26cc3   8db6 60feffff    lea esi,dword ptr ds:[esi-0x1a0]
 *  13d26cc9   8b3d e4a71001    mov edi,dword ptr ds:[0x110a7e4]
 *  13d26ccf   8bc6             mov eax,esi
 *  13d26cd1   81e0 ffffff3f    and eax,0x3fffffff
 *  13d26cd7   89b8 9001c007    mov dword ptr ds:[eax+0x7c00190],edi
 *  13d26cdd   8b2d 80a71001    mov ebp,dword ptr ds:[0x110a780]
 *  13d26ce3   0fbfed           movsx ebp,bp
 *  13d26ce6   8bd6             mov edx,esi
 *  13d26ce8   8bce             mov ecx,esi
 *  13d26cea   03cd             add ecx,ebp
 *  13d26cec   8935 dca71001    mov dword ptr ds:[0x110a7dc],esi
 *  13d26cf2   33c0             xor eax,eax
 *  13d26cf4   3bd1             cmp edx,ecx
 *  13d26cf6   0f92c0           setb al
 *  13d26cf9   8bf0             mov esi,eax
 *  13d26cfb   81fe 00000000    cmp esi,0x0
 *  13d26d01   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  13d26d07   890d 74a71001    mov dword ptr ds:[0x110a774],ecx
 *  13d26d0d   892d 80a71001    mov dword ptr ds:[0x110a780],ebp
 *  13d26d13   8915 8ca71001    mov dword ptr ds:[0x110a78c],edx
 *  13d26d19   0f85 16000000    jnz 13d26d35
 *  13d26d1f   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  13d26d26   e9 b9000000      jmp 13d26de4
 *  13d26d2b   0158 a7          add dword ptr ds:[eax-0x59],ebx
 *  13d26d2e   8608             xchg byte ptr ds:[eax],cl
 *  13d26d30  -e9 ee92ccef      jmp 039f0023
 *  13d26d35   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  13d26d3c   e9 0b000000      jmp 13d26d4c
 *  13d26d41   0144a7 86        add dword ptr ds:[edi-0x7a],eax
 *  13d26d45   08e9             or cl,ch
 *  13d26d47   d892 ccef9077    fcom dword ptr ds:[edx+0x7790efcc]
 *  13d26d4d   0fc7             ???                                      ; unknown command
 *  13d26d4f   05 a8aa1001      add eax,0x110aaa8
 *  13d26d54   44               inc esp
 *  13d26d55   a7               cmps dword ptr ds:[esi],dword ptr es:[ed>
 *  13d26d56   8608             xchg byte ptr ds:[eax],cl
 *  13d26d58  -e9 a792ccef      jmp 039f0004
 *  13d26d5d   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  13d26d63   81e0 ffffff3f    and eax,0x3fffffff
 *  13d26d69   0fb6b0 0000c007  movzx esi,byte ptr ds:[eax+0x7c00000]
 *  13d26d70   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
 *  13d26d76   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13d26d79   8b05 8ca71001    mov eax,dword ptr ds:[0x110a78c]
 *  13d26d7f   81e0 ffffff3f    and eax,0x3fffffff
 *  13d26d85   8bd6             mov edx,esi
 *  13d26d87   8890 0000c007    mov byte ptr ds:[eax+0x7c00000],dl ; jichi: hook here, get byte from dl
 *  13d26d8d   8b2d 8ca71001    mov ebp,dword ptr ds:[0x110a78c]
 *  13d26d93   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  13d26d96   81fe 00000000    cmp esi,0x0
 *  13d26d9c   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  13d26da2   8935 88a71001    mov dword ptr ds:[0x110a788],esi
 *  13d26da8   892d 8ca71001    mov dword ptr ds:[0x110a78c],ebp
 *  13d26dae   0f84 16000000    je 13d26dca
 *  13d26db4   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  13d26dbb   e9 f48b0100      jmp 13d3f9b4
 *  13d26dc0   0138             add dword ptr ds:[eax],edi
 *  13d26dc2   a7               cmps dword ptr ds:[esi],dword ptr es:[ed>
 *  13d26dc3   8608             xchg byte ptr ds:[eax],cl
 *  13d26dc5  -e9 5992ccef      jmp 039f0023
 *  13d26dca   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  13d26dd1   e9 0e000000      jmp 13d26de4
 *  13d26dd6   0158 a7          add dword ptr ds:[eax-0x59],ebx
 *  13d26dd9   8608             xchg byte ptr ds:[eax],cl
 *  13d26ddb  -e9 4392ccef      jmp 039f0023
 *  13d26de0   90               nop
 *  13d26de1   cc               int3
 */

// New line character for Broccoli games is '^'
static inline bool _broccoligarbage_ch(char c) { return c == '^'; }

// Read text from dl
static void SpecialPSPHookBroccoli(hook_context *context,  HookParam *, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD text = context->edx; // edx address
  char c = *(LPCSTR)text;
  if (c && !_broccoligarbage_ch(c)) {
    *data = text;
    *len = 1;
    *split = context->ecx;
  }
}

bool InsertBroccoliPSPHook()
{
  ConsoleOutput("Broccoli PSP: enter");

  const BYTE bytes[] =  {
    0x0f,0xc7,                      // 13d26d4d   0fc7             ???                                      ; unknown command
    0x05, XX4,                      // 13d26d4f   05 a8aa1001      add eax,0x110aaa8
    0x44,                           // 13d26d54   44               inc esp
    0xa7,                           // 13d26d55   a7               cmps dword ptr ds:[esi],dword ptr es:[ed>
    0x86,0x08,                      // 13d26d56   8608             xchg byte ptr ds:[eax],cl
    0xe9, XX4,                      // 13d26d58  -e9 a792ccef      jmp 039f0004
    0x8b,0x05, XX4,                 // 13d26d5d   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
    // Following pattern is not sufficient
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13d26d63   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0, XX4,            // 13d26d69   0fb6b0 0000c007  movzx esi,byte ptr ds:[eax+0x7c00000]
    0x8b,0x3d, XX4,                 // 13d26d70   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
    0x8d,0x7f, 0x01,                // 13d26d76   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
    0x8b,0x05, XX4,                 // 13d26d79   8b05 8ca71001    mov eax,dword ptr ds:[0x110a78c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13d26d7f   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xd6,                      // 13d26d85   8bd6             mov edx,esi
    0x88,0x90, XX4,                 // 13d26d87   8890 0000c007    mov byte ptr ds:[eax+0x7c00000],dl ; jichi: hook here, get byte from dl
    0x8b,0x2d, XX4,                 // 13d26d8d   8b2d 8ca71001    mov ebp,dword ptr ds:[0x110a78c]
    0x8d,0x6d, 0x01,                // 13d26d93   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
    0x81,0xfe, 0x00,0x00,0x00,0x00  // 13d26d96   81fe 00000000    cmp esi,0x0
  };
  enum { addr_offset = 0x13d26d87 - 0x13d26d4d };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Broccoli PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookBroccoli;
    //GROWL_DWORD(hp.address);
    ConsoleOutput("Broccoli PSP: INSERT");
    succ|=NewHook(hp, "Broccoli PSP");
  }

  ConsoleOutput("Broccoli PSP: leave");
  return succ;
}

/** 9/5/2014 jichi felistella.co.jp PSP engine, 0.9.8, 0.9.9
 *  Sample game: Summon Night 5 0.9.8/0.9.9
 *
 *  Encoding: utf8
 *  Fixed memory addresses: two matches
 *
 *  Debug method: predict the text and add break-points.
 *
 *  There are two good functions
 *  The second is used as it contains fewer garbage
 *
 *  // Not used
 *  14081173   cc               int3
 *  14081174   77 0f            ja short 14081185
 *  14081176   c705 c84c1301 40>mov dword ptr ds:[0x1134cc8],0x8989540
 *  14081180  -e9 7feef5f3      jmp 07fe0004
 *  14081185   8b35 9c491301    mov esi,dword ptr ds:[0x113499c]
 *  1408118b   8bc6             mov eax,esi
 *  1408118d   81e0 ffffff3f    and eax,0x3fffffff
 *  14081193   0fb6b8 00000008  movzx edi,byte ptr ds:[eax+0x8000000] ; jichi: hook here
 *  1408119a   8bef             mov ebp,edi
 *  1408119c   81e5 80000000    and ebp,0x80
 *  140811a2   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  140811a5   81fd 00000000    cmp ebp,0x0
 *  140811ab   c705 90491301 00>mov dword ptr ds:[0x1134990],0x0
 *  140811b5   893d 9c491301    mov dword ptr ds:[0x113499c],edi
 *  140811bb   8935 a0491301    mov dword ptr ds:[0x11349a0],esi
 *  140811c1   892d a4491301    mov dword ptr ds:[0x11349a4],ebp
 *  140811c7   0f85 16000000    jnz 140811e3
 *  140811cd   832d e44c1301 06 sub dword ptr ds:[0x1134ce4],0x6
 *  140811d4   e9 fbf71200      jmp 141b09d4
 *  140811d9   01dc             add esp,ebx
 *  140811db   95               xchg eax,ebp
 *  140811dc   98               cwde
 *  140811dd   08e9             or cl,ch
 *  140811df   40               inc eax
 *
 *  // Used
 *  141be92f   cc               int3
 *  141be930   77 0f            ja short 141be941
 *  141be932   c705 c84c1301 0c>mov dword ptr ds:[0x1134cc8],0x8988f0c
 *  141be93c  -e9 c316e2f3      jmp 07fe0004
 *  141be941   8b35 98491301    mov esi,dword ptr ds:[0x1134998]
 *  141be947   8bc6             mov eax,esi
 *  141be949   81e0 ffffff3f    and eax,0x3fffffff
 *  141be94f   0fb6b8 00000008  movzx edi,byte ptr ds:[eax+0x8000000] ; jichi: hook here
 *  141be956   81ff 00000000    cmp edi,0x0
 *  141be95c   c705 90491301 00>mov dword ptr ds:[0x1134990],0x0
 *  141be966   893d 98491301    mov dword ptr ds:[0x1134998],edi
 *  141be96c   8935 9c491301    mov dword ptr ds:[0x113499c],esi
 *  141be972   0f85 16000000    jnz 141be98e
 *  141be978   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  141be97f   e9 e4020000      jmp 141bec68
 *  141be984   01748f 98        add dword ptr ds:[edi+ecx*4-0x68],esi
 *  141be988   08e9             or cl,ch
 *  141be98a   95               xchg eax,ebp
 *  141be98b   16               push ss
 *  141be98c  ^e2 f3            loopd short 141be981
 *  141be98e   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  141be995   e9 0e000000      jmp 141be9a8
 *  141be99a   011c8f           add dword ptr ds:[edi+ecx*4],ebx
 *  141be99d   98               cwde
 *  141be99e   08e9             or cl,ch
 *  141be9a0   7f 16            jg short 141be9b8
 *  141be9a2  ^e2 f3            loopd short 141be997
 *  141be9a4   90               nop
 *  141be9a5   cc               int3
 */
// Only split text when edi is eax
// The value of edi is either eax or 0
static void SpecialPSPHookFelistella(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (text) {
    *len = ::strlen(text); // utf8
    *data = (DWORD)text;

    DWORD edi = context->edi;
    *split = FIXED_SPLIT_VALUE * (edi == eax ? 4 : 5);
  }
}
bool InsertFelistellaPSPHook()
{
  ConsoleOutput("FELISTELLA PSP: enter");
  const BYTE bytes[] =  {
    //0xcc,                              // 141be92f   cc               int3
    0x77, 0x0f,                          // 141be930   77 0f            ja short 141be941
    0xc7,0x05, XX8,                      // 141be932   c705 c84c1301 0c>mov dword ptr ds:[0x1134cc8],0x8988f0c
    0xe9, XX4,                           // 141be93c  -e9 c316e2f3      jmp 07fe0004
    0x8b,0x35, XX4,                      // 141be941   8b35 98491301    mov esi,dword ptr ds:[0x1134998]
    0x8b,0xc6,                           // 141be947   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f,      // 141be949   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8, XX4,                 // 141be94f   0fb6b8 00000008  movzx edi,byte ptr ds:[eax+0x8000000] ; jichi: hook here
    0x81,0xff, 0x00,0x00,0x00,0x00,      // 141be956   81ff 00000000    cmp edi,0x0
    0xc7,0x05, XX4, 0x00,0x00,0x00,0x00, // 141be95c   c705 90491301 00>mov dword ptr ds:[0x1134990],0x0
    0x89,0x3d, XX4,                      // 141be966   893d 98491301    mov dword ptr ds:[0x1134998],edi
    0x89,0x35, XX4,                      // 141be96c   8935 9c491301    mov dword ptr ds:[0x113499c],esi
    0x0f,0x85, XX4,                      // 141be972   0f85 16000000    jnz 141be98e
    0x83,0x2d, XX4, 0x04,                // 141be978   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
    // Above is not sufficient
    0xe9, XX4,                           // 141be97f   e9 e4020000      jmp 141bec68
    0x01,0x74,0x8f, 0x98                 // 141be984   01748f 98        add dword ptr ds:[edi+ecx*4-0x68],esi
    //0x08,0xe9,                         // 141be988   08e9             or cl,ch
    // Below could be changed for different run
    //0x95,                              // 141be98a   95               xchg eax,ebp
    //0x16                               // 141be98b   16               push ss
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x141be94f - 0x141be930 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("FELISTELLA PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|CODEC_UTF8|USING_SPLIT|NO_CONTEXT; // Fix the split value to merge all threads
    //hp.text_fun = SpecialPSPHook;
    hp.text_fun = SpecialPSPHookFelistella;
    hp.offset=regoffset(eax);
    ConsoleOutput("FELISTELLA PSP: INSERT");
    succ|=NewHook(hp, "FELISTELLA PSP");
  }

  ConsoleOutput("FELISTELLA PSP: leave");
  return succ;
}

/** 7/13/2014 jichi alchemist-net.co.jp PSP engine, 0.9.8 only, not work on 0.9.9
 *  Sample game: your diary+ (moe-ydp.iso)
 *  The memory address is fixed.
 *  Note: This pattern seems to be common that not only exists in Alchemist games.
 *
 *  Not work on 0.9.9: Amnesia Crowd
 *
 *  Debug method: simply add hardware break points to the matched memory
 *
 *  PPSSPP 0.9.8, your diary+
 *  134076f2   cc               int3
 *  134076f3   cc               int3
 *  134076f4   77 0f            ja short 13407705
 *  134076f6   c705 a8aa1001 40>mov dword ptr ds:[0x110aaa8],0x8931040
 *  13407700  -e9 ff88f2f3      jmp 07330004
 *  13407705   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  1340770b   81e0 ffffff3f    and eax,0x3fffffff
 *  13407711   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]   // jichi: hook here
 *  13407718   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
 *  1340771e   8b2d 7ca71001    mov ebp,dword ptr ds:[0x110a77c]
 *  13407724   81c5 01000000    add ebp,0x1
 *  1340772a   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13407730   81e0 ffffff3f    and eax,0x3fffffff
 *  13407736   8bd6             mov edx,esi
 *  13407738   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl      // jichi: alternatively hook here
 *  1340773e   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
 *  13407744   81c2 01000000    add edx,0x1
 *  1340774a   8bcd             mov ecx,ebp
 *  1340774c   8935 88a71001    mov dword ptr ds:[0x110a788],esi
 *  13407752   8bf2             mov esi,edx
 *  13407754   813d 88a71001 00>cmp dword ptr ds:[0x110a788],0x0
 *  1340775e   893d 70a71001    mov dword ptr ds:[0x110a770],edi
 *  13407764   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  1340776a   890d 7ca71001    mov dword ptr ds:[0x110a77c],ecx
 *  13407770   8915 80a71001    mov dword ptr ds:[0x110a780],edx
 *  13407776   892d 84a71001    mov dword ptr ds:[0x110a784],ebp
 *  1340777c   0f85 16000000    jnz 13407798
 *  13407782   832d c4aa1001 08 sub dword ptr ds:[0x110aac4],0x8
 *  13407789   e9 ce000000      jmp 1340785c
 *  1340778e   017c10 93        add dword ptr ds:[eax+edx-0x6d],edi
 *  13407792   08e9             or cl,ch
 *  13407794   8b88 f2f3832d    mov ecx,dword ptr ds:[eax+0x2d83f3f2]
 *  1340779a   c4aa 100108e9    les ebp,fword ptr ds:[edx+0xe9080110]    ; modification of segment register
 *  134077a0   0c 00            or al,0x0
 *  134077a2   0000             add byte ptr ds:[eax],al
 *  134077a4   0160 10          add dword ptr ds:[eax+0x10],esp
 *  134077a7   93               xchg eax,ebx
 *  134077a8   08e9             or cl,ch
 *  134077aa  ^75 88            jnz short 13407734
 *  134077ac   f2:              prefix repne:                            ; superfluous prefix
 *  134077ad   f3:              prefix rep:                              ; superfluous prefix
 *  134077ae   90               nop
 *  134077af   cc               int3
 */

namespace { // unnamed

// Return true if the text is a garbage character
inline bool _alchemistgarbage_ch(char c)
{
  return c == '.' || c == '/'
      || c == '#' || c == ':' // garbage in alchemist2 hook
      || c >= '0' && c <= '9'
      || c >= 'A' && c <= 'z' // also ignore ASCII 91-96: [ \ ] ^ _ `
  ;
}

// Return true if the text is full of garbage characters
bool _alchemistgarbage(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
    if (!_alchemistgarbage_ch(*p))
      return false;
  return true;
}

// 7/20/2014 jichi: Trim Rejet garbage. Sample game: 月華繚乱ROMANCE
// Such as: #Pos[1,2]
inline bool _rejetgarbage_ch(char c)
{
  return c == '#' || c == ' ' || c == '[' || c == ']' || c == ','
      || c >= 'A' && c <= 'z' // also ignore ASCII 91-96: [ \ ] ^ _ `
      || c >= '0' && c <= '9';
}

bool _rejetgarbage(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
    if (!_rejetgarbage_ch(*p))
      return false;
  return true;
}

// Trim leading garbage
LPCSTR _rejetltrim(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  if (p)
    for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
      if (!_rejetgarbage_ch(*p))
        return p;
  return nullptr;
}

// Trim trailing garbage
size_t _rejetstrlen(LPCSTR text)
{
  if (!text)
    return 0;
  size_t len = ::strlen(text),
         ret = len;
  while (len && _rejetgarbage_ch(text[len - 1])) {
    len--;
    if (text[len] == '#') // in case trim UTF-8 trailing bytes
      ret = len;
  }
  return ret;
}

} // unnamed namespace

static void SpecialPSPHookAlchemist(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (*text && !_alchemistgarbage(text)) {
    text = _rejetltrim(text);
    *data = (DWORD)text;
    *len = _rejetstrlen(text);
    *split = context->ecx;
  }
}

bool InsertAlchemistPSPHook()
{
  ConsoleOutput("Alchemist PSP: enter");
  const BYTE bytes[] =  {
     //0xcc,                         // 134076f2   cc               int3
     //0xcc,                         // 134076f3   cc               int3
     0x77, 0x0f,                     // 134076f4   77 0f            ja short 13407705
     0xc7,0x05, XX8,                 // 134076f6   c705 a8aa1001 40>mov dword ptr ds:[0x110aaa8],0x8931040
     0xe9, XX4,                      // 13407700  -e9 ff88f2f3      jmp 07330004
     0x8b,0x05, XX4,                 // 13407705   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
     0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1340770b   81e0 ffffff3f    and eax,0x3fffffff
     0x0f,0xbe,0xb0, XX4,            // 13407711   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]   // jichi: hook here
     0x8b,0x3d, XX4,                 // 13407718   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
     0x8b,0x2d, XX4,                 // 1340771e   8b2d 7ca71001    mov ebp,dword ptr ds:[0x110a77c]
     0x81,0xc5, 0x01,0x00,0x00,0x00, // 13407724   81c5 01000000    add ebp,0x1
     0x8b,0x05, XX4,                 // 1340772a   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
     0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13407730   81e0 ffffff3f    and eax,0x3fffffff
     0x8b,0xd6,                      // 13407736   8bd6             mov edx,esi
     0x88,0x90 //, XX4               // 13407738   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl      // jichi: alternatively hook here
  };
  enum { memory_offset = 3 }; // 13407711   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = 0x13407711 - 0x134076f4 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("Alchemist PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialPSPHookAlchemist;
    hp.type = USING_STRING|NO_CONTEXT; // no context is needed to get rid of variant retaddr
    ConsoleOutput("Alchemist PSP: INSERT");
    succ|=NewHook(hp, "Alchemist PSP");
  }

  ConsoleOutput("Alchemist PSP: leave");
  return succ;
}

/** 8/12/2014 jichi Konami.jp PSP engine, 0.9.8, 0.9.9,
 *  Though Alchemist/Otomate can work, it has bad split that creates too many threads.
 *
 *  Sample game: 幻想水滸�紡がれし百年の�on 0.9.8, 0.9.9
 *
 *  Memory address is FIXED.
 *  But hardware accesses are looped.
 *  Debug method: predict and breakpoint the memory address
 *
 *  There are two matches in the memory.
 *  Three looped functions are as follows.
 *  I randomply picked the first one.
 *
 *  It cannot extract character names.
 *
 *  14178f73   cc               int3
 *  14178f74   77 0f            ja short 14178f85
 *  14178f76   c705 c84c1301 a4>mov dword ptr ds:[0x1134cc8],0x88129a4
 *  14178f80  -e9 7f7071ef      jmp 03890004
 *  14178f85   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
 *  14178f8b   81e0 ffffff3f    and eax,0x3fffffff
 *  14178f91   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here, loop
 *  14178f98   81fe 40000000    cmp esi,0x40
 *  14178f9e   8935 98491301    mov dword ptr ds:[0x1134998],esi
 *  14178fa4   c705 9c491301 40>mov dword ptr ds:[0x113499c],0x40
 *  14178fae   0f85 2f000000    jnz 14178fe3
 *  14178fb4   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
 *  14178fba   81e0 ffffff3f    and eax,0x3fffffff
 *  14178fc0   0fbeb0 01000008  movsx esi,byte ptr ds:[eax+0x8000001]
 *  14178fc7   8935 98491301    mov dword ptr ds:[0x1134998],esi
 *  14178fcd   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  14178fd4   c705 c84c1301 d0>mov dword ptr ds:[0x1134cc8],0x88129d0
 *  14178fde  -e9 407071ef      jmp 03890023
 *  14178fe3   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  14178fea   e9 0d000000      jmp 14178ffc
 *  14178fef   01b429 8108e92a  add dword ptr ds:[ecx+ebp+0x2ae90881],es>
 *  14178ff6   70 71            jo short 14179069
 *  14178ff8   ef               out dx,eax                               ; i/o command
 *  14178ff9   90               nop
 *  14178ffa   cc               int3
 *
 *  1417a18c   77 0f            ja short 1417a19d
 *  1417a18e   c705 c84c1301 78>mov dword ptr ds:[0x1134cc8],0x8818378
 *  1417a198  -e9 675e71ef      jmp 03890004
 *  1417a19d   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
 *  1417a1a3   81e0 ffffff3f    and eax,0x3fffffff
 *  1417a1a9   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here, loop
 *  1417a1b0   81fe 0a000000    cmp esi,0xa
 *  1417a1b6   8935 98491301    mov dword ptr ds:[0x1134998],esi
 *  1417a1bc   c705 9c491301 0a>mov dword ptr ds:[0x113499c],0xa
 *  1417a1c6   0f84 2e000000    je 1417a1fa
 *  1417a1cc   8b05 fc491301    mov eax,dword ptr ds:[0x11349fc]
 *  1417a1d2   81e0 ffffff3f    and eax,0x3fffffff
 *  1417a1d8   8bb0 18000008    mov esi,dword ptr ds:[eax+0x8000018]
 *  1417a1de   8935 98491301    mov dword ptr ds:[0x1134998],esi
 *  1417a1e4   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  1417a1eb   e9 24000000      jmp 1417a214
 *  1417a1f0   01b0 838108e9    add dword ptr ds:[eax+0xe9088183],esi
 *  1417a1f6   295e 71          sub dword ptr ds:[esi+0x71],ebx
 *  1417a1f9   ef               out dx,eax                               ; i/o command
 *  1417a1fa   832d e44c1301 04 sub dword ptr ds:[0x1134ce4],0x4
 *  1417a201   e9 1e660000      jmp 14180824
 *  1417a206   0188 838108e9    add dword ptr ds:[eax+0xe9088183],ecx
 *  1417a20c   135e 71          adc ebx,dword ptr ds:[esi+0x71]
 *  1417a20f   ef               out dx,eax                               ; i/o command
 *  1417a210   90               nop
 *  1417a211   cc               int3
 *  1417a212   cc               int3
 *
 *  1417a303   90               nop
 *  1417a304   77 0f            ja short 1417a315
 *  1417a306   c705 c84c1301 48>mov dword ptr ds:[0x1134cc8],0x8818448
 *  1417a310  -e9 ef5c71ef      jmp 03890004
 *  1417a315   8b35 dc491301    mov esi,dword ptr ds:[0x11349dc]
 *  1417a31b   8b3d 98491301    mov edi,dword ptr ds:[0x1134998]
 *  1417a321   33c0             xor eax,eax
 *  1417a323   3bf7             cmp esi,edi
 *  1417a325   0f9cc0           setl al
 *  1417a328   8bf8             mov edi,eax
 *  1417a32a   81ff 00000000    cmp edi,0x0
 *  1417a330   893d 98491301    mov dword ptr ds:[0x1134998],edi
 *  1417a336   0f84 2f000000    je 1417a36b
 *  1417a33c   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
 *  1417a342   81e0 ffffff3f    and eax,0x3fffffff
 *  1417a348   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here, loop
 *  1417a34f   8935 98491301    mov dword ptr ds:[0x1134998],esi
 *  1417a355   832d e44c1301 03 sub dword ptr ds:[0x1134ce4],0x3
 *  1417a35c   e9 23000000      jmp 1417a384
 *  1417a361   018484 8108e9b8  add dword ptr ss:[esp+eax*4+0xb8e90881],>
 *  1417a368   5c               pop esp
 *  1417a369  ^71 ef            jno short 1417a35a
 *  1417a36b   832d e44c1301 03 sub dword ptr ds:[0x1134ce4],0x3
 *  1417a372   c705 c84c1301 54>mov dword ptr ds:[0x1134cc8],0x8818454
 *  1417a37c  -e9 a25c71ef      jmp 03890023
 *  1417a381   90               nop
 *  1417a382   cc               int3
 */
// Read text from looped address word by word
// Use reverse search to avoid looping issue assume the text is at fixed address.
static void SpecialPSPHookKonami(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  //static LPCSTR lasttext; // this value should be the same for the same game
  static size_t lastsize;

  DWORD eax = context->eax;
  LPCSTR cur = LPCSTR(eax + hp->user_value);
  if (!*cur)
    return;

  LPCSTR text = reverse_search_begin(cur);
  if (!text)
    return;
  //if (lasttext != text) {
  //  lasttext = text;
  //  lastsize = 0; // reset last size
  //}

  size_t size = ::strlen(text);
  if (size == lastsize)
    return;

  *len = lastsize = size;
  *data = (DWORD)text;

  *split = context->ebx; // ecx changes for each character, ebx is an address, edx is stable, but very large
}
bool InsertKonamiPSPHook()
{
  ConsoleOutput("KONAMI PSP: enter");
  const BYTE bytes[] =  {
                                         // 14178f73   cc               int3
    0x77, 0x0f,                          // 14178f74   77 0f            ja short 14178f85
    0xc7,0x05, XX8,                      // 14178f76   c705 c84c1301 a4>mov dword ptr ds:[0x1134cc8],0x88129a4
    0xe9, XX4,                           // 14178f80  -e9 7f7071ef      jmp 03890004
    0x8b,0x05, XX4,                      // 14178f85   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
    0x81,0xe0, 0xff,0xff,0xff,0x3f,      // 14178f8b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,                 // 14178f91   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here, loop
    0x81,0xfe, 0x40,0x00,0x00,0x00,      // 14178f98   81fe 40000000    cmp esi,0x40
    0x89,0x35 //, XX4,                      // 14178f9e   8935 98491301    mov dword ptr ds:[0x1134998],esi
    //0xc7,0x05, XX4, 0x40,0x00,0x00,0x00,  // 14178fa4   c705 9c491301 40>mov dword ptr ds:[0x113499c],0x40
    //0x0f,0x85, 0x2f,0x00,0x00,0x00,0x00,  // 14178fae   0f85 2f000000    jnz 14178fe3
    //0x8b,0x05, XX4                        // 14178fb4   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x14178f91 - 0x14178f74 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("KONAMI PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookKonami;
    ConsoleOutput("KONAMI PSP: INSERT");
    succ|=NewHook(hp, "KONAMI PSP");
  }

  ConsoleOutput("KONAMI PSP: leave");
  return succ;
}
/** 7/13/2014 jichi 5pb.jp PSP engine, 0.9.8, 0.9.9
 *  Sample game: STEINS;GATE
 *
 *  FIXME: The current pattern could crash VNR
 *
 *  Note: searching after 0x15000000 would found a wrong address on 0.9.9.
 *  Hooking to it would crash PPSSPP.
 *
 *  Float memory addresses: two matches
 *
 *  Debug method: precompute memory address and set break points, then navigate to that scene
 *
 *  Attach to this function for wrong game might cause BEX (buffer overflow) exception.
 *
 *  135752c7   90               nop
 *  135752c8   77 0f            ja short 135752d9
 *  135752ca   c705 a8aa1001 d4>mov dword ptr ds:[0x110aaa8],0x8888ed4
 *  135752d4  -e9 2badf3ef      jmp 034b0004
 *  135752d9   8b35 dca71001    mov esi,dword ptr ds:[0x110a7dc]
 *  135752df   8d76 a0          lea esi,dword ptr ds:[esi-0x60]
 *  135752e2   8b3d e4a71001    mov edi,dword ptr ds:[0x110a7e4]
 *  135752e8   8bc6             mov eax,esi
 *  135752ea   81e0 ffffff3f    and eax,0x3fffffff
 *  135752f0   89b8 1c004007    mov dword ptr ds:[eax+0x740001c],edi
 *  135752f6   8b2d bca71001    mov ebp,dword ptr ds:[0x110a7bc]
 *  135752fc   8bc6             mov eax,esi
 *  135752fe   81e0 ffffff3f    and eax,0x3fffffff
 *  13575304   89a8 18004007    mov dword ptr ds:[eax+0x7400018],ebp
 *  1357530a   8b15 b8a71001    mov edx,dword ptr ds:[0x110a7b8]
 *  13575310   8bc6             mov eax,esi
 *  13575312   81e0 ffffff3f    and eax,0x3fffffff
 *  13575318   8990 14004007    mov dword ptr ds:[eax+0x7400014],edx
 *  1357531e   8b0d b4a71001    mov ecx,dword ptr ds:[0x110a7b4]
 *  13575324   8bc6             mov eax,esi
 *  13575326   81e0 ffffff3f    and eax,0x3fffffff
 *  1357532c   8988 10004007    mov dword ptr ds:[eax+0x7400010],ecx
 *  13575332   8b3d b0a71001    mov edi,dword ptr ds:[0x110a7b0]
 *  13575338   8bc6             mov eax,esi
 *  1357533a   81e0 ffffff3f    and eax,0x3fffffff
 *  13575340   89b8 0c004007    mov dword ptr ds:[eax+0x740000c],edi
 *  13575346   8b3d aca71001    mov edi,dword ptr ds:[0x110a7ac]
 *  1357534c   8bc6             mov eax,esi
 *  1357534e   81e0 ffffff3f    and eax,0x3fffffff
 *  13575354   89b8 08004007    mov dword ptr ds:[eax+0x7400008],edi
 *  1357535a   8b3d a8a71001    mov edi,dword ptr ds:[0x110a7a8]
 *  13575360   8bc6             mov eax,esi
 *  13575362   81e0 ffffff3f    and eax,0x3fffffff
 *  13575368   89b8 04004007    mov dword ptr ds:[eax+0x7400004],edi
 *  1357536e   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
 *  13575374   8935 dca71001    mov dword ptr ds:[0x110a7dc],esi
 *  1357537a   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  13575380   81e0 ffffff3f    and eax,0x3fffffff
 *  13575386   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  1357538d   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13575393   8b35 80a71001    mov esi,dword ptr ds:[0x110a780]
 *  13575399   8935 b0a71001    mov dword ptr ds:[0x110a7b0],esi
 *  1357539f   8b35 84a71001    mov esi,dword ptr ds:[0x110a784]
 *  135753a5   8b0d 7ca71001    mov ecx,dword ptr ds:[0x110a77c]
 *  135753ab   813d 78a71001 00>cmp dword ptr ds:[0x110a778],0x0
 *  135753b5   c705 a8a71001 00>mov dword ptr ds:[0x110a7a8],0x0
 *  135753bf   8935 aca71001    mov dword ptr ds:[0x110a7ac],esi
 *  135753c5   890d b4a71001    mov dword ptr ds:[0x110a7b4],ecx
 *  135753cb   8915 b8a71001    mov dword ptr ds:[0x110a7b8],edx
 *  135753d1   0f85 16000000    jnz 135753ed
 *  135753d7   832d c4aa1001 0f sub dword ptr ds:[0x110aac4],0xf
 *  135753de   e9 e5010000      jmp 135755c8
 *  135753e3   01f0             add eax,esi
 *  135753e5   90               nop
 *  135753e6   8808             mov byte ptr ds:[eax],cl
 *  135753e8  -e9 36acf3ef      jmp 034b0023
 *  135753ed   832d c4aa1001 0f sub dword ptr ds:[0x110aac4],0xf
 *  135753f4   e9 0b000000      jmp 13575404
 *  135753f9   0110             add dword ptr ds:[eax],edx
 *  135753fb   8f               ???                                      ; unknown command
 *  135753fc   8808             mov byte ptr ds:[eax],cl
 *  135753fe  -e9 20acf3ef      jmp 034b0023
 *  13575403   90               nop
 *  13575404   77 0f            ja short 13575415
 *  13575406   c705 a8aa1001 10>mov dword ptr ds:[0x110aaa8],0x8888f10
 *  13575410  -e9 efabf3ef      jmp 034b0004
 *  13575415   8b35 a8a71001    mov esi,dword ptr ds:[0x110a7a8]
 *  1357541b   33c0             xor eax,eax
 *  1357541d   3b35 b0a71001    cmp esi,dword ptr ds:[0x110a7b0]
 *  13575423   0f9cc0           setl al
 *  13575426   8bf8             mov edi,eax
 *  13575428   81ff 00000000    cmp edi,0x0
 *  1357542e   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  13575434   0f84 22000000    je 1357545c
 *  1357543a   8b35 b4a71001    mov esi,dword ptr ds:[0x110a7b4]
 *  13575440   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13575446   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  1357544d   c705 a8aa1001 2c>mov dword ptr ds:[0x110aaa8],0x8888f2c
 *  13575457  -e9 c7abf3ef      jmp 034b0023
 *  1357545c   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  13575463   e9 0c000000      jmp 13575474
 *  13575468   011c8f           add dword ptr ds:[edi+ecx*4],ebx
 *  1357546b   8808             mov byte ptr ds:[eax],cl
 *  1357546d  -e9 b1abf3ef      jmp 034b0023
 *  13575472   90               nop
 *  13575473   cc               int3
 *  13575474   77 0f            ja short 13575485
 *  13575476   c705 a8aa1001 1c>mov dword ptr ds:[0x110aaa8],0x8888f1c
 *  13575480  -e9 7fabf3ef      jmp 034b0004
 *  13575485   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  1357548b   8b05 b8a71001    mov eax,dword ptr ds:[0x110a7b8]
 *  13575491   81e0 ffffff3f    and eax,0x3fffffff
 *  13575497   8bd6             mov edx,esi
 *  13575499   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl
 *  1357549f   8b3d b4a71001    mov edi,dword ptr ds:[0x110a7b4]
 *  135754a5   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  135754a8   8b2d b8a71001    mov ebp,dword ptr ds:[0x110a7b8]
 *  135754ae   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  135754b1   813d 68a71001 00>cmp dword ptr ds:[0x110a768],0x0
 *  135754bb   893d b4a71001    mov dword ptr ds:[0x110a7b4],edi
 *  135754c1   892d b8a71001    mov dword ptr ds:[0x110a7b8],ebp
 *  135754c7   0f85 16000000    jnz 135754e3
 *  135754cd   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  135754d4   e9 23000000      jmp 135754fc
 *  135754d9   01e4             add esp,esp
 *  135754db   90               nop
 *  135754dc   8808             mov byte ptr ds:[eax],cl
 *  135754de  -e9 40abf3ef      jmp 034b0023
 *  135754e3   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  135754ea   c705 a8aa1001 2c>mov dword ptr ds:[0x110aaa8],0x8888f2c
 *  135754f4  -e9 2aabf3ef      jmp 034b0023
 *  135754f9   90               nop
 *  135754fa   cc               int3
 *  135754fb   cc               int3
 */
namespace { // unnamed

// Characters to ignore: [%0-9A-Z]
inline bool _5pbgarbage_ch(char c)
{ return c == '%' || c >= 'A' && c <= 'Z' || c >= '0' && c <= '9'; }

// Trim leading garbage
LPCSTR _5pbltrim(LPCSTR p)
{
  enum { MAX_LENGTH = VNR_TEXT_CAPACITY };
  if (p)
    for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
      if (!_5pbgarbage_ch(*p))
        return p;
  return nullptr;
}

// Trim trailing garbage
size_t _5pbstrlen(LPCSTR text)
{
  if (!text)
    return 0;
  size_t len = ::strlen(text),
         ret = len;
  while (len && _5pbgarbage_ch(text[len - 1])) {
    len--;
    if (text[len] == '%') // in case trim UTF-8 trailing bytes
      ret = len;
  }
  return ret;
}

} // unnamed namespace

static void SpecialPSPHook5pb(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (*text) {
    text = _5pbltrim(text);
    *data = (DWORD)text;
    *len = _5pbstrlen(text);
    *split = context->ecx;
    //*split = FIXED_SPLIT_VALUE; // there is only one thread, no split used
  }
}

bool Insert5pbPSPHook()
{
  ConsoleOutput("5pb PSP: enter");

  const BYTE bytes[] =  {
    //0x90,                         // 135752c7   90               nop
    0x77, 0x0f,                     // 135752c8   77 0f            ja short 135752d9
    0xc7,0x05, XX8,                 // 135752ca   c705 a8aa1001 d4>mov dword ptr ds:[0x110aaa8],0x8888ed4
    0xe9, XX4,                      // 135752d4  -e9 2badf3ef      jmp 034b0004
    0x8b,0x35, XX4,                 // 135752d9   8b35 dca71001    mov esi,dword ptr ds:[0x110a7dc]
    0x8d,0x76, 0xa0,                // 135752df   8d76 a0          lea esi,dword ptr ds:[esi-0x60]
    0x8b,0x3d, XX4,                 // 135752e2   8b3d e4a71001    mov edi,dword ptr ds:[0x110a7e4]
    0x8b,0xc6,                      // 135752e8   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 135752ea   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb8, XX4,                 // 135752f0   89b8 1c004007    mov dword ptr ds:[eax+0x740001c],edi
    0x8b,0x2d, XX4,                 // 135752f6   8b2d bca71001    mov ebp,dword ptr ds:[0x110a7bc]
    0x8b,0xc6,                      // 135752fc   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 135752fe   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xa8, XX4,                 // 13575304   89a8 18004007    mov dword ptr ds:[eax+0x7400018],ebp
    0x8b,0x15, XX4,                 // 1357530a   8b15 b8a71001    mov edx,dword ptr ds:[0x110a7b8]
    0x8b,0xc6,                      // 13575310   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13575312   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0x90, XX4,                 // 13575318   8990 14004007    mov dword ptr ds:[eax+0x7400014],edx
    0x8b,0x0d, XX4,                 // 1357531e   8b0d b4a71001    mov ecx,dword ptr ds:[0x110a7b4]
    0x8b,0xc6,                      // 13575324   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13575326   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0x88, XX4,                 // 1357532c   8988 10004007    mov dword ptr ds:[eax+0x7400010],ecx
    0x8b,0x3d, XX4,                 // 13575332   8b3d b0a71001    mov edi,dword ptr ds:[0x110a7b0]
    0x8b,0xc6,                      // 13575338   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1357533a   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb8, XX4,                 // 13575340   89b8 0c004007    mov dword ptr ds:[eax+0x740000c],edi
    0x8b,0x3d, XX4,                 // 13575346   8b3d aca71001    mov edi,dword ptr ds:[0x110a7ac]
    0x8b,0xc6,                      // 1357534c   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1357534e   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb8, XX4,                 // 13575354   89b8 08004007    mov dword ptr ds:[eax+0x7400008],edi
    0x8b,0x3d, XX4,                 // 1357535a   8b3d a8a71001    mov edi,dword ptr ds:[0x110a7a8]
    0x8b,0xc6,                      // 13575360   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13575362   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb8, XX4,                 // 13575368   89b8 04004007    mov dword ptr ds:[eax+0x7400004],edi
    0x8b,0x15, XX4,                 // 1357536e   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
    0x89,0x35, XX4,                 // 13575374   8935 dca71001    mov dword ptr ds:[0x110a7dc],esi
    0x8b,0x05, XX4,                 // 1357537a   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13575380   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0 //, XX4          // 13575386   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
  };
  enum { memory_offset = 3 }; // 13575386   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = sizeof(bytes) - memory_offset };

  enum : DWORD { start = MemDbg::MappedMemoryStartAddress };
  DWORD stop = PPSSPP_VERSION[1] == 9 && PPSSPP_VERSION[2] == 8 ? MemDbg::MemoryStopAddress : 0x15000000;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes), start, stop);
  //GROWL_DWORD(addr);
  auto succ=false;
  if (!addr)
    ConsoleOutput("5pb PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialPSPHook5pb;
    hp.type = USING_STRING|NO_CONTEXT; // no context is needed to get rid of variant retaddr
    ConsoleOutput("5pb PSP: INSERT");
    succ|=NewHook(hp, "5pb PSP");
  }

  ConsoleOutput("5pb PSP: leave");
  return succ;
}

/** 7/19/2014 jichi kid-game.co.jp PSP engine, 0,9.8, 0.9.9
 *  Sample game: Monochrome
 *
 *  Note: sceFontGetCharInfo, sceFontGetCharGlyphImage_Clip also works
 *
 *  Debug method: breakpoint the memory address
 *  There are two matched memory address to the current text
 *
 *  == Second run ==
 *  13973a7b   90               nop
 *  13973a7c   77 0f            ja short 13973a8d
 *  13973a7e   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x885c290
 *  13973a88  -e9 77c5ecef      jmp 03840004
 *  13973a8d   8b05 90a71001    mov eax,dword ptr ds:[0x110a790]
 *  13973a93   81e0 ffffff3f    and eax,0x3fffffff
 *  13973a99   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000]
 *  13973aa0   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13973aa6   81e0 ffffff3f    and eax,0x3fffffff
 *  13973aac   0fb6b8 00008007  movzx edi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  13973ab3   81fe 00000000    cmp esi,0x0
 *  13973ab9   c705 8ca71001 00>mov dword ptr ds:[0x110a78c],0x0
 *  13973ac3   893d 9ca71001    mov dword ptr ds:[0x110a79c],edi
 *  13973ac9   8935 a0a71001    mov dword ptr ds:[0x110a7a0],esi
 *  13973acf   0f85 16000000    jnz 13973aeb
 *  13973ad5   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  13973adc   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x885c2d0
 *  13973ae6  -e9 38c5ecef      jmp 03840023
 *  13973aeb   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  13973af2   e9 0d000000      jmp 13973b04
 *  13973af7   01a0 c28508e9    add dword ptr ds:[eax+0xe90885c2],esp
 *  13973afd   22c5             and al,ch
 *  13973aff   ec               in al,dx                                 ; i/o command
 *  13973b00   ef               out dx,eax                               ; i/o command
 *  13973b01   90               nop
 *  13973b02   cc               int3
 *  13973b03   cc               int3
 *
 *  == First run ==
 *  1087394a   cc               int3
 *  1087394b   cc               int3
 *  1087394c   77 0f            ja short 1087395d
 *  1087394e   c705 a8aa1001 78>mov dword ptr ds:[0x110aaa8],0x885c278
 *  10873958  -e9 a7c6bff2      jmp 03470004
 *  1087395d   8b35 80d0da12    mov esi,dword ptr ds:[0x12dad080]
 *  10873963   8bc6             mov eax,esi
 *  10873965   81e0 ffffff3f    and eax,0x3fffffff
 *  1087396b   8bb8 0000000a    mov edi,dword ptr ds:[eax+0xa000000]
 *  10873971   81ff 00000000    cmp edi,0x0
 *  10873977   c705 70a71001 00>mov dword ptr ds:[0x110a770],0x8db0000
 *  10873981   c705 74a71001 00>mov dword ptr ds:[0x110a774],0x0
 *  1087398b   893d 90a71001    mov dword ptr ds:[0x110a790],edi
 *  10873991   8935 94a71001    mov dword ptr ds:[0x110a794],esi
 *  10873997   c705 98a71001 00>mov dword ptr ds:[0x110a798],0x0
 *  108739a1   0f85 16000000    jnz 108739bd
 *  108739a7   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  108739ae   e9 75c20100      jmp 1088fc28
 *  108739b3   0148 c3          add dword ptr ds:[eax-0x3d],ecx
 *  108739b6   8508             test dword ptr ds:[eax],ecx
 *  108739b8  -e9 66c6bff2      jmp 03470023
 *  108739bd   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  108739c4   e9 0b000000      jmp 108739d4
 *  108739c9   0190 c28508e9    add dword ptr ds:[eax+0xe90885c2],edx
 *  108739cf   50               push eax
 *  108739d0   c6               ???                                      ; unknown command
 *  108739d1   bf f290770f      mov edi,0xf7790f2
 *  108739d6   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x885c290
 *  108739e0  -e9 1fc6bff2      jmp 03470004
 *  108739e5   8b05 90a71001    mov eax,dword ptr ds:[0x110a790]
 *  108739eb   81e0 ffffff3f    and eax,0x3fffffff
 *  108739f1   0fb6b0 0000000a  movzx esi,byte ptr ds:[eax+0xa000000] ; jichi: hook here
 *  108739f8   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  108739fe   81e0 ffffff3f    and eax,0x3fffffff
 *  10873a04   0fb6b8 0000000a  movzx edi,byte ptr ds:[eax+0xa000000] ; jichi: hook here
 *  10873a0b   81fe 00000000    cmp esi,0x0
 *  10873a11   c705 8ca71001 00>mov dword ptr ds:[0x110a78c],0x0
 *  10873a1b   893d 9ca71001    mov dword ptr ds:[0x110a79c],edi
 *  10873a21   8935 a0a71001    mov dword ptr ds:[0x110a7a0],esi
 *  10873a27   0f85 16000000    jnz 10873a43
 *  10873a2d   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  10873a34   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x885c2d0
 *  10873a3e  -e9 e0c5bff2      jmp 03470023
 *  10873a43   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  10873a4a   e9 0d000000      jmp 10873a5c
 *  10873a4f   01a0 c28508e9    add dword ptr ds:[eax+0xe90885c2],esp
 *  10873a55   ca c5bf          retf 0xbfc5                              ; far return
 *  10873a58   f2:              prefix repne:                            ; superfluous prefix
 *  10873a59   90               nop
 *  10873a5a   cc               int3
 *  10873a5b   cc               int3
 */
static void SpecialPSPHookKid(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  static LPCSTR lasttext; // Prevent reading the same address multiple times
  if (text != lasttext && *text) {
    lasttext = text;
    text = _5pbltrim(text);
    *data = (DWORD)text;
    *len = _5pbstrlen(text);
    *split = context->ecx;
  }
}

bool InsertKidPSPHook()
{
  ConsoleOutput("KID PSP: enter");

  const BYTE bytes[] =  {
    //0x90,                           // 13973a7b   90               nop
    0x77, 0x0f,                     // 13973a7c   77 0f            ja short 13973a8d
    0xc7,0x05, XX8,                 // 13973a7e   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x885c290
    0xe9, XX4,                      // 13973a88  -e9 77c5ecef      jmp 03840004
    0x8b,0x05, XX4,                 // 13973a8d   8b05 90a71001    mov eax,dword ptr ds:[0x110a790]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13973a93   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0, XX4,            // 13973a99   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000]
    0x8b,0x05, XX4,                 // 13973aa0   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13973aa6   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb8, XX4,            // 13973aac   0fb6b8 00008007  movzx edi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
    0x81,0xfe, 0x00,0x00,0x00,0x00  // 13973ab3   81fe 00000000    cmp esi,0x0
  };
  enum { memory_offset = 3 }; // 13973aac   0fb6b8 00008007  movzx edi,byte ptr ds:[eax+0x7800000]
  enum { addr_offset = 0x13973aac - 0x13973a7c };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("KID PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialPSPHookKid;
    hp.type = USING_STRING|NO_CONTEXT; // no context is needed to get rid of variant retaddr

    //HookParam hp;
    //hp.address = addr + addr_offset;
    //hp.user_value = *(DWORD *)(hp.address + memory_offset);
    //hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT; // Fix the split value to merge all threads
    //hp.offset=regoffset(eax);
    //hp.split = regoffset(ecx);
    //hp.text_fun = SpecialPSPHook;

    ConsoleOutput("KID PSP: INSERT");
    succ|=NewHook(hp, "KID PSP");
  }

  ConsoleOutput("KID PSP: leave");
  return succ;
}

/** 7/13/2014 jichi imageepoch.co.jp PSP engine, 0.9.8, 0.9.9
 *  Sample game: BLACK�OCK SHOOTER
 *
 *  Float memory addresses: two matches, UTF-8
 *
 *  7/29/2014: seems to work on 0.9.9
 *
 *  Debug method: find current sentence, then find next sentence in the memory
 *  and add break-points
 *
 *  1346d34b   f0:90            lock nop                                 ; lock prefix is not allowed
 *  1346d34d   cc               int3
 *  1346d34e   cc               int3
 *  1346d34f   cc               int3
 *  1346d350   77 0f            ja short 1346d361
 *  1346d352   c705 a8aa1001 e4>mov dword ptr ds:[0x110aaa8],0x89609e4
 *  1346d35c  -e9 a32c27f0      jmp 036e0004
 *  1346d361   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  1346d367   81e0 ffffff3f    and eax,0x3fffffff
 *  1346d36d   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: or hook here
 *  1346d373   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
 *  1346d379   8bc6             mov eax,esi
 *  1346d37b   81e0 ffffff3f    and eax,0x3fffffff
 *  1346d381   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  1346d388   8d56 01          lea edx,dword ptr ds:[esi+0x1]
 *  1346d38b   8bc5             mov eax,ebp
 *  1346d38d   0fbec8           movsx ecx,al
 *  1346d390   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  1346d396   8bf5             mov esi,ebp
 *  1346d398   81f9 00000000    cmp ecx,0x0
 *  1346d39e   892d 74a71001    mov dword ptr ds:[0x110a774],ebp
 *  1346d3a4   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  1346d3aa   8915 7ca71001    mov dword ptr ds:[0x110a77c],edx
 *  1346d3b0   890d 80a71001    mov dword ptr ds:[0x110a780],ecx
 *  1346d3b6   893d 84a71001    mov dword ptr ds:[0x110a784],edi
 *  1346d3bc   0f8d 16000000    jge 1346d3d8
 *  1346d3c2   832d c4aa1001 07 sub dword ptr ds:[0x110aac4],0x7
 *  1346d3c9   e9 22000000      jmp 1346d3f0
 *  1346d3ce   010c0a           add dword ptr ds:[edx+ecx],ecx
 *  1346d3d1   96               xchg eax,esi
 *  1346d3d2   08e9             or cl,ch
 *  1346d3d4   4b               dec ebx
 *  1346d3d5   2c 27            sub al,0x27
 *  1346d3d7   f0:832d c4aa1001>lock sub dword ptr ds:[0x110aac4],0x7    ; lock prefix
 *  1346d3df   e9 bc380000      jmp 13470ca0
 *  1346d3e4   0100             add dword ptr ds:[eax],eax
 *  1346d3e6   0a96 08e9352c    or dl,byte ptr ds:[esi+0x2c35e908]
 *  1346d3ec   27               daa
 *  1346d3ed   f0:90            lock nop                                 ; lock prefix is not allowed
 *  1346d3ef   cc               int3
 */
static void SpecialPSPHookImageepoch(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  // 7/25/2014: I tried using uniquemap to eliminate duplication, which does not work
  DWORD eax = context->eax;
  DWORD text = eax + hp->user_value;
  static DWORD lasttext; // Prevent reading the same address multiple times
  if (text != lasttext && *(LPCSTR)text) {
    *data = lasttext = text;
    *len = ::strlen((LPCSTR)text); // UTF-8 is null-terminated
    *split = context->ecx; // use ecx = "this" to split?
  }
}

bool InsertImageepochPSPHook()
{
  ConsoleOutput("Imageepoch PSP: enter");

  const BYTE bytes[] =  {
    //0xcc,                         // 1346d34f   cc               int3
    0x77, 0x0f,                     // 1346d350   77 0f            ja short 1346d361
    0xc7,0x05, XX8,                 // 1346d352   c705 a8aa1001 e4>mov dword ptr ds:[0x110aaa8],0x89609e4
    0xe9, XX4,                      // 1346d35c  -e9 a32c27f0      jmp 036e0004
    0x8b,0x05, XX4,                 // 1346d361   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346d367   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb0, XX4,                 // 1346d36d   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: or hook here
    0x8b,0x3d, XX4,                 // 1346d373   8b3d 78a71001    mov edi,dword ptr ds:[0x110a778]
    0x8b,0xc6,                      // 1346d379   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1346d37b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xa8, XX4,            // 1346d381   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000] ; jichi: hook here
    0x8d,0x56, 0x01,                // 1346d388   8d56 01          lea edx,dword ptr ds:[esi+0x1]
    0x8b,0xc5,                      // 1346d38b   8bc5             mov eax,ebp
    0x0f,0xbe,0xc8                  // 1346d38d   0fbec8           movsx ecx,al
  };
  enum { memory_offset = 3 }; // 1346d381   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000]
  enum { addr_offset = 0x1346d381 - 0x1346d350 };
  //enum { addr_offset = sizeof(bytes) - memory_offset };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Imageepoch PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT; // UTF-8, though
    hp.offset=regoffset(eax);
    hp.split = regoffset(ecx);
    //hp.text_fun = SpecialPSPHook;
    hp.text_fun = SpecialPSPHookImageepoch; // since this function is common, use its own static lasttext for HPF_IgnoreSameAddress
    ConsoleOutput("Imageepoch PSP: INSERT");
    succ|=NewHook(hp, "Imageepoch PSP");
  }

  ConsoleOutput("Imageepoch PSP: leave");
  return succ;
}

/** 7/20/2014 jichi alchemist-net.co.jp PSP engine, 0.9.8, 0.9.9
 *  An alternative alchemist hook for old alchemist games.
 *  Sample game: のーふぁ�と (No Fate)
 *  The memory address is fixed.
 *
 *  Also work on 0.9.9 Otoboku PSP
 *
 *  Debug method: simply add hardware break points to the matched memory
 *
 *  Two candidate functions are seems OK.
 *
 *  Instruction pattern: 81e580808080    // and ebp,0x80808080
 *
 *  0.9.8 のーふぁ�と
 *  13400ef3   90               nop
 *  13400ef4   77 0f            ja short 13400f05
 *  13400ef6   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x889aad0
 *  13400f00  -e9 fff050f0      jmp 03910004
 *  13400f05   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13400f0b   8bc6             mov eax,esi
 *  13400f0d   81e0 ffffff3f    and eax,0x3fffffff
 *  13400f13   8bb8 00004007    mov edi,dword ptr ds:[eax+0x7400000] ; jichi
 *  13400f19   8bef             mov ebp,edi
 *  13400f1b   81ed 01010101    sub ebp,0x1010101
 *  13400f21   f7d7             not edi
 *  13400f23   23ef             and ebp,edi
 *  13400f25   81e5 80808080    and ebp,0x80808080
 *  13400f2b   81fd 00000000    cmp ebp,0x0
 *  13400f31   c705 78a71001 80>mov dword ptr ds:[0x110a778],0x80808080
 *  13400f3b   c705 7ca71001 01>mov dword ptr ds:[0x110a77c],0x1010101
 *  13400f45   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  13400f4b   892d 88a71001    mov dword ptr ds:[0x110a788],ebp
 *  13400f51   0f84 22000000    je 13400f79
 *  13400f57   8b35 80a71001    mov esi,dword ptr ds:[0x110a780]
 *  13400f5d   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  13400f63   832d c4aa1001 0c sub dword ptr ds:[0x110aac4],0xc
 *  13400f6a   e9 35ba0000      jmp 1340c9a4
 *  13400f6f   0124ab           add dword ptr ds:[ebx+ebp*4],esp
 *  13400f72   8908             mov dword ptr ds:[eax],ecx
 *  13400f74  -e9 aaf050f0      jmp 03910023
 *  13400f79   832d c4aa1001 0c sub dword ptr ds:[0x110aac4],0xc
 *  13400f80   e9 0b000000      jmp 13400f90
 *  13400f85   0100             add dword ptr ds:[eax],eax
 *  13400f87   ab               stos dword ptr es:[edi]
 *  13400f88   8908             mov dword ptr ds:[eax],ecx
 *  13400f8a  -e9 94f050f0      jmp 03910023
 *  13400f8f   90               nop
 */

static void SpecialPSPHookAlchemist2(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (*text && !_alchemistgarbage(text)) {
    *data = (DWORD)text;
    *len = ::strlen(text);
    *split = context->ecx;
  }
}

bool InsertAlchemist2PSPHook()
{
  ConsoleOutput("Alchemist2 PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 13400ef4   77 0f            ja short 13400f05
    0xc7,0x05, XX8,                 // 13400ef6   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x889aad0
    0xe9, XX4,                      // 13400f00  -e9 fff050f0      jmp 03910004
    0x8b,0x35, XX4,                 // 13400f05   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
    0x8b,0xc6,                      // 13400f0b   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13400f0d   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb8, XX4,                 // 13400f13   8bb8 00004007    mov edi,dword ptr ds:[eax+0x7400000] ; jichi: hook here
    0x8b,0xef,                      // 13400f19   8bef             mov ebp,edi
    0x81,0xed, 0x01,0x01,0x01,0x01, // 13400f1b   81ed 01010101    sub ebp,0x1010101
    0xf7,0xd7,                      // 13400f21   f7d7             not edi
    0x23,0xef,                      // 13400f23   23ef             and ebp,edi
    0x81,0xe5, 0x80,0x80,0x80,0x80, // 13400f25   81e5 80808080    and ebp,0x80808080
    0x81,0xfd, 0x00,0x00,0x00,0x00  // 13400f2b   81fd 00000000    cmp ebp,0x0
  };
  enum { memory_offset = 2 }; // 13400f13   8bb8 00004007    mov edi,dword ptr ds:[eax+0x7400000]
  enum { addr_offset = 0x13400f13 - 0x13400ef4 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("Alchemist2 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialPSPHookAlchemist2;
    hp.type = USING_STRING|NO_CONTEXT; // no context is needed to get rid of variant retaddr
    ConsoleOutput("Alchemist2 PSP: INSERT");
    succ|=NewHook(hp, "Alchemist2 PSP");
  }

  ConsoleOutput("Alchemist2 PSP: leave");
  return succ;
}

/** 7/19/2014 jichi CYBERFRONT PSP engine, 0,9.8, 0.9.9
 *  Sample game: 想�かけ�クローストゥ (0.9.9)
 *
 *  Debug method: breakpoint the memory address
 *  There are two matched memory address to the current text
 *
 *  The second is used.
 *  The #1 is missing text.
 *
 *  #1 The text is written word by word
 *
 *  0ed8be86   90               nop
 *  0ed8be87   cc               int3
 *  0ed8be88   77 0f            ja short 0ed8be99
 *  0ed8be8a   c705 c84c1301 dc>mov dword ptr ds:[0x1134cc8],0x88151dc
 *  0ed8be94  -e9 6b41b4f4      jmp 038d0004
 *  0ed8be99   8b35 cc491301    mov esi,dword ptr ds:[0x11349cc]
 *  0ed8be9f   8d76 02          lea esi,dword ptr ds:[esi+0x2]
 *  0ed8bea2   8b3d 94491301    mov edi,dword ptr ds:[0x1134994]
 *  0ed8bea8   8b05 d0491301    mov eax,dword ptr ds:[0x11349d0]
 *  0ed8beae   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8beb4   8bd7             mov edx,edi
 *  0ed8beb6   8890 00008009    mov byte ptr ds:[eax+0x9800000],dl ; jichi: hook here, write text here
 *  0ed8bebc   8b05 c8491301    mov eax,dword ptr ds:[0x11349c8]
 *  0ed8bec2   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8bec8   0fb6a8 00008009  movzx ebp,byte ptr ds:[eax+0x9800000]
 *  0ed8becf   8b05 d0491301    mov eax,dword ptr ds:[0x11349d0]
 *  0ed8bed5   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8bedb   8bd5             mov edx,ebp
 *  0ed8bedd   8890 01008009    mov byte ptr ds:[eax+0x9800001],dl
 *  0ed8bee3   8b15 d0491301    mov edx,dword ptr ds:[0x11349d0]
 *  0ed8bee9   8d52 02          lea edx,dword ptr ds:[edx+0x2]
 *  0ed8beec   892d 90491301    mov dword ptr ds:[0x1134990],ebp
 *  0ed8bef2   8935 cc491301    mov dword ptr ds:[0x11349cc],esi
 *  0ed8bef8   8915 d0491301    mov dword ptr ds:[0x11349d0],edx
 *  0ed8befe   832d e44c1301 06 sub dword ptr ds:[0x1134ce4],0x6
 *  0ed8bf05   e9 0e000000      jmp 0ed8bf18
 *  0ed8bf0a   013451           add dword ptr ds:[ecx+edx*2],esi
 *  0ed8bf0d   8108 e90f41b4    or dword ptr ds:[eax],0xb4410fe9
 *  0ed8bf13   f4               hlt                                      ; privileged command
 *  0ed8bf14   90               nop
 *  0ed8bf15   cc               int3
 *
 *  #2 The text is read
 *
 *  Issue: the text is read multiple times.
 *  Only esp > 0xfff is kept.
 *
 *  0ed8cf13   90               nop
 *  0ed8cf14   77 0f            ja short 0ed8cf25
 *  0ed8cf16   c705 c84c1301 b8>mov dword ptr ds:[0x1134cc8],0x888d1b8
 *  0ed8cf20  -e9 df30b4f4      jmp 038d0004
 *  0ed8cf25   8b05 98491301    mov eax,dword ptr ds:[0x1134998]
 *  0ed8cf2b   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8cf31   0fb6b0 00008009  movzx esi,byte ptr ds:[eax+0x9800000] ; jichi: hook here
 *  0ed8cf38   81fe 00000000    cmp esi,0x0
 *  0ed8cf3e   8935 90491301    mov dword ptr ds:[0x1134990],esi
 *  0ed8cf44   0f85 2f000000    jnz 0ed8cf79
 *  0ed8cf4a   8b05 9c491301    mov eax,dword ptr ds:[0x113499c]
 *  0ed8cf50   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8cf56   0fbeb0 00008009  movsx esi,byte ptr ds:[eax+0x9800000]
 *  0ed8cf5d   8935 90491301    mov dword ptr ds:[0x1134990],esi
 *  0ed8cf63   832d e44c1301 03 sub dword ptr ds:[0x1134ce4],0x3
 *  0ed8cf6a   c705 c84c1301 18>mov dword ptr ds:[0x1134cc8],0x888d218
 *  0ed8cf74  -e9 aa30b4f4      jmp 038d0023
 *  0ed8cf79   832d e44c1301 03 sub dword ptr ds:[0x1134ce4],0x3
 *  0ed8cf80   e9 0b000000      jmp 0ed8cf90
 *  0ed8cf85   01c4             add esp,eax
 *  0ed8cf87   d188 08e99430    ror dword ptr ds:[eax+0x3094e908],1
 *  0ed8cf8d   b4 f4            mov ah,0xf4
 *  0ed8cf8f   90               nop
 */

static void SpecialPSPHookCyberfront(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD splitvalue = context->edi;
  if (splitvalue < 0x0fff)
    return;
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (*text) {
    *data = (DWORD)text;
    *len = ::strlen(text);
    *split = splitvalue;
  }
}
bool InsertCyberfrontPSPHook()
{
  ConsoleOutput("CYBERFRONT PSP: enter");

  const BYTE bytes[] =  {
                                    // 0ed8cf13   90               nop
    0x77, 0x0f,                     // 0ed8cf14   77 0f            ja short 0ed8cf25
    0xc7,0x05, XX8,                 // 0ed8cf16   c705 c84c1301 b8>mov dword ptr ds:[0x1134cc8],0x888d1b8
    0xe9, XX4,                      // 0ed8cf20  -e9 df30b4f4      jmp 038d0004
    0x8b,0x05, XX4,                 // 0ed8cf25   8b05 98491301    mov eax,dword ptr ds:[0x1134998]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 0ed8cf2b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0, XX4,            // 0ed8cf31   0fb6b0 00008009  movzx esi,byte ptr ds:[eax+0x9800000] ; jichi: hook here
    0x81,0xfe, 0x00,0x00,0x00,0x00, // 0ed8cf38   81fe 00000000    cmp esi,0x0
    0x89,0x35, XX4,                 // 0ed8cf3e   8935 90491301    mov dword ptr ds:[0x1134990],esi
    0x0f,0x85, 0x2f,0x00,0x00,0x00, // 0ed8cf44   0f85 2f000000    jnz 0ed8cf79
    0x8b,0x05, XX4,                 // 0ed8cf4a   8b05 9c491301    mov eax,dword ptr ds:[0x113499c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 0ed8cf50   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 0ed8cf56   0fbeb0 00008009  movsx esi,byte ptr ds:[eax+0x9800000]
    0x89,0x35, XX4,                 // 0ed8cf5d   8935 90491301    mov dword ptr ds:[0x1134990],esi
    0x83,0x2d, XX4, 0x03,           // 0ed8cf63   832d e44c1301 03 sub dword ptr ds:[0x1134ce4],0x3
    0xc7,0x05 //, XX8               // 0ed8cf6a   c705 c84c1301 18>mov dword ptr ds:[0x1134cc8],0x888d218
  };
  enum { memory_offset = 3 }; // 13909a51   8890 00008007    mov byte ptr ds:[eax+0x7800000],dl
  enum { addr_offset = 0x0ed8cf31 - 0x0ed8cf14 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  //GROWL_DWORD(addr);
  if (!addr)
    ConsoleOutput("CYBERFRONT PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    //hp.offset=regoffset(eax);
    hp.text_fun = SpecialPSPHookCyberfront;
    ConsoleOutput("CYBERFRONT PSP: INSERT");
    succ|=NewHook(hp, "CYBERFRONT PSP");
  }

  ConsoleOutput("CYBERFRONT PSP: leave");
  return succ;
}


/** 7/19/2014 jichi yetigame.jp PSP engine, 0.9.8, 0.9.9
 *  Sample game: Secret Game Portable 0.9.8/0.9.9
 *
 *  Float memory addresses: two matches
 *
 *  Debug method: find current sentence, then find next sentence in the memory
 *  and add break-points. Need to patch 1 leading \u3000 space.
 *
 *  It seems that each time I ran the game, the instruction pattern would change?!
 *  == The second time I ran the game ==
 *
 *  14e49ed9   90               nop
 *  14e49eda   cc               int3
 *  14e49edb   cc               int3
 *  14e49edc   77 0f            ja short 14e49eed
 *  14e49ede   c705 a8aa1001 98>mov dword ptr ds:[0x110aaa8],0x885ff98
 *  14e49ee8  -e9 17619eee      jmp 03830004
 *  14e49eed   8b35 70a71001    mov esi,dword ptr ds:[0x110a770]
 *  14e49ef3   c1ee 1f          shr esi,0x1f
 *  14e49ef6   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  14e49efc   81e0 ffffff3f    and eax,0x3fffffff
 *  14e49f02   8bb8 14deff07    mov edi,dword ptr ds:[eax+0x7ffde14]
 *  14e49f08   0335 70a71001    add esi,dword ptr ds:[0x110a770]
 *  14e49f0e   d1fe             sar esi,1
 *  14e49f10   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  14e49f16   81e0 ffffff3f    and eax,0x3fffffff
 *  14e49f1c   89b8 00000008    mov dword ptr ds:[eax+0x8000000],edi
 *  14e49f22   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  14e49f28   81e0 ffffff3f    and eax,0x3fffffff
 *  14e49f2e   89b0 30000008    mov dword ptr ds:[eax+0x8000030],esi
 *  14e49f34   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  14e49f3a   81e0 ffffff3f    and eax,0x3fffffff
 *  14e49f40   8ba8 14deff07    mov ebp,dword ptr ds:[eax+0x7ffde14]
 *  14e49f46   8bc5             mov eax,ebp
 *  14e49f48   81e0 ffffff3f    and eax,0x3fffffff
 *  14e49f4e   0fb6b0 00000008  movzx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here
 *  14e49f55   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  14e49f58   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *
 *  == The first time I ran the game ==
 *  There are a couple of good break-points, as follows.
 *  Only the second function is hooked.
 *
 *  138cf7a2   cc               int3
 *  138cf7a3   cc               int3
 *  138cf7a4   77 0f            ja short 138cf7b5
 *  138cf7a6   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x885ff90
 *  138cf7b0  -e9 4f08a9f3      jmp 07360004
 *  138cf7b5   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cf7bb   81e0 ffffff3f    and eax,0x3fffffff
 *  138cf7c1   8bb0 14de7f07    mov esi,dword ptr ds:[eax+0x77fde14]
 *  138cf7c7   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  138cf7cd   c705 e4a71001 98>mov dword ptr ds:[0x110a7e4],0x885ff98
 *  138cf7d7   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  138cf7de   e9 0d000000      jmp 138cf7f0
 *  138cf7e3   015c48 85        add dword ptr ds:[eax+ecx*2-0x7b],ebx
 *  138cf7e7   08e9             or cl,ch
 *  138cf7e9   36:08a9 f390cccc or byte ptr ss:[ecx+0xcccc90f3],ch
 *  138cf7f0   77 0f            ja short 138cf801
 *  138cf7f2   c705 a8aa1001 5c>mov dword ptr ds:[0x110aaa8],0x885485c
 *  138cf7fc  -e9 0308a9f3      jmp 07360004
 *  138cf801   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  138cf807   81e0 ffffff3f    and eax,0x3fffffff
 *  138cf80d   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  138cf814   81fe 00000000    cmp esi,0x0
 *  138cf81a   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  138cf820   c705 80a71001 00>mov dword ptr ds:[0x110a780],0x0
 *  138cf82a   c705 84a71001 25>mov dword ptr ds:[0x110a784],0x25
 *  138cf834   c705 88a71001 4e>mov dword ptr ds:[0x110a788],0x4e
 *  138cf83e   c705 8ca71001 6e>mov dword ptr ds:[0x110a78c],0x6e
 *  138cf848   0f85 16000000    jnz 138cf864
 *  138cf84e   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  138cf855   e9 b6010000      jmp 138cfa10
 *  138cf85a   01bc48 8508e9bf  add dword ptr ds:[eax+ecx*2+0xbfe90885],>
 *  138cf861   07               pop es                                   ; modification of segment register
 *  138cf862   a9 f3832dc4      test eax,0xc42d83f3
 *  138cf867   aa               stos byte ptr es:[edi]
 *  138cf868   1001             adc byte ptr ds:[ecx],al
 *  138cf86a   06               push es
 *  138cf86b   e9 0c000000      jmp 138cf87c
 *  138cf870   017448 85        add dword ptr ds:[eax+ecx*2-0x7b],esi
 *  138cf874   08e9             or cl,ch
 *  138cf876   a9 07a9f390      test eax,0x90f3a907
 *  138cf87b   cc               int3
 *
 *  This function is used.
 *  138cfa46   cc               int3
 *  138cfa47   cc               int3
 *  138cfa48   77 0f            ja short 138cfa59
 *  138cfa4a   c705 a8aa1001 98>mov dword ptr ds:[0x110aaa8],0x885ff98
 *  138cfa54  -e9 ab05a9f3      jmp 07360004
 *  138cfa59   8b35 70a71001    mov esi,dword ptr ds:[0x110a770]
 *  138cfa5f   c1ee 1f          shr esi,0x1f
 *  138cfa62   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cfa68   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfa6e   8bb8 14de7f07    mov edi,dword ptr ds:[eax+0x77fde14]
 *  138cfa74   0335 70a71001    add esi,dword ptr ds:[0x110a770]
 *  138cfa7a   d1fe             sar esi,1
 *  138cfa7c   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  138cfa82   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfa88   89b8 00008007    mov dword ptr ds:[eax+0x7800000],edi
 *  138cfa8e   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  138cfa94   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfa9a   89b0 30008007    mov dword ptr ds:[eax+0x7800030],esi
 *  138cfaa0   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cfaa6   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfaac   8ba8 14de7f07    mov ebp,dword ptr ds:[eax+0x77fde14]
 *  138cfab2   8bc5             mov eax,ebp
 *  138cfab4   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfaba   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  138cfac1   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  138cfac4   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cfaca   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfad0   89a8 14de7f07    mov dword ptr ds:[eax+0x77fde14],ebp
 *  138cfad6   81fe 00000000    cmp esi,0x0
 *  138cfadc   892d 70a71001    mov dword ptr ds:[0x110a770],ebp
 *  138cfae2   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  138cfae8   893d aca71001    mov dword ptr ds:[0x110a7ac],edi
 *  138cfaee   0f84 16000000    je 138cfb0a
 *  138cfaf4   832d c4aa1001 0b sub dword ptr ds:[0x110aac4],0xb
 *  138cfafb   e9 24000000      jmp 138cfb24
 *  138cfb00   01b0 ff8508e9    add dword ptr ds:[eax+0xe90885ff],esi
 *  138cfb06   1905 a9f3832d    sbb dword ptr ds:[0x2d83f3a9],eax
 *  138cfb0c   c4aa 10010be9    les ebp,fword ptr ds:[edx+0xe90b0110]    ; modification of segment register
 *  138cfb12   9a 00000001 c4ff call far ffc4:01000000                   ; far call
 *  138cfb19   8508             test dword ptr ds:[eax],ecx
 *  138cfb1b  -e9 0305a9f3      jmp 07360023
 *  138cfb20   90               nop
 *  138cfb21   cc               int3
 *  138cfb22   cc               int3
 *
 *  138cfb22   cc               int3
 *  138cfb23   cc               int3
 *  138cfb24   77 0f            ja short 138cfb35
 *  138cfb26   c705 a8aa1001 b0>mov dword ptr ds:[0x110aaa8],0x885ffb0
 *  138cfb30  -e9 cf04a9f3      jmp 07360004
 *  138cfb35   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cfb3b   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfb41   8bb0 14de7f07    mov esi,dword ptr ds:[eax+0x77fde14]
 *  138cfb47   8bc6             mov eax,esi
 *  138cfb49   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfb4f   0fb6b8 00008007  movzx edi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  138cfb56   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  138cfb59   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
 *  138cfb5f   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfb65   89b0 14de7f07    mov dword ptr ds:[eax+0x77fde14],esi
 *  138cfb6b   81ff 00000000    cmp edi,0x0
 *  138cfb71   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  138cfb77   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  138cfb7d   0f84 16000000    je 138cfb99
 *  138cfb83   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  138cfb8a  ^e9 95ffffff      jmp 138cfb24
 *  138cfb8f   01b0 ff8508e9    add dword ptr ds:[eax+0xe90885ff],esi
 *  138cfb95   8a04a9           mov al,byte ptr ds:[ecx+ebp*4]
 *  138cfb98   f3:              prefix rep:                              ; superfluous prefix
 *  138cfb99   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  138cfba0   e9 0b000000      jmp 138cfbb0
 *  138cfba5   01c4             add esp,eax
 *  138cfba7   ff85 08e97404    inc dword ptr ss:[ebp+0x474e908]
 *  138cfbad   a9 f390770f      test eax,0xf7790f3
 *  138cfbb2   c705 a8aa1001 c4>mov dword ptr ds:[0x110aaa8],0x885ffc4
 *  138cfbbc  -e9 4304a9f3      jmp 07360004
 *  138cfbc1   f3:0f1015 6c1609>movss xmm2,dword ptr ds:[0x1009166c]
 *  138cfbc9   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  138cfbcf   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfbd5   8bb0 00008007    mov esi,dword ptr ds:[eax+0x7800000]
 *  138cfbdb   f3:0f101d 641609>movss xmm3,dword ptr ds:[0x10091664]
 *  138cfbe3   c7c7 00000000    mov edi,0x0
 *  138cfbe9   893d f4b12b11    mov dword ptr ds:[0x112bb1f4],edi
 *  138cfbef   8bc6             mov eax,esi
 *  138cfbf1   81e0 ffffff3f    and eax,0x3fffffff
 *  138cfbf7   0fb6a8 00008007  movzx ebp,byte ptr ds:[eax+0x7800000]  ; jichi: hook here
 *  138cfbfe   81fd 00000000    cmp ebp,0x0
 *  138cfc04   c705 70a71001 00>mov dword ptr ds:[0x110a770],0x9ac0000
 *  138cfc0e   c705 74a71001 00>mov dword ptr ds:[0x110a774],0x8890000
 *  138cfc18   892d a8a71001    mov dword ptr ds:[0x110a7a8],ebp
 *  138cfc1e   8935 aca71001    mov dword ptr ds:[0x110a7ac],esi
 *  138cfc24   c705 b4a71001 00>mov dword ptr ds:[0x110a7b4],0x8890000
 *  138cfc2e   c705 b8a71001 80>mov dword ptr ds:[0x110a7b8],0x80
 *  138cfc38   c705 bca71001 00>mov dword ptr ds:[0x110a7bc],0x0
 *  138cfc42   c705 e0a71001 00>mov dword ptr ds:[0x110a7e0],0x0
 *  138cfc4c   f3:0f111d 3ca810>movss dword ptr ds:[0x110a83c],xmm3
 *  138cfc54   f3:0f1115 40a810>movss dword ptr ds:[0x110a840],xmm2
 *  138cfc5c   0f85 16000000    jnz 138cfc78
 *  138cfc62   832d c4aa1001 0d sub dword ptr ds:[0x110aac4],0xd
 *  138cfc69   e9 32270000      jmp 138d23a0
 *  138cfc6e   0158 00          add dword ptr ds:[eax],ebx
 *  138cfc71   8608             xchg byte ptr ds:[eax],cl
 *  138cfc73  -e9 ab03a9f3      jmp 07360023
 *  138cfc78   832d c4aa1001 0d sub dword ptr ds:[0x110aac4],0xd
 *  138cfc7f   e9 0c000000      jmp 138cfc90
 *  138cfc84   01f8             add eax,edi
 *  138cfc86   ff85 08e99503    inc dword ptr ss:[ebp+0x395e908]
 *  138cfc8c   a9 f390cc77      test eax,0x77cc90f3
 *  138cfc91   0fc7             ???                                      ; unknown command
 *  138cfc93   05 a8aa1001      add eax,0x110aaa8
 *  138cfc98   f8               clc
 *  138cfc99   ff85 08e96303    inc dword ptr ss:[ebp+0x363e908]
 *  138cfc9f   a9 f38b35ac      test eax,0xac358bf3
 *  138cfca4   a7               cmps dword ptr ds:[esi],dword ptr es:[ed>
 *  138cfca5   1001             adc byte ptr ds:[ecx],al
 *  138cfca7   8b3d b4a71001    mov edi,dword ptr ds:[0x110a7b4]
 *  138cfcad   81c7 48d6ffff    add edi,-0x29b8
 *  138cfcb3   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  138cfcb9   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  138cfcbf   c705 80a71001 02>mov dword ptr ds:[0x110a780],0x2
 *  138cfcc9   c705 e4a71001 08>mov dword ptr ds:[0x110a7e4],0x8860008
 *  138cfcd3   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  138cfcda  ^e9 4914f4ff      jmp 13811128
 *  138cfcdf   90               nop
 *  138cfce0   77 0f            ja short 138cfcf1
 *  138cfce2   c705 a8aa1001 74>mov dword ptr ds:[0x110aaa8],0x8844574
 *  138cfcec  -e9 1303a9f3      jmp 07360004
 *  138cfcf1   8b35 84a71001    mov esi,dword ptr ds:[0x110a784]
 *  138cfcf7   81c6 ffffffff    add esi,-0x1
 *  138cfcfd   813d 84a71001 00>cmp dword ptr ds:[0x110a784],0x0
 *  138cfd07   8935 8ca71001    mov dword ptr ds:[0x110a78c],esi
 *  138cfd0d   0f85 16000000    jnz 138cfd29
 *  138cfd13   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  138cfd1a   c705 a8aa1001 e0>mov dword ptr ds:[0x110aaa8],0x88445e0
 *  138cfd24  -e9 fa02a9f3      jmp 07360023
 *  138cfd29   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  138cfd30  ^e9 ab15f4ff      jmp 138112e0
 *  138cfd35   90               nop
 *  138cfd36   cc               int3
 *  138cfd37   cc               int3
 *
 *  13811266   cc               int3
 *  13811267   cc               int3
 *  13811268   77 0f            ja short 13811279
 *  1381126a   c705 a8aa1001 b0>mov dword ptr ds:[0x110aaa8],0x88445b0
 *  13811274  -e9 8bedb4f3      jmp 07360004
 *  13811279   8b35 8ca71001    mov esi,dword ptr ds:[0x110a78c]
 *  1381127f   8b3d 88a71001    mov edi,dword ptr ds:[0x110a788]
 *  13811285   8b2d 84a71001    mov ebp,dword ptr ds:[0x110a784]
 *  1381128b   81c5 ffffffff    add ebp,-0x1
 *  13811291   813d 84a71001 00>cmp dword ptr ds:[0x110a784],0x0
 *  1381129b   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  138112a1   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  138112a7   892d 8ca71001    mov dword ptr ds:[0x110a78c],ebp
 *  138112ad   0f84 16000000    je 138112c9
 *  138112b3   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  138112ba   e9 21000000      jmp 138112e0
 *  138112bf   017c45 84        add dword ptr ss:[ebp+eax*2-0x7c],edi
 *  138112c3   08e9             or cl,ch
 *  138112c5   5a               pop edx
 *  138112c6   ed               in eax,dx                                ; i/o command
 *  138112c7   b4 f3            mov ah,0xf3
 *  138112c9   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  138112d0   c705 a8aa1001 c0>mov dword ptr ds:[0x110aaa8],0x88445c0
 *  138112da  -e9 44edb4f3      jmp 07360023
 *  138112df   90               nop
 *  138112e0   77 0f            ja short 138112f1
 *  138112e2   c705 a8aa1001 7c>mov dword ptr ds:[0x110aaa8],0x884457c
 *  138112ec  -e9 13edb4f3      jmp 07360004
 *  138112f1   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  138112f7   81e0 ffffff3f    and eax,0x3fffffff
 *  138112fd   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  13811304   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  1381130a   81e0 ffffff3f    and eax,0x3fffffff
 *  13811310   0fbeb8 00008007  movsx edi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  13811317   8bc6             mov eax,esi
 *  13811319   0fbee8           movsx ebp,al
 *  1381131c   3bef             cmp ebp,edi
 *  1381131e   893d 70a71001    mov dword ptr ds:[0x110a770],edi
 *  13811324   892d 74a71001    mov dword ptr ds:[0x110a774],ebp
 *  1381132a   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  13811330   0f85 16000000    jnz 1381134c
 *  13811336   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  1381133d   e9 56110000      jmp 13812498
 *  13811342   01c8             add eax,ecx
 *  13811344   45               inc ebp
 *  13811345   8408             test byte ptr ds:[eax],cl
 *  13811347  -e9 d7ecb4f3      jmp 07360023
 *  1381134c   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  13811353   e9 0c000000      jmp 13811364
 *  13811358   0190 458408e9    add dword ptr ds:[eax+0xe9088445],edx
 *  1381135e   c1ec b4          shr esp,0xb4                             ; shift constant out of range 1..31
 *  13811361   f3:              prefix rep:                              ; superfluous prefix
 *  13811362   90               nop
 *  13811363   cc               int3
 *
 *  13811362   90               nop
 *  13811363   cc               int3
 *  13811364   77 0f            ja short 13811375
 *  13811366   c705 a8aa1001 90>mov dword ptr ds:[0x110aaa8],0x8844590
 *  13811370  -e9 8fecb4f3      jmp 07360004
 *  13811375   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  1381137b   81e0 ffffff3f    and eax,0x3fffffff
 *  13811381   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  13811388   81e6 ff000000    and esi,0xff
 *  1381138e   8b3d 80a71001    mov edi,dword ptr ds:[0x110a780]
 *  13811394   81e7 ff000000    and edi,0xff
 *  1381139a   8bc7             mov eax,edi
 *  1381139c   8bfe             mov edi,esi
 *  1381139e   2bf8             sub edi,eax
 *  138113a0   8b05 e4a71001    mov eax,dword ptr ds:[0x110a7e4]
 *  138113a6   893d 70a71001    mov dword ptr ds:[0x110a770],edi
 *  138113ac   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  138113b2   8905 a8aa1001    mov dword ptr ds:[0x110aaa8],eax
 *  138113b8   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  138113bf  -e9 5fecb4f3      jmp 07360023
 *  138113c4   90               nop
 *  138113c5   cc               int3
 *  138113c6   cc               int3
 *  138113c7   cc               int3
 *
 *  138124f2   cc               int3
 *  138124f3   cc               int3
 *  138124f4   77 0f            ja short 13812505
 *  138124f6   c705 a8aa1001 d0>mov dword ptr ds:[0x110aaa8],0x88445d0
 *  13812500  -e9 ffdab4f3      jmp 07360004
 *  13812505   813d 74a71001 00>cmp dword ptr ds:[0x110a774],0x0
 *  1381250f   c705 90a71001 00>mov dword ptr ds:[0x110a790],0x0
 *  13812519   0f84 16000000    je 13812535
 *  1381251f   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  13812526   e9 21000000      jmp 1381254c
 *  1381252b   018446 8408e9ee  add dword ptr ds:[esi+eax*2+0xeee90884],>
 *  13812532   dab4f3 832dc4aa  fidiv dword ptr ds:[ebx+esi*8+0xaac42d83>
 *  13812539   1001             adc byte ptr ds:[ecx],al
 *  1381253b   02e9             add ch,cl
 *  1381253d   3302             xor eax,dword ptr ds:[edx]
 *  1381253f   0000             add byte ptr ds:[eax],al
 *  13812541   01d8             add eax,ebx
 *  13812543   45               inc ebp
 *  13812544   8408             test byte ptr ds:[eax],cl
 *  13812546  -e9 d8dab4f3      jmp 07360023
 *  1381254b   90               nop
 *  1381254c   77 0f            ja short 1381255d
 *  1381254e   c705 a8aa1001 84>mov dword ptr ds:[0x110aaa8],0x8844684
 *  13812558  -e9 a7dab4f3      jmp 07360004
 *  1381255d   8b35 78a71001    mov esi,dword ptr ds:[0x110a778]
 *  13812563   0335 8ca71001    add esi,dword ptr ds:[0x110a78c]
 *  13812569   8b3d 88a71001    mov edi,dword ptr ds:[0x110a788]
 *  1381256f   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13812572   8b2d 7ca71001    mov ebp,dword ptr ds:[0x110a77c]
 *  13812578   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  1381257b   8b15 90a71001    mov edx,dword ptr ds:[0x110a790]
 *  13812581   3b15 8ca71001    cmp edx,dword ptr ds:[0x110a78c]
 *  13812587   892d 7ca71001    mov dword ptr ds:[0x110a77c],ebp
 *  1381258d   893d 88a71001    mov dword ptr ds:[0x110a788],edi
 *  13812593   8935 94a71001    mov dword ptr ds:[0x110a794],esi
 *  13812599   0f85 16000000    jnz 138125b5
 *  1381259f   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  138125a6   c705 a8aa1001 c4>mov dword ptr ds:[0x110aaa8],0x88446c4
 *  138125b0  -e9 6edab4f3      jmp 07360023
 *  138125b5   832d c4aa1001 04 sub dword ptr ds:[0x110aac4],0x4
 *  138125bc   e9 0b000000      jmp 138125cc
 *  138125c1   019446 8408e958  add dword ptr ds:[esi+eax*2+0x58e90884],>
 *  138125c8   dab4f3 90770fc7  fidiv dword ptr ds:[ebx+esi*8+0xc70f7790>
 *  138125cf   05 a8aa1001      add eax,0x110aaa8
 *  138125d4   94               xchg eax,esp
 *  138125d5   46               inc esi
 *  138125d6   8408             test byte ptr ds:[eax],cl
 *  138125d8  -e9 27dab4f3      jmp 07360004
 *  138125dd   8b05 88a71001    mov eax,dword ptr ds:[0x110a788]
 *  138125e3   81e0 ffffff3f    and eax,0x3fffffff
 *  138125e9   0fb6b0 00008007  movzx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  138125f0   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  138125f6   81e0 ffffff3f    and eax,0x3fffffff
 *  138125fc   0fb6b8 00008007  movzx edi,byte ptr ds:[eax+0x7800000]
 *  13812603   8bc6             mov eax,esi
 *  13812605   0fbee8           movsx ebp,al
 *  13812608   8bc7             mov eax,edi
 *  1381260a   0fbed0           movsx edx,al
 *  1381260d   8b0d 90a71001    mov ecx,dword ptr ds:[0x110a790]
 *  13812613   8d49 01          lea ecx,dword ptr ds:[ecx+0x1]
 *  13812616   3bd5             cmp edx,ebp
 *  13812618   892d 70a71001    mov dword ptr ds:[0x110a770],ebp
 *  1381261e   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  13812624   893d 80a71001    mov dword ptr ds:[0x110a780],edi
 *  1381262a   8915 84a71001    mov dword ptr ds:[0x110a784],edx
 *  13812630   890d 90a71001    mov dword ptr ds:[0x110a790],ecx
 *  13812636   0f84 16000000    je 13812652
 *  1381263c   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  13812643   e9 98d70b00      jmp 138cfde0
 *  13812648   019445 8408e9d1  add dword ptr ss:[ebp+eax*2+0xd1e90884],>
 *  1381264f   d9b4f3 832dc4aa  fstenv (28-byte) ptr ds:[ebx+esi*8+0xaac>
 *  13812656   1001             adc byte ptr ds:[ecx],al
 *  13812658   06               push es
 *  13812659   e9 0e000000      jmp 1381266c
 *  1381265e   01ac46 8408e9bb  add dword ptr ds:[esi+eax*2+0xbbe90884],>
 *  13812665   d9b4f3 90cccccc  fstenv (28-byte) ptr ds:[ebx+esi*8+0xccc>
 *  1381266c   77 0f            ja short 1381267d
 *  1381266e   c705 a8aa1001 ac>mov dword ptr ds:[0x110aaa8],0x88446ac
 *  13812678  -e9 87d9b4f3      jmp 07360004
 *  1381267d   8b35 88a71001    mov esi,dword ptr ds:[0x110a788]
 *  13812683   3b35 94a71001    cmp esi,dword ptr ds:[0x110a794]
 *  13812689   0f85 16000000    jnz 138126a5
 *  1381268f   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  13812696   e9 d9000000      jmp 13812774
 *  1381269b   01d8             add eax,ebx
 *  1381269d   45               inc ebp
 *  1381269e   8408             test byte ptr ds:[eax],cl
 *  138126a0  -e9 7ed9b4f3      jmp 07360023
 *  138126a5   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  138126ac   e9 0b000000      jmp 138126bc
 *  138126b1   01b446 8408e968  add dword ptr ds:[esi+eax*2+0x68e90884],>
 *  138126b8   d9b4f3 90770fc7  fstenv (28-byte) ptr ds:[ebx+esi*8+0xc70>
 *  138126bf   05 a8aa1001      add eax,0x110aaa8
 *  138126c4   b4 46            mov ah,0x46
 *  138126c6   8408             test byte ptr ds:[eax],cl
 *  138126c8  -e9 37d9b4f3      jmp 07360004
 *  138126cd   8b35 88a71001    mov esi,dword ptr ds:[0x110a788]
 *  138126d3   8d76 01          lea esi,dword ptr ds:[esi+0x1]
 *  138126d6   813d 84a71001 00>cmp dword ptr ds:[0x110a784],0x0
 *  138126e0   8935 88a71001    mov dword ptr ds:[0x110a788],esi
 *  138126e6   0f84 16000000    je 13812702
 *  138126ec   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  138126f3   e9 24000000      jmp 1381271c
 *  138126f8   018c46 8408e921  add dword ptr ds:[esi+eax*2+0x21e90884],>
 *  138126ff   d9b4f3 832dc4aa  fstenv (28-byte) ptr ds:[ebx+esi*8+0xaac>
 *  13812706   1001             adc byte ptr ds:[ecx],al
 *  13812708   02c7             add al,bh
 *  1381270a   05 a8aa1001      add eax,0x110aaa8
 *  1381270f   bc 468408e9      mov esp,0xe9088446
 *  13812714   0bd9             or ebx,ecx
 *  13812716   b4 f3            mov ah,0xf3
 *  13812718   90               nop
 *  13812719   cc               int3
 *  1381271a   cc               int3
 *  1381271b   cc               int3
 *
 *  This function is very similar to Imageepoch, and can have duplicate text
 *  138d1486   cc               int3
 *  138d1487   cc               int3
 *  138d1488   77 0f            ja short 138d1499
 *  138d148a   c705 a8aa1001 2c>mov dword ptr ds:[0x110aaa8],0x884452c
 *  138d1494  -e9 6beba8f3      jmp 07360004
 *  138d1499   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  138d149f   81e0 ffffff3f    and eax,0x3fffffff
 *  138d14a5   0fbeb0 00008007  movsx esi,byte ptr ds:[eax+0x7800000] ; jichi: hook here
 *  138d14ac   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
 *  138d14b2   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  138d14b5   8b05 74a71001    mov eax,dword ptr ds:[0x110a774]
 *  138d14bb   81e0 ffffff3f    and eax,0x3fffffff
 *  138d14c1   8bd6             mov edx,esi
 *  138d14c3   8890 00008007    mov byte ptr ds:[eax+0x7800000],dl
 *  138d14c9   8b2d 74a71001    mov ebp,dword ptr ds:[0x110a774]
 *  138d14cf   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  138d14d2   81fe 00000000    cmp esi,0x0
 *  138d14d8   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  138d14de   892d 74a71001    mov dword ptr ds:[0x110a774],ebp
 *  138d14e4   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  138d14ea   0f85 16000000    jnz 138d1506
 *  138d14f0   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  138d14f7   e9 e8000000      jmp 138d15e4
 *  138d14fc   015445 84        add dword ptr ss:[ebp+eax*2-0x7c],edx
 *  138d1500   08e9             or cl,ch
 *  138d1502   1d eba8f383      sbb eax,0x83f3a8eb
 *  138d1507   2d c4aa1001      sub eax,0x110aac4
 *  138d150c   05 e90e0000      add eax,0xee9
 *  138d1511   0001             add byte ptr ds:[ecx],al
 *  138d1513   40               inc eax
 *  138d1514   45               inc ebp
 *  138d1515   8408             test byte ptr ds:[eax],cl
 *  138d1517  -e9 07eba8f3      jmp 07360023
 *  138d151c   90               nop
 *  138d151d   cc               int3
 *  138d151e   cc               int3
 *  138d151f   cc               int3
 */
//static void SpecialPSPHookYeti(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
//{
//  //enum { base = 0x7400000 };
//  DWORD eax = regof(eax, esp_base);
//  LPCSTR text = LPCSTR(eax + hp->user_value);
//  if (*text) {
//    *data = (DWORD)text;
//    *len = ::strlen(text); // SHIFT-JIS
//    //*split = regof(ecx, esp_base); // ecx is bad that will split text threads
//    //*split = FIXED_SPLIT_VALUE; // Similar to 5pb, it only has one thread?
//    //*split = regof(ebx, esp_base); // value of ebx is splitting
//    *split = FIXED_SPLIT_VALUE << 1; // * 2 to make it unique
//  }
//}

bool InsertYetiPSPHook()
{
  ConsoleOutput("Yeti PSP: enter");
  const BYTE bytes[] =  {
    //0xcc,                         // 14e49edb   cc               int3
    0x77, 0x0f,                     // 14e49edc   77 0f            ja short 14e49eed
    0xc7,0x05, XX8,                 // 14e49ede   c705 a8aa1001 98>mov dword ptr ds:[0x110aaa8],0x885ff98
    0xe9, XX4,                      // 14e49ee8  -e9 17619eee      jmp 03830004
    0x8b,0x35, XX4,                 // 14e49eed   8b35 70a71001    mov esi,dword ptr ds:[0x110a770]
    0xc1,0xee, 0x1f,                // 14e49ef3   c1ee 1f          shr esi,0x1f
    0x8b,0x05, XX4,                 // 14e49ef6   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14e49efc   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb8, XX4,                 // 14e49f02   8bb8 14deff07    mov edi,dword ptr ds:[eax+0x7ffde14]
    0x03,0x35, XX4,                 // 14e49f08   0335 70a71001    add esi,dword ptr ds:[0x110a770]
    0xd1,0xfe,                      // 14e49f0e   d1fe             sar esi,1
    0x8b,0x05, XX4,                 // 14e49f10   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14e49f16   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb8, XX4,                 // 14e49f1c   89b8 00000008    mov dword ptr ds:[eax+0x8000000],edi
    0x8b,0x05, XX4,                 // 14e49f22   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14e49f28   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb0, XX4,                 // 14e49f2e   89b0 30000008    mov dword ptr ds:[eax+0x8000030],esi
    0x8b,0x05, XX4,                 // 14e49f34   8b05 b4a71001    mov eax,dword ptr ds:[0x110a7b4]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14e49f3a   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xa8, XX4,                 // 14e49f40   8ba8 14deff07    mov ebp,dword ptr ds:[eax+0x7ffde14]
    0x8b,0xc5,                      // 14e49f46   8bc5             mov eax,ebp
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14e49f48   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0 //, XX4,         // 14e49f4e   0fb6b0 00000008  movzx esi,byte ptr ds:[eax+0x8000000] ; jichi: hook here
  };
  enum { memory_offset = 3 }; // 14e49f4e   0fb6b0 00000008  movzx esi,byte ptr ds:[eax+0x8000000]
  enum { addr_offset = sizeof(bytes) - memory_offset };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Yeti PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|FIXING_SPLIT|NO_CONTEXT; // Fix the split value to merge all threads
    hp.text_fun = SpecialPSPHook;
    hp.offset=regoffset(eax);
    ConsoleOutput("Yeti PSP: INSERT");
    succ|=NewHook(hp, "Yeti PSP");
  }

  ConsoleOutput("Yeti PSP: leave");
  return succ;
}

/** 7/19/2014 jichi Alternative Yeti PSP engine, 0.9.8, 0.9.9
 *  Sample game: Never 7, 0.9.8 & 0.9.9
 *  Sample game: ひまわり
 *
 *  Do not work on 0.9.9 Ever17 (7/27/2014)
 *
 *
 *  This hook does not work for 12River.
 *  However, sceFont functions work.
 *
 *  Memory address is FIXED.
 *  Debug method: breakpoint the memory address
 *  There are two matched memory address to the current text
 *
 *  There are several functions. The first one is used.
 *
 *  The text also has 5pb-like garbage, but it is difficult to trim.
 *
 *  PPSSPP 0.9.8:
 *
 *  14289802   cc               int3
 *  14289803   cc               int3
 *  14289804   77 0f            ja short 14289815
 *  14289806   c705 a8aa1001 58>mov dword ptr ds:[0x110aaa8],0x881ab58
 *  14289810  -e9 ef6767ef      jmp 03900004
 *  14289815   8b35 74a71001    mov esi,dword ptr ds:[0x110a774]
 *  1428981b   0335 78a71001    add esi,dword ptr ds:[0x110a778]
 *  14289821   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  14289827   81e0 ffffff3f    and eax,0x3fffffff
 *  1428982d   8bb8 28004007    mov edi,dword ptr ds:[eax+0x7400028]
 *  14289833   8bc6             mov eax,esi
 *  14289835   81e0 ffffff3f    and eax,0x3fffffff
 *  1428983b   8bd7             mov edx,edi
 *  1428983d   8890 10044007    mov byte ptr ds:[eax+0x7400410],dl
 *  14289843   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  14289849   81e0 ffffff3f    and eax,0x3fffffff
 *  1428984f   8bb8 84004007    mov edi,dword ptr ds:[eax+0x7400084]
 *  14289855   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
 *  1428985b   81e0 ffffff3f    and eax,0x3fffffff
 *  14289861   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  14289868   81ff 00000000    cmp edi,0x0
 *  1428986e   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  14289874   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  1428987a   892d 78a71001    mov dword ptr ds:[0x110a778],ebp
 *  14289880   0f85 16000000    jnz 1428989c
 *  14289886   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  1428988d   c705 a8aa1001 ac>mov dword ptr ds:[0x110aaa8],0x881aeac
 *  14289897  -e9 876767ef      jmp 03900023
 *  1428989c   832d c4aa1001 06 sub dword ptr ds:[0x110aac4],0x6
 *  142898a3   e9 0c000000      jmp 142898b4
 *  142898a8   0170 ab          add dword ptr ds:[eax-0x55],esi
 *  142898ab   8108 e9716767    or dword ptr ds:[eax],0x676771e9
 *  142898b1   ef               out dx,eax                               ; i/o command
 *  142898b2   90               nop
 *
 *  142878ed   cc               int3
 *  142878ee   cc               int3
 *  142878ef   cc               int3
 *  142878f0   77 0f            ja short 14287901
 *  142878f2   c705 a8aa1001 44>mov dword ptr ds:[0x110aaa8],0x8811e44
 *  142878fc  -e9 038767ef      jmp 03900004
 *  14287901   8b35 70a71001    mov esi,dword ptr ds:[0x110a770]
 *  14287907   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  1428790d   81e0 ffffff3f    and eax,0x3fffffff
 *  14287913   8bd6             mov edx,esi
 *  14287915   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl ; jichi: hook here
 *  1428791b   8b05 a8a71001    mov eax,dword ptr ds:[0x110a7a8]
 *  14287921   81e0 ffffff3f    and eax,0x3fffffff
 *  14287927   0fb6b8 00004007  movzx edi,byte ptr ds:[eax+0x7400000]
 *  1428792e   8b2d aca71001    mov ebp,dword ptr ds:[0x110a7ac]
 *  14287934   81c5 02000000    add ebp,0x2
 *  1428793a   8bd5             mov edx,ebp
 *  1428793c   8915 aca71001    mov dword ptr ds:[0x110a7ac],edx
 *  14287942   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
 *  14287948   81e0 ffffff3f    and eax,0x3fffffff
 *  1428794e   8bd7             mov edx,edi
 *  14287950   8890 01004007    mov byte ptr ds:[eax+0x7400001],dl
 *  14287956   8b15 b0a71001    mov edx,dword ptr ds:[0x110a7b0]
 *  1428795c   8d52 02          lea edx,dword ptr ds:[edx+0x2]
 *  1428795f   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  14287965   892d a8a71001    mov dword ptr ds:[0x110a7a8],ebp
 *  1428796b   8915 b0a71001    mov dword ptr ds:[0x110a7b0],edx
 *  14287971   832d c4aa1001 07 sub dword ptr ds:[0x110aac4],0x7
 *  14287978   e9 0b000000      jmp 14287988
 *  1428797d   01a8 1d8108e9    add dword ptr ds:[eax+0xe908811d],ebp
 *  14287983   9c               pushfd
 *  14287984   8667 ef          xchg byte ptr ds:[edi-0x11],ah
 *  14287987   90               nop
 *
 *  14289a2a   90               nop
 *  14289a2b   cc               int3
 *  14289a2c   77 0f            ja short 14289a3d
 *  14289a2e   c705 a8aa1001 b4>mov dword ptr ds:[0x110aaa8],0x881abb4
 *  14289a38  -e9 c76567ef      jmp 03900004
 *  14289a3d   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  14289a43   81e0 ffffff3f    and eax,0x3fffffff
 *  14289a49   8bb0 18004007    mov esi,dword ptr ds:[eax+0x7400018]
 *  14289a4f   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  14289a55   81e0 ffffff3f    and eax,0x3fffffff
 *  14289a5b   8bb8 24004007    mov edi,dword ptr ds:[eax+0x7400024]
 *  14289a61   8b2d 70a71001    mov ebp,dword ptr ds:[0x110a770]
 *  14289a67   03ee             add ebp,esi
 *  14289a69   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  14289a6f   81e0 ffffff3f    and eax,0x3fffffff
 *  14289a75   8bb0 20004007    mov esi,dword ptr ds:[eax+0x7400020]
 *  14289a7b   8bc5             mov eax,ebp
 *  14289a7d   81e0 ffffff3f    and eax,0x3fffffff
 *  14289a83   66:89b8 c2034007 mov word ptr ds:[eax+0x74003c2],di
 *  14289a8a   8bc5             mov eax,ebp
 *  14289a8c   81e0 ffffff3f    and eax,0x3fffffff
 *  14289a92   66:89b0 c0034007 mov word ptr ds:[eax+0x74003c0],si
 *  14289a99   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
 *  14289a9f   81e0 ffffff3f    and eax,0x3fffffff
 *  14289aa5   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  14289aac   81e6 ff000000    and esi,0xff
 *  14289ab2   892d 70a71001    mov dword ptr ds:[0x110a770],ebp
 *  14289ab8   893d 74a71001    mov dword ptr ds:[0x110a774],edi
 *  14289abe   8935 78a71001    mov dword ptr ds:[0x110a778],esi
 *  14289ac4   c705 e4a71001 d8>mov dword ptr ds:[0x110a7e4],0x881abd8
 *  14289ace   832d c4aa1001 09 sub dword ptr ds:[0x110aac4],0x9
 *  14289ad5  ^e9 d6c6f8ff      jmp 142161b0
 *  14289ada   90               nop
 *
 *  14289adb   cc               int3
 *  14289adc   77 0f            ja short 14289aed
 *  14289ade   c705 a8aa1001 d8>mov dword ptr ds:[0x110aaa8],0x881abd8
 *  14289ae8  -e9 176567ef      jmp 03900004
 *  14289aed   813d 70a71001 00>cmp dword ptr ds:[0x110a770],0x0
 *  14289af7   0f85 2f000000    jnz 14289b2c
 *  14289afd   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
 *  14289b03   81e0 ffffff3f    and eax,0x3fffffff
 *  14289b09   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  14289b10   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  14289b16   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  14289b1d   e9 22000000      jmp 14289b44
 *  14289b22   0110             add dword ptr ds:[eax],edx
 *  14289b24   af               scas dword ptr es:[edi]
 *  14289b25   8108 e9f76467    or dword ptr ds:[eax],0x6764f7e9
 *  14289b2b   ef               out dx,eax                               ; i/o command
 *  14289b2c   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  14289b33   c705 a8aa1001 e0>mov dword ptr ds:[0x110aaa8],0x881abe0
 *  14289b3d  -e9 e16467ef      jmp 03900023
 *
 *  PPSSPP 0.9.9 (7/27/2014)
 *
 *  0ed85942   cc               int3
 *  0ed85943   cc               int3
 *  0ed85944   77 0f            ja short 0ed85955
 *  0ed85946   c705 c84c1301 58>mov dword ptr ds:[0x1134cc8],0x881ab58
 *  0ed85950  -e9 afa6aef4      jmp 03870004
 *  0ed85955   8b35 94491301    mov esi,dword ptr ds:[0x1134994]
 *  0ed8595b   0335 98491301    add esi,dword ptr ds:[0x1134998]
 *  0ed85961   8b05 fc491301    mov eax,dword ptr ds:[0x11349fc]
 *  0ed85967   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8596d   8bb8 28008009    mov edi,dword ptr ds:[eax+0x9800028]
 *  0ed85973   8bc6             mov eax,esi
 *  0ed85975   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8597b   8bd7             mov edx,edi
 *  0ed8597d   8890 10048009    mov byte ptr ds:[eax+0x9800410],dl
 *  0ed85983   8b05 d0491301    mov eax,dword ptr ds:[0x11349d0]
 *  0ed85989   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed8598f   8bb8 84008009    mov edi,dword ptr ds:[eax+0x9800084]
 *  0ed85995   8b05 cc491301    mov eax,dword ptr ds:[0x11349cc]
 *  0ed8599b   81e0 ffffff3f    and eax,0x3fffffff
 *  0ed859a1   0fb6a8 00008009  movzx ebp,byte ptr ds:[eax+0x9800000] ; jichi: hook here
 *  0ed859a8   81ff 00000000    cmp edi,0x0
 *  0ed859ae   8935 90491301    mov dword ptr ds:[0x1134990],esi
 *  0ed859b4   893d 94491301    mov dword ptr ds:[0x1134994],edi
 *  0ed859ba   892d 98491301    mov dword ptr ds:[0x1134998],ebp
 *  0ed859c0   0f85 16000000    jnz 0ed859dc
 *  0ed859c6   832d e44c1301 06 sub dword ptr ds:[0x1134ce4],0x6
 *  0ed859cd   c705 c84c1301 ac>mov dword ptr ds:[0x1134cc8],0x881aeac
 *  0ed859d7  -e9 47a6aef4      jmp 03870023
 *  0ed859dc   832d e44c1301 06 sub dword ptr ds:[0x1134ce4],0x6
 *  0ed859e3   e9 0c000000      jmp 0ed859f4
 *  0ed859e8   0170 ab          add dword ptr ds:[eax-0x55],esi
 *  0ed859eb   8108 e931a6ae    or dword ptr ds:[eax],0xaea631e9
 *  0ed859f1   f4               hlt                                      ; privileged command
 *  0ed859f2   90               nop
 */
// TODO: Is reverse_strlen a better choice?
static void SpecialPSPHookYeti2(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  if (BYTE c = *(BYTE *)text) {
    *data = (DWORD)text;
    //*len = text[1] ? 2 : 1;
    *len = ::LeadByteTable[c];

    *split = context->edx;
    //DWORD ecx = regof(ecx, esp_base);
    //*split = ecx ? (FIXED_SPLIT_VALUE << 1) : 0; // << 1 to be unique, non-zero ecx is what I want
  }
}

bool InsertYeti2PSPHook()
{
  ConsoleOutput("Yeti2 PSP: enter");

  const BYTE bytes[] =  {
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14289827   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb8, XX4,                 // 1428982d   8bb8 28004007    mov edi,dword ptr ds:[eax+0x7400028]
    0x8b,0xc6,                      // 14289833   8bc6             mov eax,esi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14289835   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xd7,                      // 1428983b   8bd7             mov edx,edi
    0x88,0x90, XX4,                 // 1428983d   8890 10044007    mov byte ptr ds:[eax+0x7400410],dl
    0x8b,0x05, XX4,                 // 14289843   8b05 b0a71001    mov eax,dword ptr ds:[0x110a7b0]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14289849   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb8, XX4,                 // 1428984f   8bb8 84004007    mov edi,dword ptr ds:[eax+0x7400084]
    0x8b,0x05, XX4,                 // 14289855   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1428985b   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xa8 //, XX4          // 14289861   0fb6a8 00004007  movzx ebp,byte ptr ds:[eax+0x7400000] ; jichi: hook here
                                    // 14289b10   8935 70a71001    mov dword ptr ds:[0x110a770],esi
                                    // 14289b16   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
  };
  enum { memory_offset = 3 };
  enum { addr_offset = sizeof(bytes) - memory_offset };
  //enum { addr_offset = sizeof(bytes) + 4 }; // point to next statement after ebp is assigned
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Yeti2 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookYeti2;
    ConsoleOutput("Yeti2 PSP: INSERT");
    succ|=NewHook(hp, "Yeti2 PSP");
  }

  ConsoleOutput("Yeti2 PSP: leave");
  return succ;
}

/** 7/22/2014 jichi: Nippon1 PSP engine, 0.9.8 only
 *  Sample game: ぁ�の�リンスさまっ♪  (0.9.8 only)
 *
 *  Memory address is FIXED.
 *  Debug method: breakpoint the precomputed address
 *
 *  The data is in (WORD)bp instead of eax.
 *  bp contains SHIFT-JIS CODEC_ANSI_BE data.
 *
 *  There is only one text thread.
 *
 *  134e0553   cc               int3
 *  134e0554   77 0f            ja short 134e0565
 *  134e0556   c705 a8aa1001 34>mov dword ptr ds:[0x110aaa8],0x8853a34
 *  134e0560  -e9 9ffa03f0      jmp 03520004
 *  134e0565   8b35 74a71001    mov esi,dword ptr ds:[0x110a774]
 *  134e056b   d1e6             shl esi,1
 *  134e056d   c7c7 987db708    mov edi,0x8b77d98
 *  134e0573   03fe             add edi,esi
 *  134e0575   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
 *  134e057b   8bc7             mov eax,edi
 *  134e057d   81e0 ffffff3f    and eax,0x3fffffff
 *  134e0583   66:89a8 00004007 mov word ptr ds:[eax+0x7400000],bp ; jichi: hook here
 *  134e058a   8b2d 8c7df70f    mov ebp,dword ptr ds:[0xff77d8c]
 *  134e0590   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  134e0593   892d 8c7df70f    mov dword ptr ds:[0xff77d8c],ebp
 *  134e0599   8b05 e4a71001    mov eax,dword ptr ds:[0x110a7e4]
 *  134e059f   c705 74a71001 00>mov dword ptr ds:[0x110a774],0x8b70000
 *  134e05a9   892d 78a71001    mov dword ptr ds:[0x110a778],ebp
 *  134e05af   8935 7ca71001    mov dword ptr ds:[0x110a77c],esi
 *  134e05b5   8905 a8aa1001    mov dword ptr ds:[0x110aaa8],eax
 *  134e05bb   832d c4aa1001 0c sub dword ptr ds:[0x110aac4],0xc
 *  134e05c2  -e9 5cfa03f0      jmp 03520023
 */
// Read text from bp
// TODO: This should be expressed as general hook without extern fun
static void SpecialPSPHookNippon1(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  LPCSTR text = LPCSTR(context->base + hp->offset); // dynamic offset, ebp or esi
  if (*text) {
    *data = (DWORD)text;
    *len = !text[0] ? 0 : !text[1] ? 1 : 2; // bp or si has at most two bytes
    //*len = ::LeadByteTable[*(BYTE *)text] // TODO: Test leadbytetable
    *split = context->ecx;
  }
}

bool InsertNippon1PSPHook()
{
  ConsoleOutput("Nippon1 PSP: enter");

  const BYTE bytes[] =  {
    //0xcc,                         // 134e0553   cc               int3
    0x77, 0x0f,                     // 134e0554   77 0f            ja short 134e0565
    0xc7,0x05, XX8,                 // 134e0556   c705 a8aa1001 34>mov dword ptr ds:[0x110aaa8],0x8853a34
    0xe9, XX4,                      // 134e0560  -e9 9ffa03f0      jmp 03520004
    0x8b,0x35, XX4,                 // 134e0565   8b35 74a71001    mov esi,dword ptr ds:[0x110a774]
    0xd1,0xe6,                      // 134e056b   d1e6             shl esi,1
    0xc7,0xc7, XX4,                 // 134e056d   c7c7 987db708    mov edi,0x8b77d98
    0x03,0xfe,                      // 134e0573   03fe             add edi,esi
    0x8b,0x2d, XX4,                 // 134e0575   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
    0x8b,0xc7,                      // 134e057b   8bc7             mov eax,edi
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 134e057d   81e0 ffffff3f    and eax,0x3fffffff
    0x66,0x89,0xa8, XX4,            // 134e0583   66:89a8 00004007 mov word ptr ds:[eax+0x7400000],bp ; jichi: hook here
    0x8b,0x2d, XX4,                 // 134e058a   8b2d 8c7df70f    mov ebp,dword ptr ds:[0xff77d8c]
    0x8d,0x6d, 0x01                 // 134e0590   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x134e0583 - 0x134e0554 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Nippon1 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset=regoffset(ebp); 
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookNippon1;
    ConsoleOutput("Nippon1 PSP: INSERT");
    succ|=NewHook(hp, "Nippon1 PSP");
  }

  ConsoleOutput("Nippon1 PSP: leave");
  return succ;
}

/** 7/26/2014 jichi: Alternative Nippon1 PSP engine, 0.9.8 only
 *  Sample game: 神�悪戯 (0.9.8 only)
 *  Issue: character name cannot be extracted
 *
 *  Memory address is FIXED.
 *  Debug method: breakpoint the precomputed address
 *
 *  This function is the one that write the text into the memory.
 *
 *  13d13e8b   0f92c0           setb al
 *  13d13e8e   8bf8             mov edi,eax
 *  13d13e90   81ff 00000000    cmp edi,0x0
 *  13d13e96   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  13d13e9c   8935 dca71001    mov dword ptr ds:[0x110a7dc],esi
 *  13d13ea2   0f85 16000000    jnz 13d13ebe
 *  13d13ea8   832d c4aa1001 0a sub dword ptr ds:[0x110aac4],0xa
 *  13d13eaf   c705 a8aa1001 cc>mov dword ptr ds:[0x110aaa8],0x887c2cc
 *  13d13eb9  -e9 65c1a3ef      jmp 03750023
 *  13d13ebe   832d c4aa1001 0a sub dword ptr ds:[0x110aac4],0xa
 *  13d13ec5   e9 0e000000      jmp 13d13ed8
 *  13d13eca   01a8 c28708e9    add dword ptr ds:[eax+0xe90887c2],ebp
 *  13d13ed0   4f               dec edi
 *  13d13ed1   c1a3 ef90cccc cc shl dword ptr ds:[ebx+0xcccc90ef],0xcc   ; shift constant out of range 1..31
 *  13d13ed8   77 0f            ja short 13d13ee9
 *  13d13eda   c705 a8aa1001 a8>mov dword ptr ds:[0x110aaa8],0x887c2a8
 *  13d13ee4  -e9 1bc1a3ef      jmp 03750004
 *  13d13ee9   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  13d13eef   81e0 ffffff3f    and eax,0x3fffffff
 *  13d13ef5   0fb7b0 0000c007  movzx esi,word ptr ds:[eax+0x7c00000]
 *  13d13efc   8b3d fccd5a10    mov edi,dword ptr ds:[0x105acdfc]
 *  13d13f02   8bef             mov ebp,edi
 *  13d13f04   d1e5             shl ebp,1
 *  13d13f06   81c5 e8cd9a08    add ebp,0x89acde8
 *  13d13f0c   8bc5             mov eax,ebp
 *  13d13f0e   81e0 ffffff3f    and eax,0x3fffffff
 *  13d13f14   66:89b0 2000c007 mov word ptr ds:[eax+0x7c00020],si ; jichi: hook here
 *  13d13f1b   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13d13f1e   893d fccd5a10    mov dword ptr ds:[0x105acdfc],edi
 *  13d13f24   8b15 dca71001    mov edx,dword ptr ds:[0x110a7dc]
 *  13d13f2a   8d52 10          lea edx,dword ptr ds:[edx+0x10]
 *  13d13f2d   8b05 e4a71001    mov eax,dword ptr ds:[0x110a7e4]
 *  13d13f33   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  13d13f39   c705 7ca71001 e8>mov dword ptr ds:[0x110a77c],0x89acde8
 *  13d13f43   8935 80a71001    mov dword ptr ds:[0x110a780],esi
 *  13d13f49   892d 84a71001    mov dword ptr ds:[0x110a784],ebp
 *  13d13f4f   8915 dca71001    mov dword ptr ds:[0x110a7dc],edx
 *  13d13f55   8905 a8aa1001    mov dword ptr ds:[0x110aaa8],eax
 *  13d13f5b   832d c4aa1001 0b sub dword ptr ds:[0x110aac4],0xb
 *  13d13f62  -e9 bcc0a3ef      jmp 03750023
 *  13d13f67   90               nop
 */

// 8/13/2014: 5pb might crash on 0.9.9.
bool InsertNippon2PSPHook()
{
  ConsoleOutput("Nippon2 PSP: enter");

  const BYTE bytes[] =  {
    0xe9, XX4,                      // 13d13ee4  -e9 1bc1a3ef      jmp 03750004
    0x8b,0x05, XX4,                 // 13d13ee9   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13d13eef   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb7,0xb0, XX4,            // 13d13ef5   0fb7b0 0000c007  movzx esi,word ptr ds:[eax+0x7c00000]
    0x8b,0x3d, XX4,                 // 13d13efc   8b3d fccd5a10    mov edi,dword ptr ds:[0x105acdfc]
    0x8b,0xef,                      // 13d13f02   8bef             mov ebp,edi
    0xd1,0xe5,                      // 13d13f04   d1e5             shl ebp,1
    0x81,0xc5, XX4,                 // 13d13f06   81c5 e8cd9a08    add ebp,0x89acde8
    0x8b,0xc5,                      // 13d13f0c   8bc5             mov eax,ebp
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13d13f0e   81e0 ffffff3f    and eax,0x3fffffff
    0x66,0x89,0xb0 //, XX4          // 13d13f14   66:89b0 2000c007 mov word ptr ds:[eax+0x7c00020],si ; jichi: hook here
  };
  enum { memory_offset = 3 };
  enum { addr_offset = sizeof(bytes) - memory_offset };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Nippon2 PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.offset=regoffset(esi); 
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookNippon1;
    ConsoleOutput("Nippon2 PSP: INSERT");
    succ|=NewHook(hp, "Nippon2 PSP");
  }

  ConsoleOutput("Nippon2 PSP: leave");
  return succ;
}

#if 0 // 8/9/2014 jichi: cannot find a good function

/** 8/9/2014 jichi Typemoon.com PSP engine, 0.9.8, 0.9.9,
 *
 *  Sample game: Fate CCC
 *  This game is made by both TYPE-MOON and Imageepoch
 *  But the encoding is SHIFT-JIS than UTF-8 like other Imageepoch games.
 *  Otomate hook will produce significant amount of garbage.
 *
 *  Memory address is FIXED.
 *  There are two matches in the memory.
 *
 *  Debug method: breakpoint the memory address
 *  The hooked functions were looping which made it difficult to debug.
 *
 *  Two looped functions are as follows. The first one is used
 *  The second function is tested as bad.
 *
 *  Registers: (all of them are fixed except eax)
 *  EAX 08C91373
 *  ECX 00000016
 *  EDX 00000012
 *  EBX 0027A580
 *  ESP 0353E6D0
 *  EBP 0000000B
 *  ESI 0000001E
 *  EDI 00000001
 *  EIP 1351E14D
 *
 *  1351e12d   f0:90            lock nop                                 ; lock prefix is not allowed
 *  1351e12f   cc               int3
 *  1351e130   77 0f            ja short 1351e141
 *  1351e132   c705 a8aa1001 b8>mov dword ptr ds:[0x110aaa8],0x88ed7b8
 *  1351e13c  -e9 c31e27f0      jmp 03790004
 *  1351e141   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
 *  1351e147   81e0 ffffff3f    and eax,0x3fffffff
 *  1351e14d   0fbeb0 01004007  movsx esi,byte ptr ds:[eax+0x7400001] ; or jichi: hook here
 *  1351e154   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
 *  1351e15a   81e0 ffffff3f    and eax,0x3fffffff
 *  1351e160   8bb8 50004007    mov edi,dword ptr ds:[eax+0x7400050]
 *  1351e166   81e6 ff000000    and esi,0xff
 *  1351e16c   8bc6             mov eax,esi
 *  1351e16e   8b35 a8a71001    mov esi,dword ptr ds:[0x110a7a8]
 *  1351e174   0bf0             or esi,eax
 *  1351e176   c1e6 10          shl esi,0x10
 *  1351e179   c1fe 10          sar esi,0x10
 *  1351e17c   893d 78a71001    mov dword ptr ds:[0x110a778],edi
 *  1351e182   8935 7ca71001    mov dword ptr ds:[0x110a77c],esi
 *  1351e188   c705 e4a71001 d4>mov dword ptr ds:[0x110a7e4],0x88ed7d4
 *  1351e192   832d c4aa1001 07 sub dword ptr ds:[0x110aac4],0x7
 *  1351e199   e9 0e000000      jmp 1351e1ac
 *  1351e19e   01ac3e 8e08e97b  add dword ptr ds:[esi+edi+0x7be9088e],eb>
 *  1351e1a5   1e               push ds
 *  1351e1a6   27               daa
 *  1351e1a7   f0:90            lock nop                                 ; lock prefix is not allowed
 *  1351e1a9   cc               int3
 *
 *  13513f23   cc               int3
 *  13513f24   77 0f            ja short 13513f35
 *  13513f26   c705 a8aa1001 d4>mov dword ptr ds:[0x110aaa8],0x88e7bd4
 *  13513f30  -e9 cfc027f0      jmp 03790004
 *  13513f35   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  13513f3b   81e0 ffffff3f    and eax,0x3fffffff
 *  13513f41   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
 *  13513f48   8b3d 84a71001    mov edi,dword ptr ds:[0x110a784]
 *  13513f4e   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  13513f51   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  13513f57   81e0 ffffff3f    and eax,0x3fffffff
 *  13513f5d   8bd6             mov edx,esi
 *  13513f5f   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl ; jichi: bad hook
 *  13513f65   8b2d 78a71001    mov ebp,dword ptr ds:[0x110a778]
 *  13513f6b   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  13513f6e   33c0             xor eax,eax
 *  13513f70   3b3d 80a71001    cmp edi,dword ptr ds:[0x110a780]
 *  13513f76   0f9cc0           setl al
 *  13513f79   8bf0             mov esi,eax
 *  13513f7b   8b15 7ca71001    mov edx,dword ptr ds:[0x110a77c]
 *  13513f81   8d52 01          lea edx,dword ptr ds:[edx+0x1]
 *  13513f84   81fe 00000000    cmp esi,0x0
 *  13513f8a   892d 78a71001    mov dword ptr ds:[0x110a778],ebp
 *  13513f90   8915 7ca71001    mov dword ptr ds:[0x110a77c],edx
 *  13513f96   893d 84a71001    mov dword ptr ds:[0x110a784],edi
 *  13513f9c   8935 88a71001    mov dword ptr ds:[0x110a788],esi
 *  13513fa2   0f84 16000000    je 13513fbe
 *  13513fa8   832d c4aa1001 07 sub dword ptr ds:[0x110aac4],0x7
 *  13513faf  ^e9 70ffffff      jmp 13513f24
 *  13513fb4   01d4             add esp,edx
 *  13513fb6   7b 8e            jpo short 13513f46
 *  13513fb8   08e9             or cl,ch
 *  13513fba   65:c027 f0       shl byte ptr gs:[edi],0xf0               ; shift constant out of range 1..31
 *  13513fbe   832d c4aa1001 07 sub dword ptr ds:[0x110aac4],0x7
 *  13513fc5   e9 0e000000      jmp 13513fd8
 *  13513fca   01f0             add eax,esi
 *  13513fcc   7b 8e            jpo short 13513f5c
 *  13513fce   08e9             or cl,ch
 *  13513fd0   4f               dec edi
 *  13513fd1   c027 f0          shl byte ptr ds:[edi],0xf0               ; shift constant out of range 1..31
 *  13513fd4   90               nop
 *  13513fd5   cc               int3
 *  13513fd6   cc               int3
 */
// Read text from dl
static void SpecialPSPHookTypeMoon(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  DWORD eax = regof(eax, esp_base);
  DWORD text = eax + hp->user_value - 1; // the text is in the previous byte
  if (BYTE c = *(BYTE *)text) { // unsigned char
    *data = text;
    *len = ::LeadByteTable[c]; // 1 or 2
    //*split = regof(ecx, esp_base);
    //*split = regof(edx, esp_base);
    *split = regof(ebx, esp_base);
  }
}
bool InsertTypeMoonPSPHook()
{
  ConsoleOutput("TypeMoon PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 1351e130   77 0f            ja short 1351e141
    0xc7,0x05, XX8,                 // 1351e132   c705 a8aa1001 b8>mov dword ptr ds:[0x110aaa8],0x88ed7b8
    0xe9, XX4,                      // 1351e13c  -e9 c31e27f0      jmp 03790004
    0x8b,0x05, XX4,                 // 1351e141   8b05 aca71001    mov eax,dword ptr ds:[0x110a7ac]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1351e147   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 1351e14d   0fbeb0 01004007  movsx esi,byte ptr ds:[eax+0x7400001] ;  jichi: hook here
    0x8b,0x05, XX4,                 // 1351e154   8b05 dca71001    mov eax,dword ptr ds:[0x110a7dc]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1351e15a   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb8, XX4,                 // 1351e160   8bb8 50004007    mov edi,dword ptr ds:[eax+0x7400050]
    0x81,0xe6, 0xff,0x00,0x00,0x00, // 1351e166   81e6 ff000000    and esi,0xff
    0x8b,0xc6,                      // 1351e16c   8bc6             mov eax,esi
    0x8b,0x35, XX4,                 // 1351e16e   8b35 a8a71001    mov esi,dword ptr ds:[0x110a7a8]
    0x0b,0xf0,                      // 1351e174   0bf0             or esi,eax
    0xc1,0xe6, 0x10,                // 1351e176   c1e6 10          shl esi,0x10
    0xc1,0xfe, 0x10                 // 1351e179   c1fe 10          sar esi,0x10
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x1351e14d - 0x1351e130 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("TypeMoon PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|NO_CONTEXT;
    hp.text_fun = SpecialPSPHookTypeMoon;
    ConsoleOutput("TypeMoon PSP: INSERT");
    NewHook(hp, "TypeMoon PSP");
  }

  ConsoleOutput("TypeMoon PSP: leave");
  return addr;
}

#endif // 0

#if 0 // 7/25/2014: This function is not invoked? Why?
/** 7/22/2014 jichi: KOEI TECMO PSP, 0.9.8
 *  Sample game: 金色のコルダ3
 *
 *  134598e2   cc               int3
 *  134598e3   cc               int3
 *  134598e4   77 0f            ja short 134598f5
 *  134598e6   c705 a8aa1001 8c>mov dword ptr ds:[0x110aaa8],0x880f08c
 *  134598f0  -e9 0f67fbef      jmp 03410004
 *  134598f5   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  134598fb   81e0 ffffff3f    and eax,0x3fffffff
 *  13459901   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: hook here
 *  13459907   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
 *  1345990d   8d7f 04          lea edi,dword ptr ds:[edi+0x4]
 *  13459910   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
 *  13459916   81e0 ffffff3f    and eax,0x3fffffff
 *  1345991c   89b0 00004007    mov dword ptr ds:[eax+0x7400000],esi
 *  13459922   8b2d 84a71001    mov ebp,dword ptr ds:[0x110a784]
 *  13459928   8d6d 04          lea ebp,dword ptr ss:[ebp+0x4]
 *  1345992b   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
 *  13459931   81fa 01000000    cmp edx,0x1
 *  13459937   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  1345993d   893d 7ca71001    mov dword ptr ds:[0x110a77c],edi
 *  13459943   892d 84a71001    mov dword ptr ds:[0x110a784],ebp
 *  13459949   c705 88a71001 01>mov dword ptr ds:[0x110a788],0x1
 *  13459953   0f84 16000000    je 1345996f
 *  13459959   832d c4aa1001 09 sub dword ptr ds:[0x110aac4],0x9
 *  13459960   e9 17000000      jmp 1345997c
 *  13459965   0190 f08008e9    add dword ptr ds:[eax+0xe90880f0],edx
 *  1345996b   b4 66            mov ah,0x66
 *  1345996d   fb               sti
 *  1345996e   ef               out dx,eax                               ; i/o command
 *  1345996f   832d c4aa1001 09 sub dword ptr ds:[0x110aac4],0x9
 *  13459976  ^e9 ddc1ffff      jmp 13455b58
 *  1345997b   90               nop
 */
bool InsertTecmoPSPHook()
{
  ConsoleOutput("Tecmo PSP: enter");

  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 134598e4   77 0f            ja short 134598f5
    0xc7,0x05, XX8,                 // 134598e6   c705 a8aa1001 8c>mov dword ptr ds:[0x110aaa8],0x880f08c
    0xe9, XX4,                      // 134598f0  -e9 0f67fbef      jmp 03410004
    0x8b,0x05, XX4,                 // 134598f5   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 134598fb   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xb0, XX4,                 // 13459901   8bb0 00004007    mov esi,dword ptr ds:[eax+0x7400000] ; jichi: hook here
    0x8b,0x3d, XX4,                 // 13459907   8b3d 7ca71001    mov edi,dword ptr ds:[0x110a77c]
    0x8d,0x7f, 0x04,                // 1345990d   8d7f 04          lea edi,dword ptr ds:[edi+0x4]
    0x8b,0x05, XX4,                 // 13459910   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13459916   81e0 ffffff3f    and eax,0x3fffffff
    0x89,0xb0 //, XX4,                 // 1345991c   89b0 00004007    mov dword ptr ds:[eax+0x7400000],esi
    //0x8b,0x2d, XX4,                 // 13459922   8b2d 84a71001    mov ebp,dword ptr ds:[0x110a784]
    //0x8d,0x6d, 0x04,                // 13459928   8d6d 04          lea ebp,dword ptr ss:[ebp+0x4]
    //0x8b,0x15, XX4,                 // 1345992b   8b15 78a71001    mov edx,dword ptr ds:[0x110a778]
    //0x81,0xfa, 0x01,0x00,0x00,0x00  // 13459931   81fa 01000000    cmp edx,0x1
  };
  enum { memory_offset = 2 };
  enum { addr_offset = 0x13459901 - 0x134598e4 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Tecmo PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    hp.offset=regoffset(eax);
    hp.split = regoffset(ecx);
    hp.text_fun = SpecialPSPHook;
    ConsoleOutput("Tecmo PSP: INSERT");
    NewHook(hp, "Tecmo PSP");
  }

  ConsoleOutput("Tecmo PSP: leave");
  return addr;
}
#endif // 0

#if 0 // 8/9/2014 jichi: does not work

bool InsertKadokawaPSPHook()
{
  ConsoleOutput("Kadokawa PSP: enter");
  const BYTE bytes[] =  {
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 134844f3   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0, XX4,            // 134844f9   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here, byte by byte
    0x8b,0x05, XX4,                 // 13484500   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 13484506   81e0 ffffff3f    and eax,0x3fffffff
    0x8b,0xd6,                      // 1348450c   8bd6             mov edx,esi
    0x88,0x90, XX4,                 // 1348450e   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl
    0x8b,0x3d, XX4,                 // 13484514   8b3d 84a71001    mov edi,dword ptr ds:[0x110a784]
    0x8d,0x7f, 0x01,                // 1348451a   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
    0x8b,0x2d, XX4,                 // 1348451d   8b2d 7ca71001    mov ebp,dword ptr ds:[0x110a77c]
    0x8d,0x6d, 0x01,                // 13484523   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
    0x3b,0x3d, XX4,                 // 13484526   3b3d 74a71001    cmp edi,dword ptr ds:[0x110a774]
    0x89,0x35, XX4,                 // 1348452c   8935 70a71001    mov dword ptr ds:[0x110a770],esi
    0x89,0x2d, XX4,                 // 13484532   892d 7ca71001    mov dword ptr ds:[0x110a77c],ebp
    0x89,0x3d, XX4,                 // 13484538   893d 84a71001    mov dword ptr ds:[0x110a784],edi
    // Above is not sufficient
    //0x0f,0x84, XX4,                 // 1348453e   0f84 16000000    je 1348455a
    //0x83,0x2d, XX4, 0x05,           // 13484544   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
    //0xe9, XX4,                      // 1348454b  ^e9 8cffffff      jmp 134844dc
    //0x01,0x38,                      // 13484550   0138             add dword ptr ds:[eax],edi
    //0xb0, 0x84,                     // 13484552   b0 84            mov al,0x84
    //0x08,0xe9                       // 13484554   08e9             or cl,ch
    // Below will change at runtime
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x134844f9 - 0x134844f3 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr) {
    ConsoleOutput("Kadokawa PSP: pattern not found");
    return false;
  }
  addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes), addr);
  addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes), addr);

  if (!addr)
    ConsoleOutput("Kadokawa PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    hp.offset=regoffset(eax);
    hp.split = regoffset(ecx);
    hp.length_offset = 1; // byte by byte
    hp.text_fun = SpecialPSPHook;

    //GROWL_DWORD2(hp.address, hp.user_value);
    ConsoleOutput("Kadokawa PSP: INSERT");
    NewHook(hp, "Kadokawa PSP");
  }

  ConsoleOutput("Kadokawa PSP: leave");
  return addr;
}
#endif // 0

#if 0 // FIXME: I am not able to find stable pattern in PSP 0.9.9.1

/** 9/21/2014 jichi Otomate PPSSPP 0.9.9.1
 *  Sample game: Amnesia Later
 *
 *  There are four fixed memory addresses.
 *  The two out of four can be used.
 *  (The other twos have loops or cannot be debugged).
 *
 *  This function is the same as PPSSPP 0.9.9.1 (?).
 *
 *  14039126   cc               int3
 *  14039127   cc               int3
 *  14039128   77 0f            ja short 14039139
 *  1403912a   c705 988e1301 3c>mov dword ptr ds:[0x1138e98],0x8922c3c
 *  14039134  -e9 cb6e83ef      jmp 03870004
 *  14039139   8b05 688b1301    mov eax,dword ptr ds:[0x1138b68]
 *  1403913f   81e0 ffffff3f    and eax,0x3fffffff
 *  14039145   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000]   ; jichi: text accessed, but looped
 *  1403914c   8b05 6c8b1301    mov eax,dword ptr ds:[0x1138b6c]
 *  14039152   81e0 ffffff3f    and eax,0x3fffffff
 *  14039158   0fbeb8 00000008  movsx edi,byte ptr ds:[eax+0x8000000]
 *  1403915f   3bf7             cmp esi,edi
 *  14039161   8935 748b1301    mov dword ptr ds:[0x1138b74],esi
 *  14039167   893d 7c8b1301    mov dword ptr ds:[0x1138b7c],edi
 *  1403916d   0f84 2f000000    je 140391a2
 *  14039173   8b05 688b1301    mov eax,dword ptr ds:[0x1138b68]
 *  14039179   81e0 ffffff3f    and eax,0x3fffffff
 *  1403917f   0fb6b0 00000008  movzx esi,byte ptr ds:[eax+0x8000000]   ; jichi: hook here
 *  14039186   8935 608b1301    mov dword ptr ds:[0x1138b60],esi
 *  1403918c   832d b48e1301 04 sub dword ptr ds:[0x1138eb4],0x4
 *  14039193   e9 24000000      jmp 140391bc
 *  14039198   0170 2c          add dword ptr ds:[eax+0x2c],esi
 *  1403919b   92               xchg eax,edx
 *  1403919c   08e9             or cl,ch
 *  1403919e   816e 83 ef832db4 sub dword ptr ds:[esi-0x7d],0xb42d83ef
 *  140391a5   8e13             mov ss,word ptr ds:[ebx]                 ; modification of segment register
 *  140391a7   0104e9           add dword ptr ds:[ecx+ebp*8],eax
 *  140391aa   b2 59            mov dl,0x59
 *  140391ac   0000             add byte ptr ds:[eax],al
 *  140391ae   014c2c 92        add dword ptr ss:[esp+ebp-0x6e],ecx
 *  140391b2   08e9             or cl,ch
 *  140391b4   6b6e 83 ef       imul ebp,dword ptr ds:[esi-0x7d],-0x11
 *  140391b8   90               nop
 *  140391b9   cc               int3
 *  140391ba   cc               int3
 */
// Get bytes in esi
static void SpecialPSPHookOtomate2(hook_context *context,  HookParam *hp, uintptr_t *data, uintptr_t *split, size_t*len)
{
  //static uniquemap uniq;
  DWORD text = esp_base + regoffset(esi);
  if (*(LPCSTR *)text) {
    *split = regof(ecx, esp_base); // this would cause lots of texts, but it works for all games
    *data = text;
    *len = 1;
  }
}

bool InsertOtomate2PSPHook()
{
  ConsoleOutput("Otomate2 PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 14039128   77 0f            ja short 14039139
    0xc7,0x05, XX8,                 // 1403912a   c705 988e1301 3c>mov dword ptr ds:[0x1138e98],0x8922c3c
    0xe9, XX4,                      // 14039134  -e9 cb6e83ef      jmp 03870004
    0x8b,0x05, XX4,                 // 14039139   8b05 688b1301    mov eax,dword ptr ds:[0x1138b68]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1403913f   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 14039145   0fbeb0 00000008  movsx esi,byte ptr ds:[eax+0x8000000]   ; jichi: text accessed, but looped
    0x8b,0x05, XX4,                 // 1403914c   8b05 6c8b1301    mov eax,dword ptr ds:[0x1138b6c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14039152   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb8, XX4,            // 14039158   0fbeb8 00000008  movsx edi,byte ptr ds:[eax+0x8000000]
    0x3b,0xf7,                      // 1403915f   3bf7             cmp esi,edi
    0x89,0x35, XX4,                 // 14039161   8935 748b1301    mov dword ptr ds:[0x1138b74],esi
    0x89,0x3d, XX4,                 // 14039167   893d 7c8b1301    mov dword ptr ds:[0x1138b7c],edi
    0x0f,0x84, 0x2f,0x00,0x00,0x00, // 1403916d   0f84 2f000000    je 140391a2

    //0x8b,0x05, XX4,                 // 14039173   8b05 688b1301    mov eax,dword ptr ds:[0x1138b68]
    //0x81,0xe0, 0xff,0xff,0xff,0x3f, // 14039179   81e0 ffffff3f    and eax,0x3fffffff
    //0x0f,0xb6,0xb0, XX4,            // 1403917f   0fb6b0 00000008  movzx esi,byte ptr ds:[eax+0x8000000]   ; jichi: text accessed
    //0x89,0x35, XX4,                 // 14039186   8935 608b1301    mov dword ptr ds:[0x1138b60],esi   ; jichi: hook here, get lower bytes in esi
    //0x83,0x2d, XX4, 0x04            // 1403918c   832d b48e1301 04 sub dword ptr ds:[0x1138eb4],0x4
  };
  enum { addr_offset = 0x14039186 - 0x14039128 };

  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr) {
    ConsoleOutput("Otomate2 PSP: leave: first pattern not found");
    return false;
  }
  addr += addr_offset;

  //0x89,0x35, XX4,                 // 14039186   8935 608b1301    mov dword ptr ds:[0x1138b60],esi   ; jichi: hook here, get lower bytes in esi
  enum : WORD { mov_esi = 0x3589 };
  if (*(WORD *)addr != mov_esi) {
    ConsoleOutput("Otomate2 PSP: leave: second pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING|NO_CONTEXT;
  hp.text_fun = SpecialPSPHookOtomate2;
  ConsoleOutput("Otomate2 PSP: INSERT");
  NewHook(hp, "Otomate PSP");

  ConsoleOutput("Otomate2 PSP: leave");
  return addr;
}

#endif // 0

/** 8/9/2014 jichi Kadokawa.co.jp PSP engine, 0.9.8, ?,
 *
 *  Sample game: 未来日�work on 0.9.8, not tested on 0.9.9
 *
 *  FIXME: Currently, only the character name works
 *
 *  Memory address is FIXED.
 *  Debug method: predict and breakpoint the memory address
 *
 *  There are two matches in the memory, and only one function accessing them.
 *
 *  Character name function is as follows.
 *  The scenario is the text after the name.
 *
 *  1348d79f   cc               int3
 *  1348d7a0   77 0f            ja short 1348d7b1
 *  1348d7a2   c705 a8aa1001 fc>mov dword ptr ds:[0x110aaa8],0x884c6fc
 *  1348d7ac  -e9 532844f0      jmp 038d0004
 *  1348d7b1   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
 *  1348d7b7   81e0 ffffff3f    and eax,0x3fffffff
 *  1348d7bd   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
 *  1348d7c4   81fe 00000000    cmp esi,0x0
 *  1348d7ca   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  1348d7d0   0f85 2f000000    jnz 1348d805
 *  1348d7d6   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  1348d7dc   81e0 ffffff3f    and eax,0x3fffffff
 *  1348d7e2   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
 *  1348d7e9   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  1348d7ef   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  1348d7f6   c705 a8aa1001 5c>mov dword ptr ds:[0x110aaa8],0x884c75c
 *  1348d800  -e9 1e2844f0      jmp 038d0023
 *  1348d805   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  1348d80c   e9 0b000000      jmp 1348d81c
 *  1348d811   0108             add dword ptr ds:[eax],ecx
 *  1348d813   c78408 e9082844 >mov dword ptr ds:[eax+ecx+0x442808e9],0x>
 *  1348d81e   c705 a8aa1001 08>mov dword ptr ds:[0x110aaa8],0x884c708
 *  1348d828  -e9 d72744f0      jmp 038d0004
 *  1348d82d   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
 *  1348d833   81e0 ffffff3f    and eax,0x3fffffff
 *  1348d839   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
 *  1348d840   81fe 00000000    cmp esi,0x0
 *  1348d846   8935 88a71001    mov dword ptr ds:[0x110a788],esi
 *  1348d84c   0f85 16000000    jnz 1348d868
 *  1348d852   832d c4aa1001 03 sub dword ptr ds:[0x110aac4],0x3
 *  1348d859   e9 aa030000      jmp 1348dc08
 *  1348d85e   0154c7 84        add dword ptr ds:[edi+eax*8-0x7c],edx
 *  1348d862   08e9             or cl,ch
 *  1348d864   bb 2744f083      mov ebx,0x83f04427
 *  1348d869   2d c4aa1001      sub eax,0x110aac4
 *  1348d86e   03e9             add ebp,ecx
 *  1348d870   0c 00            or al,0x0
 *  1348d872   0000             add byte ptr ds:[eax],al
 *  1348d874   0114c7           add dword ptr ds:[edi+eax*8],edx
 *  1348d877   8408             test byte ptr ds:[eax],cl
 *  1348d879  -e9 a52744f0      jmp 038d0023
 *  1348d87e   90               nop
 *  1348d87f   cc               int3
 *
 *  Scenario function is as follows.
 *  But I am not able to find it at runtime.
 *
 *  13484483   90               nop
 *  13484484   77 0f            ja short 13484495
 *  13484486   c705 a8aa1001 30>mov dword ptr ds:[0x110aaa8],0x884b030
 *  13484490  -e9 6fbb59f3      jmp 06a20004
 *  13484495   8b35 74a71001    mov esi,dword ptr ds:[0x110a774]
 *  1348449b   81fe 00000000    cmp esi,0x0
 *  134844a1   9c               pushfd
 *  134844a2   8bc6             mov eax,esi
 *  134844a4   8b35 84a71001    mov esi,dword ptr ds:[0x110a784]
 *  134844aa   03f0             add esi,eax
 *  134844ac   8935 74a71001    mov dword ptr ds:[0x110a774],esi
 *  134844b2   9d               popfd
 *  134844b3   0f8f 0c000000    jg 134844c5
 *  134844b9   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  134844c0  ^e9 23b0f9ff      jmp 1341f4e8
 *  134844c5   832d c4aa1001 02 sub dword ptr ds:[0x110aac4],0x2
 *  134844cc   e9 0b000000      jmp 134844dc
 *  134844d1   0138             add dword ptr ds:[eax],edi
 *  134844d3   b0 84            mov al,0x84
 *  134844d5   08e9             or cl,ch
 *  134844d7   48               dec eax
 *  134844d8   bb 59f39077      mov ebx,0x7790f359
 *  134844dd   0fc7             ???                                      ; unknown command
 *  134844df   05 a8aa1001      add eax,0x110aaa8
 *  134844e4   38b0 8408e917    cmp byte ptr ds:[eax+0x17e90884],dh
 *  134844ea   bb 59f38b05      mov ebx,0x58bf359
 *  134844ef  ^7c a7            jl short 13484498
 *  134844f1   1001             adc byte ptr ds:[ecx],al
 *  134844f3   81e0 ffffff3f    and eax,0x3fffffff
 *  134844f9   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here, byte by byte
 *  13484500   8b05 84a71001    mov eax,dword ptr ds:[0x110a784]
 *  13484506   81e0 ffffff3f    and eax,0x3fffffff
 *  1348450c   8bd6             mov edx,esi
 *  1348450e   8890 00004007    mov byte ptr ds:[eax+0x7400000],dl
 *  13484514   8b3d 84a71001    mov edi,dword ptr ds:[0x110a784]
 *  1348451a   8d7f 01          lea edi,dword ptr ds:[edi+0x1]
 *  1348451d   8b2d 7ca71001    mov ebp,dword ptr ds:[0x110a77c]
 *  13484523   8d6d 01          lea ebp,dword ptr ss:[ebp+0x1]
 *  13484526   3b3d 74a71001    cmp edi,dword ptr ds:[0x110a774]
 *  1348452c   8935 70a71001    mov dword ptr ds:[0x110a770],esi
 *  13484532   892d 7ca71001    mov dword ptr ds:[0x110a77c],ebp
 *  13484538   893d 84a71001    mov dword ptr ds:[0x110a784],edi
 *  1348453e   0f84 16000000    je 1348455a
 *  13484544   832d c4aa1001 05 sub dword ptr ds:[0x110aac4],0x5
 *  1348454b  ^e9 8cffffff      jmp 134844dc
 *  13484550   0138             add dword ptr ds:[eax],edi
 *  13484552   b0 84            mov al,0x84
 *  13484554   08e9             or cl,ch
 *  13484556   c9               leave
 *  13484557   ba 59f3832d      mov edx,0x2d83f359
 *  1348455c   c4aa 100105e9    les ebp,fword ptr ds:[edx+0xe9050110]    ; modification of segment register
 *  13484562   0e               push cs
 *  13484563   0000             add byte ptr ds:[eax],al
 *  13484565   0001             add byte ptr ds:[ecx],al
 *  13484567   4c               dec esp
 *  13484568   b0 84            mov al,0x84
 *  1348456a   08e9             or cl,ch
 *  1348456c   b3 ba            mov bl,0xba
 *  1348456e   59               pop ecx
 *  1348456f   f3:              prefix rep:                              ; superfluous prefix
 *  13484570   90               nop
 *  13484571   cc               int3
 *  13484572   cc               int3
 *  13484573   cc               int3
 */
bool InsertKadokawaNamePSPHook()
{
  ConsoleOutput("Kadokawa Name PSP: enter");
  const BYTE bytes[] =  {
    0x77, 0x0f,                     // 1348d7a0   77 0f            ja short 1348d7b1
    0xc7,0x05, XX8,                 // 1348d7a2   c705 a8aa1001 fc>mov dword ptr ds:[0x110aaa8],0x884c6fc
    0xe9, XX4,                      // 1348d7ac  -e9 532844f0      jmp 038d0004
    0x8b,0x05, XX4,                 // 1348d7b1   8b05 78a71001    mov eax,dword ptr ds:[0x110a778]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1348d7b7   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xb6,0xb0, XX4,            // 1348d7bd   0fb6b0 00004007  movzx esi,byte ptr ds:[eax+0x7400000] ; jichi: hook here
    0x81,0xfe, 0x00,0x00,0x00,0x00, // 1348d7c4   81fe 00000000    cmp esi,0x0
    0x89,0x35, XX4,                 // 1348d7ca   8935 70a71001    mov dword ptr ds:[0x110a770],esi
    0x0f,0x85, 0x2f,0x00,0x00,0x00, // 1348d7d0   0f85 2f000000    jnz 1348d805
    0x8b,0x05, XX4,                 // 1348d7d6   8b05 7ca71001    mov eax,dword ptr ds:[0x110a77c]
    0x81,0xe0, 0xff,0xff,0xff,0x3f, // 1348d7dc   81e0 ffffff3f    and eax,0x3fffffff
    0x0f,0xbe,0xb0, XX4,            // 1348d7e2   0fbeb0 00004007  movsx esi,byte ptr ds:[eax+0x7400000]
    0x89,0x35 //, XX4,              // 1348d7e9   8935 70a71001    mov dword ptr ds:[0x110a770],esi
  };
  enum { memory_offset = 3 };
  enum { addr_offset = 0x1348d7bd - 0x1348d7a0 };
  auto succ=false;
  DWORD addr = SafeMatchBytesInPSPMemory(bytes, sizeof(bytes));
  if (!addr)
    ConsoleOutput("Kadokawa Name PSP: pattern not found");
  else {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.type = USING_STRING|USING_SPLIT|NO_CONTEXT;
    hp.offset=regoffset(eax);
    hp.split = regoffset(edx);
    hp.text_fun = SpecialPSPHook;

    //GROWL_DWORD2(hp.address, hp.user_value);
    ConsoleOutput("Kadokawa Name PSP: INSERT");
    succ|=NewHook(hp, "Kadokawa Name PSP");
  }

  ConsoleOutput("Kadokawa Name PSP: leave");
  return succ;
}

bool InsertPPSSPPHooks()
{
  //if (PPSSPP_VERSION[1] == 9 && (PPSSPP_VERSION[2] > 9 || PPSSPP_VERSION[2] == 9 && PPSSPP_VERSION[3] >= 1)) // >= 0.9.9.1

  ConsoleOutput("PPSSPP: enter");

  // http://stackoverflow.com/questions/940707/how-do-i-programatically-get-the-version-of-a-dll-or-exe-file
    // get the version info for the file requested
	 // if (DWORD dwSize = ::GetFileVersionInfoSizeW(processPath, nullptr)) {
	 // UINT len = 0;
	 // BYTE * buf = new BYTE[dwSize];
	 // VS_FIXEDFILEINFO * info = nullptr;
	 // if (::GetFileVersionInfoW(processPath, 0, dwSize, buf)
		//   && ::VerQueryValueW(buf, L"\\", (LPVOID*)&info, &len)
		//   && info) 
	 // {
		//  PPSSPP_VERSION[0] = HIWORD(info->dwFileVersionMS),
		//	  PPSSPP_VERSION[1] = LOWORD(info->dwFileVersionMS),
		//	  PPSSPP_VERSION[2] = HIWORD(info->dwFileVersionLS),
		//	  PPSSPP_VERSION[3] = LOWORD(info->dwFileVersionLS);
		//  
	 // } 
	 // else 
		//  ConsoleOutput("failed to get PPSSPP version");
	 // delete[] buf;
	 // 
  //}


  if (PPSSPP_VERSION[1] == 9 && PPSSPP_VERSION[2] == 9 && PPSSPP_VERSION[3] == 0) // 0.9.9.0
    InsertOtomatePPSSPPHook();

  //bool engineFound = false;
  Insert5pbPSPHook();
  InsertCyberfrontPSPHook();
  InsertImageepoch2PSPHook();
  InsertFelistellaPSPHook();

  InsertBroccoliPSPHook();
  InsertIntensePSPHook();
  //InsertKadokawaNamePSPHook(); // disabled
  InsertKonamiPSPHook();

  if (PPSSPP_VERSION[1] == 9 && PPSSPP_VERSION[2] == 8) { // only works for 0.9.8 anyway
    InsertNippon1PSPHook();
    InsertNippon2PSPHook(); // This could crash PPSSPP 099 just like 5pb
  }

  //InsertTecmoPSPHook();

  // Generic hooks

  bool bandaiFound = InsertBandaiPSPHook();
  InsertBandaiNamePSPHook();

  // Hooks whose pattern is not generic enouph

  InsertYetiPSPHook();
  InsertYeti2PSPHook();

  InsertAlchemistPSPHook();
  InsertAlchemist2PSPHook();

  //InsertTypeMoonPSPHook() // otomate is creating too many garbage
  //|| InsertOtomatePSPHook();
  InsertOtomatePSPHook();

  if (!bandaiFound) {
    // KID pattern is a subset of BANDAI, and hence MUST NOT be together with BANDAI
    // Sample BANDAI game that could be broken by KID: 寮�のサクリファイス
    InsertKidPSPHook(); // KID could lose text, could exist in multiple game

    InsertImageepochPSPHook();  // Imageepoch could crash vnrcli for School Rumble PSP
  }

  ConsoleOutput("PPSSPP: leave");
  return true;
}
#endif

bool PPSSPPengine::attach_function() {
  return InsertPPSSPPcommonhooks();
}
 