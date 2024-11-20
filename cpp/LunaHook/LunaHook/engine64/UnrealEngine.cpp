#include "UnrealEngine.h"

void ENTERGRAMfilter(TextBuffer *buffer, HookParam *hp)
{
  std::wstring str = buffer->strW();
  std::wregex reg1(L"\\|(.*?)\u300a(.*?)\u300b");
  std::wstring result1 = std::regex_replace(str, reg1, L"$1");
  std::wregex reg2(L"\u3000|\n");
  std::wstring result2 = std::regex_replace(result1, reg2, L"");
  buffer->from(result2);
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
  if (!addr)
    return false;
  HookParam hp;
  hp.address = addr + 14;
  hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
  hp.filter_fun = ENTERGRAMfilter;
  hp.offset = get_reg(regs::rsi);
  hp.lineSeparator = L"\\n";
  return NewHook(hp, "UnrealEngine");
}
namespace
{
  bool ue5()
  {
    // https://github.com/HIllya51/LunaTranslator/issues/1175
    const BYTE BYTES[] = {
        0x48, 0x89, 0x5C, 0x24, 0x08, 0x48, 0x89, 0x6C, 0x24, 0x10, 0x48, 0x89, 0x74, 0x24, 0x18, 0x57, 0x41, 0x56, 0x41, 0x57, 0x48, 0x83, 0xEC, 0x20, 0x48, 0x8B, 0x59, 0x10, 0x45, 0x33, 0xF6, 0x4C, 0x8B, 0xFA, 0x48, 0x8B, 0xF1, 0x48, 0x85, 0xDB, 0x74, XX, 0x8B, 0x43, 0x08, 0x85, 0xC0, 0x74, XX, 0x8D, 0x48, 0x01, 0xF0, 0x0F, 0xB1, 0x4B, 0x08, 0x74, XX, 0x85, 0xc0, 0x75, XX, 0x33, 0xdb, 0x49, 0x8b, 0x06, 0xb9, 0x40, 0x00, 0x00, 0x00};
    auto addr = MemDbg::findBytes(BYTES, sizeof(BYTES), processStartAddress, processStopAddress);
    if (!addr)
      return false;
    HookParam hp;
    hp.address = addr;
    hp.type = USING_STRING | CODEC_UTF16 | NO_CONTEXT;
    hp.offset = get_stack(5);
    hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
    {
      auto s = buffer->strW();
      static std::wstring last;
      if (startWith(s, last))
      {
        buffer->from(s.substr(last.size(), s.size() - last.size()));
      }
      last = s;
    };
    return NewHook(hp, "UnrealEngine5");
  }
}
bool UnrealEngine::attach_function()
{
  return InsertENTERGRAM() || ue5();
}
