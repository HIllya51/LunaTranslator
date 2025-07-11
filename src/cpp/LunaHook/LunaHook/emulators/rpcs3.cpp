#include "rpcs3.h"
#include "rpcs3_1.h"
#include "JIT_Keeper.hpp"
namespace
{
    uintptr_t getDoJitAddress()
    {
        // rpcs3/Emu/Cell/PPUThread.cpp
        /*
        extern void ppu_register_function_at(u32 addr, u32 size, ppu_intrp_func_t ptr = nullptr)
        {
               // Initialize specific function
            if (ptr)
            {
                ppu_ref(addr) = reinterpret_cast<ppu_intrp_func_t>((reinterpret_cast<uptr>(ptr) & 0xffff'ffff'ffffu) | (uptr(ppu_ref(addr)) & ~0xffff'ffff'ffffu));
                return;
            }

            if (!size)
            {
                if (g_cfg.core.ppu_debug)
                {
                    ppu_log.error("ppu_register_function_at(0x%x): empty range", addr);
                }

                return;
            }
        ……
        */
        char log[] = "ppu_register_function_at(0x%x): empty range";
        auto logstrptr = MemDbg::findBytes(log, sizeof(log), processStartAddress, processStopAddress);
        ConsoleOutput("%p", logstrptr);
        if (logstrptr == 0)
            return 0;
        auto addr = MemDbg::find_leaorpush_addr(logstrptr, processStartAddress, processStopAddress);
        ConsoleOutput("%p", addr);
        if (!addr)
            return 0;
        // ff cc cc cc,find不到。。
        BYTE start[] = {XX, 0xCC, 0xCC, 0xCC};
        addr = reverseFindBytes(start, sizeof(start), addr - 0x200, addr, 4, true);
        ConsoleOutput("%p", addr);
        return addr;
    }
    std::unordered_map<DWORD, emfuncinfo> emfunctionhooks;

    struct GameInfo
    {
        std::string GameID;
        std::wstring game;
        std::wstring lastcheck;
    } game_info;

    static std::set<std::pair<uintptr_t, uintptr_t>> timeoutbreaks;

    auto MatchGameId = [](const auto &idsv) -> const char *
    {
        if (const auto *id = std::get_if<const char *>(&idsv))
        {
            if (game_info.GameID == *id)
                return *id;
            return nullptr;
        }
        else if (const auto *ids = std::get_if<std::vector<const char *>>(&idsv))
        {
            if (!game_info.GameID.size())
                return nullptr;
            for (auto &&id : *ids)
            {
                if (game_info.GameID == id)
                {
                    return id;
                }
            }
            return nullptr;
        }
        return nullptr;
    };
    void dohookemaddr_1(uintptr_t em_address, uintptr_t ret)
    {
        auto found = emfunctionhooks.find(em_address);
        if (found == emfunctionhooks.end())
            return;
        auto op = found->second;
        auto getmatched = MatchGameId(op._id);
        if (!getmatched)
            return;
        timeoutbreaks.insert(std::make_pair(em_address, ret));
        HookParam hpinternal;
        hpinternal.address = ret;
        hpinternal.emu_addr = em_address; // 用于生成hcode
        hpinternal.type = USING_STRING | NO_CONTEXT | BREAK_POINT | op.type;
        hpinternal.codepage = 932;
        hpinternal.text_fun = op.hookfunc;
        hpinternal.filter_fun = op.filterfun;
        hpinternal.offset = op.offset;
        hpinternal.padding = op.padding;
        hpinternal.jittype = JITTYPE::RPCS3;
        NewHook(hpinternal, getmatched);
    }

    void dohookemaddr(uintptr_t em_address, uintptr_t ret)
    {
        jitaddraddr(em_address, ret, JITTYPE::RPCS3);
        dohookemaddr_1(em_address, ret);
    }

    bool unsafeinithooks()
    {
        // rpcs0.0.30，不知道为什么ppu_register_function_at不全。不过看代码得到映射表了，直接弄吧。
        // rpcs3/Emu/Cell/PPUThread.cpp
        //  Get pointer to executable cache
        /*
        static inline u8* ppu_ptr(u32 addr)
        {
            return vm::g_exec_addr + u64{addr} * 2;
        }
        */
        HookParam hp;
        hp.type = DIRECT_READ;
        hp.address = 0x500000000;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            for (auto [addr, info] : emfunctionhooks)
            {
                auto table = addr * 2 + 0x500000000;
                if (IsBadReadPtr((void *)table, sizeof(uintptr_t)))
                    continue;
                auto funcaddr = *(uintptr_t *)table;
                funcaddr &= 0x0000ffffffffffff;
                if (!funcaddr)
                    continue;
                auto p = std::make_pair(addr, funcaddr);
                if (timeoutbreaks.count(p))
                    continue;
                dohookemaddr(addr, funcaddr);
                delayinsertNewHook(addr);
            }
        };
        return NewHook(hp, "g_exec_addr");
    }
}

namespace
{
    void initgameid()
    {
        auto wininfos = get_proc_windows();
        for (auto &&info : wininfos)
        {
            auto match = re::match(info.title, LR"((.*?)\|(.*?)\|(.*?)\|(.*) \[(.*?)\])");
            if (!match)
                return;
            auto curr = match.value()[5].str() + match.value()[4].str();
            if (game_info.lastcheck == curr)
                return;
            game_info.lastcheck = curr;
            game_info.game = curr;
            game_info.GameID = wcasta(match.value()[5].str());
            return HostInfo(HOSTINFO::EmuGameName, curr.c_str());
        }
    }
    void trygetgameinwindowtitle()
    {
        initgameid();
        HookParam hp;
        hp.address = 0x4000;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            initgameid();
        };
        hp.type = DIRECT_READ;
        NewHook(hp, "GameInfo");
    }
}

bool attach_function1()
{
    auto DoJitPtr = getDoJitAddress();
    if (!DoJitPtr)
        return false;
    rpcs3_load_functions(emfunctionhooks);
    trygetgameinwindowtitle();
    unsafeinithooks();
    HookParam hp;
    hp.address = DoJitPtr;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto em_address = context->rcx; // *(uint32_t*)*(uintptr_t*)(context->base+emoffset);
        auto entrypoint = context->r8;  //*(uintptr_t*)*(uintptr_t*)(context->base+jitoffset)-0x0008000000000000;
        if (!em_address || !entrypoint)
            return;
        dohookemaddr(em_address, entrypoint);
        delayinsertNewHook(em_address);
    };
    return NewHook(hp, "rpcs3jit");
}

bool rpcs3::attach_function()
{
    if (!attach_function1())
        HostInfo(HOSTINFO::Warning, TR[EMUVERSIONTOOOLD]);
    return true;
}
