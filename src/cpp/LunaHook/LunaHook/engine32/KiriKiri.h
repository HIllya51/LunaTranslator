

class KiriKiri : public ENGINE
{
public:
    KiriKiri()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"*.xp3") || Util::SearchResourceString(L"TVP(KIRIKIRI)");
        };
    };
    bool attach_function();
};
