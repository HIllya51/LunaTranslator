

class Ciel : public ENGINE
{
public:
    Ciel()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"sys/kidoku.dat";
    };
    bool attach_function();
};