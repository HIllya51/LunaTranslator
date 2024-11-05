

class Alice : public ENGINE
{
public:
    Alice()
    {

        check_by = CHECK_BY::ALL_TRUE;
    };
    bool attach_function();
};