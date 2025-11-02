#include "Jellyfish.h"

bool Jellyfish::Jellyfish_attach_function()
{
  // https://vndb.org/r13456
  // GREEN～秋空のスクリーン～ STANDARD EDITION
  // https://vndb.org/r1136
  // LOVERS～恋に落ちたら…～

  const BYTE bytes[] = {
      0x8a,
      XX,
      0x01, // mov     cl, [ecx+1]
      0x80,
      XX,
      0x6e, // cmp     cl, 6Eh ; 'n'
      0x75,
      XX,
  };
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), minaddr, maxaddr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr, 0x1000);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING;
  hp.filter_fun = [](TextBuffer *buffer, HookParam *)
  {
    if (buffer->size == 2)
      return buffer->clear();
    StringCharReplacer(buffer, TEXTANDLEN("\\n"), '\n');
    StringCharReplacer(buffer, TEXTANDLEN("\\N"), '\n');

    buffer->from(re::sub(buffer->strA(), "\\\\[0-7a-zA-Z]"));
  };

  return NewHook(hp, "Jellyfish");
}

bool Jellyfish::Jellyfish_attach_function2()
{
  // https://vndb.org/r109826
  // Sisters: Last Day of Summer

  const BYTE bytes[] = {
      0x68, 0xB0, 0x04, 0x00, 0x00, 0x68, 0x40, 0x06, 0x00, 0x00};
  std::map<DWORD, int> count;
  DWORD maxa = 0;
  int maxi = 0;
  for (auto _ : Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, minaddr, maxaddr))
  {
    _ = findfuncstart(_);
    if (_ == 0)
      continue;
    if (!count.count(_))
      count[_] = 0;
    count[_] += 1;
    if (count[_] >= maxi)
    {
      maxi = count[_];
      maxa = _;
    }
  }
  if (maxa == 0)
    return false;
  HookParam hp;
  hp.address = maxa; // 0x2F2E1+(DWORD)ism;
  hp.type = USING_CHAR | CODEC_UTF16;
  hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
  {
    if (context->argof(3) == 3)
      return;
    *split = (context->argof(3)) != 0; // 多行文本
    buffer->from_t((WORD)context->argof(1));
    // 不可以快进，否则会有重复
  };

  return NewHook(hp, "Jellyfish");
}

bool Jellyfish::Jellyfish_attach_function3()
{
  // https://vndb.org/v2249
  // DEEP VOICE

  // 不可以快进，否则会有重复
  const BYTE bytes[] = {
      0x03, 0xd0,
      0x81, 0xFA, 0xE0, 0x01, 0x00, 0x00,
      0x0f, 0x8f, XX4};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minaddr, maxaddr);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr;
  hp.offset = stackoffset(1);
  hp.type = USING_CHAR;
  return NewHook(hp, "Jellyfish3");
}
bool Jellyfish::attach_function()
{
  std::tie(minaddr, maxaddr) = Util::QueryModuleLimits(ism);
  return Jellyfish_attach_function() || Jellyfish_attach_function2() || Jellyfish_attach_function3();
}