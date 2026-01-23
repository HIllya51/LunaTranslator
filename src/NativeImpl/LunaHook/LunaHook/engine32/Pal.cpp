#include "Pal.h"
/** jichi 6/1/2014 AMUSE CRAFT
 *  Related brands: http://erogetrailers.com/brand/2047
 *  Sample game: 魔女こいにっ� *  See:  http://sakuradite.com/topic/223
 *  Sample H-code: /HBN-4*0:18@26159:MAJOKOI_try.exe (need remove context, though)
 *
 *  Sample games:
 *  - 時計仕掛け�レイライン
 *  - きみと僕との騎士の日� *
 *  /HBN-4*0:18@26159:MAJOKOI_TRY.EXE
 *  - addr: 155993
 *  - length_offset: 1
 *  - module: 104464j455
 *  - off: 4294967288 = 0xfffffff8
 *  - split: 24 = 0x18
 *  - type: 1112 = 0x458
 *
 *  Call graph:
 *  - hook reladdr:  0x26159, fun reladdr: 26150
 *  - scene fun reladdr: 0x26fd0
 *    - arg1 and arg3 are pointers
 *    - arg2 is the text
 *  - scenairo only reladdr: 0x26670
 *  Issue for implementing embeded engine: two functions are needed to be hijacked
 *
 *  013c614e     cc             int3
 *  013c614f     cc             int3
 *  013c6150  /$ 55             push ebp ; jichi: function starts, this function seems to process text encoding
 *  013c6151  |. 8bec           mov ebp,esp
 *  013c6153  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  013c6156  |. 0fb608         movzx ecx,byte ptr ds:[eax]
 *  013c6159  |. 81f9 81000000  cmp ecx,0x81 ; jichi: hook here
 *  013c615f  |. 7c 0d          jl short majokoi_.013c616e
 *  013c6161  |. 8b55 08        mov edx,dword ptr ss:[ebp+0x8]
 *  013c6164  |. 0fb602         movzx eax,byte ptr ds:[edx]
 *  013c6167  |. 3d 9f000000    cmp eax,0x9f
 *  013c616c  |. 7e 1c          jle short majokoi_.013c618a
 *  013c616e  |> 8b4d 08        mov ecx,dword ptr ss:[ebp+0x8]
 *  013c6171  |. 0fb611         movzx edx,byte ptr ds:[ecx]
 *  013c6174  |. 81fa e0000000  cmp edx,0xe0
 *  013c617a  |. 7c 30          jl short majokoi_.013c61ac
 *  013c617c  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
 *  013c617f  |. 0fb608         movzx ecx,byte ptr ds:[eax]
 *  013c6182  |. 81f9 fc000000  cmp ecx,0xfc
 *  013c6188  |. 7f 22          jg short majokoi_.013c61ac
 *  013c618a  |> 8b55 08        mov edx,dword ptr ss:[ebp+0x8]
 *  013c618d  |. 0fb642 01      movzx eax,byte ptr ds:[edx+0x1]
 *  013c6191  |. 83f8 40        cmp eax,0x40
 *  013c6194  |. 7c 16          jl short majokoi_.013c61ac
 *  013c6196  |. 8b4d 08        mov ecx,dword ptr ss:[ebp+0x8]
 *  013c6199  |. 0fb651 01      movzx edx,byte ptr ds:[ecx+0x1]
 *  013c619d  |. 81fa fc000000  cmp edx,0xfc
 *  013c61a3  |. 7f 07          jg short majokoi_.013c61ac
 *  013c61a5  |. b8 01000000    mov eax,0x1
 *  013c61aa  |. eb 02          jmp short majokoi_.013c61ae
 *  013c61ac  |> 33c0           xor eax,eax
 *  013c61ae  |> 5d             pop ebp
 *  013c61af  \. c3             retn
 */
