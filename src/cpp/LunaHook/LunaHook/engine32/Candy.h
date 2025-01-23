

class Candy : public ENGINE
{
public:
    Candy()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.fpk", L"data\\*.fpk"};
        is_engine_certain = false;
    };
    bool attach_function();
};

class WillowSoft : public ENGINE
{
public:
    WillowSoft()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Selene.dll";
        is_engine_certain = false;
    };
    bool attach_function();
};
