

class Azurite : public ENGINE
{
public:
    Azurite()
    {
        is_engine_certain = false;
        check_by = CHECK_BY::FILE_ALL;
        // https://vndb.org/v55
        // イシカとホノリ
        check_by_target = check_by_list{L"Data01", L"Data02", L"Grphic", L"ih_ed", L"ih_op", L"SE", L"Voice", L"PCM/*.mp3"};
    };
    bool attach_function();
};