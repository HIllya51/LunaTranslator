

class Waffle : public ENGINE
{
public:
    Waffle()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"cfg.pak";
    };
    bool attach_function();
};