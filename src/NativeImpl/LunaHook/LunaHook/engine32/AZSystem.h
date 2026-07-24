

class AZSystem : public ENGINE
{
public:
    AZSystem()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"voice.arc", L"music.arc", L"script.arc", L"sound.arc", L"sysgraph.arc", L"system.arc", L"graphic.arc"};
        is_engine_certain = false;
    };
    bool attach_function();
};
