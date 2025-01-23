

class TerraLunar : public ENGINE
{
public:
    TerraLunar()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"data_script.pac";
    };
    bool attach_function();
};
