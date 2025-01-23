

class ScrPlayer : public ENGINE
{
public:
    ScrPlayer()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"ScrPlayer.exe";
    };
    bool attach_function();
};