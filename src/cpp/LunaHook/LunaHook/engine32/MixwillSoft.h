
// https://vndb.org/v10193
class MixwillSoft : public ENGINE
{
public:
    MixwillSoft()
    {
        check_by = CHECK_BY::FILE_ALL;
        // 实际进程为r2/r2.exe
        check_by_target = check_by_list{L"r2/r2.exe", L"dat/snd*.arc", L"dat/res*.arc", L"dat/tex*.arc", L"dat/txt*.arc"};
    };
    bool attach_function();
};