

class ArcSystemWorks : public ENGINE
{
public:
    ArcSystemWorks()
    {
        check_by = CHECK_BY::FILE_ALL;
        check_by_target = check_by_list{L"DATA/text/*.lst", L"DATA/STORY/SCRIPT/*.PAC", L"DATA/STORY/image/*.HIP"};
    };
    bool attach_function();
};