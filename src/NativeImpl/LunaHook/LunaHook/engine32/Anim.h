

class Anim : public ENGINE
{
public:
    Anim()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"voice\\*.pck";
        is_engine_certain = false;
    };
    bool attach_function();
};