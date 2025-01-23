

class Taskforce2 : public ENGINE
{
public:
    Taskforce2()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"taskforce2") || !wcsncmp(processName_lower, L"taskfo~", 7) || Util::CheckFile(L"Taskforce2.exe"));
        };
    };
    bool attach_function();
};