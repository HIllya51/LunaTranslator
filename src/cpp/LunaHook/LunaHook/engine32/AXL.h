

class AXL : public ENGINE
{
public:
    AXL()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"script.arc";
        is_engine_certain = false;
    };
    bool attach_function();
};