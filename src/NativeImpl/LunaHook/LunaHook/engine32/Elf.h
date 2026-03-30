

class Elf : public ENGINE
{
    int type = 0;

public:
    Elf()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            if (Util::CheckFileAll({L"data.arc", L"mes.arc"}, true) &&
                Util::CheckFileAny({L"effect.arc", L"effect.awf"}, true))
            {
                // flutter of birds～鳥達の羽ばたき～ WIN10版本
                // https://vndb.org/v2379
                // 很奇怪，FindFirstFileW在win7上true，在win11上false，但PathFileExists在两者都是true
                // https://vndb.org/v2307
                // 愛のチカラ   ->effect.awf
                type = 1;
            }
            else if (Util::CheckFileAll({L"*.scx", L"data/cg/cg.bin", L"data/cg/cg.pak", L"data/cg/hiz/*.hiz"}))
            {
                //[060127][エルフ] AVキング (mdf+mds)
                type = 2;
            }

            return type;
        };
        // Util::CheckFile(L"Silkys.exe") ||    // It might or might not have Silkys.exe
        // data, effect, layer, mes, music
    };
    bool attach_function();
};

class Elf2 : public ENGINE
{
public:
    Elf2()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // check_by_list{L"data.arc",L"Ai5win.exe",L"mes.arc"};
            return Util::CheckFile(L"Ai5win.exe", true) && Util::CheckFileAny({L"data.arc", L"MISC\\data.arc"}, true) && (Util::CheckFileAny({L"mes.arc", L"MISC\\mes.arc"}, true));
        };
    };
    bool attach_function();
};

class ElfFunClubFinal : public ENGINE
{
public:
    ElfFunClubFinal()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return wcscmp(processName_lower, L"fanclub.exe") == 0;
        };
    };
    bool attach_function();
};