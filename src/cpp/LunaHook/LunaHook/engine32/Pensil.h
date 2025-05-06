

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
            return (Util::CheckFile(L"PSetup.exe") ||
                    Util::CheckFile(L"PENCIL.*") ||
                    Util::SearchResourceString(L"2XT -")) ||
                   Util::CheckFile(L"MovieTexture.dll") ||
                   ((Util::SearchResourceString(L"2RM") && Util::SearchResourceString(L"Adventure Engine"))) ||
                   (Util::CheckFile(L"archive.dat") && Util::CheckFile(L"bgm.dat") && Util::CheckFile(L"se.dat") && Util::CheckFile(L"voice.dat") && Util::CheckFile(L"save\\syssave.dat")); // 鬼孕の学園　スク水少女異種姦凌辱劇
        };
    };
    bool attach_function();
};
