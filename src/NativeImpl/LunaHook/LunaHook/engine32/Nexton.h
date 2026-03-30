

class Nexton : public ENGINE
{
public:
    Nexton()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"aInfo.db") ||
                   Util::CheckFileAll({L"cfg.cfg", L"SystemConfig.exe", L"data.arc", L"se_000.arc", L"voice_000.arc"});
        };
    };
    bool attach_function();
};

class Nexton1 : public ENGINE
{
public:
    Nexton1()
    {

        check_by = CHECK_BY::FILE;
        // old nexton game
        check_by_target = L"comnArc.arc";
        is_engine_certain = false;
    };
    bool attach_function();
};