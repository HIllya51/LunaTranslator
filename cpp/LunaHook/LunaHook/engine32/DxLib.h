

class DxLib : public ENGINE
{
public:
    DxLib()
    {

        check_by = CHECK_BY::FILE;
        check_by_target = L"*.bcx";
        is_engine_certain = false;
    };
    bool attach_function();
};