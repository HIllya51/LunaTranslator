

class ApRicoT : public ENGINE
{
public:
    ApRicoT()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.a*";
    };
    bool attach_function();
};

class ApRicoTlast : public ApRicoT
{
public:
    ApRicoTlast()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.dat";
        is_engine_certain = false;
    };
};
class ApRicoTOld : public ENGINE
{
public:
    ApRicoTOld()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto _1 = {L"adv.dat", L"bgm.dat", L"map.dat", L"minichara.dat", L"minigame.dat", L"SCENARIO.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"};
            auto succ = std::all_of(_1.begin(), _1.end(), Util::CheckFile);
            auto _2 = {L"adv.dat", L"bgm.dat", L"field.dat", L"mini.dat", L"script.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"};
            succ = succ || std::all_of(_2.begin(), _2.end(), Util::CheckFile);
            auto _4 = {L"adv.dat", L"bgm.dat", L"script.dat", L"SE.dat", L"sec.dat", L"std.dat", L"system.dat", L"voice.dat"};
            succ = succ || std::all_of(_4.begin(), _4.end(), Util::CheckFile);
            auto _3 = {L"sec.dat", L"bgm.dat", L"script.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat",
                       L"adv/event.dat", L"adv/sprite.dat", L"adv/mask.dat", L"adv/effect.dat", L"adv/bg.dat"};
            succ = succ || std::all_of(_3.begin(), _3.end(), Util::CheckFile);
            return succ;
        };
    };
    bool attach_function();
};