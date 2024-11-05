

class pchooks : public ENGINE
{
public:
    pchooks()
    {

        check_by = CHECK_BY::ALL_TRUE;
        dontstop = true;
    };
    bool attach_function();
};
