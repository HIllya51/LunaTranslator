

class TinkerBell : public ENGINE
{
public:
    TinkerBell()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            wchar_t arcdatpattern[] = L"Arc0%d.dat";
            wchar_t arcdat[20];
            bool iswendybell = false;
            for (int i = 0; i < 10; i++)
            {
                wsprintf(arcdat, arcdatpattern, i);
                if (Util::CheckFile(arcdat))
                {
                    iswendybell = true;
                    break;
                }
            }
            return (wcsstr(processName_lower, L"c,system")) || iswendybell || Util::SearchResourceString(L"TinkerBell");
        };
    };
    bool attach_function();
};

class TinkerBellold : public ENGINE
{
public:
    TinkerBellold()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            wchar_t arcdatpattern[] = L"arc%c.dat";
            wchar_t arcdat[20];
            bool iswendybell = false;
            for (int i = 'a'; i <= 'z'; i++)
            {
                wsprintf(arcdat, arcdatpattern, i);
                if (Util::CheckFile(arcdat))
                {
                    iswendybell = true;
                    break;
                }
            }
            return iswendybell && Util::CheckFile(L"head.dat");
        };
    };
    bool attach_function();
};