

class ZeroEscape : public ENGINE
{
public:
    ZeroEscape()
    {
        // Zero Escape: The Nonary Games
        // https://store.steampowered.com/app/477740/Zero_Escape_The_Nonary_Games/
        check_by = CHECK_BY::FILE;
        check_by_target = L"ze*_data*.bin";
    };
    bool attach_function();
};