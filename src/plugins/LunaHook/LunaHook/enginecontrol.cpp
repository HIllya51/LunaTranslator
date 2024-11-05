
WCHAR *processName,        // cached
    processPath[MAX_PATH]; // cached
WCHAR processName_lower[MAX_PATH];
uintptr_t processStartAddress, processStopAddress;

std::vector<ENGINE *> check_engines();

bool ENGINE::check_function()
{
    switch (check_by)
    {
    case CHECK_BY::ALL_TRUE:
    {
        is_engine_certain = false;
        return true;
    }
    case CHECK_BY::FILE:
    {
        return (Util::CheckFile(std::get<check_by_single>(check_by_target)));
    }
    case CHECK_BY::FILE_ALL:
    {
        auto _list = std::get<check_by_list>(check_by_target);
        return std::all_of(_list.begin(), _list.end(), Util::CheckFile);
    }
    case CHECK_BY::FILE_ANY:
    {
        auto _list = std::get<check_by_list>(check_by_target);
        return std::any_of(_list.begin(), _list.end(), Util::CheckFile);
    }
    case CHECK_BY::RESOURCE_STR:
    {
        return (Util::SearchResourceString(std::get<check_by_single>(check_by_target)));
    }

    case CHECK_BY::CUSTOM:
    {
        return std::get<check_by_custom_function>(check_by_target)();
    }
    default:
        return false;
    }
}
bool safematch(ENGINE *m)
{
    bool matched = false;
    __try
    {
        matched = m->check_function();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(Match_Error, m->getenginename());
        // ConsoleOutput("match ERROR");
    }
    return matched;
}
bool safeattach(ENGINE *m)
{
    bool attached = false;
    __try
    {
        attached = m->attach_function();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(Attach_Error, m->getenginename());
        // ConsoleOutput("attach ERROR");
    }
    return attached;
}
bool checkengine()
{

    auto engines = check_engines();
    std::vector<const char *> infomations = {
        "match failed",
        "attach failed",
        "attach success"};
    int current = 0;
    for (auto m : engines)
    {
        current += 1;

        bool matched = safematch(m);
        bool attached = matched && safeattach(m);

        // ConsoleOutput("Progress %d/%d, checked engine %s, %s",current,total,m->getenginename(),infomations[matched+attached]);
        // ConsoleOutput("Progress %d/%d, %s",current,total,infomations[matched+attached]);
        if (matched == false)
            continue;
        ConsoleOutput(MatchedEngine, m->getenginename());
        if (m->dontstop)
        {
            continue;
        }

        if (m->is_engine_certain)
        {
            ConsoleOutput(ConfirmStop, m->getenginename());
            return attached;
        }

        if (attached)
        {
            ConsoleOutput(Attach_Stop, m->getenginename());
            return true;
        }
    }

    return false;
}
void HIJACK()
{
    static bool once = false;
    if (once)
        return;
    once = true;
    GetModuleFileNameW(nullptr, processPath, MAX_PATH);
    processName = wcsrchr(processPath, L'\\') + 1;

    wcscpy_s(processName_lower, processName);
    _wcslwr_s(processName_lower); // lower case

    std::tie(processStartAddress, processStopAddress) = Util::QueryModuleLimits(GetModuleHandleW(nullptr), 0, 1 + PAGE_NOACCESS);
    spDefault.minAddress = processStartAddress;
    spDefault.maxAddress = processStopAddress;
    ConsoleOutput(ProcessRange, processStartAddress, processStopAddress);

    if (processStartAddress + 0x40000 > processStopAddress)
        ConsoleOutput(WarningDummy);

    bool result = false;
    __try
    {
        result = checkengine();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(HIJACK_ERROR);
    }

    if (result == false)
    {
        PcHooks::hookOtherPcFunctions();
    }
}