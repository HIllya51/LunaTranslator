

class NNNConfig : public ENGINE
{
public:
    NNNConfig()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"nnnConfig2.exe";
        is_engine_certain = false;
    };
    bool attach_function();
};

class gazelle : public NNNConfig
{
public:
    gazelle()
    {
        // https://vndb.org/v6180
        // 海の女神 空の女神
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::CheckFile(L"nnndir/*.txt");
        };
        is_engine_certain = false;
    };
};