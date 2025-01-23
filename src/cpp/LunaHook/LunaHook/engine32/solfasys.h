
// https://vndb.org/v5183
// 朝っぱらから発情家族

/*
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments",          "Solfa Novel System(Based on STUDIO SELDOM Adventure System Version 5.29/(c)AKIYAMA Kouhei)"
      VALUE "CompanyName",       "sol-fa-soft"
      VALUE "FileDescription",   "solfasys"
      VALUE "FileVersion",       "5, 29, 0, 0"
      VALUE "InternalName",      "solfasys"
      VALUE "LegalCopyright",    "sol-fa-soft"
      VALUE "OriginalFilename",  "solfasys.exe"
      VALUE "ProductName",       "solfa25"
      VALUE "ProductVersion",    "5, 29, 0, 0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}
*/

// https://vndb.org/v5175
// ななちゃんといっしょ

/*
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments",          "Solfa Standard Novel System(Based on STUDIO SELDOM Adventure System Version 5.20/(c)AKIYAMA Kouhei)"
      VALUE "CompanyName",       "sol-fa-soft"
      VALUE "FileDescription",   "solfasys"
      VALUE "FileVersion",       "1, 0, 0, 0"
      VALUE "InternalName",      "solfasys"
      VALUE "LegalCopyright",    "sol-fa-soft"
      VALUE "OriginalFilename",  "solfasys.exe"
      VALUE "ProductName",       "solfasys"
      VALUE "ProductVersion",    "1, 0, 0, 0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}
*/
class solfasys : public ENGINE
{
public:
  solfasys()
  {

    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      return Util::SearchResourceString(L"Solfa Novel System") || Util::SearchResourceString(L"Solfa Standard Novel System");
    };
    is_engine_certain = false;
  };
  bool attach_function();
};