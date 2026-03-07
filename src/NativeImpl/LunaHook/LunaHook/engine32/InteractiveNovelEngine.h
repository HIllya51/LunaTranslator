

class InteractiveNovelEngine : public ENGINE
{
public:
    InteractiveNovelEngine()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return GetModuleHandle(L"mscorwks.dll") && Util::SearchResourceString(L"Interactive Novel Engine");
        };
    };
    bool attach_function();
};