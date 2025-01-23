

class Footy2 : public ENGINE
{
public:
    Footy2()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"Footy2.dll";
    };
    bool attach_function();
};