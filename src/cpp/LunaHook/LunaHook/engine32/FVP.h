

class FVP : public ENGINE
{
public:
    FVP()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"*.hcb";
    };
    bool attach_function();
};