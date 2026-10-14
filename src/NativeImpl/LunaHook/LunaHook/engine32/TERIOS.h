
/*
FILEVERSION    1,0,0,18
PRODUCTVERSION 1,0,0,18
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
      VALUE "CompanyName",       "TERIOS"
      VALUE "FileDescription",   "いきなり　はっぴぃベル"
      VALUE "FileVersion",       "1.0.0.18"
      VALUE "InternalName",      "言午 女家"
      VALUE "LegalCopyright",    "Copyright  2001  TERIOS"
      VALUE "LegalTrademarks",   ""
      VALUE "OriginalFilename",  "FIANCEE.EXE"
      VALUE "ProductName",       "HappyBell"
      VALUE "ProductVersion",    "1.00"
      VALUE "Comments",          "Windows 95/98/Me/2000pro"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 932
  }
}

*/
class TERIOS : public ENGINE
{
public:
    TERIOS()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::StringFileInfo;
        check_by_target = L"TERIOS"; // STREAM.PAK
    };
    bool attach_function();
};