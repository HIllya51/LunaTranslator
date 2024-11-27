

class Moonstone : public ENGINE
{
public:
    Moonstone()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"bgm.pak") && Util::CheckFile(L"data.pak") && Util::CheckFile(L"voice.pak") && Util::SearchResourceString(L"mts");
        };
    };
    bool attach_function();
};