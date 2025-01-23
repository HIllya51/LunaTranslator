

class Ohgetsu : public ENGINE
{
public:
    Ohgetsu()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        // check_by_target=check_by_list{L"script.pac",L"se.pac",L"visual.pac",L"voice.pac",L"music.pac",L"mov00001.mpg"};
        // それは舞い散る桜のように FullEffect
        check_by_target = check_by_list{L"script.pac", L"se.pac", L"visual.pac", L"voice*.pac"}; //,L"music.pac",L"mov00001.mpg"};
    };
    bool attach_function();
};