

class EME : public ENGINE
{
public:
    EME()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"emecfg.ecf";
    };
    bool attach_function();
};