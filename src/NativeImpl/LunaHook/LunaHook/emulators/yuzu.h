

class yuzu : public ENGINE
{
public:
    bool isedenv0_0_4_rc2_above = false;
    yuzu()
    {
        jittype = JITTYPE::YUZU;
        is_engine_certain = false;
        check_by = CHECK_BY::CUSTOM;
        check_by_target = [&]()
        {
            auto exes = {L"suyu.exe", L"yuzu.exe", L"sudachi.exe", L"citron.exe", L"sumi.exe"};
            auto succ = std::any_of(exes.begin(), exes.end(), [](const wchar_t *e)
                                    { return wcscmp(processName_lower, e) == 0; }) &&
                        (GetModuleHandleW(L"Qt6Core.dll") || GetModuleHandleW(L"Qt5Core.dll"));
            if (succ)
                return true;
            if (wcscmp(processName_lower, L"eden.exe"))
                return false;
            char edensig[] = "Eden is an emulator for the Nintendo Switch";
            // 新版本的Eden静态链接了Qt
            if (!(GetModuleHandleW(L"Qt6Core.dll") || GetModuleHandleW(L"Qt5Core.dll") || MemDbg::findBytes(edensig, sizeof(edensig), processStartAddress, processStopAddress)))
                return false;
            /*
            Eden v0.0.4 rc2 引入了 ：
        size_t aslr_offset = ((::Settings::values.rng_seed_enabled.GetValue()
        ? ::Settings::values.rng_seed.GetValue()
        : std::rand()) * 0x734287f27) & 0xfff000;
            使得地址具有偏移。使用0x734287f27作为sig来区分版本。
            */
            BYTE edennewsig[] = {XX, 0x69, XX, 0x27, 0x7F, 0x28, 0x00,
                                 0x81, XX, 0x00, 0xF0, 0xFF, 0x00};
            isedenv0_0_4_rc2_above = MemDbg::findBytes(edennewsig, sizeof(edennewsig), processStartAddress, processStopAddress);
            return true;
        };
        auto _enginename = wcasta(processName);
        enginename = _enginename.substr(0, _enginename.size() - 4);
    };
    bool attach_function();
    bool attach_function1();
};
