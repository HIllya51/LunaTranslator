

class Unicorn : public ENGINE
{
public:
    Unicorn()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.szs", L"Data\\*.szs"};
    };
    bool attach_function();
};

class Unicorn_Anesen : public ENGINE
{
public:
    Unicorn_Anesen()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"BGM", L"DATA", L"MGD", L"MSD", L"SE", L"VOICE"};
    };
    bool attach_function();
};