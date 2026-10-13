
/*
FILEVERSION    1,2,0,1
PRODUCTVERSION 1,2,0,1
FILEFLAGSMASK  0x3F
FILEFLAGS      0x0
FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041103a4"
    {
      VALUE "Comments",          "せ・ん・せ・い 生声"
      VALUE "CompanyName",       "株式会社ディーオー"
      VALUE "FileDescription",   "せ・ん・せ・い 生声"
      VALUE "FileVersion",       "1, 0, 0, 1"
      VALUE "InternalName",      "TEANAM"
      VALUE "LegalCopyright",    "Copyright (C) 1998,1999 D.O. corp."
      VALUE "LegalTrademarks",   "株式会社ディーオー"
      VALUE "OriginalFilename",  "TEANAM.EXE"
      VALUE "ProductName",       "TEANAM アプリケーション"
      VALUE "ProductVersion",    "1, 0, 0, 1"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 932
  }
}

*/
class TEANAM : public ENGINE
{
public:
    TEANAM()
    {

        check_by = CHECK_BY::StringFileInfo;
        check_by_target = L"TEANAM";
    };
    bool attach_function();
};