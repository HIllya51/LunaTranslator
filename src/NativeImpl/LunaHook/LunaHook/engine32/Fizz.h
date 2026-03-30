

class Fizz : public ENGINE
{
public:
    Fizz()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            if (!Util::CheckFileAll({L"data.gsp", L"Image*.gsp", L"bgm*.gsp", L"se.gsp"}))
                return false;
            if (Util::CheckFile(L"voice/*.gsp"))
            {
                typex = 1;
            }
            else
            {
                typex = 2;
            }
            return true;
        };
    };
    bool attach_function();
    int typex = 0;
};