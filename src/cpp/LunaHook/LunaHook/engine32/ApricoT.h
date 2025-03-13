

class ApricoT : public ENGINE
{
public:
    ApricoT()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.a*";
    };
    bool attach_function();
};

class ApricoTlast : public ApricoT
{
public:
    ApricoTlast()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.dat";
        is_engine_certain = false;
    };
};
class CROSSNET : public ENGINE
{
public:
    CROSSNET()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"adv.dat", L"bgm.dat", L"map.dat", L"minichara.dat", L"minigame.dat", L"SCENARIO.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"};
            return std::all_of(_.begin(), _.end(), Util::CheckFile);
        };
    };
    bool attach_function();
};