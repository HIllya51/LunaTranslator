

class H_do_C : public ENGINE
{
public:
    H_do_C()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        { return Util::CheckFile(L"*.pak") && Util::SearchResourceString(L"(C) Ｈ℃"); };
    };
    bool attach_function();
};