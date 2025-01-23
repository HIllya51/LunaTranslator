

class Interlude : public ENGINE
{
public:
    Interlude()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"script.pak", L"system.pak", L"title.pak"};
        is_engine_certain = false;
    };
    bool attach_function();
};
