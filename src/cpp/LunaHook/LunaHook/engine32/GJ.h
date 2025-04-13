

class GJ : public ENGINE
{
public:
    GJ()
    {
        // https://vndb.org/v11164
        // 百機夜行
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"back.usi", L"battle.usi", L"bgm.usi", L"intermission.usi", L"scenario.usi", L"status.usi", L"system.usi", L"title.usi"};
    };
    bool attach_function();
};
