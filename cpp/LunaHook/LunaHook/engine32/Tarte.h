

class Tarte : public ENGINE
{
public:
    Tarte()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"caf\\script.caf";
        is_engine_certain = false;
    };
    bool attach_function();
};