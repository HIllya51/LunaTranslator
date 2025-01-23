

class TSSystem : public ENGINE
{
public:
    TSSystem()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName, L"TSSystem") || Util::CheckFile(L"TSSystem.exe"));
        };
    };
    bool attach_function();
};