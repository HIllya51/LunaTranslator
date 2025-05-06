
// https://vndb.org/v760
// 魔界天使ジブリール
/*
BLOCK "StringFileInfo"
  {
    BLOCK "041104b0"
    {
      VALUE "Comments"
      VALUE "CompanyName",       "FrontWing Co.,LTD."
      VALUE "FileDescription",   "ADV"
      VALUE "FileVersion",       "1, 0, 0, 1"
      VALUE "InternalName",      "ADV2.1"
      VALUE "LegalCopyright",    "Copyright (C) 2002,2003 FrontWing"
      VALUE "LegalTrademarks"
      VALUE "OriginalFilename",  "ADV.exe"
      VALUE "PrivateBuild",      "7d,3c,49,00"
      VALUE "ProductName",       "ADV"
      VALUE "ProductVersion",    "1, 0, 0, 1"
      VALUE "SpecialBuild"
    }
  }
*/
class FrontWing : public ENGINE
{
public:
  FrontWing()
  {

    check_by = CHECK_BY::RESOURCE_STR;
    check_by_target = L"FrontWing Co.,LTD.";
  };
  bool attach_function();
};
class FrontWing2 : public ENGINE
{
public:
  FrontWing2()
  {
    //[071227][フロントウイング] タイムリープ
    check_by = CHECK_BY::FILE_ALL;
    check_by_target = check_by_list{L"MDT\\*.dat", L"BGM.dat", L"CHIP.dat", L"ef.dat", L"Init.dat", L"SE.dat"};
  };
  bool attach_function();
};