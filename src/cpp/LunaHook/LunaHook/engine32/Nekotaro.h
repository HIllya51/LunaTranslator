
class Nekotaro : public ENGINE
{
public:
    Nekotaro()
    {
        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Nekotaro Game System for Win95/98";
    };
    bool attach_function();
};