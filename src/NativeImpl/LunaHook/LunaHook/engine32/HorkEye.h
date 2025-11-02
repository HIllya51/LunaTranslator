

class HorkEye : public ENGINE
{
public:
    HorkEye()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"HorkEye";
    };
    bool attach_function();
};