
// FILEVERSION    1,1,2,42
// PRODUCTVERSION 1,1,2,42
// FILEFLAGSMASK  0x3F
// FILEFLAGS      0x0
// FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
// FILETYPE       VFT_APP
// FILESUBTYPE    0x0
// {
//   BLOCK "StringFileInfo"
//   {
//     BLOCK "041103A4"
//     {
//       VALUE "CompanyName",       ""
//       VALUE "FileDescription",   "Adventure Game Engine"
//       VALUE "FileVersion",       "1.1.2.42"
//       VALUE "InternalName",      "ransel"
//       VALUE "LegalCopyright",    "Copyright (c) 2001-2002 苦魔鬼轟丸 KUMAKI,Todorokimaru all right reserved."
//       VALUE "LegalTrademarks",   ""
//       VALUE "OriginalFilename",  "ransel.exe"
//       VALUE "ProductName",       "ransel"
//       VALUE "ProductVersion",    "1.1"
//       VALUE "Comments",          "ranselとはランドセルの語源でオランダ語です。"
//     }
//   }
//   BLOCK "VarFileInfo"
//   {
//     VALUE "Translation", 0x411, 932
//   }
// }

class ransel : public ENGINE
{
public:
    ransel()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Adventure Game Engine";
    };
    bool attach_function();
};