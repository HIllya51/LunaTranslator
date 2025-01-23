

class Circus2 : public ENGINE
{
public:
    Circus2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"AdvData\\GRP\\NAMES.DAT";
    };
    bool attach_function();
};