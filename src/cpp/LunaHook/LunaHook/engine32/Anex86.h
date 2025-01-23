

class Anex86 : public ENGINE
{
public:
    Anex86()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"anex86") || Util::CheckFile(L"anex86.exe"));
        };
    };
    bool attach_function();
};