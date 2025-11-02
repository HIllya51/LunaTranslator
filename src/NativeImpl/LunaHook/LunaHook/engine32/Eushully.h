

class Eushully : public ENGINE
{
public:
    Eushully()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"AGERC.DLL"; // 6/1/2014 jichi: Eushully, AGE.EXE
    };
    bool attach_function();
};
