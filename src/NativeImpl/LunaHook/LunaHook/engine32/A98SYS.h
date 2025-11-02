

class A98SYS : public ENGINE
{
public:
    A98SYS()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"A98SYS.PAK"; // STREAM.PAK
    };
    bool attach_function();
};