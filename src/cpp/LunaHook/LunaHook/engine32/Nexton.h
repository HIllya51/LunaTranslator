

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
                   (Util::CheckFile(L"cfg.cfg") &&
                    Util::CheckFile(L"SystemConfig.exe") &&
                    Util::CheckFile(L"data.arc") &&
                    Util::CheckFile(L"se_000.arc") &&
                    Util::CheckFile(L"voice_000.arc"));
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