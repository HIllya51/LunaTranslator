

class shyakunage : public ENGINE
{
public:
    shyakunage()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"image.dat";
        is_engine_certain = false;
    };
    bool attach_function();
};
