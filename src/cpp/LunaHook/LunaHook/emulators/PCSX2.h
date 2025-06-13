

class PCSX2 : public ENGINE
{
    std::string enginename = "PCSX2";
    std::optional<version_t> version;

public:
    PCSX2()
    {
        version = queryversion();
        if (version)
        {
            auto [a, b, c, d] = version.value();
            std::stringstream ss;
            ss << enginename << " " << a << "." << b << "." << c << "." << d;
            enginename = ss.str();
        }
        jittype = JITTYPE::PCSX2;
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        { return Util::CheckFile(L"pcsx2-qt.exe") || Util::SearchResourceString(L"PCSX2"); };
    };
    bool attach_function();
    bool attach_function1();
    const char *getenginename() override
    {
        return enginename.c_str();
    }
};
