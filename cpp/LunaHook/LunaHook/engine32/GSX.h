

class GSX : public ENGINE
{
public:
    GSX()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Game Script eXecuter";
    };
    bool attach_function();
};
