// https://vndb.org/v10190
// 想い出の彼方

/*
FILEVERSION    1,0,7,15
PRODUCTVERSION 1,0,7,15
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
      VALUE "Comments",          "$"
      VALUE "CompanyName",       "yonie software"
      VALUE "FileDescription",   "ｼﾅﾘｵﾌﾟﾚｲﾔｰ"
      VALUE "FileVersion",       "1, 0, 7, 15"
      VALUE "InternalName",      "Sceplay"
      VALUE "LegalCopyright",    "Copyright (C) 2000 Youhei Sueda"
      VALUE "LegalTrademarks",   "$"
      VALUE "OriginalFilename",  "Sceplay.exe"
      VALUE "PrivateBuild",      "$"
      VALUE "ProductName",       "ｼﾅﾘｵﾌﾟﾚｲﾔｰ"
      VALUE "ProductVersion",    "1, 0, 7, 15"
      VALUE "SpecialBuild",      "$"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/

class Sceplay : public ENGINE
{
public:
  Sceplay()
  {

    check_by = CHECK_BY::RESOURCE_STR;
    check_by_target = L"Sceplay";
  };
  bool attach_function();
};