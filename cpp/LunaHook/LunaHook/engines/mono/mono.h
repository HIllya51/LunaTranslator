

class mono : public ENGINE
{
public:
    mono()
    {
        jittype = JITTYPE::UNITY;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [this]()
        { return attach_function_(); };
    };
    bool attach_function_();
    bool attach_function() { return true; }
};
