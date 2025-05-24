#include "TeethingRing.h"

bool TeethingRing_attach_function()
{
  // https://vndb.org/v5635
  // キミとボクとエデンの林檎
  // HSF932#-C@85FB0:EDEN.exe
  BYTE bytes[] = {
      0x8B, 0x0A, 0x8B, 0xC1, 0x83, 0xF8, 0x20,
      0x0F, 0x8F, XX4,
      0x0F, 0x84, XX4,
      0x48,
      0xBE, 0x0F, 0x00, 0x00, 0x00, 0x3B, 0xC6,
      0x77, XX};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  BYTE sehstart[] = {
      0x6a, 0xff,
      0x68, XX4,
      0x64, 0xa1, 0, 0, 0, 0};
  addr = reverseFindBytes(sehstart, sizeof(sehstart), addr - 0x100, addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr; // 0x84C70+(DWORD)GetModuleHandle(0);
  hp.type = USING_STRING | NO_CONTEXT | FULL_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto _this = (void *)context->THISCALLTHIS;
    auto a2 = (DWORD *)context->argof(1);

    auto v2 = *a2;
    if ((int)*a2 <= 32)
    {
      if (*a2 != 32)
      {
        switch (v2)
        {

        case 16:
          auto v4 = (char *)(*(int(__thiscall **)(void *, DWORD))(*(DWORD *)_this + 60))(_this, a2[1]);
          buffer->from(v4);
        }
      }
    }
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    // #F【琉星】#F
    auto str = buffer->strA();
    if (all_ascii(str))
      return buffer->clear();
    strReplace(str, "#F");
    buffer->from(str);
  };
  return NewHook(hp, "TeethingRing");
}

bool TeethingRing_attach_function2()
{
  // https://vndb.org/v791
  // きると

  BYTE bytes[] = {
      0x8b, 0x4e, 0x18,
      0x83, 0xf9, 0x10,
      0x53,
      0x8d, 0x5e, 0x04,
      0x72, 0x04,
      0x8b, 0x13,
      0xeb, 0x02,
      0x8b, 0xd3,
      0x83, 0xf9, 0x10,
      0x72, 0x04,
      0x8b, 0x0b,
      0xeb, 0x02};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.type = USING_STRING | NO_CONTEXT | FULL_STRING;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    auto _this = (DWORD *)context->THISCALLTHIS;
    auto v13 = _this[6];
    auto v14 = _this + 1;
    DWORD *v16;
    if (v13 < 0x10)
      v16 = _this + 1;
    else
      v16 = (DWORD *)*v14;
    auto a2 = context->argof(1);
    *split = (DWORD)_this;
    buffer->from((char *)((DWORD)v16 + a2));
  };
  hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
  {
    auto str = buffer->strA();
    if (all_ascii(str))
      return buffer->clear();
    strReplace(str, "#F");
    // 俺はこのアクシデントが、何か幸#<さい>先#<さき>のいいもののように思えて、鞄を抱え直してギルドへの階段を昇り始めた。
    str = re::sub(str, "#<(.*?)>");
    buffer->from(str);
  };
  return NewHook(hp, "TeethingRing");
}

bool TeethingRing::attach_function()
{
  return TeethingRing_attach_function() || TeethingRing_attach_function2();
}