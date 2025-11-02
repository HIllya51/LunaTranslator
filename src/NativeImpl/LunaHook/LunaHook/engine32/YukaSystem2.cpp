#include "YukaSystem2.h"
/** jichi 7/6/2014 YukaSystem2
 *  Sample game: セミラミスの天秤
 *
 *  Observations from Debug:
 *  - Ollydbg got UTF8 text memory address
 *  - Hardware break points have loops on 0x4010ED
 *  - The hooked function seems to take 3 parameters, and arg3 is the right text
 *  - The text appears character by character
 *
 *  Runtime stack:
 *  - return address
 *  - arg1 pointer's pointer
 *  - arg2 text
 *  - arg3 pointer's pointer
 *  - code address or -1, maybe a handle
 *  - unknown pointer
 *  - return address
 *  - usually zero
 *
 *  0040109d     cc             int3
 *  0040109e     cc             int3
 *  0040109f     cc             int3
 *  004010a0  /$ 55             push ebp
 *  004010a1  |. 8bec           mov ebp,esp
 *  004010a3  |. 8b45 14        mov eax,dword ptr ss:[ebp+0x14]
 *  004010a6  |. 50             push eax                                 ; /arg4
 *  004010a7  |. 8b4d 10        mov ecx,dword ptr ss:[ebp+0x10]          ; |
 *  004010aa  |. 51             push ecx                                 ; |arg3
 *  004010ab  |. 8b55 0c        mov edx,dword ptr ss:[ebp+0xc]           ; |
 *  004010ae  |. 52             push edx                                 ; |arg2
 *  004010af  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]           ; |
 *  004010b2  |. 50             push eax                                 ; |arg1
 *  004010b3  |. e8 48ffffff    call semirami.00401000                   ; \semirami.00401000
 *  004010b8  |. 83c4 10        add esp,0x10
 *  004010bb  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  004010be  |. 5d             pop ebp
 *  004010bf  \. c3             retn
 *  004010c0  /$ 55             push ebp
 *  004010c1  |. 8bec           mov ebp,esp
 *  004010c3  |. 8b45 14        mov eax,dword ptr ss:[ebp+0x14]
 *  004010c6  |. 50             push eax                                 ; /arg4
 *  004010c7  |. 8b4d 10        mov ecx,dword ptr ss:[ebp+0x10]          ; |
 *  004010ca  |. 51             push ecx                                 ; |arg3
 *  004010cb  |. 8b55 0c        mov edx,dword ptr ss:[ebp+0xc]           ; |
 *  004010ce  |. 52             push edx                                 ; |arg2
 *  004010cf  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]           ; |
 *  004010d2  |. 50             push eax                                 ; |arg1
 *  004010d3  |. e8 58ffffff    call semirami.00401030                   ; \semirami.00401030
 *  004010d8  |. 83c4 10        add esp,0x10
 *  004010db  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  004010de  |. 5d             pop ebp
 *  004010df  \. c3             retn
 *  004010e0  /$ 55             push ebp ; jichi: function begin, hook here, bp-based frame, arg2 is the text
 *  004010e1  |. 8bec           mov ebp,esp
 *  004010e3  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8] ; jichi: ebp+0x8 = arg2
 *  004010e6  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc] ; jichi: arg3 is also a pointer of pointer
 *  004010e9  |. 8a11           mov dl,byte ptr ds:[ecx]
 *  004010eb  |. 8810           mov byte ptr ds:[eax],dl    ; jichi: eax is the data
 *  004010ed  |. 5d             pop ebp
 *  004010ee  \. c3             retn
 *  004010ef     cc             int3
 */

// Ignore image and music file names
// Sample text: "Voice\tou00012.ogg""運命論って云うのかなあ……神さまを信じてる人が多かったからだろうね、何があっても、それ�神さまが�刁�ちに与えられた試練なんだって、そ぀�ってたみたい。勿論、今でもそ぀��てあ�人はぁ�ぱぁ�るん�けど�
// Though the input string is UTF-8, it should be ASCII compatible.
static bool _yk2garbage(const char *p)
{
  // Q_ASSERT(p);
  while (char ch = *p++)
  {
    if (!(
            ch >= '0' && ch <= '9' ||
            ch >= 'A' && ch <= 'z' || // also ignore ASCII 91-96: [ \ ] ^ _ `
            ch == '"' || ch == '.' || ch == '-' || ch == '#'))
      return false;
  }
  return true;
}

// Get text from arg2
static void SpecialHookYukaSystem2(hook_context *context, HookParam *hp, uintptr_t *data, uintptr_t *split, size_t *len)
{
  DWORD arg2 = context->stack[2], // [esp+0x8]
      arg3 = context->stack[3];   // [esp+0xc]
                                  // arg4 = argof(4, esp_base); // there is no arg4. arg4 is properlly a function pointer
  LPCSTR text = (LPCSTR)arg2;
  if (*text && !_yk2garbage(text))
  { // I am sure this could be null
    *data = (DWORD)text;
    *len = ::strlen(text); // UTF-8 is null-terminated
    if (arg3)
      *split = *(DWORD *)arg3;
  }
}

