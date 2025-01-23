

class jukujojidai : public ENGINE
{
public:
    jukujojidai()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"adv", L"bg", L"bgm", L"ch", L"ev", L"se", L"system", L"voice"};
    };
    bool attach_function();
};
