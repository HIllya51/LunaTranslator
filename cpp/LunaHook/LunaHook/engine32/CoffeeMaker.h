

class CoffeeMaker : public ENGINE
{
public:
    CoffeeMaker()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"VIC.EPK", L"MUS.EPK", L"SE.EPK", L"CG.EPK", L"SCR.EPK"};
    };
    bool attach_function();
};