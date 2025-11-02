// https://store.steampowered.com/app/828380/Death_Mark_Vol1/
// Death Mark Vol.1 - 死印之迷雾
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
      VALUE "FileVersion",       "1.0.0.0"
      VALUE "InternalName",      "Death Mark.exe"
      VALUE "LegalCopyright",    "©EXPERIENCE. Licensed to and published by Aksys Games."
      VALUE "OriginalFilename",  "Death Mark.exe"
      VALUE "ProductName",       "Death Mark"
      VALUE "ProductVersion",    "1.0.0.0"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/
class AksysGames : public ENGINE
{
public:
  AksysGames()
  {

    check_by = CHECK_BY::RESOURCE_STR;
    check_by_target = L"Aksys Games";
    is_engine_certain = false;
  };
  bool attach_function();
};