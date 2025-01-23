

class DAC : public ENGINE
{
public:
    DAC()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"*.dpk") && Util::SearchResourceString(L"DAC");
        };
    };
    bool attach_function();
};