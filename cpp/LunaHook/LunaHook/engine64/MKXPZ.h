/*
FILEVERSION    2,4,2,0
PRODUCTVERSION 2,4,2,0
FILEFLAGSMASK  0x0
FILEFLAGS      0x0
FILEOS         VOS_UNKNOWN
FILETYPE       VFT_UNKNOWN
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "040904b0"
    {
      VALUE "FileVersion",       "2.4.2"
      VALUE "OriginalFilename",  "mkxp-z.exe"
      VALUE "ProductName",       "mkxp-z"
      VALUE "ProductVersion",    "2.4.2"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x409, 1200
  }
}

*/

class MKXPZ : public ENGINE
{
public:
  MKXPZ()
  {
    check_by = CHECK_BY::RESOURCE_STR;
    check_by_target = L"mkxp-z";
  };
  bool attach_function();
};