

class Giga : public ENGINE
{
public:
    Giga()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Dat\\*.pac";
    };
    bool attach_function();
};