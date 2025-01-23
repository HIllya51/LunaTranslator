

class Bootup : public ENGINE
{
public:
    Bootup()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Bootup.dat";
        is_engine_certain = false;
        // lstrlenW can also find text with repetition though
    };
    bool attach_function();
};
