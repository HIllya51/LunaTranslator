#include "Live.h"
bool InsertLiveDynamicHook(LPVOID addr, DWORD frame, DWORD stack)
{
  if (addr != ::GetGlyphOutlineA || !frame)
    return false;
  DWORD k = *(DWORD *)frame;
  k = *(DWORD *)(k + 4);
  if (*(BYTE *)(k - 5) != 0xe8)
    k = *(DWORD *)(frame + 4);
  DWORD j = k + *(DWORD *)(k - 4);
  if (j > processStartAddress && j < processStopAddress)
  {
    HookParam hp;
    hp.address = j;
    hp.offset = regoffset(edx);
    hp.type = CODEC_ANSI_BE;
    ConsoleOutput("INSERT DynamicLive");
    return NewHook(hp, "Live");
    // RegisterEngineType(ENGINE_LIVE);
  }
  ConsoleOutput("DynamicLive: failed");
  return true; // jichi 12/25/2013: return true
}
// void InsertLiveHook()
//{
//   ConsoleOutput("Probably Live. Wait for text.");
//   trigger_fun=InsertLiveDynamicHook;
//   SwitchTrigger(true);
// }
bool InsertLiveHook()
{
  const BYTE ins[] = {0x64, 0x89, 0x20, 0x8b, 0x45, 0x0c, 0x50};
  ULONG addr = MemDbg::findBytes(ins, sizeof(ins), processStartAddress, processStopAddress);
  if (!addr)
  {
    return false;
  }
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(edx);
  hp.type = CODEC_ANSI_BE;
  return NewHook(hp, "Live");
}
static bool live2()
{
  const BYTE ins[] = {
      /*
      CODE:0017D697 33 C0                                         xor     eax, eax
  CODE:0017D699 8A 45 FB                                      mov     al, [ebp+var_5]
  CODE:0017D69C 3D AA 00 00 00                                cmp     eax, 0AAh       ; switch 171 cases
  CODE:0017D6A1 0F 87 30 13 00 00                             ja      def_17D6A7      ; jumptable 0017D6A7 default case
  CODE:0017D6A7 FF 24 85 AE D6 17 00                          jmp     jpt_17D6A7[eax*4] ; switch jump
      */
      /*
      CODE:0017DF9C 8D 55 AC                                      lea     edx, [ebp+var_54] ; jumptable 0017D6A7 case 50
   CODE:0017DF9F 8B C3                                         mov     eax, ebx
   CODE:0017DFA1 8B 08                                         mov     ecx, [eax]
   CODE:0017DFA3 FF 91 40 02 00 00                             call    dword ptr [ecx+240h]
   CODE:0017DFA9 8B 55 AC                                      mov     edx, [ebp+var_54]
   <--- edx
   CODE:0017DFAC 8B C6                                         mov     eax, esi
   CODE:0017DFAE E8 F5 E6 FF FF                                call    sub_17C6A8
   CODE:0017DFB3 E9 35 0A 00 00                                jmp     loc_17E9ED
      */
      0x33, 0xc0,
      0x8a, 0x45, XX,
      0x3d, 0xaa, 0x00, 0x00, 0x00,
      0x0f, 0x87, XX4,
      0xff, 0x24, 0x85, XX4};
  ULONG addr = MemDbg::findBytes(ins, sizeof(ins), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  auto jmptable = *(DWORD **)(addr + sizeof(ins) - 4);
  auto target = jmptable[0x32];
  ConsoleOutput("%p", target);
  const BYTE CHECKOK[] = {
      0x8d, 0x55, XX,
      0x8b, 0xc3,
      0x8b, 0x08,
      0xff, 0x91, XX4,
      0x8b, 0x55, XX};
  if (!MatchPattern(target, CHECKOK, sizeof(CHECKOK)))
    return false;
  HookParam hp;
  hp.address = target + sizeof(CHECKOK);
  hp.offset = regoffset(edx);
  hp.type = USING_STRING | NO_CONTEXT;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    static std::string last;
    auto s = buffer->strA();
    if (startWith(s, last))
    {
      auto _ = s.substr(last.size());
      buffer->from(Trim(_));
    }
    else
    {
      buffer->from(Trim(s));
    }
    last = s;
  };

  return NewHook(hp, "Live2");
}
bool Live::attach_function()
{

  return InsertLiveHook() | live2();
}