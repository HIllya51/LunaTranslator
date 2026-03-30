

class Moonstone : public ENGINE
{
public:
    Moonstone()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFileAll({L"bgm.pak", L"data.pak", L"voice.pak"}) && Util::SearchResourceString(L"mts");
        };
    };
    bool attach_function();
};