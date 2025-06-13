
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
        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"PPSSPP*.exe";
        jittype = JITTYPE::PPSSPP;
    };
    bool attach_function();
    bool attach_function1();
    const char *getenginename() override
    {
        return enginename.c_str();
    }
};
