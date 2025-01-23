

class GameMaker : public ENGINE
{
public:
    GameMaker()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"GMResource.dll";
        is_engine_certain = false;
    };
    bool attach_function();
};