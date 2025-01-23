

class UnknownEngine : public ENGINE
{
public:
    UnknownEngine()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"*.aqa";
    };
    bool attach_function();
};