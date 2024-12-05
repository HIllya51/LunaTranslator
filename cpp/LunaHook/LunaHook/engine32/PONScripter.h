

class PONScripter : public ENGINE
{
public:
    PONScripter()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"arc.nsa") && (Util::SearchResourceString(L"Proportional ONScripter") || Util::SearchResourceString(L"Ponscripter") || Util::SearchResourceString(L"ponscr.exe"));
        };
    };
    bool attach_function();
};
