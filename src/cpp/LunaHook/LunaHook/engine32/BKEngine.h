

class BKEngine : public ENGINE
{
public:
    BKEngine()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE;
        check_by_target = L"*.bkarc";
    };
    bool attach_function();
};
