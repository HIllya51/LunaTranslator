

class AIL : public ENGINE
{
public:
    AIL()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"*.wa", L"Gall*.da", L"Pall*.da", L"vall*.da", L"sall.sn", L"help/*.ht"}) ||
                   Util::CheckFile(L"Gall*.dat");
        };
    };
    bool attach_function();
};