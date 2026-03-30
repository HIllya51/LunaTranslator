

class NeXAS : public ENGINE
{
public:
    NeXAS()
    {

        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = []()
        {
            return Util::SearchResourceString(L"NeXAS") ||
                   (Util::CheckFile(L"*.pac") && Util::CheckFileAny({L"Thumbnail.pac", L"Thumbnail5.pac"}));
        };
    };
    bool attach_function();
};
