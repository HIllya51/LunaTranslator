

class PCSX2 : public ENGINE
{
    std::optional<version_t> version;

public:
    PCSX2()
    {
        enginename = "PCSX2";
        version = queryversion();
        if (version)
        {
            auto [a, b, c, d] = version.value();
            std::stringstream ss;
            ss << enginename.value() << " " << a << "." << b << "." << c << "." << d;
            enginename = ss.str();
        }
        jittype = JITTYPE::PCSX2;
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        { return Util::CheckFile(L"pcsx2-qt.exe") || Util::SearchResourceString(L"PCSX2 PS2 Emulator"); };
    };
    bool attach_function();
    bool attach_function1();
};
