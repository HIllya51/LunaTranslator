

class Debonosu : public ENGINE
{
public:
    Debonosu()
    {
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // 神楽創世記-久遠-
            // 官方中英版，bmp.pak在语言目录里。
            auto paks = {L"bmp.pak", L"EN\\bmp.pak", L"ZHCN\\bmp.pak", L"ZHTW\\bmp.pak"};
            return (std::any_of(paks.begin(), paks.end(), Util::CheckFile) && Util::CheckFile(L"dsetup.dll")) || (Util::SearchResourceString(L"でぼの巣製作所"));
        };
    };
    bool attach_function();
};