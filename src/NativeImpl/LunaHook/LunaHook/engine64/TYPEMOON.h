

class TYPEMOON : public ENGINE
{
public:
    TYPEMOON()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"data*.hfa";
    };
    bool attach_function();
};
