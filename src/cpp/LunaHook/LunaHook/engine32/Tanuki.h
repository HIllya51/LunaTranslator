

class Tanuki : public ENGINE
{
public:
    Tanuki()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.tac";
    };
    bool attach_function();
};

class Tanuki_last : public Tanuki
{
public:
    Tanuki_last()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.g2";
    };
    bool attach_function();
};