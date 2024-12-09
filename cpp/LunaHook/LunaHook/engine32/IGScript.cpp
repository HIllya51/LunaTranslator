#include "IGScript.h"
namespace
{
  void LucaSystemFilter1(TextBuffer *buffer, HookParam *)
  {
    StringFilter(buffer, "\x81\x94", 2);
    // 秋&冬  官中
    StringReplacer(buffer, "\x82\xa1", 2, "\xa3\xac", 2); // ，
    StringReplacer(buffer, "\x82\xa3", 2, "\xa1\xa3", 2); // 。
    StringReplacer(buffer, "\x82\xa5", 2, "\xa1\xa2", 2); // 、
    StringReplacer(buffer, "\x83\x48", 2, "\xa1\xb1", 2); // ”
    StringReplacer(buffer, "\x83\x44", 2, "\xa3\xbf", 2); // ？
    StringReplacer(buffer, "\x83\x42", 2, "\xa3\xa1", 2); //!
    StringReplacer(buffer, "\x82\xa7", 2, "\xa1\xb9", 2); // 」
    StringReplacer(buffer, "\x82\xc1", 2, "\xa1\xb7", 2); // 》
    StringReplacer(buffer, "\x83\x46", 2, "\xa1\xaf", 2); // ’
  }
  template <int arg>
  void SpecialHookigi(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD Src = context->stack[arg];
    DWORD Size = context->stack[arg + 1];
    if (strlen((char *)Src) <= 2)
      return;
    if (strlen((char *)Src) >= Size)
      return;
    if (strlen((char *)Src) < Size - 4)
      return;
    buffer->from((char *)Src);
    // ConsoleOutput(WideStringToString(StringToWideString((char*)Src,936).value()).c_str());
    // std::string xx;
    // for(int i=0;i<*len;i++){
    //   xx+=" "+std::to_string(*(BYTE*)(Src+i));

    // }
    // ConsoleOutput(xx.c_str());
  }
}
bool IGScript1attach_function()
{
  /*
  FLOWERS
  * https://vndb.org/v15395
  * https://vndb.org/v14267
  * https://vndb.org/v18152
  * https://vndb.org/r82704
  */
  const BYTE bytes[] = {
      // memcpy(dst,src,size)
      0x81, 0xf9, 0x00, 0x01, 0x00, 0x00,
      0x72, XX,
      0x83, 0x3d, XX4, 0x00,
      0x74, XX,
      0x57, 0x56,
      0x83, 0xe7, 0x0f,
      0x83, 0xe6, 0x0f,
      0x3b, 0xfe};
  HMODULE module = GetModuleHandleW(L"Script.dll");
  auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
  if (addr == 0)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x100);
  if (addr == 0)
    return false;
  HookParam hp;
  hp.address = addr;
  const BYTE funcstart[] = {
      0x55, 0x8b, 0xec, 0x57, 0x56};
  bool insertgbk = memcmp(funcstart, (LPVOID *)addr, 5) == 0;
  hp.text_fun = SpecialHookigi<2>;
  hp.type = NO_CONTEXT;
  // hp.filter_fun=LucaSystemFilter1;
  bool succ = NewHook(hp, "IGScript");

  if (insertgbk)
  {
    hp.address += 5;
    hp.text_fun = SpecialHookigi<5>;
    // 仅官中适用这个过滤器。日语原版不需要过滤
    hp.filter_fun = LucaSystemFilter1;
    succ |= NewHook(hp, "IGScript_1");
  }
  return succ;
}
namespace
{
  void LucaSystemFilter(TextBuffer *buffer, HookParam *)
  {
    auto text = reinterpret_cast<LPSTR>(buffer->buff);

    if (text[0] == '\x81' && text[1] == '\x94')
      return buffer->clear();

    StringCharReplacer(buffer, "\x81\x90", 2, ' '); // new line
    // replacement from Flowers 4 config.json
    CharReplacer(buffer, '\xA5', ' ');
    CharReplacer(buffer, '\xA2', '<');
    CharReplacer(buffer, '\xA3', '>');
    CharReplacer(buffer, '\xA1', '\"');
    CharReplacer(buffer, '\xA4', '\'');
    CharReplacer(buffer, '\xA7', 'à');
    CharReplacer(buffer, '\xA8', 'è');
    CharReplacer(buffer, '\xA9', 'é');
    CharReplacer(buffer, '\xAA', 'ë');
    CharReplacer(buffer, '\xAB', 'ō');
    CharReplacer(buffer, '\xB0', '-');
    CharReplacer(buffer, '\xBB', ' ');

    while (cpp_strnstr(text, "  ", buffer->size)) // Erasing all but one whitespace from strings
      StringCharReplacer(buffer, "  ", 2, ' ');

    if (text[0] == ' ')
      ::memmove(text, text + 1, --buffer->size);
  }

  bool InsertLucaSystemHook()
  {

    /*
     * Sample games:
     * https://vndb.org/v15395
     * https://vndb.org/v14267
     * https://vndb.org/v18152
     * https://vndb.org/r82704
     */
    const BYTE bytes[] = {
        0xCC,                   // int 3
        0xE9, XX4,              // jmp d3d9.dll+1E420
        0x56,                   // push esi
        0x57,                   // push edi
        0x8B, 0x7C, 0x24, 0x20, // mov edi,[esp+20]
        0x8B, 0xD8,             // mov ebx,eax
        0x8B, 0x07              // mov eax,[edi]
    };
    const BYTE bytes2[] = {
        0xCC,             // int 3
        0x83, 0xEC, 0x0C, // sub esp,0C      <- hook here
        0x53,             // push ebx
        0x55,             // push ebp
        0x56              // push esi
    };

    HMODULE module = GetModuleHandleW(L"Script.dll");
    auto [minAddress, maxAddress] = Util::QueryModuleLimits(module);
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
    if (!addr)
    {
      addr = MemDbg::findBytes(bytes2, sizeof(bytes2), minAddress, maxAddress);
      if (!addr)
      {
        ConsoleOutput("LucaSystem: pattern not found");
        return false;
      }
    }

    HookParam hp;
    hp.address = addr + 1;
    hp.offset = stackoffset(1);
    hp.padding = 0x04;
    hp.type = USING_STRING;
    hp.filter_fun = LucaSystemFilter;

    return NewHook(hp, "LucaSystem");
  }
}
bool IGScript::attach_function()
{

  auto b1 = IGScript1attach_function();
  b1 = InsertLucaSystemHook() || b1;
  return b1;
}