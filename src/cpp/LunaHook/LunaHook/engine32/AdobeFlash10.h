

class AdobeFlash10 : public ENGINE
{
public:
    AdobeFlash10()
    {

        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"Adobe Flash Player 10";
    };
    bool attach_function();
};