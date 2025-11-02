

class Yatagarasu : public ENGINE
{
public:
    Yatagarasu()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Yatagarasu";
    };
    bool attach_function();
};
/*
FILEVERSION    1,0,0,0
PRODUCTVERSION 1,0,0,0
FILEFLAGSMASK  0x17
FILEFLAGS      0x0
FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "CompanyName",       "Yatagarasu"
      VALUE "FileDescription",   "テンタクルロード"
      VALUE "FileVersion",       "1, 0, 0, 0"
      VALUE "InternalName",      "Tentacle"
      VALUE "LegalCopyright",    "(C)2011 Yatagarasu Co.,Ltd."
      VALUE "OriginalFilename",  "Tentacle.exe"
      VALUE "ProductName",       "テンタクルロード アプリケーション"
      VALUE "ProductVersion",    "1, 0, 0, 0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/