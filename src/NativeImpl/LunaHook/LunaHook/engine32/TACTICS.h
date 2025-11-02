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
      VALUE "CompanyName",       "ﾀｸﾃｨｸｽ"
      VALUE "FileDescription",   "すずがうたう日"
      VALUE "FileVersion",       "1.00"
      VALUE "InternalName",      "SUZUUTA"
      VALUE "LegalCopyright",    "Copyright (C) 1999"
      VALUE "OriginalFilename",  "SUZU.EXEC"
      VALUE "ProductName",       "SuzuGaUtauHi"
      VALUE "ProductVersion",    "1.00"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/

/*
FILEVERSION    1,1,0,0
PRODUCTVERSION 1,1,0,0
FILEFLAGSMASK  0x3F
FILEFLAGS      0x0
FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041103A4"
    {
      VALUE "CompanyName",       "Tactics"
      VALUE "FileDescription",   "Cheerio! ver1.1"
      VALUE "FileVersion",       "1.1.0.0"
      VALUE "InternalName",      "Tactics Game System"
      VALUE "LegalCopyright",    "(c)Tactics 2000"
      VALUE "LegalTrademarks",   ""
      VALUE "OriginalFilename",  "CHEERIO.EXE"
      VALUE "ProductName",       "Cheerio! ver1.1"
      VALUE "ProductVersion",    "1.1.0.0"
      VALUE "Comments",          ""
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 932
  }
}

*/
class TACTICS : public ENGINE
{
public:
  TACTICS()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    { return Util::SearchResourceString(L"ﾀｸﾃｨｸｽ") || Util::SearchResourceString(L"Tactics"); };
  };
  bool attach_function();
};