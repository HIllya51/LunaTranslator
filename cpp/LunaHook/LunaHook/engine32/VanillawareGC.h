

class VanillawareGC : public ENGINE
{
public:
    VanillawareGC()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Dolphin.exe";
    };
    bool attach_function();
};
