#include "Triangle.h"
bool InsertTriangleHook()
{
  for (DWORD i = processStartAddress; i < processStopAddress - 4; i++)
  {
    DWORD j = 0;
    if ((*(DWORD *)i & 0xffffff) == 0x75403c)
    {
      j = i + 4 + *(BYTE *)(i + 3);
    }
    else if ((*(DWORD *)i & 0xffffffff) == 0x850f403c)
      // 长跳转
      // エグゼクタースクリプト
      j = i + 4 + *(int *)(i + 4);

    if (j)
    {
      for (DWORD k = j + 0x20; j < k; j++)
        if (*(BYTE *)j == 0xe8)
        {
          DWORD t = j + 5 + *(DWORD *)(j + 1);
          if (t > processStartAddress && t < processStopAddress)
          {
            HookParam hp;
            hp.address = t;
            hp.offset = stackoffset(1);
            hp.type = USING_STRING;
            ConsoleOutput("INSERT Triangle");
            return NewHook(hp, "Triangle");
          }
        }
    }
  }

  // ConsoleOutput("Old/Unknown Triangle engine.");
  ConsoleOutput("Triangle: failed");
  return false;
}

bool Triangle::attach_function()
{
  PcHooks::hookGDIFunctions();
  trigger_fun = [](LPVOID addr, hook_context *context)
  {
    // Triangle  やっぱり妹がすきっ！
    if ((DWORD)addr != (DWORD)TextOutA)
      return false;
    if (auto addr = MemDbg::findEnclosingAlignedFunction(context->retaddr))
    {
      if (*(BYTE *)(addr - 2) == 0xeb) // jmp xx, MONSTER PARK～化け物に魅入られし姫～，在函数中间中断
        addr = MemDbg::findEnclosingAlignedFunction_strict(context->retaddr);
      if (!addr)
        return true;
      HookParam hp;
      hp.address = addr;
      hp.offset = stackoffset(4);
      hp.split = stackoffset(1);
      hp.type = USING_STRING | USING_SPLIT;
      hp.embed_hook_font = F_TextOutA;
      hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
      {
        // ▼
        auto s = buffer->viewA();
        if (s.find("\x81\xa5") != s.npos)
          buffer->clear();
      };
      NewHook(hp, "Triangle2_TextOutA");
    }
    return true;
  };
  return InsertTriangleHook();
}

bool InsertTrianglePixHook()
{

  /*
   * Sample games:
   * https://vndb.org/v38070
   * https://vndb.org/v42090
   * https://vndb.org/v41025
   */
  const BYTE bytes[] = {
      0x50,                   // push eax           << hook here
      0xE8, XX4,              // call FinalIgnition.exe+4DE10
      0x8B, 0x83, XX4,        // mov eax,[ebx+0000DCA0]
      0x8D, 0x8D, XX4,        // lea ecx,[ebp-0000022C]
      0x83, 0x7D, 0x44, 0x10, // cmp dword ptr [ebp+44],10
      0xFF, 0x75, 0x40        // push [ebp+40]
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
    return false;

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.index = 0;
  hp.type = CODEC_UTF8 | USING_STRING | NO_CONTEXT;
  hp.filter_fun = NewLineCharToSpaceFilterA;
  return NewHook(hp, "TrianglePix");
}
bool Triangle2_attach_function()
{
  const BYTE bytes[] = {
      0x0f, 0x57, XX,
      0x68, 0x0F, 0x27, 0x00, 0x00,
      0x0f, 0x57, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  ConsoleOutput("%p", addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(5);
  hp.type = USING_STRING | CODEC_UTF8 | NO_CONTEXT;
  return NewHook(hp, "triangle");
}
bool Triangle2::attach_function()
{
  return Triangle2_attach_function() || InsertTrianglePixHook();
}
bool TriangleM1()
{
  auto _ = L"${FirstName}";
  ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
  if (!addr)
    return false;

  BYTE pushoffset[] = {0x68, XX4};
  *(DWORD *)(pushoffset + 1) = addr;
  addr = MemDbg::findBytes(pushoffset, sizeof(pushoffset), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(2);
  hp.type = USING_STRING | CODEC_UTF16;
  return NewHook(hp, "TriangleM");
}
bool TriangleM2()
{
  BYTE _[] = {0x33, 0xff, 0x66, 0x39, 0x3b, 0x74};
  ULONG addr = MemDbg::findBytes(_, sizeof(_), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(ebx);
  hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
  return NewHook(hp, "TriangleM");
}
bool TriangleM::attach_function()
{
  // 蛇香のライラ ～Allure of MUSK～ 第一夜 ヨーロピアン・ナイト 体験版
  auto _1 = TriangleM1();
  auto _2 = TriangleM2();
  return _1 || _2;
}