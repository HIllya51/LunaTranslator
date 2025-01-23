

class TeethingRing : public ENGINE
{
public:
    TeethingRing()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"TeethingRing";
    };
    bool attach_function();
};