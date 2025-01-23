

class CodeX : public ENGINE
{
public:
    CodeX()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.xfl";
        is_engine_certain = false;
    };
    bool attach_function();
};