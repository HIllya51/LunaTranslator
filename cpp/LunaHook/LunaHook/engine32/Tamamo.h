

class Tamamo : public ENGINE
{
public:
    Tamamo()
    {

        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{
            L"data.pck",
            L"image.pck",
            L"script.pck"};
    };
    bool attach_function();
};