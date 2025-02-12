#include "Aksys.h"
namespace
{
  bool _Aksys()
  {
    // https://vndb.org/v25385
    // Spirit Hunter: NG
    /*
    int __usercall sub_4CDD70@<eax>(const char *a1@<edx>, int a2, _DWORD *a3, int *a4)
    {
      int result; // eax
      const char *v6; // [esp+Ch] [ebp-8h] BYREF

      *a3 = strlen(a1);
      if ( *a1 && a2 )
      {
        v6 = a1;
        if ( (unsigned __int8)sub_4CAEB0(&v6) )
        {
          *a4 = sub_4CAF70(0, 0, 0x3A4u, (const unsigned __int16 *)a1, 0xFDE9u);
          return 0;
        }
        else
        {
          return -2141454316;
        }
      }
      else
      {
        result = 0;
        *a4 = 0;
      }
      return result;
    }
    */
    BYTE bytes[] = {
        0x68, 0xe9, 0xfd, 0, 0,
        0x56,
        0x68, 0xa4, 0x03, 0, 0,
        0x33, XX,
        0x33, XX,
        0xe8};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    addr = findfuncstart(addr);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = regoffset(edx);
    hp.split = regoffset(edx);
    hp.type = USING_STRING | USING_SPLIT;
    hp.filter_fun = [](TextBuffer *buffer, HookParam *)
    {
      StringFilter(buffer, TEXTANDLEN("@1r"));
      StringFilter(buffer, TEXTANDLEN("@-1r"));
      if (!StringToWideString(buffer->viewA(), 932).has_value())
        buffer->clear();
    };
    return NewHook(hp, "Aksys");
  }
}
bool Aksys::attach_function()
{
  return _Aksys();
}