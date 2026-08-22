

class _5pb : public ENGINE
{
public:
    _5pb()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"data\\*.cpk", L"*.cpk", L"*.mpk", L"data\\*.mpk"};
    };
    bool attach_function();
};

class _5pb_2 : public ENGINE
{
public:
    _5pb_2()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"wind3d11data/*.bin", L"wind3d11data/*.psb.m"};
    };
    bool attach_function();
};
