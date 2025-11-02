

class Suika2 : public ENGINE
{
public:
    Suika2()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"suika.exe", L"conf/config.txt"};
    };
    bool attach_function();
};