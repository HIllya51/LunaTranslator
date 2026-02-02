
/*
FILEVERSION    1,0,0,0
PRODUCTVERSION 1,0,0,0
FILEFLAGSMASK  0x3F
FILEFLAGS      VS_FF_PRIVATEBUILD | VS_FF_SPECIALBUILD
FILEOS         VOS_NT_WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments",          "PG : 末広 明日香"
      VALUE "CompanyName",       "みるくかふぇ"
      VALUE "FileDescription",   "紅く輝く雪"
      VALUE "FileVersion",       "1, 0, 0, 0"
      VALUE "InternalName",      "紅く輝く雪"
      VALUE "LegalCopyright",    "Copyright (C) 2003  みるくかふぇ"
      VALUE "LegalTrademarks",   " "
      VALUE "OriginalFilename",  "紅く輝く雪.exe"
      VALUE "PrivateBuild",      " "
      VALUE "ProductName",       "紅く輝く雪"
      VALUE "ProductVersion",    "1, 0, 0, 0"
      VALUE "SpecialBuild",      " "
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}
*/
class Milk : public ENGINE
{
public:
    Milk()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"bcg.rsa", L"demo.rsa", L"font.rsa", L"mask.rsa", L"parts.rsa", L"script.rsa", L"se.rsa", L"voice.rsa"};
    };
    bool attach_function();
};
