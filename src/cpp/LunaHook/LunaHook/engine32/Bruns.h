

class Bruns : public ENGINE
{
public:
    Bruns()
    {

        check_by = CHECK_BY::CUSTOM;
        is_engine_certain = false;
        check_by_target = []()
        {
            return Util::CheckFile(L"args.txt") || (wcsstr(processName_lower, L"bruns") || Util::CheckFile(L"bruns.exe"));
        };
        // check_by=CHECK_BY::FILE;
        // check_by_target=L"args.txt";
        // if (Util::CheckFile(L"libscr.dll")) { // already checked
        //  InsertBrunsHook();
        //  return true;
        //}

        // jichi 10/12/2013: Sample args.txt:
        // See: http://tieba.baidu.com/p/2631413816
        // -workdir
        // .
        // -loadpath
        // .
        // am.cfg
    };
    bool attach_function();
};