
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
bool safematch(ENGINE *m, const char *enginename)
{
    bool matched = false;
    __try
    {
        matched = m->check_function();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(TR[Match_Error], enginename);
        // ConsoleOutput("match ERROR");
    }
    return matched;
}
bool safeattach(ENGINE *m, const char *enginename)
{
    bool attached = false;
    __try
    {
        attached = m->attach_function();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(TR[Attach_Error], enginename);
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
        auto enginename = m->getenginename();
        bool matched = safematch(m, enginename.c_str());

        // ConsoleOutput("Progress %d/%d, checked engine %s, %s",current,engines.size(),m->getenginename(),infomations[matched+attached]);
        // ConsoleOutput("Progress %d/%d, %s",current,engines.size(),infomations[matched+attached]);
        if (!matched)
            continue;
        ConsoleOutput(TR[MatchedEngine], enginename.c_str());
        bool attached = safeattach(m, enginename.c_str());
        if (attached)
        {
            jittypedefault = m->jittype;
            if (jittypedefault != JITTYPE::PC)
            {
                spDefault.isjithook = true;
                spDefault.minAddress = 0;
                spDefault.maxAddress = -1;
                if (jittypedefault != JITTYPE::UNITY)
                    HostInfo(HOSTINFO::EmuConnected, TR[IsEmuNotify], enginename.c_str());
            }
        }
        if (m->is_engine_certain)
        {
            ConsoleOutput(TR[ConfirmStop], enginename.c_str());
            return attached;
        }

        if (attached)
        {
            ConsoleOutput(TR[Attach_Stop], enginename.c_str());
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
    ConsoleOutput(TR[ProcessRange], processStartAddress, processStopAddress);

    if (processStartAddress + 0x40000 > processStopAddress)
        ConsoleOutput(TR[WarningDummy]);

    bool result = false;
    __try
    {
        result = checkengine();
    }
    __except (EXCEPTION_EXECUTE_HANDLER)
    {
        ConsoleOutput(TR[HIJACK_ERROR]);
    }

    if (!result)
    {
        PcHooks::hookGdiGdiplusD3dxFunctions();
        PcHooks::hookOtherPcFunctions();
    }
}