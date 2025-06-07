#include "PCSX2.h"
#include "PCSX2_1.h"
#include "JIT_Keeper.hpp"
namespace GameList
{
    enum class EntryType
    {
        PS2Disc,
        // ……
    };

    enum class Region
    {
        NTSC_B,
        // ……
    };
    struct Entry
    {
        EntryType type = EntryType::PS2Disc;
        Region region; //= Region::Other;

        std::string path;
        std::string serial;
        std::string title;
        std::string title_sort;
        std::string title_en;
        // ……
    };
}
namespace
{
    std::string current_serial;
    // BASEBLOCKEX* BaseBlocks::New(u32 startpc, uptr fnptr)->void __fastcall BaseBlocks::New(BaseBlocks *this, unsigned int startpc, unsigned __int64 fnptr)
    // static void iopRecRecompile(u32 startpc);
    // static void recRecompile(const u32 startpc);-> void __fastcall recRecompile(VMManager::Internal *startpc)
    // void CBreakPoints::AddBreakPoint(BreakPointCpu cpu, u32 addr, bool temp, bool enabled)-》 void __fastcall CBreakPoints::AddBreakPoint(BreakPointCpu cpu, unsigned int addr, unsigned __int8 a3, bool a4)
    // void MainWindow::startGameListEntry(const GameList::Entry* entry, std::optional<s32> save_slot, std::optional<bool> fast_boot)
    uint64_t BaseBlocksNew, recRecompile, iopRecRecompile;
    uint64_t dynarecCheckBreakpoint, psxDynarecCheckBreakpoint; // 用于防止AddBreakPoint使游戏卡住
    uint64_t startGameListEntry;
    typedef void(__fastcall *tAddBreadPoint)(BreakPointCpu cpu, u32 addr, bool temp, bool enabled);
    tAddBreadPoint AddBreakPoint = nullptr;

