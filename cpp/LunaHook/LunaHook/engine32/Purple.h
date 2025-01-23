

class Purple : public ENGINE
{
public:
    Purple()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"WAIT.TAM", L"data.hed", L"data.dat"};
    };
    bool attach_function();
};

class Purple2 : public ENGINE
{
public:
    Purple2()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"misc\\*.pk", L"music\\*.px"};
    };
    bool attach_function();
};