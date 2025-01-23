

class Tenco : public ENGINE
{
public:
    Tenco()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"Check.mdx") || Util::SearchResourceString(L"TENCO / MONOCHROMA Inc.");
        };
    };
    bool attach_function();
};