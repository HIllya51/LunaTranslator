/*
FILEVERSION    1,0,0,1
PRODUCTVERSION 1,0,0,1
FILEFLAGSMASK  0x3F
FILEFLAGS      VS_FF_SPECIALBUILD
FILEOS         VOS_NT_WINDOWS32
FILETYPE       VFT_APP
FILESUBTYPE    0x0
{
  BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments",          "Seraphim"
      VALUE "CompanyName",       "Assemblage Corporation / A.Sumeragi&Fantom"
      VALUE "FileDescription",   "Seraphim"
      VALUE "FileVersion",       "1.02"
      VALUE "InternalName",      "Seraph"
      VALUE "LegalCopyright",    "1998-2000 A.Sumeragi&Fantom"
      VALUE "OriginalFilename",  "Seraph.exe"
      VALUE "ProductName",       "Seraphim"
      VALUE "ProductVersion",    "Version 1.21"
      VALUE "SpecialBuild",      "0.00"
    }
  }
  BLOCK "VarFileInfo"
  {
    VALUE "Translation", 0x411, 1200
  }
}

*/

class Seraphim : public ENGINE
{
public:
  Seraphim()
  {
    check_by = CHECK_BY::CUSTOM;
    check_by_target = []()
    {
      return Util::CheckFileAll({L"ArchPac.Dat", L"ScnPac.Dat", L"Voice0.dat"}) && Util::SearchResourceString(L"Seraphim");
    };
  };
  bool attach_function();
};