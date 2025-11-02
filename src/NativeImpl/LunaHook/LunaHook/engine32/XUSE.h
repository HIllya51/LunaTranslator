

class XUSE : public ENGINE
{
public:
    XUSE()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"CD/BV*";
        is_engine_certain = false;
    };
    bool attach_function();
};