

class BunBun : public ENGINE
{
public:
    BunBun()
    {

        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            // 保健室～マジカルピュアレッスン♪～
            // https://vndb.org/v351
            //_se.bin vce.bin str.bin vis.bin tak.bin
            return Util::CheckFile(L"pac/*.bin") && Util::SearchResourceString(L"BunBun");
        };
    };
    bool attach_function();
};