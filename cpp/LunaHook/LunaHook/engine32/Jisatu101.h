

class Jisatu101 : public ENGINE
{
public:
    Jisatu101()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"101.exe";
        is_engine_certain = false;
    };
    bool attach_function();
};