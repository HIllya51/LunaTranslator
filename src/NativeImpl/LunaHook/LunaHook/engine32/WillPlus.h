

class WillPlus : public ENGINE
{
public:
    WillPlus()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"Rio.arc", L"Chip*.arc"};
    };
    bool attach_function();
};

class Willold : public ENGINE
{
public:
    Willold()
    {
        // https://vndb.org/v17755
        // 凌辱鬼
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"*.BIN", L"DATA\\*.ENV", L"DATA\\*.WBP"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            if (checkfile)
            {
                auto __ = R"(Software\WILL\)";
                checkfile &= !!MemDbg::findBytes(__, strlen(__), processStartAddress, processStopAddress);
            }
            return checkfile;
        };
    }
    bool attach_function();
};