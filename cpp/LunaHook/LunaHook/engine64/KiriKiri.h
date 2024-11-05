

class KiriKiri : public ENGINE
{
public:
    KiriKiri()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::CheckFile(L"*.xp3") || Util::SearchResourceString(L"TVP(KIRIKIRI)");
        };
    };
    bool attach_function();
};
