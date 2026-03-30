

class AZScript : public ENGINE
{
public:
    AZScript()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"scenario.axr", L"bgm.axr", L"cg.axr", L"movie.axr", L"voice.axr", L"se.axr"}) &&
                   Util::SearchResourceString(L"AZScript/VNEngine");
        };
        is_engine_certain = false;
    };
    bool attach_function();
};
