

class Tomato : public ENGINE
{
public:
    Tomato()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"*.kun", L"*.arc"};
    };
    bool attach_function();
};