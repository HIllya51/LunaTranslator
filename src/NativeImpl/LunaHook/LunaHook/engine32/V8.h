

class V8 : public ENGINE
{
public:
    V8()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [this]()
        { return attach_function_(); };
    };
    bool attach_function_();
    bool attach_function() { return true; }
};
