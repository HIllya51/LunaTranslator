

class Stronger : public ENGINE
{
public:
    Stronger()
    {
        check_by = CHECK_BY::FILE;
        check_by_target = L"data/sinario/*.spt";
        is_engine_certain = false;
    };
    bool attach_function();
};