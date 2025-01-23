

class GuruGuruSMF4 : public ENGINE
{
public:
    GuruGuruSMF4()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (bool)GetModuleHandle(L"GuruGuruSMF4.dll");
        };
    };
    bool attach_function();
};