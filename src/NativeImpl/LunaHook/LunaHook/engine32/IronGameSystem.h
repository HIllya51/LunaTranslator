

class IronGameSystem : public ENGINE
{
public:
    IronGameSystem()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"igs_sample") || !wcsncmp(processName_lower, L"igs_sa~", 7) || Util::CheckFile(L"igs_sample.exe"));
        };
    };
    bool attach_function();
};