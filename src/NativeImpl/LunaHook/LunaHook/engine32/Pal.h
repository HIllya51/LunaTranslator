

class Pal : public ENGINE
{
public:
    Pal()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"dll\\Pal.dll") || GetModuleHandleW(L"Pal.dll");
        };
    };
    bool attach_function();
};