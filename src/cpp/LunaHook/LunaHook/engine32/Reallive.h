

class Reallive : public ENGINE
{
public:
    Reallive()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return (wcsstr(processName_lower, L"reallive") || Util::CheckFile(L"Reallive.exe") || Util::CheckFile(L"REALLIVEDATA\\Start.ini"));
        };
    };
    bool attach_function();
};

class Reallive_old : public Reallive
{
public:
    Reallive_old()
    {
        // DEVOTE2 いけない放課後
        check_by = CHECK_BY::FILE_ALL;
        //,L"sys\\*",L"PDT\\*",L"Gameexe.ini"是独有的，其他siglus也有
        check_by_target = check_by_list{L"G00\\*.g00", L"bgm\\*.nwa", L"koe\\*", L"wav\\*", L"sys\\*", L"PDT\\*", L"Gameexe.ini"};
    };
};

class avg3216d : public ENGINE
{
public:
    avg3216d()
    {
        //[980731][13cm] 好き好き大好き!
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"koe\\*.koe", L"PDT\\*.pdt", L"Gameexe.ini"};
    };
    bool attach_function();
};

class RealliveX : public Reallive
{
public:
    RealliveX()
    {
        // 部分远古版本
        check_by = CHECK_BY::RESOURCE_STR;
        check_by_target = L"RealLive";
    };
};