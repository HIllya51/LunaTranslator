

class AZScript : public ENGINE
{
public:
    AZScript()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"scenario.axr") && Util::CheckFile(L"bgm.axr") && Util::CheckFile(L"cg.axr") && Util::CheckFile(L"movie.axr") && Util::CheckFile(L"voice.axr") && Util::CheckFile(L"se.axr") && Util::SearchResourceString(L"AZScript/VNEngine");
        };
        is_engine_certain = false;
    };
    bool attach_function();
};
