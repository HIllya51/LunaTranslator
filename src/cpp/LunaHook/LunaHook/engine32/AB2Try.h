

class AB2Try : public ENGINE
{
public:
    AB2Try()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Yanesdk.dll";
    };
    bool attach_function();
};