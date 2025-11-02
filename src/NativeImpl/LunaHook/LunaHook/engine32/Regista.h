

class Regista : public ENGINE
{
public:
    Regista()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"data\\*.afs";
        is_engine_certain = false;
    };
    bool attach_function();
};