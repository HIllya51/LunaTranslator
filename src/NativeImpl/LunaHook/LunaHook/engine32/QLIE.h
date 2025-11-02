

class QLIE : public ENGINE
{
public:
    QLIE()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"GameData\\*.pack";
        // jichi 12/25/2013: It may or may not be QLIE.
        // AlterEgo also has GameData/sound.pack but is not QLIE
        is_engine_certain = false;
    };
    bool attach_function();
};