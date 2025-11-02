#include "SRPGStudio.h"

bool SRPGStudio::attach_function()
{
  // NAGINATA SOFT
  // HERO'S PARTY R
  // https://store.steampowered.com/app/1804020/HEROS_PARTY_R/
  auto dll = GetModuleHandleW(L"OLEAUT32.dll");
  if (dll == 0)
    return 0;
  auto addr = GetProcAddress(dll, "SysAllocString");
  if (!addr)
    return 0;
  HookParam hp;
  hp.address = (DWORD)addr;
  hp.offset = stackoffset(1);
  hp.type = USING_STRING | CODEC_UTF16 | EMBED_ABLE | EMBED_AFTER_NEW;
  return NewHook(hp, "SRPGStudio");
}