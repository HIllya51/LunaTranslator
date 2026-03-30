

class Pensil : public ENGINE
{
public:
    Pensil()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // jichi 2/28/2015: Delay checking Pensil in case something went wrong
            // File pattern observed in [Primula] 大正×対称アリス episode I
            // - PSetup.exe no longer exists
            // - MovieTexture.dll information shows MovieTex dynamic library, copyright Pensil 2013
            // - ta_trial.exe information shows 2XT - Primula Adventure Engine
            return (Util::CheckFileAny({L"PSetup.exe", L"PENCIL.*"}) || Util::SearchResourceString(L"2XT -")) ||
                   Util::CheckFile(L"MovieTexture.dll") ||
                   (Util::SearchResourceString(L"2RM") && Util::SearchResourceString(L"Adventure Engine")) ||
                   Util::CheckFileAll({L"archive.dat", L"bgm.dat", L"se.dat", L"voice.dat",
                                        L"save\\syssave.dat"}); // 鬼孕の学園　スク水少女異種姦凌辱劇
        };
    };
    bool attach_function();
};
