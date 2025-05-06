

class Elf : public ENGINE
{
public:
    Elf()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // flutter of birds～鳥達の羽ばたき～ WIN10版本
            // https://vndb.org/v2379
            // 很奇怪，FindFirstFileW在win7上true，在win11上false，但PathFileExists在两者都是true
            auto paks = {L"data.arc", L"effect.arc", L"mes.arc"};
            return std::all_of(paks.begin(), paks.end(), [](auto f)
                               { return Util::CheckFile_exits(f, true); });
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