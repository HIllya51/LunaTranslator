

class Yuris : public ENGINE
{
public:
    Yuris()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            // jichi 8/1/2014: YU-RIS engine, lots of clockup game also has this pattern
            // jichi 8/14/2013: CLOCLUP: "ノーブレスオブリージュ" would crash the game.
            return (Util::CheckFile(L"pac\\*.ypf") || Util::CheckFile(L"*.ypf")) && (!Util::CheckFile(L"noblesse.exe"));
        };
    };
    bool attach_function();

private:
    UINT codepage;
    bool InsertYuris1Hook();
    bool InsertYuris2Hook();
    bool InsertYuris5Hook();
    bool InsertYuris4Hook();
    bool InsertYuris6Hook();
    bool yuris7();
    bool yuris8();
    UINT codepagechecker();
};