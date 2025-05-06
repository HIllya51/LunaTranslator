

class Ryokucha : public ENGINE
{
public:
    Ryokucha()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*_checksum.exe";
    };
    bool attach_function();
};
class Ryokucha2 : public ENGINE
{
public:
    Ryokucha2()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"sc\\*.scc";
        is_engine_certain = false;
    };
    bool attach_function();
};

class ScenarioPlayer_last : public ENGINE
{
public:
    ScenarioPlayer_last()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"*.iar",
            L"*.sec5"};
    };
    bool attach_function();
};
class Ryokuchaold : public Ryokucha
{
public:
    Ryokuchaold()
    {
        // 巫女さんファイター！涼子ちゃん
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"img\\*.iar",
            L"*.sec5"};
        is_engine_certain = false;
    };
};