#include "DISCOVERY.h"
namespace
{
  bool DISCOVERY1()
  {
    // https://vndb.org/v4053
    // 小雪の朱－コユキノアカ－

    BYTE sig[] = {
        /*
        if ( *(v6 - 2) != 23
          || *(v6 - 3) != sub_40C130(255, 255, 255)
          || sub_418190(*(v6 - 4), v6 - 1) != 1
          || dword_B81054 && dword_975570 )*/

        0x83, 0x7b, 0xf8, 0x17,
        0x75, XX,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0x68, 0xff, 0x00, 0x00, 0x00,
        0xe8};
    auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_CHAR;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
      auto v6 = (int *)context->ebx - 4;
      buffer->from_t<WORD>(*v6);
    };
    return NewHook(hp, "DISCOVERY");
  }
  bool DISCOVERY2()
  {
    // [090828] [DISCOVERY MARS] 寝盗られ女教師 美帆先生○×日誌
    BYTE sig1[] = {
        /*
        v3 = *(int *)((char *)&dword_507F64 + v0);
          if ( v3 == 16513 )
        */
        0x8b, XX, XX4,
        0x3d, 0x81, 0x40, 0x00, 0x00};
    bool succ = false;
    for (auto addr : Util::SearchMemory(sig1, sizeof(sig1), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
      auto strptr = *(int *)(addr + 2);
      BYTE sig[] = {
          /*
          if ( *(int *)((char *)&dword_507F6C + v0) != 26
        || *(int *)((char *)&dword_507F68 + v0) != sub_40D1A0()
        || sub_41A160(*(int *)((char *)&dword_507F64 + v0)) != 1
        || dword_4D9AAC && dword_CCEE90 )
      */
          0x83, 0xbe, XX4, 0x1a,
          0x75, XX,
          0xb9, 0xff, 0x00, 0x00, 0x00,
          0x8b, 0xd1,
          0x8b, 0xc1,
          0xe8};
      addr = reverseFindBytes(sig, sizeof(sig), addr - 0x100, addr);
      if (!addr)
        continue;
      HookParam hp;
      hp.address = addr;
      hp.type = USING_CHAR;
      hp.user_value = strptr;
      hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
      {
        auto c = context->esi + hp->user_value;
        buffer->from_t<WORD>(*(int *)c);
      };
      succ |= NewHook(hp, "DISCOVERY");
    }
    return succ;
  }
}
bool DISCOVERY::attach_function()
{
  return DISCOVERY1() || DISCOVERY2();
}