

class PCSX2 : public ENGINE
{
public:
    PCSX2()
    {
        jittype = JITTYPE::PCSX2;
        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        { return Util::CheckFile(L"pcsx2-qt.exe") || Util::SearchResourceString(L"PCSX2"); };
    };
    bool attach_function();
    bool attach_function1();
};
