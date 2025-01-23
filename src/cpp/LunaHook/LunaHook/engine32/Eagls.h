

class Eagls : public ENGINE
{
public:
    Eagls()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"EAGLS.dll";
    };
    bool attach_function();
};