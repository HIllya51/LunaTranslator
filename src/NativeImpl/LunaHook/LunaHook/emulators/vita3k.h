

class vita3k : public ENGINE
{
    std::optional<version_t> version;

public:
    vita3k()
    {
        enginename = "vita3k";
        version = queryversion();
        if (version)
        {
            auto [a, b, c, d] = version.value();
            std::stringstream ss;
            ss << enginename.value() << " " << a << "." << b << "." << c << "." << d;
            enginename = ss.str();
        }
        jittype = JITTYPE::VITA3K;
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::CheckFile(L"Vita3K.exe") || Util::SearchResourceString(L"Vita3K PSVita Emulator");
        };
    };
    bool attach_function();
    bool attach_function1();
};
