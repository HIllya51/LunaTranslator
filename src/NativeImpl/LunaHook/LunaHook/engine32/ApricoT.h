

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
            return Util::CheckFileAll({L"adv.dat", L"bgm.dat", L"map.dat", L"minichara.dat", L"minigame.dat",
                                        L"SCENARIO.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"}) ||
                   Util::CheckFileAll({L"adv.dat", L"bgm.dat", L"field.dat", L"mini.dat", L"script.dat",
                                        L"SE.dat", L"std.dat", L"system.dat", L"voice.dat"}) ||
                   Util::CheckFileAll({L"adv.dat", L"bgm.dat", L"script.dat", L"SE.dat", L"sec.dat", L"std.dat", L"system.dat", L"voice.dat"}) ||
                   Util::CheckFileAll({L"sec.dat", L"bgm.dat", L"script.dat", L"SE.dat", L"std.dat", L"system.dat", L"voice.dat",
                                        L"adv/event.dat", L"adv/sprite.dat", L"adv/mask.dat", L"adv/effect.dat", L"adv/bg.dat"});
        };
    };
    bool attach_function();
};