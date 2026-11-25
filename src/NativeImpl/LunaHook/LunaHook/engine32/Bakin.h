
/*
FILEVERSION    1,12,9,3
PRODUCTVERSION 1,12,9,3
FILEFLAGSMASK  0x3F
FILEFLAGS      0x0
FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x0, 1200
  }
  BLOCK "StringFileInfo"
  {
    BLOCK "000004b0"
    {
      VALUE "Comments",          "SMILE GAME BUILDER RPG Player"
      VALUE "CompanyName",       "SmileBoom Co.Ltd."
      VALUE "FileDescription",   "SGB RPG Player"
      VALUE "FileVersion",       "1.12.9.3"
      VALUE "InternalName",      "sgb_rpgplayer.exe"
      VALUE "LegalCopyright",    "Copyright c 2016 SmileBoom Co.Ltd. All Rights Reserved."
      VALUE "LegalTrademarks",   ""
      VALUE "OriginalFilename",  "sgb_rpgplayer.exe"
      VALUE "ProductName",       "SGB RPG Player"
      VALUE "ProductVersion",    "1.12.9.3"
      VALUE "Assembly Version",  "1.12.9.3"
    }
  }
}

*/

class Bakin : public ENGINE
{
public:
  Bakin()
  {
    check_by = CHECK_BY::StringFileInfo;
    check_by_target = L"SMILE GAME BUILDER RPG Player";
    is_engine_certain = true;
  };
  bool attach_function();
};
