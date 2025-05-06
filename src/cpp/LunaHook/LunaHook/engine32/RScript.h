// https://vndb.org/v5096
// 行殺♥ 新選組　人斬り美少女あどべんちゃ～

/*
FILEVERSION    1,0,0,0
PRODUCTVERSION 3,0,0,0
FILEFLAGSMASK  0x3F
FILEFLAGS      0x0
FILEOS         VOS_NT_WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments"
      VALUE "CompanyName",       "LiarSoft"
      VALUE "FileDescription",   "RScript"
      VALUE "FileVersion",       "1, 0, 0, 0"
      VALUE "InternalName",      "RScript"
      VALUE "LegalCopyright",    "Copyright (C)LiarSoft 2001"
      VALUE "LegalTrademarks"
      VALUE "OriginalFilename",  "RScript.exe"
      VALUE "PrivateBuild"
      VALUE "ProductName",       "WindWing RScript"
      VALUE "ProductVersion",    "3, 0, 0, 0"
      VALUE "SpecialBuild"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/
class RScript : public ENGINE
{
public:
  RScript()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      auto _ = {
          L"grpe\\*.lim",
          L"grps\\*.lim",
          L"grpo\\*.lim",
          L"scr\\*.gsc",
      };
      auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
      return checkfile && Util::SearchResourceString(L"RScript");
    };
    is_engine_certain = false;
  };
  bool attach_function();
};