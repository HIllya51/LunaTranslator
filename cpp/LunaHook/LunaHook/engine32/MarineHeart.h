

class MarineHeart : public ENGINE
{
public:
    MarineHeart()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName, L"SAISYS") || Util::CheckFile(L"SaiSys.exe"));
        };
    };
    bool attach_function();
};