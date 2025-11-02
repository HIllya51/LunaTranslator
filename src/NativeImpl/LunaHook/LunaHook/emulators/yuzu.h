

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
            auto exes = {L"suyu.exe", L"yuzu.exe", L"sudachi.exe", L"citron.exe", L"eden.exe", L"sumi.exe"};
            return std::any_of(exes.begin(), exes.end(), [](const wchar_t *e)
                               { return wcscmp(processName_lower, e) == 0; }) &&
                   (GetModuleHandleW(L"Qt6Core.dll") || GetModuleHandleW(L"Qt5Core.dll"));
        };
        auto _enginename = wcasta(processName);
        enginename = _enginename.substr(0, _enginename.size() - 4);
    };
    bool attach_function();
    bool attach_function1();
};
