

class Sakuradog : public ENGINE
{
public:
    Sakuradog()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"SE.dat", L"GRP.dat", L"SNR.dat", L"VOICE.dat", L"BGM.dat", L"DATA.dat", L"ADV.inf", L"ADV.exe"};
        is_engine_certain = false;
    };
    bool attach_function();
};
