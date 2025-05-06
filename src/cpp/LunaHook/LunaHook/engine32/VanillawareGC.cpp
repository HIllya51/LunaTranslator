#include "VanillawareGC.h"

/** jichi 7/20/2014 Vanillaware
 *  Tested game: 朧村正
 *
 *  Debugging method: grep the saving message
 *
 *  1609415e   cc               int3
 *  1609415f   cc               int3
 *  16094160   77 0f            ja short 16094171
 *  16094162   c705 00fb6701 80>mov dword ptr ds:[0x167fb00],0x80216b80
 *  1609416c  -e9 f9be06f1      jmp 0710006a
 *  16094171   8b35 8cf86701    mov esi,dword ptr ds:[0x167f88c]
 *  16094177   81c6 ffffffff    add esi,-0x1
 *  1609417d   8bce             mov ecx,esi
 *  1609417f   81c1 01000000    add ecx,0x1
 *  16094185   f7c1 0000000c    test ecx,0xc000000
 *  1609418b   74 0b            je short 16094198
 *  1609418d   51               push ecx
 *  1609418e   e8 36bff9f2      call 090300c9
 *  16094193   83c4 04          add esp,0x4
 *  16094196   eb 11            jmp short 160941a9
 *  16094198   8bc1             mov eax,ecx
 *  1609419a   81e0 ffffff3f    and eax,0x3fffffff
 *  160941a0   0fb680 00000810  movzx eax,byte ptr ds:[eax+0x10080000] ; jichi: hook here
 *  160941a7   66:90            nop
 *  160941a9   81c6 01000000    add esi,0x1
 *  160941af   8905 80f86701    mov dword ptr ds:[0x167f880],eax
 *  160941b5   813d 80f86701 00>cmp dword ptr ds:[0x167f880],0x0
 *  160941bf   c705 8cf86701 00>mov dword ptr ds:[0x167f88c],0x0
 *  160941c9   8935 90f86701    mov dword ptr ds:[0x167f890],esi
 *  160941cf   7c 14            jl short 160941e5
 *  160941d1   7f 09            jg short 160941dc
 *  160941d3   c605 0cfb6701 02 mov byte ptr ds:[0x167fb0c],0x2
 *  160941da   eb 26            jmp short 16094202
 *  160941dc   c605 0cfb6701 04 mov byte ptr ds:[0x167fb0c],0x4
 *  160941e3   eb 07            jmp short 160941ec
 *  160941e5   c605 0cfb6701 08 mov byte ptr ds:[0x167fb0c],0x8
 *  160941ec   832d 7c4cb101 06 sub dword ptr ds:[0x1b14c7c],0x6
 *  160941f3   e9 20000000      jmp 16094218
 *  160941f8   0188 6b2180e9    add dword ptr ds:[eax+0xe980216b],ecx
 *  160941fe   0e               push cs
 *  160941ff   be 06f1832d      mov esi,0x2d83f106
 *  16094204   7c 4c            jl short 16094252
 *  16094206   b1 01            mov cl,0x1
 *  16094208   06               push es
 *  16094209   e9 c2000000      jmp 160942d0
 *  1609420e   0198 6b2180e9    add dword ptr ds:[eax+0xe980216b],ebx
 *  16094214   f8               clc
 *  16094215   bd 06f1770f      mov ebp,0xf77f106
 *  1609421a   c705 00fb6701 88>mov dword ptr ds:[0x167fb00],0x80216b88
 *  16094224  -e9 41be06f1      jmp 0710006a
 *  16094229   8b0d 90f86701    mov ecx,dword ptr ds:[0x167f890]
 *  1609422f   81c1 01000000    add ecx,0x1
 *  16094235   f7c1 0000000c    test ecx,0xc000000
 *  1609423b   74 0b            je short 16094248
 *  1609423d   51               push ecx
 *  1609423e   e8 86bef9f2      call 090300c9
 *  16094243   83c4 04          add esp,0x4
 *  16094246   eb 11            jmp short 16094259
 *  16094248   8bc1             mov eax,ecx
 *  1609424a   81e0 ffffff3f    and eax,0x3fffffff
 *  16094250   0fb680 00000810  movzx eax,byte ptr ds:[eax+0x10080000]
 *  16094257   66:90            nop
 *  16094259   8b35 90f86701    mov esi,dword ptr ds:[0x167f890]
 *  1609425f   81c6 01000000    add esi,0x1
 *  16094265   8905 80f86701    mov dword ptr ds:[0x167f880],eax
 *  1609426b   8105 8cf86701 01>add dword ptr ds:[0x167f88c],0x1
 *  16094275   813d 80f86701 00>cmp dword ptr ds:[0x167f880],0x0
 *  1609427f   8935 90f86701    mov dword ptr ds:[0x167f890],esi
 *  16094285   7c 14            jl short 1609429b
 *  16094287   7f 09            jg short 16094292
 *  16094289   c605 0cfb6701 02 mov byte ptr ds:[0x167fb0c],0x2
 *  16094290   eb 26            jmp short 160942b8
 *  16094292   c605 0cfb6701 04 mov byte ptr ds:[0x167fb0c],0x4
 *  16094299   eb 07            jmp short 160942a2
 *  1609429b   c605 0cfb6701 08 mov byte ptr ds:[0x167fb0c],0x8
 *  160942a2   832d 7c4cb101 04 sub dword ptr ds:[0x1b14c7c],0x4
 *  160942a9  ^e9 6affffff      jmp 16094218
 *  160942ae   0188 6b2180e9    add dword ptr ds:[eax+0xe980216b],ecx
 *  160942b4   58               pop eax
 *  160942b5   bd 06f1832d      mov ebp,0x2d83f106
 *  160942ba   7c 4c            jl short 16094308
 *  160942bc   b1 01            mov cl,0x1
 *  160942be   04 e9            add al,0xe9
 *  160942c0   0c 00            or al,0x0
 *  160942c2   0000             add byte ptr ds:[eax],al
 *  160942c4   0198 6b2180e9    add dword ptr ds:[eax+0xe980216b],ebx
 *  160942ca   42               inc edx
 *  160942cb   bd 06f1cccc      mov ebp,0xccccf106
 *  160942d0   77 0f            ja short 160942e1
 *  160942d2   c705 00fb6701 98>mov dword ptr ds:[0x167fb00],0x80216b98
 *  160942dc  -e9 89bd06f1      jmp 0710006a
 *  160942e1   8b05 84fb6701    mov eax,dword ptr ds:[0x167fb84]
 *  160942e7   81e0 fcffffff    and eax,0xfffffffc
 *  160942ed   8905 00fb6701    mov dword ptr ds:[0x167fb00],eax
 *  160942f3   832d 7c4cb101 01 sub dword ptr ds:[0x1b14c7c],0x1
 *  160942fa  -e9 11bd06f1      jmp 07100010
 *  160942ff   832d 7c4cb101 01 sub dword ptr ds:[0x1b14c7c],0x1
 *  16094306  ^e9 91f8ffff      jmp 16093b9c
 *  1609430b   cc               int3
 */
