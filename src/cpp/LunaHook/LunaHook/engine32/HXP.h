

class HXP : public ENGINE
{
public:
    HXP()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"DATA\\*.HXP";
    };
    bool attach_function();
};