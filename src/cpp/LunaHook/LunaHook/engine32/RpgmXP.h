

class RpgmXP : public ENGINE
{
public:
    RpgmXP()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.rgssad";
        is_engine_certain = false;
    };
    bool attach_function();
};