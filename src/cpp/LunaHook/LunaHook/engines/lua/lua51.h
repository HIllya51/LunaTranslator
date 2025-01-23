

class lua51 : public ENGINE
{
public:
    lua51()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"lua5.1.dll", L"lua51.dll"};
        is_engine_certain = false;
    };
    bool attach_function();
};