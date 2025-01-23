

class utawarerumono : public ENGINE
{
public:
    utawarerumono()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"Data/*.sdat";
        is_engine_certain = false;
    };
    bool attach_function();
};