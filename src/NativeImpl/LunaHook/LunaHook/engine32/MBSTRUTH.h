

class MBSTRUTH : public ENGINE
{
public:
    MBSTRUTH()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"game.001", L"game.002", L"game.dat"};
    };
    bool attach_function();
};