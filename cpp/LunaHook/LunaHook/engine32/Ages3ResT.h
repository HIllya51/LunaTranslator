

class Ages3ResT : public ENGINE
{
public:
    Ages3ResT()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Ages3ResT.dll";
    };
    bool attach_function();
};