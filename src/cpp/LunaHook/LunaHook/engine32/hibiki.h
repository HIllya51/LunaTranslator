

class hibiki : public ENGINE
{
public:
    hibiki()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"arc/*.dat";
        is_engine_certain = false;
    };
    bool attach_function();
};