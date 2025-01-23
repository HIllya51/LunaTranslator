

class SYSD : public ENGINE
{
public:
    SYSD()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.dpk", L"SYSD.INI"};
        is_engine_certain = false;
    };
    bool attach_function();
};