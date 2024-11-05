

class ACTGS : public ENGINE
{
public:
    ACTGS()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"ACTRESS Game System";
    };
    bool attach_function();
};