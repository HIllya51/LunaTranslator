// FILEVERSION    1,0,0,0
// PRODUCTVERSION 1,0,0,0
// FILEFLAGSMASK  0x17
// FILEFLAGS      0x0
// FILEOS         VOS_UNKNOWN | VOS__WINDOWS32
// FILETYPE       VFT_UNKNOWN
// FILESUBTYPE    0x0
// {
//   BLOCK "StringFileInfo"
//   {
//     BLOCK "041104b0"
//     {
//       VALUE "FileVersion",       "1, 0, 0, 0"
//       VALUE "InternalName",      "明日はきっと、晴れますように　体験版"
//       VALUE "LegalCopyright",    "Copyright (C)Hug 2009"
//       VALUE "ProductName",       "明日はきっと、晴れますように"
//       VALUE "ProductVersion",    "1, 0, 0, 0"
//     }
//   }
//   BLOCK "VarFileInfo"
//   {
//     VALUE "Translation", 0x411, 1200
//   }
// }

class Hug : public ENGINE
{
public:
    Hug()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"data/data*.hud", L"data/img.hud", L"data/mv.hud", L"data/se.hud", L"data/txt.hud", L"data/vo.hud", L"data/bgm/*.hum"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            return checkfile && Util::SearchResourceString(L"Copyright (C)Hug");
        };
    };
    bool attach_function();
};