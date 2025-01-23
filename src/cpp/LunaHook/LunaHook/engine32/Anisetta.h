

class Anisetta : public ENGINE
{
public:
    Anisetta()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"*.pd", L".pb"};
        is_engine_certain = false;
    };
    bool attach_function();
};