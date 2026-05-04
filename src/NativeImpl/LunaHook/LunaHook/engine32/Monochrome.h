
/*
FILEVERSION    3,5,23996,1
PRODUCTVERSION 3,5,23996,1
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
      VALUE "Comments",          "Programmed by 池神龍一(Hurry Rabbit+)"
      VALUE "CompanyName",       "PANDA HOUSE"
      VALUE "FileDescription",   "Script Engine 'Monochrome' (Virtual Machine Emulator)"
      VALUE "FileVersion",       "3, 5, 23996, 1"
      VALUE "InternalName",      "Monochrome"
      VALUE "LegalCopyright",    "Copyright (C) 1999 PANDA HOUSE All Rights Reserved"
      VALUE "LegalTrademarks"
      VALUE "OriginalFilename",  "LLesson.exe"
      VALUE "PrivateBuild"
      VALUE "ProductName",       "ラブレッスン"
      VALUE "ProductVersion",    "3, 5, 23996, 1"
      VALUE "SpecialBuild"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 932
  }
}

*/
class Monochrome : public ENGINE
{
public:
    Monochrome()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [](){
            return Util::SearchStringFileInfo(L"PANDA HOUSE") && Util::SearchStringFileInfo(L"Monochrome");
        };
    };
    bool attach_function();
};