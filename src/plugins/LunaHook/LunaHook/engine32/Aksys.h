

class Aksys : public ENGINE
{
public:
    Aksys()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"System.bra";
        is_engine_certain = false;
    };
    bool attach_function();
};