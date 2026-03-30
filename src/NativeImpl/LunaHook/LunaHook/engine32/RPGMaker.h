

class RPGMaker : public ENGINE
{
public:
    RPGMaker()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcscmp(processName_lower, L"game.dat") == 0) &&
                   Util::CheckFileAll({L"data/game.dat", L"data/psl.dat", L"data/scenario.dat", L"data/system.dat"});
        };
        is_engine_certain = false;
    };
    bool attach_function();
};
