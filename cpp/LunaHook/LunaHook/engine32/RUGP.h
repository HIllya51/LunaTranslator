

class RUGP : public ENGINE
{
public:
    RUGP()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"rugp") || Util::CheckFile(L"rugp.exe"));
        };
    };
    bool attach_function();
};