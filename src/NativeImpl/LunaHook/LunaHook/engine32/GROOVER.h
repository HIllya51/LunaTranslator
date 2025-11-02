

class GROOVER : public ENGINE
{
public:
    GROOVER()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []() -> bool
        {
            return Util::CheckFile(L"Data/GRP.ARC") && Util::CheckFile(L"Data/SCR.ARC") && Util::CheckFile(L"Data/SND.ARC") &&
                   Util::SearchResourceString(L"GROOVER");
        };
    };
    bool attach_function();
};