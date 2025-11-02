

class Artemis : public ENGINE
{
public:
    Artemis()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.pfs";
    };
    bool attach_function();
};