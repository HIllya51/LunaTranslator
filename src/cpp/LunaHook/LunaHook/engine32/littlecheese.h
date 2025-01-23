

class littlecheese : public ENGINE
{
public:
    littlecheese()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.bmx";
        is_engine_certain = false;
    };
    bool attach_function();
};