

class TamaokaSoft : public ENGINE
{
public:
    TamaokaSoft()
    {
        // 世界ノ全テノ全テ 通常版
        // https://vndb.org/r21299
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"ac.acv", L"bg.acv", L"char.acv", L"ed.acv", L"info.acv", L"op.acv", L"se.acv", L"snr.acv", L"voice.acv"};
    };
    bool attach_function();
};