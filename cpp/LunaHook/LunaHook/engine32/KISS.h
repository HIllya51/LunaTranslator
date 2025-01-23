

class KISS : public ENGINE
{
public:
    KISS()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"GameData\\script.ysb";
        is_engine_certain = false;
    };
    bool attach_function();
};