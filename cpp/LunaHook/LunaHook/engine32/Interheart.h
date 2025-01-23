

class Interheart : public ENGINE
{
public:
    Interheart()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Pack\\*.fpk";
        is_engine_certain = false;
    };
    bool attach_function();
};