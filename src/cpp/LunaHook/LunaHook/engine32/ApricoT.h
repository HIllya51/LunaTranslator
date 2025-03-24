

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
class MapleColors : public ENGINE
{
public:
    MapleColors()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _ = {L"adv.dat", L"bgm.dat", L"map.dat", L"minichara.dat", L"minigame.dat", L"SCENARIO.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"};
            auto succ = std::all_of(_.begin(), _.end(), Util::CheckFile);
            auto _2 = {L"adv.dat", L"bgm.dat", L"field.dat", L"mini.dat", L"script.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"};
            succ = succ || std::all_of(_2.begin(), _2.end(), Util::CheckFile);
            return succ;
        };
    };
    bool attach_function();
};