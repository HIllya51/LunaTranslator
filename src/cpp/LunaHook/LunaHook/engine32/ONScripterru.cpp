#include "ONScripterru.h"
void ONScripterruCommonFilter(TextBuffer *buffer)
{

  auto text = reinterpret_cast<LPSTR>(buffer->buff);
  StringCharReplacer(buffer, TEXTANDLEN("{n}"), ' ');
  if (cpp_strnstr(text, "{c:", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{c:"), TEXTANDLEN(":"));
  }
  if (cpp_strnstr(text, "{e:", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{e:"), TEXTANDLEN(":"));
  }
  if (cpp_strnstr(text, "{f:", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{f:"), TEXTANDLEN(":"));
  }
  if (cpp_strnstr(text, "{i:", buffer->size))
  {
    StringFilter(buffer, TEXTANDLEN("{i:"));
  }
  if (cpp_strnstr(text, "{p:", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("{p:"), TEXTANDLEN("}"));
  }
  CharFilter(buffer, '}');

  if (cpp_strnstr(text, "[", buffer->size))
  {
    StringFilterBetween(buffer, TEXTANDLEN("["), TEXTANDLEN("]"));
  }
}

void ONScripterru1Filter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(buffer->buff);

  if (text[0] == ':' || text[1] == '{')
    return buffer->clear();

  ONScripterruCommonFilter(buffer);
  CharFilter(buffer, '`');
}

bool InsertONScripterruHook1()
{

  /*
   * Sample games:
   * Umineko Project (all text displayed)
   */
  const BYTE bytes[] = {
      0x90,            // nop
      0x55,            // push ebp   << hook here
      0x57,            // push edi
      0x31, 0xED,      // xor ebp,ebp
      0x56,            // push esi
      0x53,            // push ebx
      0x83, 0xEC, 0x3C // sub esp,3C
  };

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
  {
    ConsoleOutput("ONScripter-RU 1: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + 1;
  hp.offset = regoffset(eax);
  hp.type = USING_STRING | CODEC_UTF8;
  hp.filter_fun = ONScripterru1Filter;
  ConsoleOutput("INSERT ONScripter-RU 1");
  return NewHook(hp, "ONScripter-RU1");
}

void StringBetween(char *str, size_t *size, const char *fr, size_t frlen, const char *to, size_t tolen)
{
  size_t len = *size,
         curlen;

  char *start = cpp_strnstr(str, fr, len);
  if (!*start)
    return;
  // start += frlen;
  char *end = cpp_strnstr((start += frlen), to, len - (start - str));
  if (!*end)
    return;
  ::memmove(str, start, end - start);

  *size = end - start;
  // str[*size] = '\0';
}

void ONScripterru2Filter(TextBuffer *buffer, HookParam *)
{
  StringBetween((char *)buffer->buff, &buffer->size, "`", 1, "`", 1);

  ONScripterruCommonFilter(buffer);
}

bool InsertONScripterruHook2()
{

  /*
   * Sample games:
   * Umineko Project (partial text displayed)
   */
  const BYTE bytes[] = {
      0x0F, 0xB6, 0x04, 0x18, // movzx eax,byte ptr [eax+ebx]   << hook here
      0x89, 0x74, 0x24, 0x04, // mov [esp+04],esi
      0x43,                   // inc ebx
      0x89, 0x44, 0x24, 0x08  // mov [esp+08],eax
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("ONScripter-RU 2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.split = regoffset(esi);
  hp.type = USING_STRING | CODEC_UTF8 | USING_SPLIT | KNOWN_UNSTABLE;
  // hp.type =  USING_STRING | CODEC_UTF8 | USING_SPLIT;
  hp.filter_fun = ONScripterru2Filter;
  ConsoleOutput("INSERT ONScripter-RU 2");
  return NewHook(hp, "ONScripter-RU2");
}

bool ONScripterru::attach_function()
{

  bool ok = InsertONScripterruHook1();
  return InsertONScripterruHook2() || ok;
}