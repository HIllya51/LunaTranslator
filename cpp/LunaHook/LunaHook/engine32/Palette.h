

class Palette : public ENGINE
{
public:
    Palette()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"data\\*.pak";
    };
    bool attach_function();
};