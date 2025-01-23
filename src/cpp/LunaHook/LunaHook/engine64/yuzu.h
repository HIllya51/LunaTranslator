

class yuzu : public ENGINE
{
public:
    yuzu()
    {
        jittype = JITTYPE::YUZU;
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            auto exes = {L"suyu.exe", L"yuzu.exe", L"sudachi.exe", L"citron.exe"};
            return std::any_of(exes.begin(), exes.end(), [](const wchar_t *e)
                               { return wcscmp(processName_lower, e) == 0; });
        };
    };
    bool attach_function();
};
