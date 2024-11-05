#include"ONScripterru.h"
void ONScripterruCommonFilter(char *text, size_t *len)
{
  StringCharReplacer(text, len, "{n}", 3, ' ');

  if (cpp_strnstr(text, "{c:", *len)) {
    StringFilterBetween(text, len, "{c:", 3, ":", 1);
  }
  if (cpp_strnstr(text, "{e:", *len)) {
    StringFilterBetween(text, len, "{e:", 3, ":", 1);
  }
  if (cpp_strnstr(text, "{f:", *len)) {
    StringFilterBetween(text, len, "{f:", 3, ":", 1);
  }
  if (cpp_strnstr(text, "{i:", *len)) {
    StringFilter(text, len, "{i:", 3);
  }
  if (cpp_strnstr(text, "{p:", *len)) {
    StringFilterBetween(text, len, "{p:", 3, "}", 1);
  }
  CharFilter(text, len, '}');

  if (cpp_strnstr(text, "[", *len)) {
    StringFilterBetween(text, len, "[", 1, "]", 1);
  }

}

bool ONScripterru1Filter(LPVOID data, size_t *size, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(data);
  auto len = reinterpret_cast<size_t *>(size);

  if ( *len == 0 || text[0] == ':' || text[1] == '{')
	return false;

  ONScripterruCommonFilter(text, len);
  CharFilter(text, len, '`');

  return true;
}

bool InsertONScripterruHook1() 
{
  
    /*
    * Sample games:
    * Umineko Project (all text displayed)
    */
  const BYTE bytes[] = {
    0x90,                      // nop 
    0x55,                      // push ebp   << hook here
    0x57,                      // push edi
    0x31, 0xED,                // xor ebp,ebp
    0x56,                      // push esi
    0x53,                      // push ebx
    0x83, 0xEC, 0x3C           // sub esp,3C
  };

  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr) {
    ConsoleOutput("ONScripter-RU 1: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + 1;
  hp.offset=get_reg(regs::eax);
  hp.type =  USING_STRING | CODEC_UTF8;
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
  //start += frlen;
  char *end = cpp_strnstr((start += frlen), to, len - (start - str));
  if (!*end)
	  return;
  ::memmove(str, start, end - start);

  *size = end - start;
  //str[*size] = '\0';
}

bool ONScripterru2Filter(LPVOID data, size_t *size, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(data);
  auto len = reinterpret_cast<size_t *>(size);

  StringBetween(text, len, "`", 1, "`", 1);

  ONScripterruCommonFilter(text, len);

  return true;
}

bool InsertONScripterruHook2() 
{
  
    /*
    * Sample games:
    * Umineko Project (partial text displayed)
    */
  const BYTE bytes[] = {
    0x0F, 0xB6, 0x04, 0x18,    // movzx eax,byte ptr [eax+ebx]   << hook here
    0x89, 0x74, 0x24, 0x04,    // mov [esp+04],esi
    0x43,                      // inc ebx
    0x89, 0x44, 0x24, 0x08     // mov [esp+08],eax
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr) {
    ConsoleOutput("ONScripter-RU 2: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset=get_reg(regs::eax);
  hp.split  =get_reg(regs::esi);
  hp.type =  USING_STRING | CODEC_UTF8 | USING_SPLIT | KNOWN_UNSTABLE;
  //hp.type =  USING_STRING | CODEC_UTF8 | USING_SPLIT;
  hp.filter_fun = ONScripterru2Filter;
  ConsoleOutput("INSERT ONScripter-RU 2");
  return NewHook(hp, "ONScripter-RU2");
}

bool ONScripterru::attach_function() {
    
   bool ok = InsertONScripterruHook1();
  return  InsertONScripterruHook2() || ok;
} 