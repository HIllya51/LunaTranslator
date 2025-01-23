

class Cage : public ENGINE
{
public:
    Cage()
    {
        // https://vndb.org/v8381
        // 夢姿 ～ゆめのすがた～
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"script.msb", L"data*.ym"};
    };
    bool attach_function();
};