
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
    BLOCK "001104b0"
    {
      VALUE "CompanyName",       "CAPCOM CO., LTD."
      VALUE "FileDescription",   "大逆転裁判1＆2　-成歩堂龍ノ介の冒險と覺悟-"
      VALUE "FileVersion",       "1.0.0.0"
      VALUE "InternalName",      "TGAAC.exe"
      VALUE "LegalCopyright",    "©CAPCOM CO., LTD. 2021 ALL RIGHTS RESERVED."
      VALUE "OriginalFilename",  "TGAAC.exe"
      VALUE "ProductName",       "大逆転裁判1＆2　-成歩堂龍ノ介の冒險と覺悟-"
      VALUE "ProductVersion",    "1.0.0.0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x11, 1200
  }
}
*/
class CAPCOM : public ENGINE
{
public:
  CAPCOM()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      return Util::CheckFile(L"nativeDX11x64\\archive\\*.arc") && Util::SearchStringFileInfo(L"CAPCOM CO., LTD.");
    };
  };
  bool attach_function();
};