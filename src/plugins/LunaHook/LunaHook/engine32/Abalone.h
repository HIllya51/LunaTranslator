

class Abalone : public ENGINE
{
public:
    Abalone()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Archive.dat";
        is_engine_certain = false;
    };
    bool attach_function();
};