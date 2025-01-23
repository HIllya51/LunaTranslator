#include "hibiki.h"

bool hibikihook()
{
  // ＬＯＶＥＬＹ×Ｃ∧ＴＩＯＮ
  /*seg000:0044FC05 83 FF 20                      cmp     edi, 20h ; ' '
  seg000:0044FC08 0F 84 E6 00 00 00             jz      loc_44FCF4
  seg000:0044FC08
  seg000:0044FC0E 81 FF 00 30 00 00             cmp     edi, 3000h
  seg000:0044FC14 0F 84 E9 00 00 00             jz      loc_44FD03*/
  const BYTE bytes[] = {
      0x83, 0xff, 0x20,
      0x0f, 0x84, XX4,
      0x81, 0xff, 0x00, 0x30, 0x00, 0x00,
      0x0f, 0x84, XX4};

  auto addrs = Util::SearchMemory(bytes, sizeof(bytes), PAGE_EXECUTE, processStartAddress, processStopAddress);
  bool succ = false;
  for (auto addr : addrs)
  {
    addr = MemDbg::findEnclosingAlignedFunction(addr);
    if (!addr)
    {
      continue;
    }
    HookParam hp;
    hp.address = addr;

    hp.offset = stackoffset(3);
    hp.type = CODEC_UTF16;

    ConsoleOutput("INSERT hibiki_extra %p", addr);

    succ |= NewHook(hp, "hibiki_extra");
  }

  return succ;
}
void YaneSDKFilter(TextBuffer *buffer, HookParam *)
{
  auto text = reinterpret_cast<LPWSTR>(buffer->buff);
  static std::wstring prevText;
  text[buffer->size / sizeof(wchar_t)] = L'\0'; // clean text

  if (!prevText.compare(text))
    return buffer->clear();
  prevText = text;

  StringCharReplacer(buffer, L"[r]", 3, L' ');
  StringFilter(buffer, L"[np]", 4);

  if (cpp_wcsnstr(text, L"'", buffer->size / sizeof(wchar_t)))
  { // [桜木'さくらぎ]
    StringFilterBetween(buffer, L"'", 1, L"]", 1);
  }
  CharFilter(buffer, L'[');
  CharFilter(buffer, L']');
}

bool InsertYaneSDKHook()
{

  /*
   * Sample games:
   * https://vndb.org/v21734
   * https://vndb.org/v21455
   * https://vndb.org/v20406
   */
  const BYTE bytes[] = {
      0x83, 0xF9, 0x08,      // cmp ecx,08         << hook here
      0x8D, 0x45, 0x0C,      // lea eax,[ebp+0C]
      0x8D, 0x4D, 0xBC,      // lea ecx,[ebp-44]
      0x0F, 0x43, 0xC2,      // cmovae eax,edx
      0x0F, 0xB7, 0x04, 0x70 // movzx eax,word ptr [eax+esi*2]
  };

  ULONG range = min(processStopAddress - processStartAddress, MAX_REL_ADDR);
  ULONG addr = MemDbg::findBytes(bytes, sizeof(bytes), processStartAddress, processStartAddress + range);
  if (!addr)
  {
    ConsoleOutput("YaneSDK: pattern not found");
    return false;
  }

  HookParam hp;
  hp.address = addr;
  hp.offset = regoffset(eax);
  hp.filter_fun = YaneSDKFilter;
  hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
  ConsoleOutput("INSERT YaneSDK");

  return NewHook(hp, "YaneSDK");
}
bool hibiki::attach_function()
{

  return hibikihook() || InsertYaneSDKHook();
}