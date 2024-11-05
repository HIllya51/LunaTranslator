

class AOS : public ENGINE
{
public:
    AOS()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.aos";
    };
    bool attach_function();
};