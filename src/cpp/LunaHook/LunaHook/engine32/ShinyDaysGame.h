

class ShinyDaysGame : public ENGINE
{
public:
    ShinyDaysGame()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"shinydays") || !wcsncmp(processName_lower, L"shinyd~", 7) || Util::CheckFile(L"ShinyDays.exe"));
        };
    };
    bool attach_function();
};