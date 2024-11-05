

class lucasystem : public ENGINE
{
public:
    lucasystem()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"files/*.PAK";
    };
    bool attach_function();
};
