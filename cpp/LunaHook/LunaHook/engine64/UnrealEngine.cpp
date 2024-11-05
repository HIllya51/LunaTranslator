#include "UnrealEngine.h"

bool ENTERGRAMfilter(void *data, size_t *size, HookParam *hp)
{

  auto text = reinterpret_cast<LPWSTR>(data);
  std::wstring str = std::wstring(text, *size / 2);
  std::wregex reg1(L"\\|(.*?)\x300a(.*?)\x300b");
  std::wstring result1 = std::regex_replace(str, reg1, L"$1");
  std::wregex reg2(L"\x3000|\n");
  std::wstring result2 = std::regex_replace(result1, reg2, L"");
  write_string_overwrite(text, size, result2);
  return true;
};
bool InsertENTERGRAM()
{
  // https://vndb.org/v40521
  //[240125][1208048][エンターグラム] すだまリレイシヨン パッケージ版 (mdf+mds)

  const BYTE BYTES[] = {
      0x48, 0x8B, 0x43, 0x38,
      0x48, 0x8D, 0x7C, 0x24, 0x30,
      0x48, 0x8B, 0x74, 0x24, 0x20,
      0x48, 0x85, 0xC0,
      0x48, 0x8B, 0xCD,
      0x48, 0x89, 0x6C, 0x24, 0x40,
      0x48, 0x0F, 0x45, 0xF8};
  auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
  if (addr == 0)
    return false;
  HookParam hp;
  hp.address = addr + 14;
  hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
  hp.filter_fun = ENTERGRAMfilter;
  hp.offset = get_reg(regs::rsi);
  hp.newlineseperator = L"\\n";
  return NewHook(hp, "UnrealEngine");
}
bool UnrealEngine::attach_function()
{
  return InsertENTERGRAM();
}
