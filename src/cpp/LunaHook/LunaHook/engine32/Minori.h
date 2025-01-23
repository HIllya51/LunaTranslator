

class Minori : public ENGINE
{
public:
    Minori()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.paz";
        is_engine_certain = false;
    };
    bool attach_function();
};