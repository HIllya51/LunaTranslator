
// https://vndb.org/v2330
// 月ノ光太陽ノ影

class Aromarie : public ENGINE
{
public:
    Aromarie()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"scene.db", L"script.axr", L"se.axr", L"system.db", L"user.db", L"koe.axr", L"cg.axr", L"bgm.axr"};
        is_engine_certain = false;
    };
    bool attach_function();
};