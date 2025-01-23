

class Nijyuei : public ENGINE
{
public:
    Nijyuei()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Nijyuei.kpd";
    };
    bool attach_function();
};