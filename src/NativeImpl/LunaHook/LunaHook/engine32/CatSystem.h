

class CatSystem : public ENGINE
{
public:
    CatSystem()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.int";
        is_engine_certain = false;
    };
    bool attach_function();
};