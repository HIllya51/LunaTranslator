

class Bishop : public ENGINE
{
public:
    Bishop()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"GRAPHICS\\PACK.PK";
        is_engine_certain = false;
    };
    bool attach_function();
};

class Bishop2 : public ENGINE
{
public:
    Bishop2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.bsa";
        is_engine_certain = false;
    };
    bool attach_function();
};