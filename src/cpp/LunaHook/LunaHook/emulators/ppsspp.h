
class PPSSPPWindows : public ENGINE
{
    std::string enginename = "PPSSPP";
    std::optional<version_t> version;

public:
    PPSSPPWindows()
    {
        version = queryversion();
        if (version)
        {
            auto [a, b, c, d] = version.value();
            std::stringstream ss;
            ss << enginename << " " << a << "." << b << "." << c << "." << d;
            enginename = ss.str();
        }
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        jittype = JITTYPE::PPSSPP;
        check_by_target = []()
        {
            return Util::CheckFile(L"PPSSPP*.exe") || Util::SearchResourceString(L"PPSSPP PSP emulator");
        };
    };
    bool attach_function();
    bool attach_function1();
    const char *getenginename() override
    {
        return enginename.c_str();
    }
};
