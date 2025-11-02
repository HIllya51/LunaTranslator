class NoEngine : public ENGINE
{
public:
    bool attach_function()
    {
        ConsoleOutput("IGNORE %s", getenginename().c_str());
        return false;
    }
};
class Patisserie : public NoEngine
{
public:
    Patisserie()
    {
        // Patisserie
        // DINGIR（ディンギル）
        // 这作依赖于python23.dll，会被匹配到renpy，执行PyRun_SimpleString，PyGILState_Release。执行PyGILState_Release时会崩溃，原因未知，且GDI32函数就可以读取到文本，故予跳过。
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return GetModuleHandle(L"python23.dll") && GetModuleHandle(L"GR.dll") && Util::CheckFile(L"dingir/data/bg.bin") && Util::CheckFile(L"dingir/data/abb/*.abb");
        };
    }
};
class oldSystem40ini : public NoEngine
{
public:
    oldSystem40ini()
    {
        // jichi 1/19/2015: Disable inserting Lstr for System40
        // See: http://sakuradite.com/topic/618

        check_by = CHECK_BY::FILE;
        check_by_target = L"System40.ini";
    };
};
// class RPGMakerRGSS3:public NoEngine{
//     public:
//     RPGMakerRGSS3(){
//       // jichi 6/7/2015: RPGMaker v3

//         check_by=CHECK_BY::FILE;
//         check_by_target=L"*.rgss3a";
//     };
// };

// class FVP:public NoEngine{
//     public:
//     FVP(){
//       // 7/28/2015 jichi: Favorite games

//         check_by=CHECK_BY::FILE;
//         check_by_target=L"*.hcb";
//     };
// };

class AdvPlayerHD : public NoEngine
{
public:
    AdvPlayerHD()
    {
        // supposed to be WillPlus

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"AdvHD.exe", L"AdvHD.dll"};
    };
};

class DPM : public NoEngine
{
public:
    DPM()
    {
        // jichi 4/30/2015: Skip games made from らすこう, such as とある人妻のネトラレ事情
        // It has garbage from lstrlenW. Correct text is supposed to be in TabbedTextOutA.

        check_by = CHECK_BY::FILE;
        check_by_target = L"data_cg.dpm";
    };
};

class Escude_ignore : public NoEngine
{
public:
    Escude_ignore()
    {
        // jichi 3/19/2014: Escude game
        // Example: bgm.bin gfx.bin maou.bin script.bin snd.bin voc.bin

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"gfx.bin", L"snd.bin", L"voc.bin"};
    };
};

class Chartreux : public NoEngine
{
public:
    Chartreux()
    {

        // jichi 12/28/2014: "Chartreux Inc." in Copyright.
        // Sublimary brands include Rosebleu, MORE, etc.
        // GetGlyphOutlineA already works.

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Chartreux";
    };
};
class lcsebody : public NoEngine
{
public:
    lcsebody()
    {

        check_by = CHECK_BY::CUSTOM;
        // jichi 3/19/2014: LC-ScriptEngine, GetGlyphOutlineA
        check_by_target = []()
        {
            return (wcsstr(processName, L"lcsebody") || !wcsncmp(processName, L"lcsebo~", 7) || Util::CheckFile(L"lcsebody*"));
        };
    };
};
// class FVP2:public NoEngine{
//     public:
//     FVP2(){

//         check_by=CHECK_BY::CUSTOM;
//         // jichi 3/19/2014: LC-ScriptEngine, GetGlyphOutlineA
//         check_by_target=[](){

//           wchar_t str[MAX_PATH];
//           DWORD i;
//           for (i = 0; processName[i]; i++) {
//             str[i] = processName[i];
//             if (processName[i] == L'.')
//               break;
//           }
//           *(DWORD *)(str + i + 1) = 0x630068; //.hcb
//           *(DWORD *)(str + i + 3) = 0x62;
//           // jichi 10/3/2013: such like アトリエかぐや
//           return (Util::CheckFile(str));
//         };
//     };
// };

// if (Util::CheckFile(L"AGERC.DLL")) { // jichi 3/17/2014: Eushully, AGE.EXE
//   ConsoleOutput("IGNORE Eushully");
//   return true;
// }
// if (Util::CheckFile(L"*\\Managed\\UnityEngine.dll")) { // jichi 12/3/2013: Unity (BALDRSKY ZERO)
//   ConsoleOutput("IGNORE Unity");
//   return true;
// }
// if (Util::CheckFile(L"bsz_Data\\Managed\\UnityEngine.dll") || Util::CheckFile(L"bsz2_Data\\Managed\\UnityEngine.dll")) {
//   ConsoleOutput("IGNORE Unity");
//   return true;
// }
