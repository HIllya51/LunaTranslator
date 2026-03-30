

class Arcturus : public ENGINE
{
    int type = 0;

public:
    Arcturus()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            if (!Util::CheckFileAll({L"advdata/voice.dat", L"advdata/mes/*.mes", L"advdata/se/*.pcm"}))
                return false;
            if (Util::SearchResourceString(L"Getchu"))
                type = 1;
            else if (Util::SearchResourceString(L"LANTERNROOMS") && Util::SearchResourceString(L"NISE"))
                type = 2;
            return type != 0;
        };
    };
    bool attach_function();
};