

class yuzu : public ENGINE
{
public:
    yuzu()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcscmp(processName_lower, L"suyu.exe") == 0 || wcscmp(processName_lower, L"yuzu.exe") == 0 || wcscmp(processName_lower, L"sudachi.exe") == 0);
        };
    };
    bool attach_function();
};
