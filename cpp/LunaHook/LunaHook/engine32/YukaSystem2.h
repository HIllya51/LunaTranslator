

class YukaSystem2 : public ENGINE
{
public:
    YukaSystem2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.ykc";
    };
    bool attach_function();
};