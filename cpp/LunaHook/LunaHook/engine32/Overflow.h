

class Overflow : public ENGINE
{
public:
    Overflow()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"Packs/*.GPK"};
    };
    bool attach_function();
};