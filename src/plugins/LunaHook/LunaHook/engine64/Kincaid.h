
// FILEVERSION    0,0,0,1
// PRODUCTVERSION 0,0,0,1
// FILEFLAGSMASK  0x3F
// FILEFLAGS      0x0
// FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
// FILETYPE       VFT_DLL
// FILESUBTYPE    0x0
// {
//   BLOCK "StringFileInfo"
//   {
//     BLOCK "080904b0"
//     {
//       VALUE "CompanyName",       "Cookiedraggy"
//       VALUE "FileDescription",   "The Adventures of Kincaid"
//       VALUE "FileVersion",       "0.0.0.1"
//       VALUE "LegalCopyright",    "(c) 2019 Cookiedraggy"
//       VALUE "PrivateBuild",      "01.00.00.00"
//       VALUE "ProductName",       "The Adventures of Kincaid"
//       VALUE "ProductVersion",    "0.0.0.1"
//     }
//   }
//   BLOCK "VarFileInfo"
//   {
//     VALUE "Translation", 0x809, 1200
//   }
// }

class Kincaid : public ENGINE
{
public:
    Kincaid()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"Cookiedraggy") || Util::SearchResourceString(L"The Adventures of Kincaid");
        };
    };
    bool attach_function();
};