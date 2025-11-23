
/*
FILEVERSION    1,0,0,1
PRODUCTVERSION 1,0,0,1
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
      VALUE "CompanyName",       " "
      VALUE "FileDescription",   "AGE_System"
      VALUE "FileVersion",       "1, 0, 0, 1"
      VALUE "InternalName",      "AGE_System"
      VALUE "LegalCopyright",    "Copyright (C) 2012"
      VALUE "LegalTrademarks"
      VALUE "OriginalFilename",  "AGE_System.exe"
      VALUE "PrivateBuild"
      VALUE "ProductName",       "AGE_System"
      VALUE "ProductVersion",    "1, 0, 0, 1"
      VALUE "SpecialBuild"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/
//(18禁ゲーム) [170331] [ルネ] ようこそ！ スケベエルフの森へ パッケージ版
class AGE_System : public ENGINE
{
public:
  AGE_System()
  {

    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      auto s = check_by_list{L"Agrd.pac", L"vic.pac", L"se.pac", L"mus.pac"};
      return Util::SearchResourceString(L"AGE_System") // 已破解
             || std::all_of(s.begin(), s.end(), [](auto f)
                            { return Util::CheckFile_exits(f); }); // 未破解
    };
  };
  bool attach_function();
};