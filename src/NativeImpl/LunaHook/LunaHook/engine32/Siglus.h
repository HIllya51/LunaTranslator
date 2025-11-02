

class Siglus : public ENGINE
{
public:
    Siglus()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"siglusengine") || !wcsncmp(processName_lower, L"siglus~", 7) || Util::CheckFile(L"SiglusEngine.exe"));
        };
    };
    bool attach_function();
};