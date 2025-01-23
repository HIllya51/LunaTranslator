

class ShinaRio : public ENGINE
{
public:
    ShinaRio()
    {

        check_by = CHECK_BY::FILE_ANY;
        check_by_target = check_by_list{L"RIO.INI", L"*.war"};
        is_engine_certain = false;
        // DWORD len = wcslen(str);

        // jichi 8/24/2013: Checking for Rio.ini or $procname.ini
        // wcscpy(str+len-4, L"_?.war");
        // if (Util::CheckFile(str)) {
        //  InsertShinaHook();
        //  return true;
        //}
    };
    bool attach_function();
};