static bool InsertOldPalHook() // this is used in case the new pattern does not work
{
  const BYTE bytes[] = {
      0x55,             // 013c6150  /$ 55             push ebp ; jichi: function starts
      0x8b, 0xec,       // 013c6151  |. 8bec           mov ebp,esp
      0x8b, 0x45, 0x08, // 013c6153  |. 8b45 08        mov eax,dword ptr ss:[ebp+0x8]
      0x0f, 0xb6, 0x08, // 013c6156  |. 0fb608         movzx ecx,byte ptr ds:[eax]
      0x81, 0xf9        // 81000000  // 013c6159  |. 81f9 81000000  cmp ecx,0x81 ; jichi: hook here
  };
  enum
  {
    addr_offset = sizeof(bytes) - 2
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  // GROWL_DWORD(reladdr); // supposed to be 0x21650
  // GROWL_DWORD(reladdr  + addr_offset);
  // reladdr = 0x26159; // 魔女こいにっ�trial
  if (!addr)
  {
    ConsoleOutput("AMUSE CRAFT: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  // hp.type = NO_CONTEXT|USING_SPLIT|DATA_INDIRECT; // 0x418
  // hp.type = NO_CONTEXT|USING_SPLIT|DATA_INDIRECT|RELATIVE_SPLIT;  // Use relative address to prevent floating issue
  hp.type = NO_CONTEXT | USING_SPLIT | DATA_INDIRECT;
  hp.offset = regoffset(eax); // eax
  ConsoleOutput("INSERT AMUSE CRAFT");
  return NewHook(hp, "Pal");
}
namespace
{
  template <typename strT>
  strT trim(strT text, int *size)
  {
    // int length = ::strlen(text);
    auto length = *size;
    if (text[0] == '<' && text[1] == 'c')
    {
      auto p = ::strchr(text + 2, '>');
      if (!p)
        return text;
      p++;
      length -= p - text;
      text = p; // skip leading '<c .. >'
    }

    if (text[length - 1] == '>' && text[length - 2] == 'c' && text[length - 3] == '/' && text[length - 4] == '<')
      length -= 4; // skip the trailing </c>'

    *size = length;
    return text;
  }
  LPSTR trimmedText;
  int trimmedSize;
  void before(hook_context *s, HookParam *hp, TextBuffer *buffer, uintptr_t *role)
  {
    auto text = (LPSTR)s->stack[2]; // text in arg2
    if (!text || !*text)
      return;

    int size = ::strlen(text);
    trimmedSize = size;
    trimmedText = trim(text, &trimmedSize);
    if (trimmedSize <= 0 || !trimmedText || !*trimmedText)
      return;
    auto retaddr = s->stack[0];
    if (*(WORD *)(retaddr - 8) == 0x088b) // 8b08  mov ecx,dword ptr ds:[eax]
      *role = s->stack[3] ? Engine::ScenarioRole : Engine::NameRole;
    buffer->from(trimmedText, trimmedSize);
  }
  void after(hook_context *s, TextBuffer buffer, HookParam *)
  {
    std::string newData = buffer.strA();
    auto text = (LPSTR)s->stack[2]; // text in arg2
    int prefixSize = trimmedText - text;
    int size = ::strlen(text);
    int suffixSize = size - prefixSize - trimmedSize;
    // if (prefixSize)
    //   newData.prepend(text, prefixSize);
    if (suffixSize)
      newData.append(trimmedText + trimmedSize, suffixSize);
    ::strcpy(trimmedText, newData.c_str());
  }

  std::string rubyRemove(std::string text)
  {
    text = re::sub(text, "<r(.*?)>(.*?)</r>", "$2");
    text = re::sub(text, "<c(.*?)>(.*?)</c>", "$2");
    text = re::sub(text, "<s(.*?)>(.*?)</s>", "$2");
    return text;
  }
}
static bool InsertNewPal1Hook()
{
  // 有乱码，无法处理。并且遇到某些中文字符会闪退
  const BYTE bytes[] = {
      0x55,             // 002c6ab0   55               push ebp
      0x8b, 0xec,       // 002c6ab1   8bec             mov ebp,esp
      0x83, 0xec, 0x78, // 002c6ab3   83ec 78          sub esp,0x78
      0xa1, XX4,        // 002c6ab6   a1 8c002f00      mov eax,dword ptr ds:[0x2f008c]
      0x33, 0xc5,       // 002c6abb   33c5             xor eax,ebp
      0x89, 0x45, 0xf8  // 002c6abd   8945 f8          mov dword ptr ss:[ebp-0x8],eax ; mireado : small update
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Pal1: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2); // arg2
  hp.type = USING_STRING | EMBED_ABLE | NO_CONTEXT;
  hp.text_fun = before;
  hp.embed_fun = after;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    buffer->from(rubyRemove(buffer->strA()));
  };
  hp.embed_hook_font = F_CreateFontIndirectA | F_CreateFontA;
  ConsoleOutput("INSERT Pal1");
  return NewHook(hp, "Pal");
}
// Eguni 2016/11/06
// Supporting new Pal engine, tested with 恋×シンアイ彼女
static bool InsertNewPal2Hook()
{
  const BYTE bytes[] = {
      0x55,             // 0124E220   55               push ebp; doesn't works... why?
      0x8b, 0xec,       // 0124E221   8bec             mov ebp,esp
      0x83, 0xec, 0x7c, // 0124E223   83ec 7c          sub esp,0x7C
      0xa1, XX4,        // 0124E226   a1 788D2901      mov eax,dword ptr ds:[0x2f008c]
      0x33, 0xc5,       // 0124E22B   33c5             xor eax,ebp
      0x89, 0x45, 0xfc, // 0124E22D   8945 FC          mov dword ptr ss:[ebp-0x8],eax ; mireado : small update
      0xe8              // 0136e230   e8			   call 01377800
  };
  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("Pal2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2); // arg2
  hp.type = USING_STRING;
  ConsoleOutput("INSERT Pal2");
  return NewHook(hp, "Pal");
}
namespace
{
  bool redcheris()
  {
    const BYTE bytes[] = {
        // int __usercall sub_44E1E0@<eax>(
        //        char *a1@<edx>,

        // if ( *(_DWORD *)a1 == 1047683644 )
        0x8B, 0x06,
        0x3D, 0x3C, 0x62, 0x72, 0x3E,
        0x75, 0x10};
    ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
    if (!addr)
      return false;
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW;
    // 无法编码的字符无法显示，若开启dyna则会直接略过这个字，还不如不开。
    //[230929] [ユニゾンシフト] 恋とHしかしていない！
    hp.lineSeparator = L"<br>";
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      buffer->from(rubyRemove(buffer->strA()));
    };
    return NewHook(hp, "Pal");
  }
}

bool InsertPalHook() // use Old Pal first, which does not have ruby
{
  auto succ = false;
  for (auto func : {"PalSpriteCreateTextEx", "PalSpriteCreateText", "PalFontDrawText"})
  {
    HookParam hp;
    hp.type = USING_STRING | MODULE_OFFSET | FUNCTION_OFFSET;
    wcscpy_s(hp.module, L"Pal.dll");
    strcpy_s(hp.function, func);
    hp.offset = stackoffset(2);
    succ |= NewHook(hp, func);
  }
  bool embed = InsertNewPal1Hook();
  bool b1 = InsertOldPalHook() || InsertNewPal2Hook();

  bool b2 = redcheris();
  return b1 || b2 || embed || succ;
}

bool Pal::attach_function()
{

  return InsertPalHook();
}
