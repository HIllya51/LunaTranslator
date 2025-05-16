

class GuruGuruSMF4 : public ENGINE
{
public:
    GuruGuruSMF4()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []() -> bool
        {
            return GetModuleHandle(L"GuruGuruSMF4.dll");
        };
    };
    bool attach_function();
};