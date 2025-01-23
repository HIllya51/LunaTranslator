

class splushwave : public ENGINE
{
public:
    splushwave()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"splush wave";
        is_engine_certain = false;
    };
    bool attach_function();
};