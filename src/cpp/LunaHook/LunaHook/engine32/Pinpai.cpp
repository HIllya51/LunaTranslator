#include "Pinpai.h"
// https://vndb.org/v11397
// X'mas Present

bool Pinpai::attach_function()
{
  BYTE bytes2[] = {
      /*
     if ( *a3 == 0x81 && a3[1] == 64 )
    {
      this[514] += 24;
      return 1;
    }
      */
      0X83, 0XEC, XX,
      0X53,
      0X56,
      0X57,
      0X8B, 0X7C, 0X24, XX,
      0X8B, 0XF1,
      0X8A, 0X17,
      0X80, 0XFA, 0X81,
      0X75, XX,
      0X80, 0X7F, 0X01, 0X40,
      0X75, XX,
      0X8B, 0X86, XX4,
      0X5F,
      0X83, 0XC0, 0X18};
  auto addr = MemDbg::findBytes(bytes2, sizeof(bytes2), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_CHAR | DATA_INDIRECT;
  hp.offset = stackoffset(2);
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    if (buffer->viewA() == "\x83\xcb")
      buffer->clear();
    else if (buffer->viewA() == "\x83\xca")
      buffer->clear();
  };
  return NewHook(hp, "Pinpai");
}