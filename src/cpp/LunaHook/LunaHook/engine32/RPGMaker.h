

class RPGMaker : public ENGINE
{
public:
    RPGMaker()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto s = check_by_list{L"data/game.dat", L"data/psl.dat", L"data/scenario.dat", L"data/system.dat"};
            return (wcscmp(processName_lower, L"game.dat") == 0) && std::all_of(s.begin(), s.end(), Util::CheckFile);
        };
        is_engine_certain = false;
    };
    bool attach_function();
};
