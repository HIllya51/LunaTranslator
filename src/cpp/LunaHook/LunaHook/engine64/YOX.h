

class YOX : public ENGINE
{
public:
    YOX()
    {

        check_by = CHECK_BY::FILE;
        is_engine_certain = false;
        check_by_target = L"base/*.dat";
    };
    bool attach_function();
};
