

class RRE : public ENGINE
{
public:
    RRE()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"rrecfg.rcf";
    };
    bool attach_function();
};