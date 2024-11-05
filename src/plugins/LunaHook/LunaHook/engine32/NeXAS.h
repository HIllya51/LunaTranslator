

class NeXAS : public ENGINE
{
public:
    NeXAS()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"NeXAS") || (Util::CheckFile(L"*.pac") && (Util::CheckFile(L"Thumbnail.pac") || Util::CheckFile(L"Thumbnail5.pac")));
        };
    };
    bool attach_function();
};
