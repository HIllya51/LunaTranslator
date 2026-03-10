/*
FILEVERSION    1,0,0,0
PRODUCTVERSION 1,0,0,0
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
      VALUE "Comments",          "Xmas Present"
      VALUE "CompanyName",       "有限会社ティーツー"
      VALUE "FileDescription",   "Xmas"
      VALUE "FileVersion",       "1, 0, 0, 0"
      VALUE "InternalName",      "Xmas Present"
      VALUE "LegalCopyright",    "Copyright (C) 2000 ピンパイ"
      VALUE "OriginalFilename",  "Xmas.exe"
      VALUE "ProductName",       "Xmas Present"
      VALUE "ProductVersion",    "1, 0, 0, 0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/
class Pinpai : public ENGINE
{
public:
  Pinpai()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      auto _ = {L"bgm/*.wdt", L"eve/*.sdt", L"gra/*.gdt", L"se/*.wdt", L"voice/*.wdt"};
      auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
      return checkfile && Util::SearchResourceString(L"Xmas Present");
    };
  };
  bool attach_function();
};