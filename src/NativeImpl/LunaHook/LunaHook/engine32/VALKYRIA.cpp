#include "VALKYRIA.h"

bool VALKYRIA::attach_function()
{
  auto addr = findiatcallormov((DWORD)GetTextExtentPoint32A, processStartAddress, processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sehstart[] = {
      0x6a, 0xff,
      0x68, XX4,
      0x64, 0xa1, 0, 0, 0, 0,
      0x50,
      0x81, 0xec, XX4,
      0xa1, XX4};
  addr = reverseFindBytes(sehstart, sizeof(sehstart), addr - 0x400, addr, 0, true);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING;
  hp.offset = stackoffset(5);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    // 实际上是单字符
    auto str = buffer->strA();
    static bool isspace = false;
    if (isspace && str == "\x81\x40")
      buffer->clear();
    else if (str == "\\r" || str == "\\R")
    {
      isspace = true;
      buffer->clear();
      // buffer->from("\n");
    }
    else
    {
      isspace = false;
    }
    //   switch ( v12 )
    // {
    //   case 'U':
    //   case 'u':
    //     String[0] = strtol(a6 + 2, 0, 16);
    //     String[1] = 0;
    //     HIBYTE(v92) = v14;
    //     LOWORD(v92) = a4;
    //     BYTE2(v92) = BYTE2(a4);
    //     return sub_454C40(a2, a3, v92, a5, String, (int)lprcDst, a8);
    //   case 'R':
    //   case 'r':
    //     sub_453E20();
    //     return 0;
    //   case '\\':
    //     wcscpy(String, L"\\");
    //     HIBYTE(v91) = HIBYTE(this);
    //     LOWORD(v91) = a4;
    //     BYTE2(v91) = BYTE2(a4);
    //     return sub_454C40(a2, a3, v91, a5, String, (int)a7, a8);
    // }
  };
  if (NewHook(hp, "VALKYRIA"))
  {
    PcHooks::hookGDIFunctions(GetTextExtentPoint32W);
    return true;
  }
  return false;
}