

class Silkys : public ENGINE
{
public:
    Silkys()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"data.arc", L"effect.arc", L"Script.arc"};
        /// Almost the same as Silkys except mes.arc is replaced by Script.arc
    };
    bool attach_function();
};
class SilkysOld : public ENGINE
{
public:
    SilkysOld()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"bgm.AWF", L"effect.AWF", L"gcc.ARC", L"mes.ARC", L"sequence.ARC"};
        /// Almost the same as Silkys except mes.arc is replaced by Script.arc
    };
    bool attach_function();
};

class Siglusold : public ENGINE
{
public:
    Siglusold()
    {
        // 女系家族
        // https://vndb.org/v5650
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.mfg", L"*.mff", L"*.mfm", L"*.mfs"};
    };
    bool attach_function();
};

class Silkyssakura : public ENGINE
{
public:
    Silkyssakura()
    {
        // いれかわ　お姉ちゃん、ぼくの身体でオナニーしちゃうの!
        check_by = CHECK_BY::FILE;
        check_by_target = L"pak\\data001.pak";
    };
    bool attach_function();
};

class Silkysveryveryold : public ENGINE
{
public:
    Silkysveryveryold()
    {
        // flutter of birds II 天使たちの翼
        // https://vndb.org/v2380
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        { return Util::CheckFile_exits(L"*SYS*.ifl"); }; // L"*SYS.ifl";
    };
    bool attach_function();
};

class Aisystem6 : public ENGINE
{
public:
    Aisystem6()
    {
        // 肢体を洗う
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto check1 = Util::CheckFile(L"script.arc") && Util::CheckFile(L"sequence.arc") && Util::CheckFile(L"mask.arc") && Util::CheckFile(L"bitmap.arc") && Util::CheckFile(L"flag0000");
            if (!check1)
                return false;
            char AISYSTEM_6[] = "AISYSTEM_6";
            return 0 != MemDbg::findBytes(AISYSTEM_6, sizeof(AISYSTEM_6), processStartAddress, min(processStopAddress, processStartAddress + 0x100000));
        };
    };
    bool attach_function();
};