

class cef : public ENGINE
{
public:
    cef()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return GetModuleHandleW(L"libcef.dll");
        };
    };
    bool attach_function();
};
