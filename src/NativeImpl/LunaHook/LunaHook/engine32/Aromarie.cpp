#include "Aromarie.h"

// https://vndb.org/v2330
// 月ノ光太陽ノ影

bool Aromarie::attach_function()
{
  auto name = []()
  {
    char aSelectNameVoic[] = "select name,voiceBase,soundMode from envCharacter where name=?;";
    auto paSelectNameVoic = MemDbg::findBytes(aSelectNameVoic, sizeof(aSelectNameVoic), processStartAddress, processStopAddress);
    if (!paSelectNameVoic)
      return false;
    auto push = MemDbg::findPushAddress(paSelectNameVoic, processStartAddress, processStopAddress);
    if (!push)
      return false;
    auto addr = MemDbg::findEnclosingAlignedFunction(push);
    if (!addr)
      return false;
    auto checks = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (!checks.size())
      return false;
    auto last = checks[checks.size() - 1];
    addr = MemDbg::findEnclosingAlignedFunction(last);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_OVERWRITE | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.offset = stackoffset(1);
    return NewHook(hp, "AromarieName");
  }();
  auto text = []()
  {
    BYTE sig[] = {
        // if ( (unsigned __int8)((v6 ^ 0x20) + 95) < 0x3Cu )
        /*
        .text:0040799E                 mov     cl, al
  .text:004079A0                 xor     ecx, 20h
  .text:004079A3                 add     ecx, 5Fh ; '_'
  .text:004079A6                 and     ecx, 0FFh
  .text:004079AC                 cmp     ecx, 3Ch ; '<'
  .text:004079AF                 jl      loc_407C13
  .text:004079B5                 cmp     al, 5Ch ; '\'
        */
        0x8A, 0xC8,
        0x83, 0xF1, 0x20,
        0x83, 0xC1, 0x5F,
        0x81, 0xE1, 0xFF, 0x00, 0x00, 0x00,
        0x83, 0xF9, 0x3C,
        0x0F, XX, XX4,
        0x3C, 0x5C};
    auto check = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
    if (!check)
      return false;
    auto addr = MemDbg::findEnclosingAlignedFunction(check);
    if (!addr)
      return false;
    auto checks = findxref_reverse_checkcallop(addr, processStartAddress, processStopAddress, 0xe8);
    if (!checks.size())
      return false;
    auto last = checks[checks.size() - 1];
    addr = MemDbg::findEnclosingAlignedFunction(last);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | EMBED_ABLE | EMBED_AFTER_NEW | EMBED_DYNA_SJIS | NO_CONTEXT;
    hp.offset = stackoffset(1);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strA();
      s = re::sub(s, R"(\\\w)");
      s = re::sub(s, R"(%.*?%)");
      buffer->from(s);
    };
    return NewHook(hp, "AromarieText");
  }();
  return name && text;
}