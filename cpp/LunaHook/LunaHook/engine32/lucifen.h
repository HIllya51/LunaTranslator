

class Lucifen : public ENGINE
{
public:
    Lucifen()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.lpk";
    };
    bool attach_function();
};