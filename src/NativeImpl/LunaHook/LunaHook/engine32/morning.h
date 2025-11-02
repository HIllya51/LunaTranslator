

class morning : public ENGINE
{
public:
    morning()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.ttd";
        is_engine_certain = false;
    };
    bool attach_function();
};