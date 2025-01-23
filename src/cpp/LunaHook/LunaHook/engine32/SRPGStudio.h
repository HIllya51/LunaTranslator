

class SRPGStudio : public ENGINE
{
public:
    SRPGStudio()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"runtime.rts";
    };
    bool attach_function();
};