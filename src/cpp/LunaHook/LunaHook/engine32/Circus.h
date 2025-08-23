
class Circus : public ENGINE
{
    bool c1;
    bool old;
    bool c2;

public:
    Circus()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]() -> bool
        {
            c1 = Util::CheckFile(L"AdvData\\DAT\\NAMES.DAT");
            //[041213][CIRCUS]最終試験くじら
            auto _ = {L"Pack/Bg.pak", L"Pack/Bustup.pak", L"Pack/Cg.pak", L"Pack/Movie*.pak", L"Pack/Script.pak", L"Pack/Sound.pak", L"Pack/System.pak", L"Pack/Thumbnail.pak"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            old = checkfile && Util::SearchResourceString(L"Circus");
            c2 = Util::CheckFile(L"AdvData\\GRP\\NAMES.DAT") || Util::CheckFile(L"AdvData\\GRP\\Circus2.CRX");
            return c1 || old || c2;
        };
    };
    bool attach_function();
};