namespace
{ // unnamed

  // Return true if the text is a garbage character
  inline bool _vanillawaregarbage_ch(char c)
  {
    return c == ' ' || c == '.' || c == '/' || c >= '0' && c <= '9' || c >= 'A' && c <= 'z' // also ignore ASCII 91-96: [ \ ] ^ _ `
        ;
  }

  // Return true if the text is full of garbage characters
  bool _vanillawaregarbage(LPCSTR p)
  {
    enum
    {
      MAX_LENGTH = VNR_TEXT_CAPACITY
    };
    for (int count = 0; *p && count < MAX_LENGTH; count++, p++)
      if (!_vanillawaregarbage_ch(*p))
        return false;
    return true;
  }
} // unnamed namespace

static void SpecialGCHookVanillaware(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
  DWORD eax = context->eax;
  LPCSTR text = LPCSTR(eax + hp->user_value);
  static LPCSTR lasttext;
  if (lasttext != text && *text && !_vanillawaregarbage(text))
  {
    lasttext = text;
    *split = context->ecx;
    buffer->from(text);
    //*split = FIXED_SPLIT_VALUE;
  }
}

// jichi 7/17/2014: Search mapped memory for emulators
ULONG _SafeMatchBytesInMappedMemory(LPCVOID pattern, DWORD patternSize, BYTE wildcard,
                                    ULONG start, ULONG stop, ULONG step)
{
  for (ULONG i = start; i < stop; i += step) // + patternSize to avoid overlap
    if (ULONG r = SafeFindBytes(pattern, patternSize, i, i + step + patternSize + 1))
      return r;
  return 0;
}
ULONG SafeMatchBytesInGCMemory(LPCVOID pattern, DWORD patternSize)
{
  enum : ULONG
  {
    start = MemDbg::MappedMemoryStartAddress // 0x01000000
    ,
    stop = MemDbg::MemoryStopAddress // 0x7ffeffff
    ,
    step = start
  };
  return _SafeMatchBytesInMappedMemory(pattern, patternSize, XX, start, stop, step);
}
bool InsertVanillawareGCHook()
{
  ConsoleOutput("Vanillaware GC: enter");

  const BYTE bytes[] = {
      0x83, 0xc4, 0x04,                   // 16094193   83c4 04          add esp,0x4
      0xeb, 0x11,                         // 16094196   eb 11            jmp short 160941a9
      0x8b, 0xc1,                         // 16094198   8bc1             mov eax,ecx
      0x81, 0xe0, 0xff, 0xff, 0xff, 0x3f, // 1609419a   81e0 ffffff3f    and eax,0x3fffffff
      0x0f, 0xb6, 0x80, XX4,              // 160941a0   0fb680 00000810  movzx eax,byte ptr ds:[eax+0x10080000] ; jichi: hook here
      0x66, 0x90,                         // 160941a7   66:90            nop
      0x81, 0xc6, 0x01, 0x00, 0x00, 0x00  // 160941a9   81c6 01000000    add esi,0x1
                                          // 0x89,05 80f86701      // 160941af   8905 80f86701    mov dword ptr ds:[0x167f880],eax
                                          // 0x81,3d 80f86701 00   // 160941b5   813d 80f86701 00>cmp dword ptr ds:[0x167f880],0x0
                                          // 0xc7,05 8cf86701 00   // 160941bf   c705 8cf86701 00>mov dword ptr ds:[0x167f88c],0x0
                                          // 0x89,35 90f86701      // 160941c9   8935 90f86701    mov dword ptr ds:[0x167f890],esi
                                          // 0x7c, 14              // 160941cf   7c 14            jl short 160941e5
                                          // 0x7f, 09              // 160941d1   7f 09            jg short 160941dc
                                          // 0xc6,05 0cfb6701 02   // 160941d3   c605 0cfb6701 02 mov byte ptr ds:[0x167fb0c],0x2
                                          // 0xeb, 26              // 160941da   eb 26            jmp short 16094202
  };
  enum
  {
    memory_offset = 3
  }; // 160941a0   0fb680 00000810  movzx eax,byte ptr ds:[eax+0x10080000]
  enum
  {
    addr_offset = 0x160941a0 - 0x16094193
  };

  DWORD addr = SafeMatchBytesInGCMemory(bytes, sizeof(bytes));
  auto succ = false;
  if (!addr)
    ConsoleOutput("Vanillaware GC: pattern not found");
  else
  {
    HookParam hp;
    hp.address = addr + addr_offset;
    hp.user_value = *(DWORD *)(hp.address + memory_offset);
    hp.text_fun = SpecialGCHookVanillaware;
    hp.type = USING_STRING | NO_CONTEXT; // no context is needed to get rid of variant retaddr
    ConsoleOutput("Vanillaware GC: INSERT");
    succ |= NewHook(hp, "Vanillaware GC");
  }

  ConsoleOutput("Vanillaware GC: leave");
  return succ;
}
/** jichi 7/20/2014 Dolphin
 *  Tested with Dolphin 4.0
 */
bool InsertGCHooks()
{
  // TODO: Add generic hooks
  return InsertVanillawareGCHook();
  // return false;
}

bool VanillawareGC::attach_function()
{
  return InsertGCHooks();
}