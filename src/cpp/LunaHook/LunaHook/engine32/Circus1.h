

class Circus1 : public ENGINE
{
public:
    Circus1()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"AdvData\\DAT\\NAMES.DAT";
    };
    bool attach_function();
};

class Circus_old : public ENGINE
{
public:
    Circus_old()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            //[041213][CIRCUS]最終試験くじら
            auto _ = {L"Pack/Bg.pak", L"Pack/Bustup.pak", L"Pack/Cg.pak", L"Pack/Movie*.pak", L"Pack/Script.pak", L"Pack/Sound.pak", L"Pack/System.pak", L"Pack/Thumbnail.pak"};
            auto checkfile = std::all_of(_.begin(), _.end(), Util::CheckFile);
            return checkfile && Util::SearchResourceString(L"Circus");
        };
    };
    bool attach_function();
};