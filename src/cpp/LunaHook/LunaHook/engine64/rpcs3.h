

class rpcs3 : public ENGINE
{
public:
    rpcs3()
    {
        jittype = JITTYPE::RPCS3;
        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"rpcs3.exe";
    };
    bool attach_function();
};
