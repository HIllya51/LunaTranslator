

class GROOVER : public ENGINE
{
public:
    GROOVER()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []() -> bool
        {
            return GetModuleHandle(L"HdSnr3.dll") && GetModuleHandle(L"RoFAS.dll") && GetModuleHandle(L"RoSnd.dll") &&
                   Util::CheckFile(L"Data/GRP.ARC") && Util::CheckFile(L"Data/SCR.ARC") && Util::CheckFile(L"Data/SND.ARC") &&
                   Util::SearchResourceString(L"GROOVER");
        };
    };
    bool attach_function();
};