    bool find_BaseBlocksNew_and_dynarecCheckBreakpoint()
    {
        constexpr BYTE sig_dynarecCheckBreakpoint[] = {
            0x48, 0x83, 0xec, XX,
            0x8b, 0x35, XX4,
            0x8b, 0x05, XX4,
            0x48, 0x39, 0x05, XX4,
            0x75, 0x0d,
            0x83, 0x3d, XX4, 0x00,
            0x0f, 0x85, XX4,
            0xb9, 0x01, 0x00, 0x00, 0x00,
            0x89, 0xf2};
        constexpr BYTE sig_BaseBlocksNew[] = {
            0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54, 0x56, 0x57, 0x55, 0x53,
            0x48, 0x83, 0xEC, 0x28,
            XX, 0x89, XX,
            0x89, 0xd3,
            XX, 0x89, XX,
            0x48, 0x8b, XX,
            0x48, 0x8d, XX, 0x08,
            XX, 0x8b, XX, 0x08};

        dynarecCheckBreakpoint = MemDbg::findBytes(sig_dynarecCheckBreakpoint, sizeof(sig_dynarecCheckBreakpoint), processStartAddress, processStopAddress);
        if (!dynarecCheckBreakpoint)
            return false;
        dynarecCheckBreakpoint = MemDbg::findEnclosingAlignedFunction((uintptr_t)dynarecCheckBreakpoint);
        if (!dynarecCheckBreakpoint)
            return false;

        BaseBlocksNew = MemDbg::findBytes(sig_BaseBlocksNew, sizeof(sig_BaseBlocksNew), processStartAddress, processStopAddress);
        if (!BaseBlocksNew)
            return false;
        return true;
    }
    bool findstartGameListEntry()
    {
        char fmtstr[] = "This save state does not exist.";
        auto fmtstrptr = MemDbg::findBytes(fmtstr, sizeof(fmtstr), processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        fmtstrptr = MemDbg::find_leaorpush_addr(fmtstrptr, processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        BYTE sig2[] = {0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54};
        startGameListEntry = reverseFindBytes(sig2, sizeof(sig2), fmtstrptr - 0x200, fmtstrptr, 0, true);
        if (!startGameListEntry)
        {
            BYTE sig3[] = {0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x54}; // v1.7.4473
            startGameListEntry = reverseFindBytes(sig3, sizeof(sig3), fmtstrptr - 0x200, fmtstrptr, 0, true);
        }
        return startGameListEntry;
    }
    bool findrecRecompile()
    {
        char fmtstr[] = "recRecompile: Could not enable launch arguments for fast boot mode; unidentified BIOS version! Please report this to the PCSX2 developers.";
        auto fmtstrptr = MemDbg::findBytes(fmtstr, sizeof(fmtstr), processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        fmtstrptr = MemDbg::find_leaorpush_addr(fmtstrptr, processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        BYTE sig2[] = {0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54};
        recRecompile = (decltype(recRecompile))reverseFindBytes(sig2, sizeof(sig2), fmtstrptr - 0x1000, fmtstrptr, 0, true);
        if (!recRecompile)
        {
            BYTE sig3[] = {0x55, 0x41, 0x57, 0x41, 0x56, 0x41, 0x55, 0x41, 0x54}; // v1.7.4473
            recRecompile = reverseFindBytes(sig3, sizeof(sig3), fmtstrptr - 0x300, fmtstrptr, 0, true);
        }
        if (!recRecompile)
        {
            // 2.3.407
            recRecompile = (decltype(recRecompile))reverseFindBytes(sig2, sizeof(sig2), fmtstrptr - 0x2200, fmtstrptr, 0, true);
        }
        return recRecompile;
    }
    bool findAddBreakPoint()
    {
        constexpr BYTE sig_AddBreakPoint_1[] = {
            0x89, 0xd0,
            0x25, 0x00, 0x00, 0x00, 0x60,
            0x3d, 0x00, 0x00, 0x00, 0x20,
            0xb8, 0xff, 0xff, 0xff, 0x0f,
            0xb9, 0xff, 0xff, 0xff, 0x7f};
        constexpr BYTE sig_AddBreakPoint_2[] = {
            0x89, 0xc8,
            0x25, 0x00, 0x00, 0x00, 0x60,
            0x3d, 0x00, 0x00, 0x00, 0x20,
            0xb8, 0xff, 0xff, 0xff, 0x0f,
            0x41, 0xbb, 0xff, 0xff, 0xff, 0x7f};
        AddBreakPoint = (decltype(AddBreakPoint))MemDbg::findBytes(sig_AddBreakPoint_1, sizeof(sig_AddBreakPoint_1), processStartAddress, processStopAddress);
        if (!AddBreakPoint)
        {
            AddBreakPoint = (decltype(AddBreakPoint))MemDbg::findBytes(sig_AddBreakPoint_2, sizeof(sig_AddBreakPoint_2), processStartAddress, processStopAddress);
        }
        if (!AddBreakPoint)
            return false;
        BYTE sig2[] = {0x41, 0x57, 0x41, 0x56, 0x41, 0x54};
        AddBreakPoint = (decltype(AddBreakPoint))reverseFindBytes(sig2, sizeof(sig2), (uintptr_t)AddBreakPoint - 0x600, (uintptr_t)AddBreakPoint, 0, true);
        if (!AddBreakPoint)
            return false;
        return true;
    }
    bool find_cpuRegistersPack()
    {
        BYTE sig_OpCodeImpl_CACHE_1[] = {
            0x48, 0x83, 0xec, XX,
            0x8b, 0x05, XX4,
            0x89, 0xc2,
            0xc1, 0xea, 0x10,
            0x83, 0xe2, 0x1f,
            0x8d, 0x4a, 0xf9,
            0x83, 0xf9, 0x15,
            0x0f, 0x87, XX4};
        BYTE sig_OpCodeImpl_CACHE_2[] = {
            0x48, 0x83, 0xec, XX, // v1.7.4977
            0x8b, XX, XX4,
            0x41, 0x89, XX,
            0x41, 0xc1, 0xe8, 0x10,
            0x41, 0x83, 0xe0, 0x1f,
            0x41, 0x8d, 0x48, 0xf9,
            0x83, 0xf9, 0x15,
            0x0f, 0x87, XX4};
        auto OpCodeImpl_CACHE = MemDbg::findBytes(sig_OpCodeImpl_CACHE_1, sizeof(sig_OpCodeImpl_CACHE_1), processStartAddress, processStopAddress);
        if (!OpCodeImpl_CACHE)
        {
            OpCodeImpl_CACHE = MemDbg::findBytes(sig_OpCodeImpl_CACHE_2, sizeof(sig_OpCodeImpl_CACHE_2), processStartAddress, processStopAddress);
        }
        if (!OpCodeImpl_CACHE)
            return false;
        _cpuRegistersPack = (decltype(_cpuRegistersPack))(OpCodeImpl_CACHE + 4 + 6 + *(int *)(OpCodeImpl_CACHE + 4 + 2) - 0x2ac);
        return true;
    }
    bool hookFunctions()
    {
        if (!(findstartGameListEntry() &&
              find_BaseBlocksNew_and_dynarecCheckBreakpoint() &&
              findrecRecompile() &&
              findAddBreakPoint() &&
              find_cpuRegistersPack()))
            return false;

        auto EEmem = GetProcAddress(GetModuleHandle(NULL), "EEmem");
        if (!EEmem)
            return false;
        eeMem = *(decltype(eeMem) *)EEmem;
        return true;
    }
    void SafeAddBreakPoint(u32 addr, bool enable = true)
    {
        __try
        {
            AddBreakPoint(BREAKPOINT_EE, addr, false, enable);
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
        }
    }
    std::unordered_map<DWORD, emfuncinfo> emfunctionhooks;

    auto MatchGameId = [](const auto &idsv) -> const char *
    {
        if (const auto *id = std::get_if<const char *>(&idsv))
        {
            if (current_serial == *id)
                return *id;
            return nullptr;
        }
        else if (const auto *ids = std::get_if<std::vector<const char *>>(&idsv))
        {
            if (!current_serial.size())
                return nullptr;
            for (auto &&id : *ids)
            {
                if (current_serial == id)
                {
                    return id;
                }
            }
            return nullptr;
        }
        return nullptr;
    };
    void CheckForHook(uint64_t em_address, uintptr_t entrypoint)
    {
        auto found = emfunctionhooks.find(em_address);
        if (found == emfunctionhooks.end())
            return;
        auto op = found->second;
        auto useid = MatchGameId(op._id);
        if (!useid)
            return;
        HookParam hpinternal;
        hpinternal.address = entrypoint;
        hpinternal.emu_addr = em_address; // 用于生成hcode
        hpinternal.type = NO_CONTEXT | BREAK_POINT | op.type;
        if (!(op.type & USING_CHAR))
            hpinternal.type |= USING_STRING;
        hpinternal.codepage = 932;
        hpinternal.text_fun = op.hookfunc;
        hpinternal.filter_fun = op.filterfun;
        hpinternal.offset = op.offset;
        hpinternal.padding = op.padding;
        hpinternal.jittype = JITTYPE::PCSX2;
        NewHook(hpinternal, useid);
    }
    std::set<uint32_t> recRecompileReady;
}
bool PCSX2_UserHook_delayinsert(uint32_t addr)
{
    if (!recRecompileReady.count(addr))
    {
        SafeAddBreakPoint(addr);
        return true;
    }
    return false;
}
bool PCSX2::attach_function1()
{
    auto minver = std::make_tuple(1u, 7u, 4473u, 0u);
    auto version = queryversion();
    if (version && version < minver)
        return false;
    if (!hookFunctions())
        return false;
    pcsx2_load_functions(emfunctionhooks);
    bool succ = true;
    {
        HookParam hp;
        hp.address = BaseBlocksNew;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            unsigned int startpc = context->argof(2);
            uint64_t fnptr = context->argof(3);
            jitaddraddr(startpc, fnptr, JITTYPE::PCSX2);
        };
        succ = succ && NewHook(hp, "BaseBlocks::New");
    }
    {
        HookParam hp;
        hp.address = startGameListEntry;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            const GameList::Entry *entry = (GameList::Entry *)context->rdx;
            current_serial = entry->serial;
            jitaddrclear();
            HostInfo(HOSTINFO::EmuGameName, "%s %s", entry->serial.c_str(), entry->title.c_str());
            for (auto &&[addr, op] : emfunctionhooks)
            {
                if (!(op.type & DIRECT_READ))
                    continue;
                auto useid = MatchGameId(op._id);
                if (!useid)
                    continue;
                HookParam hpinternal;
                hpinternal.address = emu_addr(addr);
                hpinternal.emu_addr = addr;
                hpinternal.jittype = JITTYPE::PCSX2;
                hpinternal.type = op.type;
                hpinternal.codepage = 932;
                hpinternal.text_fun = op.hookfunc;
                hpinternal.filter_fun = op.filterfun;
                hpinternal.offset = op.offset;
                hpinternal.padding = op.padding;
                NewHook(hpinternal, useid);
            }
        };
        succ = succ && NewHook(hp, "startGameListEntry");
    }
    auto hookrecompile = [&](auto addr, auto name)
    {
        HookParam hp;
        hp.address = addr;
        hp.user_value = (uintptr_t)new uintptr_t;
        hp.text_fun = [](hook_context *context, HookParam *hp, auto *, auto *)
        {
            unsigned int startpc = context->argof(1);
            *(uintptr_t *)(hp->user_value) = startpc;

            if (*(BYTE *)(context->retaddr) != 0xe9) // 会被谜之取消
            {
                HookParam hpinternal;
                hpinternal.user_value = hp->user_value;
                hpinternal.address = context->retaddr;
                hpinternal.text_fun = [](hook_context *context, HookParam *hp, auto *, auto *)
                {
                    unsigned int startpc = *(uintptr_t *)(hp->user_value);
                    std::lock_guard _(maplock);
                    auto found = emuaddr2jitaddr.find(startpc);
                    if (found == emuaddr2jitaddr.end())
                        return;
                    recRecompileReady.insert(startpc);
                    auto fnptr = found->second.second;
                    CheckForHook(startpc, fnptr);
                    delayinsertNewHook(startpc);
                };
                NewHook(hpinternal, "Ret");
            }
        };
        succ = succ && NewHook(hp, name);
    };
    if (!succ)
        return false;
    dont_detach = true; // 不可以detach，detach后会导致游戏卡住，可能是dynarecCheckBreakpoint被恢复的原因。
    hookrecompile(recRecompile, "recRecompile");
    // hookrecompile(iopRecRecompile, "iopRecRecompile");
    patch_fun_ptrs = {
        {(void *)dynarecCheckBreakpoint, +[]() {}},
        //{(void *)psxDynarecCheckBreakpoint, +[]() {}},
    };
    patch_fun_ptrs_patch_once();
    for (auto &&[addr, op] : emfunctionhooks)
    {
        if (!(op.type & DIRECT_READ))
            SafeAddBreakPoint(addr);
    }
    return true;
}

bool PCSX2::attach_function()
{
    if (!attach_function1())
        HostInfo(HOSTINFO::Warning, TR[EMUVERSIONTOOOLD]);
    return true;
}
