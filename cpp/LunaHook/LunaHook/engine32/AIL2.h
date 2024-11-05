

class AIL2 : public ENGINE
{
public:
    AIL2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Gall*.dat";
    };
    bool attach_function();
};