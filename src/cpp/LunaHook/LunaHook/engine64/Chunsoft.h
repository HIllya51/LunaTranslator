

class Chunsoft : public ENGINE
{
public:
    Chunsoft()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"piyolx\\*", L"piyo\\*"};
    };
    bool attach_function();
};