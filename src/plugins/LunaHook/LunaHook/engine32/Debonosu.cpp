#include "Debonosu.h"

namespace
{ // unnamed
  int _type;
  void SpecialHookDebonosuScenario(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    DWORD retn = stack->retaddr;
    if (*(WORD *)retn == 0xc483)
    { // add esp, $  old Debonosu game
      hp->offset = get_stack(1);
      _type = 1;
    }
    else
    { // new Debonosu game
      hp->offset = get_reg(regs::eax);
      _type = 2;
    }
    // hp->type ^= EXTERN_HOOK;
    hp->text_fun = nullptr;
    *split = FIXED_SPLIT_VALUE;
    buffer->from_cs((char *)*(DWORD *)(stack->base + hp->offset));
  }
  void hook_after(hook_stack *s, void *data, size_t len)
  {
    static std::string ts;
    ts = std::string((LPSTR)data, len);

    if (_type == 1)
    {
      s->stack[1] = (DWORD)ts.c_str();
    }
    else
    {
      s->ecx = (DWORD)ts.c_str();
    }
  }
  bool InsertDebonosuScenarioHook()
  {
    DWORD addr = Util::FindImportEntry(processStartAddress, (DWORD)lstrcatA);
    if (!addr)
    {
      ConsoleOutput("Debonosu: lstrcatA is not called");
      return false;
    }
    DWORD search = 0x15ff | (addr << 16); // jichi 10/20/2014: call dword ptr ds
    addr >>= 16;
    for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
      if (*(DWORD *)i == search &&
          *(WORD *)(i + 4) == addr && // call dword ptr lstrcatA
          *(BYTE *)(i - 5) == 0x68)
      { // push $
        DWORD push = *(DWORD *)(i - 4);
        for (DWORD j = i + 6, k = j + 0x10; j < k; j++)
          if (*(BYTE *)j == 0xb8 &&
              *(DWORD *)(j + 1) == push)
            if (DWORD hook_addr = SafeFindEnclosingAlignedFunction(i, 0x200))
            {
              HookParam hp;
              hp.address = hook_addr;
              hp.text_fun = SpecialHookDebonosuScenario;
              // hp.type = USING_STRING;
              hp.hook_after = hook_after;
              hp.hook_font = F_MultiByteToWideChar | F_GetTextExtentPoint32A;
              hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT | FIXING_SPLIT | EMBED_ABLE |  EMBED_DYNA_SJIS; // there is only one thread
              hp.filter_fun = [](void *data, size_t *len, HookParam *hp)
              {
                return write_string_overwrite(data, len, std::regex_replace(std::string((char *)data, *len), std::regex("\\{(.*?)/(.*?)\\}"), "$1"));
              };
              ConsoleOutput("INSERT Debonosu");

              return NewHook(hp, "Debonosu");
            }
      }

    ConsoleOutput("Debonosu: failed");
    // ConsoleOutput("Unknown Debonosu engine.");
    return false;
  }
  void SpecialHookDebonosuName(hook_stack *stack, HookParam *hp, uintptr_t *data, uintptr_t *split, size_t *len)
  {
    DWORD text = stack->ecx;
    if (!text)
      return;
    *data = text;
    *len = ::strlen((LPCSTR)text);
    *split = FIXED_SPLIT_VALUE << 1;
  }
  bool InsertDebonosuNameHook()
  {
    const BYTE bytes[] = {
        // 0032f659   32c0             xor al,al
        // 0032f65b   5b               pop ebx
        // 0032f65c   8be5             mov esp,ebp
        // 0032f65e   5d               pop ebp
        // 0032f65f   c3               retn
        0x55,             // 0032f660   55               push ebp    ; jichi: name text in ecx, which could be zero though
        0x8b, 0xec,       // 0032f661   8bec             mov ebp,esp
        0x81, 0xec, XX4,  // 0032f663   81ec 2c080000    sub esp,0x82c
        0x8b, 0x45, 0x08, // 0032f669   8b45 08          mov eax,dword ptr ss:[ebp+0x8]
        0x53,             // 0032f66c   53               push ebx
        0x56,             // 0032f66d   56               push esi
        0x8b, 0xf1,       // 0032f66e   8bf1             mov esi,ecx
        0x85, 0xc0,       // 0032f670   85c0             test eax,eax
        0x8d, 0x4d, 0xf0, // 0032f672   8d4d f0          lea ecx,dword ptr ss:[ebp-0x10]
        0x0f, 0x45, 0xc8, // 0032f675   0f45c8           cmovne ecx,eax
        0x57              // 0032f678   57               push edi
    };
    ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
    {
      ConsoleOutput("DebonosuName: pattern NOT FOUND");
      return false;
    }
    HookParam hp;
    hp.address = addr;
    // hp.text_fun = SpecialHookDebonosuName;
    hp.offset = get_reg(regs::ecx);
    // hp.type = USING_STRING;
    hp.type = USING_STRING | NO_CONTEXT | USING_SPLIT | EMBED_ABLE |  EMBED_AFTER_NEW; //|FIXING_SPLIT; // there is only one thread
    ConsoleOutput("INSERT DebonosuName");

    return NewHook(hp, "DebonosuName");
  }

} // unnamed namespace
bool attach(ULONG startAddress, ULONG stopAddress)
{
  ULONG addr = 0;
  {
    const char *msg = "D3DFont::Draw";
    if (addr = MemDbg::findBytes(msg, ::strlen(msg + 1), startAddress, stopAddress))
      addr = MemDbg::findPushAddress(addr, startAddress, stopAddress);
  }
  if (!addr)
  {

    const uint8_t bytes[] = {
        0x50,             // 0010fb80   50               push eax
        0xff, 0x75, 0x14, // 0010fb81   ff75 14          push dword ptr ss:[ebp+0x14]
        0x8b, 0xce,       // 0010fb84   8bce             mov ecx,esi
        0xff, 0x75, 0x10  // 0010fb86   ff75 10          push dword ptr ss:[ebp+0x10]
    };
    addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  }
  if (!addr)
  {
    return false;
  }
  // addr = MemDbg::findEnclosingAlignedFunction(addr); // This might not work as the address is not always aligned
  addr = MemDbg::findEnclosingFunctionAfterInt3(addr);
  if (!addr)
  {
    return false;
  }
  HookParam hp;
  hp.address = addr;
  // hp.text_fun = SpecialHookDebonosuName;
  hp.offset = 20;
  // hp.type = USING_STRING;
  hp.type = USING_STRING | NO_CONTEXT; //|FIXING_SPLIT; // there is only one thread

  return NewHook(hp, "Debonosu2");
}

