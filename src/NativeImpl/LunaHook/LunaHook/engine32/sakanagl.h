

class sakanagl : public ENGINE
{
    HMODULE hmodule;

public:
    sakanagl()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = [&]() -> bool
        {
            return hmodule = GetModuleHandleW(L"sakanagl.dll");
        };
    };
    bool attach_function();
};
