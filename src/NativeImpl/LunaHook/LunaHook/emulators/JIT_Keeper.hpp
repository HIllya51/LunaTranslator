
template <typename InfoT>
struct JIT_Keeper
{
    // 存在问题：当移除dll，然后模拟器切换游戏进行clear，然后注入dll，会初始化不正确的映射表。
    // 且如果游戏ID也发生切换，会显示到不正确的ID，且会导致在新游戏内由于ID错误无法加载新JIT的钩子。
    struct Datas
    {
        InfoT game_info;
        std::vector<HookParam> records;
        decltype(JIT_HP_Records) JIT_HP_Records;
        decltype(emuaddr2jitaddr) emuaddr2jitaddr;
        decltype(jitaddr2emuaddr) jitaddr2emuaddr;
    };
    Datas **ptr;
    HANDLE handle;
    // ptr指向保存数据的指针，不析构，保存到进程结束
    // handle不Close，用于在dll Detach&Attach后找到ptr数据所在的地址，不保存实际内容
    JIT_Keeper(std::function<void(uint64_t, uintptr_t)> checkfunction)
    {
        constexpr int sz = sizeof(void *);
        std::wstring name = L"LUNA_JIT_MAP_KEEPER_" + std::to_wstring(GetCurrentProcessId());
        handle = CreateFileMappingW(INVALID_HANDLE_VALUE, &allAccess, PAGE_EXECUTE_READWRITE, 0, sz, name.c_str());
        bool existsbefore = GetLastError() == ERROR_ALREADY_EXISTS;
        ptr = (decltype(ptr))MapViewOfFile(handle, FILE_MAP_ALL_ACCESS | FILE_MAP_EXECUTE, 0, 0, sz);
        if (!existsbefore)
        {
            *ptr = new Datas;
        }
        if (!(*ptr)->game_info.load())
        {
            // 目前仅PSP支持通过窗口标题检查这个。
            // 但当游戏仅重新加载时，ID未切换，但实际上映射表会变化，无法检查这种情况。
            // 所以大部分情况下，判断这个没啥用。但加上这个判断不会使结果变差
            return;
        }
        for (auto &&hp : (*ptr)->JIT_HP_Records)
        {
            if (hp.text_fun || hp.filter_fun) // 指向的函数失效，重新走。
            {
                checkfunction(hp.emu_addr, hp.address);
            }
            else
            {
                NewHook(hp, hp.name); // USERHOOK
            }
        }
        emuaddr2jitaddr = std::move((*ptr)->emuaddr2jitaddr);
        jitaddr2emuaddr = std::move((*ptr)->jitaddr2emuaddr);
    }
    ~JIT_Keeper()
    {
        (*ptr)->game_info.save();
        // 保持地址
        {
            std::lock_guard _(JIT_HP_Records_lock);
            (*ptr)->JIT_HP_Records = std::move(JIT_HP_Records);
        }
        {
            std::lock_guard _(maplock);
            (*ptr)->emuaddr2jitaddr = std::move(emuaddr2jitaddr);
            (*ptr)->jitaddr2emuaddr = std::move(jitaddr2emuaddr);
        }
    }
    static void CreateStatic(std::function<void(uint64_t, uintptr_t)> checkfunction)
    {
        // dll Detach时析构static变量
        static JIT_Keeper<InfoT> _(checkfunction);
    }
};