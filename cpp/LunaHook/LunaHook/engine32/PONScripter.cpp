#include"PONScripter.h"
  
bool InsertPONScripterHook()
{
	if (DWORD str = MemDbg::findBytes("CBString::Failure in (CBString", 30, processStartAddress, processStopAddress))
	{
		if (DWORD calledAt = MemDbg::findBytes(&str, sizeof(str), processStartAddress, processStopAddress))
		{
			DWORD funcs[] = { 0xec8b55, 0xe58955 };
			DWORD addr = MemDbg::findBytes(funcs, 3, calledAt - 0x100, calledAt);
			if (!addr) addr = MemDbg::findBytes(funcs + 1, 3, calledAt - 0x100, calledAt);
			if (addr)
			{
				HookParam hp;
				hp.address = addr;
				hp.type = USING_STRING | CODEC_UTF8 | DATA_INDIRECT;
				hp.offset=get_stack(1);
				hp.index = 0xc;
				return NewHook(hp, "PONScripter");
			}
			else ConsoleOutput("failed to find function start");
		}
		else ConsoleOutput("failed to find string reference");
	}
	else ConsoleOutput("failed to find string");
	return false;
}
bool PONScripterFilter(LPVOID data, size_t *size, HookParam *)
{
  auto text = reinterpret_cast<LPSTR>(data);
  auto len = reinterpret_cast<size_t *>(size);
  static std::string prevText;

  for (int i=0; i<*len; i++) {
    if (text[i] == '^' || text[i]=='@' || text[i]=='\\' || text[i]=='\n') {
      text[i] = '\0';
      *len = i;
      break;
    }
  }

  if (!prevText.compare(text))
    return false;
  prevText = text;

  StringFilter(text, len, "#", 7);	// remove # followed by 6 chars

  return true;
}

bool InsertPONScripterEngHook() 
{
  
    /*
    * Sample games:
    * https://vndb.org/v24770
    */
  const BYTE bytes[] = {
    0x89, 0xD0,                 // mov eax,edx
    0x8D, 0x75, 0xD8,           // lea esi,[ebp-28]
    0x89, 0x55, 0xB4,           // mov [ebp-4C],edx
    0x83, 0xC0, 0x01,           // add eax,01
    0x89, 0x45, 0xC0            // mov [ebp-40],eax    << hook here
  };
  enum { addr_offset = sizeof(bytes) - 3 };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr) {
    ConsoleOutput("PONScripterEng: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr + addr_offset;
  hp.offset=get_reg(regs::eax);
  hp.type = USING_STRING|CODEC_UTF8;
  hp.filter_fun = PONScripterFilter;
  ConsoleOutput("INSERT PONScripterEng");
  return NewHook(hp, "PONScripterEng");
}

bool InsertPONScripterJapHook() 
{
  
    /*
    * Sample games:
    * https://vndb.org/v24770
    */
  const BYTE bytes[] = {
    0x8D, 0x87, XX4,            // lea eax,[edi+00000198]               << hook here
    0x8B, 0x0D, XX4,            // mov ecx,[ciconia_phase1.exe+3D82C0]
    0x89, 0x55, 0xB4,           // mov [ebp-4C],edx
    0xC6, 0x45, 0xAE, 0x00,     // mov byte ptr [ebp-52],00
    0x89, 0x45, 0xA4,           // mov [ebp-5C],eax
    0x8B, 0x01,                 // mov eax,[ecx]
    0x8B, 0x75, 0xB4            // mov esi,[ebp-4C]
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr) {
    ConsoleOutput("PONScripterJap: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset=get_reg(regs::edx);
  hp.type = USING_STRING|CODEC_UTF8;
  hp.filter_fun = PONScripterFilter;
  ConsoleOutput("INSERT PONScripterJap");
  return NewHook(hp, "PONScripterJap");
}
bool PONScripter::attach_function() {
    
    bool ok = InsertPONScripterEngHook() && InsertPONScripterJapHook();
  	return  ok || InsertPONScripterHook(); // If a language hook is missing, the original code is executed
}  