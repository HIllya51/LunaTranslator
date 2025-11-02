

class _5pb : public ENGINE
{
public:
    _5pb()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"data\\*.cpk", L"*.cpk", L"*.mpk", L"USRDIR\\*.mpk"};
    };
    bool attach_function();
};

class _5pb_2 : public ENGINE
{
public:
    _5pb_2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"windata/script_body.bin";
        is_engine_certain = false;
    };
    bool attach_function();
};