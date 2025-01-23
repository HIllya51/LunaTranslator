

class Exp : public ENGINE
{
public:
    Exp()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"model\\*.hed";
    };
    bool attach_function();
};