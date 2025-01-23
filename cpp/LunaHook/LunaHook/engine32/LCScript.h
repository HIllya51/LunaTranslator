

#define LCSE_0 "[0]"   // pseudo separator
#define LCSE_0W L"[0]" // pseudo separator
class LCScript : public ENGINE
{
public:
  LCScript()
  {

    check_by = CHECK_BY::CUSTOM;
    // jichi 3/19/2014: LC-ScriptEngine, GetGlyphOutlineA
    check_by_target = []()
    {
      return (wcsstr(processName, L"lcsebody") || !wcsncmp(processName, L"lcsebo~", 7) || Util::CheckFile(L"lcsebody*"));
    };
  };
  bool attach_function();
};