

class Retouch : public ENGINE
{
    HMODULE hm;

public:
    Retouch()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            hm = GetModuleHandle(L"resident.dll");
            return hm;
        };
    };
    bool attach_function();
};