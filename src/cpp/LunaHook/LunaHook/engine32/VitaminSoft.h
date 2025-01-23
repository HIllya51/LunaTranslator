

class VitaminSoft : public ENGINE
{
public:
    VitaminSoft()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.fpk";
        is_engine_certain = false;
    };
    bool attach_function();
};