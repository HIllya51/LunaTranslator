

class Nitroplus2 : public ENGINE
{
public:
    Nitroplus2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.npk";
        is_engine_certain = false;
    };
    bool attach_function();
};