

class GXP : public ENGINE
{
public:
    GXP()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.gxp";
    };
    bool attach_function();
};