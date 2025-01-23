

class EntisGLS : public ENGINE
{
public:
    EntisGLS()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Data\\*.dat";
        is_engine_certain = false;
    };
    bool attach_function();
};