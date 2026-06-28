#include "rpcs3.h"
#include "rpcs3_1.h"
#include "JIT_Keeper.hpp"

bool RPCS3_UserHook_insert(HookParam hp, LPCSTR name, std::function<bool(HookParam hp, LPCSTR)> fn)
{
    auto table = RPCS3::ppu_ptr(hp.emu_addr);
    if (IsBadReadPtr((void *)table, sizeof(uintptr_t)))
        return false;
    auto funcaddr = *(uintptr_t *)table;
    funcaddr &= 0x0000ffffffffffff;
    if (!funcaddr)
        return false;
    hp.address = funcaddr;
    return fn(hp, name);
}
namespace
{
    uintptr_t find_string_function(const char *str, size_t size)
    {
        auto logstrptr = MemDbg::findBytes(str, size, processStartAddress, processStopAddress);
        if (logstrptr == 0)
            return 0;
        auto addr = MemDbg::find_leaorpush_addr(logstrptr, processStartAddress, processStopAddress);
        if (!addr)
            return 0;
        BYTE start[] = {XX, 0xCC, 0xCC, 0xCC};
        addr = reverseFindBytes(start, sizeof(start), addr - 0x200, addr, 4, true);
        return addr;
    }
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
        return find_string_function(log, sizeof(log));
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
    void dohookemaddr_1(uint32_t em_address, uintptr_t ret)
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
        hpinternal.text_fun = op.text_fun;
        hpinternal.filter_fun = op.filterfun;
        hpinternal.offset = op.offset;
        hpinternal.padding = op.padding;
        hpinternal.jittype = JITTYPE::RPCS3;
        NewHook(hpinternal, getmatched);
    }

    void dohookemaddr(uint32_t em_address, uintptr_t ret)
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
#if 0
            static bool once = true;
            if (once)
            {
                once = false;
                FILE *f;
                fopen_s(&f, "JIT_ADDR_MAP_DUMP.txt", "w");
                std::stringstream cache;
                cache << std::hex;
                for (auto addr = 0x10000; addr < 0x400000; addr += 4)
                {
                    auto table = RPCS3::ppu_ptr(addr);
                    if (IsBadReadPtr((void *)table, sizeof(uintptr_t)))
                        continue;
                    auto funcaddr = *(uintptr_t *)table;
                    funcaddr &= 0x0000ffffffffffff;
                    if (!funcaddr)
                        continue;
                    cache << addr << " => " << funcaddr << "\n";
                }
                fprintf(f, "%s", cache.str().c_str());
                fclose(f);
            }
#endif
            for (auto [addr, info] : emfunctionhooks)
            {
                uintptr_t funcaddr;
                if (info.type & DIRECT_READ)
                {
                    funcaddr = RPCS3::emu_addr(addr);
                }
                else
                {
                    auto table = RPCS3::ppu_ptr(addr);
                    if (IsBadReadPtr((void *)table, sizeof(uintptr_t)))
                        continue;
                    funcaddr = *(uintptr_t *)table;
                    funcaddr &= 0x0000ffffffffffff;
                    if (!funcaddr)
                        continue;
                }
                auto p = std::make_pair(addr, funcaddr);
                if (timeoutbreaks.count(p))
                    continue;
                dohookemaddr(addr, funcaddr);
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
            auto match = re::match(info.title, LR"((.*?)\|(.*?)\|(.*?)\|(.*)\[(.*?)\])");
            if (!match)
                return;
            auto curr = match.value()[5].str() + match.value()[4].str();
            if (game_info.lastcheck == curr)
                return;
            game_info.lastcheck = curr;
            game_info.game = Trim(match.value()[4].str());
            game_info.GameID = wcasta(Trim(match.value()[5].str()));
            return Msg::EmuGameInfo(game_info.GameID.c_str(),
                                    WideStringToString(game_info.game).c_str());
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

/*

namespace vm
{
    static u8* memory_reserve_4GiB(void* _addr, u64 size = 0x100000000, bool is_memory_mapping = false)
    {
        for (u64 addr = reinterpret_cast<u64>(_addr) + 0x100000000; addr < 0x8000'0000'0000; addr += 0x100000000)
        {
            if (auto ptr = utils::memory_reserve(size, reinterpret_cast<void*>(addr), is_memory_mapping))
            {
                return static_cast<u8*>(ptr);
            }
        }

        fmt::throw_exception("Failed to reserve vm memory");
    }

    // Emulated virtual memory
    u8* const g_base_addr = memory_reserve_4GiB(reinterpret_cast<void*>(0x2'0000'0000), 0x2'0000'0000, true);

    // Unprotected virtual memory mirror
    u8* const g_sudo_addr = g_base_addr + 0x1'0000'0000;

    // Auxiliary virtual memory for executable areas
    u8* const g_exec_addr = memory_reserve_4GiB(g_sudo_addr, 0x300000000);
*/
static bool rpcs_g_base_addr()
{
    const char failed[] = "Failed to reserve vm memory";
    auto f_memory_reserve_4GiB = find_string_function(failed, sizeof(failed));
    if (!f_memory_reserve_4GiB)
        return false;
    for (auto addr : findxref_reverse_checkcallop(f_memory_reserve_4GiB, processStartAddress, processStopAddress, 0xe8))
    {
        BYTE ret[] = {0x48, 0x89, 0x05, XX4};
        if (MatchPattern(addr + 5, ret, sizeof(ret)))
        {
            BYTE cc[] = {0x48, XX, 0x00, 0x00, 0x00, 0x00, 0x02, 0x00, 0x00, 0x00};
            auto check1 = reverseFindBytes(cc, sizeof(cc), addr - 0x20, addr);
            BYTE cc2[] = {0x48, XX, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x00, 0x00};
            auto check2 = reverseFindBytes(cc2, sizeof(cc2), addr - 0x20, addr);
            if (check1)
            {
                RPCS3::g_base_addr = (decltype(RPCS3::g_base_addr))*(uintptr_t *)(addr + 5 + *(int *)(addr + 5 + 3) + 7);
            }
            else if (check2)
            {
                RPCS3::g_exec_addr = (decltype(RPCS3::g_exec_addr))*(uintptr_t *)(addr + 5 + *(int *)(addr + 5 + 3) + 7);
            }
        }
    }
    Msg::Log("%p %p", RPCS3::g_base_addr, RPCS3::g_exec_addr);
    return RPCS3::g_base_addr && RPCS3::g_exec_addr;
}
bool attach_function1()
{
    auto DoJitPtr = getDoJitAddress();
    if (!DoJitPtr)
        return false;
    if (!rpcs_g_base_addr())
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
    };
    return NewHook(hp, "rpcs3jit");
}
bool rpcs3::attach_function()
{
    if (!attach_function1())
        Msg::EmuWarning(TR[EMUVERSIONTOOOLD]);
    return true;
}
