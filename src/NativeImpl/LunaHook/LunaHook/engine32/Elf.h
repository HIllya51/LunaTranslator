

class Elf : public ENGINE
{
    int type = 0;

public:
    Elf()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            // flutter of birds～鳥達の羽ばたき～ WIN10版本
            // https://vndb.org/v2379
            // 很奇怪，FindFirstFileW在win7上true，在win11上false，但PathFileExists在两者都是true
            auto paks = {L"data.arc", L"mes.arc"};
            // https://vndb.org/v2307
            // 愛のチカラ   ->effect.awf
            auto paks2 = {L"effect.arc", L"effect.awf"};
            //[060127][エルフ] AVキング (mdf+mds)
            auto avking = {L"*.scx", L"data/cg/cg.bin", L"data/cg/cg.pak", L"data/cg/hiz/*.hiz"};
            if (std::all_of(paks.begin(), paks.end(), [](auto f)
                            { return Util::CheckFile_exits(f, true); }) &&
                std::any_of(paks2.begin(), paks2.end(), [](auto f)
                            { return Util::CheckFile_exits(f, true); }))
                type = 1;
            else if (std::all_of(avking.begin(), avking.end(), Util::CheckFile))
                type = 2;

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
            return Util::CheckFile_exits(L"Ai5win.exe", true) && (Util::CheckFile_exits(L"data.arc", true) || Util::CheckFile_exits(L"MISC\\data.arc", true)) && (Util::CheckFile_exits(L"mes.arc", true) || Util::CheckFile_exits(L"MISC\\mes.arc", true));
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