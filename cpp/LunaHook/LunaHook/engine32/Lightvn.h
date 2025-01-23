

class Lightvn : public ENGINE
{
public:
    Lightvn()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return GetModuleHandleW(L"Engine.dll") && GetModuleHandleW(L"BugTrapU.dll");
        };
    };
    bool attach_function();
};
