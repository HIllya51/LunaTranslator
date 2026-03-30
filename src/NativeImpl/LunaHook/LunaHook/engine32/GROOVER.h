

class GROOVER : public ENGINE
{
public:
    GROOVER()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []() -> bool
        {
            return Util::CheckFileAll({L"Data/GRP.ARC", L"Data/SCR.ARC", L"Data/SND.ARC"}) &&
                   Util::SearchResourceString(L"GROOVER");
        };
    };
    bool attach_function();
};