bool InsertYukaSystem2Hook()
{
  const BYTE bytes[] = {
      0x55,             // 004010e0  /$ 55             push ebp ; jichi; hook here
      0x8b, 0xec,       // 004010e1  |. 8bec           mov ebp,esp
      0x8b, 0x45, 0x08, // 004010e3  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8] ; jichi: ebp+0x8 = arg2
      0x8b, 0x4d, 0x0c, // 004010e6  |. 8b4d 0c        mov ecx,dword ptr ss:[ebp+0xc]
      0x8a, 0x11,       // 004010e9  |. 8a11           mov dl,byte ptr ds:[ecx]
      0x88, 0x10,       // 004010eb  |. 8810           mov byte ptr ds:[eax],dl    ; jichi: eax is the address to text
      0x5d,             // 004010ed  |. 5d             pop ebp
      0xc3              // 004010ee  \. c3             retn
  };
  // enum { addr_offset = 0 };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(addr); // supposed to be 0x4010e0
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.split = stackoffset(2);
  hp.type = USING_SPLIT | USING_STRING | CODEC_UTF8; // UTF-8, though
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    // セミラミスの天秤
    // セミラミスの天秤 Fated Dolls

    auto str = buffer->strA();

    if (all_ascii(str))
      return buffer->clear();
    str = re::sub(str, R"(@r\((.*?),(.*?)\))", "$1");

    auto wstr = StringToWideString(str);

    if (wstr.size() == 1)
      return buffer->clear();

    for (auto wc : wstr)
    {
      if ((wc >= 'A' && wc <= 'z') ||
          (wc >= '0' && wc <= '9') ||
          (wc == '"') || (wc == '.') || (wc == '-') || (wc == '#') ||
          (wc == 65533) || (wc == 2))
        return buffer->clear();
    }
    buffer->from(str);
  };
  // hp.text_fun = SpecialHookYukaSystem2;
  ConsoleOutput("INSERT YukaSystem2");
  return NewHook(hp, "YukaSystem2");
}
namespace
{
  bool hook2()
  {
    // 君を仰ぎ乙女は姫に
    // ずっとつくしてあげるの!
    const BYTE bytes[] = {
        0x0F, 0xB6, 0x07,
        0x83, 0xE8, 0x40,
        0x75, XX,
        0x0F, 0xB6, 0x47, 0x01,
        0x83, 0xE8, 0x67,
        0x8D, 0x4F, 0x01,
        0x75, XX,
        0x0F, 0xB6, 0x41, 0x01,
        0x83, 0xC1, 0x01,
        0x83, 0xE8, 0x66,
        0x74, XX};
    // enum { addr_offset = 0 };
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    // GROWL_DWORD(addr); // supposed to be 0x4010e0
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_SPLIT | DATA_INDIRECT;
    hp.index = 0;
    hp.split = stackoffset(1);
    return NewHook(hp, "YukaSystem2");
  }
}
namespace __
{
  void YukaSystem1Filter(TextBuffer *buffer, HookParam *)
  {
    auto text = reinterpret_cast<LPSTR>(buffer->buff);

    // if acii add a space at the end of the sentence overwriting null terminator
    if (buffer->size >= 2 && text[buffer->size - 2] > 0)
      text[buffer->size++] = ' ';

    if (cpp_strnstr(text, "@r(", buffer->size))
    {
      StringFilterBetween(buffer, TEXTANDLEN("@r("), TEXTANDLEN(")")); // @r(2,はと)
    }
  }

  bool InsertYukaSystem1Hook()
  {
    /*
     * Sample games:
     * https://vndb.org/r71601
     * https://vndb.org/v7507
     */
    const BYTE bytes[] = {
        0x80, 0x3D, XX4, 0x01, // cmp byte ptr [kimihime.exe+16809C],01     << hook here
        0x75, 0x11,            // jne kimihime.exe+42D74
        0xB9, XX4,             // mov ecx,kimihime.exe+C7F8C
        0xC6, 0x05, XX4, 0x00  // mov byte ptr [kimihime.exe+1516C5],00
    };
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
    {
      ConsoleOutput("YukaSystem1: pattern not found");
      return false;
    }

    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(eax);
    hp.type = USING_STRING | KNOWN_UNSTABLE;
    hp.filter_fun = YukaSystem1Filter;
    ConsoleOutput("INSERT YukaSystem1");
    return NewHook(hp, "YukaSystem1");
  }
}
namespace
{
  bool h1()
  {
    // https://vndb.org/v540
    // シャマナシャマナ～月とこころと太陽の魔法～
    auto addr = Util::FindImportEntry(processStartAddress, (DWORD)IsDBCSLeadByteEx);
    if (!addr)
      return false;
    const BYTE bytes[] = {
        0xff, 0x15, XX4,
        0x83, 0xf8, 0x01,
        0x0f, 0x85, XX4,
        0x33, 0xd2,
        0xb9, 0x02, 0x00, 0x00, 0x00,
        0xbf, XX4,
        0x8b, 0xf3,
        0x33, 0xc0,
        0xf3, 0xa6,
        0x74, XX,
        0xb8, XX4,
        0x8a, 0x48, 0x02,
        0x83, 0xc0, 0x02,
        0x83, 0xc2, 0x02,
        0x84, 0xc9,
        0x74, XX,
        0xb9, 0x02, 0x00, 0x00, 0x00,
        0x8b, 0xf8,
        0x8b, 0xf3,
        0x33, 0xed,
        0xf3, 0xa6};
    memcpy((void *)(bytes + 2), &addr, 4);
    addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = stackoffset(2);
    hp.type = USING_CHAR | DATA_INDIRECT;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      CharFilter(buffer, '@');
    };
    return NewHook(hp, "caramelbox");
  }
}
bool YukaSystem2::attach_function()
{
  bool _1 = h1() || __::InsertYukaSystem1Hook();
  return InsertYukaSystem2Hook() || hook2() || _1;
}