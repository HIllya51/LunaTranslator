

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
