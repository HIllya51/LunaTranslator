

class akatombo : public ENGINE
{
public:
    akatombo()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"akatombo";
        is_engine_certain = false;
    };
    bool attach_function();
};