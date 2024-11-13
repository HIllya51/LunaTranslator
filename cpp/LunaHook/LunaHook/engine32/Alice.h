

class Alice : public ENGINE
{
public:
    Alice()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = [this]()
        { return attach_function_(); };
    };
    bool attach_function_();
    bool attach_function() { return true; }
};