namespace
{
  bool debox()
  {
    //[240726][1282636][でぼの巣製作所] 神楽漫遊記～桂香と初花～ DL版 (files)
    auto lua51 = GetModuleHandle(L"lua5.1.dll");
    if (!lua51)
      return false;
    auto lua_tolstring = (DWORD)GetProcAddress(lua51, "lua_tolstring");
    if (!lua_tolstring)
      return false;
    auto addrs = findiatcallormov_all(lua_tolstring, processStartAddress, processStartAddress, processStopAddress, PAGE_EXECUTE);
    auto succ = false;
    for (auto addr : addrs)
    {
      HookParam hp;
      hp.address = addr + 6;
      hp.type = USING_STRING | NO_CONTEXT;
      hp.offset = get_reg(regs::eax);
      hp.filter_fun = [](LPVOID data, size_t *size, HookParam *)
      {
        auto text = reinterpret_cast<LPSTR>(data);
        auto len = reinterpret_cast<size_t *>(size);
        if (all_ascii(text, *len))
          return false;

        std::string str = std::string(text, *len);
        std::regex reg1("\\{(.*?)/(.*?)\\}");
        std::string result1 = std::regex_replace(str, reg1, "$1");

        return write_string_overwrite(text, len, result1);
        return true;
      };
      succ |= NewHook(hp, "debonosu");
    }
    return succ;
  }
}
bool InsertDebonosuHook()
{
  bool ok = InsertDebonosuScenarioHook();
  if (ok)
    InsertDebonosuNameHook();
  return ok;
}

bool Debonosu::attach_function()
{
  // 1/1/2016 jich: skip izumo4 from studio ego that is not supported by debonosu
  if (Util::CheckFile(L"*izumo4*.exe"))
  {
    PcHooks::hookOtherPcFunctions();
    return true;
  }
  return InsertDebonosuHook() || debox();
}