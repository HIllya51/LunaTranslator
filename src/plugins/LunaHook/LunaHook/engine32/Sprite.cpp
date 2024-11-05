#include "Sprite.h"

bool Sprite_attach_function()
{
  // 恋と選挙とチョコレート
  auto m = GetModuleHandle(L"dirapi.dll");
  auto [minAddress, maxAddress] = Util::QueryModuleLimits(m);
  const BYTE bytes[] = {
      0x83, 0xF8, 0x40,
      0x74, XX,
      0x83, 0xF8, 0x43,
      0x74, XX,
      0x83, XX, 0xFF,
      0xEB, XX,
      0x8D, 0x45, 0xF8,
      XX,
      XX,
      XX,
      //+20
      0xE8, XX4,
      0x89, 0x45, 0xF0,
      0x8D, 0x45, 0xF4,
      0x50,
      XX,
      0xE8, XX4};
  auto addr = MemDbg::findBytes(bytes, sizeof(bytes), minAddress, maxAddress);
  if (addr == 0)
    return false;
  if (((*(int *)(addr + 22)) + addr + 22) != ((*(int *)(addr + 35)) + addr + 35))
    return false;
  HookParam hp;
  hp.address = addr + sizeof(bytes);
  hp.offset = get_reg(regs::eax);
  hp.type = USING_STRING;
  return NewHook(hp, "Sprite");
}
namespace
{
  bool _h1()
  {
    // https://vndb.org/v1714
    //[Selen]はらみこ
    auto FlashAssetx32 = GetModuleHandleW(L"Flash Asset.x32");
    if (FlashAssetx32 == 0)
      return false;
    auto [s, e] = Util::QueryModuleLimits(FlashAssetx32);
    const BYTE bytes[] = {
        0x56, 0x57, 0x6a, 0xff,
        0xff, 0x75, 0x08, // ebp+8
        0x53,
        0x68, 0xe4, 0x04, 0x00, 0x00,
        0xff, 0x15, XX4 // MultiByteToWideChar
    };
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), s, e);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr + sizeof(bytes); // 不知道从哪jump到call MultiByteToWideChar的
    hp.offset = get_stack(5);
    hp.type = USING_STRING;
    hp.filter_fun = [](LPVOID data, size_t *size, HookParam *) -> bool
    {
      static int idx = 0;
      return (idx++) % 2;
    };
    return NewHook(hp, "Flash Asset");
  }

  bool _h2()
  {
    auto TextXtra = GetModuleHandleW(L"TextXtra.x32");
    if (TextXtra == 0)
      return false;
    auto [s, e] = Util::QueryModuleLimits(TextXtra);
    const BYTE bytes[] = {
        0xff, 0x75, 0x18,
        0x8d, 0x88, 0xb8, 0x00, 0x00, 0x00,
        0xff, 0x75, 0x14,
        0xff, 0x75, 0x10,
        0xff, 0x75, 0x0c,
        0xe8, XX4,
        0x66, 0x85, 0xc0,
        0x74};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), s, e);
    if (addr == 0)
      return false;
    addr = findfuncstart(addr, 0x100);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_stack(2);
    hp.type = USING_STRING | CODEC_UTF8 | EMBED_ABLE | EMBED_AFTER_NEW ;
    return NewHook(hp, "TextXtra");
  }
}
bool Sprite::attach_function()
{
  return Sprite_attach_function() | _h1() | _h2();
}
namespace
{
  bool h3()
  {
    // https://vndb.org/v5864
    // in white

    auto TextXtra = GetModuleHandleW(L"TextXtra.x32");
    if (TextXtra == 0)
      return false;
    auto [s, e] = Util::QueryModuleLimits(TextXtra);
    // Text Asset.x32->this function
    const BYTE bytes[] = {
        0x55, 0x8b, 0xec,
        0x56,
        0x8b, 0x75, 0x08,
        0x8b, 0x46, 0x04,
        0x66, 0x8b, 0x48, 0x32,
        0x51,
        0x6a, 0x00,
        0xff, 0x75, 0x18,
        0xff, 0x75, 0x14,
        0xff, 0x75, 0x10,
        0xff, 0x75, 0x0c,
        0xff, 0x70, 0x24,
        0xe8, XX4,
        0x66, 0x85, 0xc0,
        0x74, XX};
    auto addr = MemDbg::findBytes(bytes, sizeof(bytes), s, e);
    if (addr == 0)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.offset = get_stack(2);
    hp.type = USING_STRING;
    return NewHook(hp, "TextXtra2");
  }
}
bool TextXtra_x32::attach_function()
{
  return _h2() || h3();
}