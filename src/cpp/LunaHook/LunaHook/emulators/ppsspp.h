
class PPSSPPWindows : public ENGINE
{
public:
    PPSSPPWindows()
    {
        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"PPSSPP*.exe";
        jittype = JITTYPE::PPSSPP;
    };
    bool attach_function();
    bool attach_function1();
};
