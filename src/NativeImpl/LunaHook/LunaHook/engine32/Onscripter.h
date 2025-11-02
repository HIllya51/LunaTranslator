

class Onscripter : public ENGINE
{
public:
    Onscripter()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc.nsa";
        is_engine_certain = false;
    };
    bool attach_function();
};