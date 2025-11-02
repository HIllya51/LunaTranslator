#include "yuzu.h"
#include "yuzu_1.h"
#include "JIT_Keeper.hpp"

namespace
{
    auto isFastMem = true;

    auto isVirtual = true; // Process.arch === 'x64' && Process.platform === 'windows';
    auto idxDescriptor = isVirtual == true ? 2 : 1;
    auto idxEntrypoint = idxDescriptor + 1;

    uintptr_t getDoJitAddress()
    {
        // Dynarmic::Backend::X64::EmitX64::RegisterBlock
        auto RegisterBlockSig1 = "E8 ?? ?? ?? ?? 4? 8B ?? 4? 8B ?? 4? 8B ?? E8 ?? ?? ?? ?? 4? 89?? 4? 8B???? ???????? 4? 89?? ?? 4? 8B?? 4? 89";
        auto RegisterBlock = find_pattern(RegisterBlockSig1, processStartAddress, processStopAddress);
        if (RegisterBlock)
        {
            auto beginSubSig1 = "CC 40 5? 5? 5?";
            auto lookbackSize = 0x400;
            auto address = RegisterBlock - lookbackSize;
            auto subs = find_pattern(beginSubSig1, address, address + lookbackSize);
            if (subs)
            {
                return subs + 1;
            }
        }

        auto PatchSig1 = "4????? 4????? 4????? FF?? ?? 4????? ?? 4????? 75 ?? 4????? ?? 4????? ?? 4?";
        auto Patch = find_pattern(PatchSig1, processStartAddress, processStopAddress);
        if (Patch)
        {
            auto beginSubSig1 = "4883EC ?? 48";
            auto lookbackSize = 0x80;
            auto address = Patch - lookbackSize;
            auto subs = find_pattern(beginSubSig1, address, address + lookbackSize);
            if (subs)
            {
                idxDescriptor = 1;
                idxEntrypoint = 2;
                return subs;
            }
        }
        return 0;
    }

    std::unordered_map<DWORD, emfuncinfo> emfunctionhooks;

    struct GameInfo
    {
        std::string name{""};
        uint64_t id{0};
        std::string version{""};
    } game_info;
    bool checkiscurrentgame(const emfuncinfo &em)
    {
        if ((game_info.version.size()) && game_info.name.size() && (game_info.id != 0))
        {
            // 判断是有效的info
            auto checkversion = (em._version == 0) || (std::string(em._version) == (game_info.version));
            bool checkid;

            auto visitf = [&](auto &&_ids)
            {
                using T = std::decay_t<decltype(_ids)>;
                if constexpr (std::is_same_v<T, uint64_t>)
                {
                    checkid = _ids == game_info.id;
                }
                else if constexpr (std::is_same_v<T, std::vector<uint64_t>>)
                {
                    checkid = std::any_of(_ids.begin(), _ids.end(), [=](uint64_t _id)
                                          { return _id == game_info.id; });
                }
            };
            std::visit(visitf, em._id);

            return checkid && checkversion;
        }
        else
        {
            // 加载游戏后在hook，没有办法获取id。
            // 标题里没有id，只有version，没啥必要判断了，直接true得了。
            return true;
        }
    }
}
namespace
{
    std::string ull2hex(uint64_t u)
    {
        std::stringstream num;
        num << std::uppercase
            << std::hex
            << std::setw(16)
            << std::setfill('0')
            << u;
        return num.str();
    }
}
namespace
{
    bool LOG_INFO()
    {
        // 其中，部分版本的target是放在string_view里的，部分版本的target是个裸char*指针。
        static const char target[] = "Booting game: {:016X} | {} | {}";
        auto addr = MemDbg::findBytes(target, sizeof(target), processStartAddress, processStopAddress);
        if (!addr)
            return false;
        addr = MemDbg::find_leaorpush_addr(addr, processStartAddress, processStopAddress);
        if (!addr)
            return false;
        /*
.text:0000000140B117B2 48 8D 05 67 EB 51 00                          lea     rax, aBootingGame016 ; "Booting game: {:016X} | {} | {}"
.text:0000000140B117B9 48 89 44 24 28                                mov     qword ptr [rsp+420h+var_3F8], rax
.text:0000000140B117BE 48 8D 05 DB EA 51 00                          lea     rax, aBootgame  ; "BootGame"
.text:0000000140B117C5 48 89 44 24 20                                mov     [rsp+420h+Reserved], rax
.text:0000000140B117CA 41 B9 5B 08 00 00                             mov     r9d, 85Bh
.text:0000000140B117D0 4D 8B C2                                      mov     r8, r10
.text:0000000140B117D3 B2 02                                         mov     dl, 2
.text:0000000140B117D5 B1 52                                         mov     cl, 52h ; 'R'
.text:0000000140B117D5                               ;   } // starts at 140B11600
.text:0000000140B117D7                               ;   try {
.text:0000000140B117D7 E8 44 55 73 FF                                call    sub_140246D20
        */
        BYTE sig[] = {
            0xb2, XX,
            0xb1, XX,
            0xe8, XX4};
        addr = MemDbg::findBytes(sig, sizeof(sig), addr, addr + 0x100);
        if (!addr)
            return false;
        HookParam hp;
        hp.address = addr + 9 + *(int *)(addr + 5);
        hp.user_value = *(char *)(addr + 1) | ((*(char *)(addr + 3)) << 8);
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            if (((uint8_t)context->argof(2) | ((uint8_t)context->argof(1) << 8)) != hp->user_value)
                return;
            auto loadinfo = (char *)context->argof(5);
            if (strcmp("BootGame", loadinfo))
                return;
            loadinfo = (char *)context->argof(6);
            if (!((strcmp(target, loadinfo) == 0) ||
                  ((!IsBadReadPtr(*(char **)loadinfo, sizeof(target))) &&
                   (strcmp(target, *(char **)loadinfo) == 0))))
                return;
            auto param = (uint64_t *)context->argof(7);
            auto v134 = (uint64_t *)param[1];
            auto title_id = v134[0];
            auto title_name = std::string((char *)v134[2], v134[3]);
            title_name = title_name.substr(0, title_name.size() - sizeof("(64-bit)")); // const auto instruction_set_suffix = is_64bit ? tr("(64-bit)") : tr("(32-bit)");
            auto title_version = std::string((char *)v134[4], v134[5]);
            game_info = GameInfo{title_name, title_id, title_version};
            if (game_info.id)
            {
                HostInfo(HOSTINFO::EmuGameName, "%s %s %s", game_info.name.c_str(), ull2hex(game_info.id).c_str(), game_info.version.c_str());
            }
            jitaddrclear();
        };
        return NewHook(hp, "LOG_INFO");
    }
}
namespace
{
    void NS_CheckEmAddrHOOKable(uint64_t em_address, uintptr_t entrypoint)
    {
        auto found = emfunctionhooks.find(em_address);
        if (found == emfunctionhooks.end())
            return;
        auto op = found->second;
        if (!(checkiscurrentgame(op)))
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
        hpinternal.jittype = JITTYPE::YUZU;

        std::string ids;
        auto visitf = [&](auto &&_ids)
        {
            using T = std::decay_t<decltype(_ids)>;
            if constexpr (std::is_same_v<T, uint64_t>)
            {
                ids = ull2hex(_ids);
            }
            else if constexpr (std::is_same_v<T, std::vector<uint64_t>>)
            {
                if (std::any_of(_ids.begin(), _ids.end(), [=](uint64_t _id)
                                { return _id == game_info.id; }))
                {
                    ids = ull2hex(game_info.id);
                }
                else
                {
                    ids = ull2hex(_ids[0]);
                }
            }
        };
        std::visit(visitf, op._id);

        NewHook(hpinternal, ids.c_str());
    }
}
struct NSGameInfoC
{
    GameInfo info;
    bool load()
    {
        game_info = std::move(info);
        if (game_info.id)
        {
            HostInfo(HOSTINFO::EmuGameName, "%s %s %s", game_info.name.c_str(), ull2hex(game_info.id).c_str(), game_info.version.c_str());
        }
        return true;
    }
    void save()
    {
        info = std::move(game_info);
    }
};
// template <typename T1, typename T2>
// void vectorpairAsmap(const std::array<T1> &, std::unordered_map<T2> &)
// {
// }

bool yuzu::attach_function1()
{
    auto DoJitPtr = getDoJitAddress();
    if (!DoJitPtr)
        return false;
    yuzu_load_functions(emfunctionhooks);
    JIT_Keeper<NSGameInfoC>::CreateStatic(NS_CheckEmAddrHOOKable);
    if (!LOG_INFO())
        return false;
    HookParam hp;
    hp.address = DoJitPtr;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto descriptor = context->argof(idxDescriptor + 1); // r8
        auto entrypoint = context->argof(idxEntrypoint + 1); // r9
        auto em_address = *(uint64_t *)descriptor;
        if (!entrypoint)
            return;
        jitaddraddr(em_address, entrypoint, JITTYPE::YUZU);
        NS_CheckEmAddrHOOKable(em_address, entrypoint);
        delayinsertNewHook(em_address);
    };
    return NewHook(hp, "YuzuDoJit");
}
bool yuzu::attach_function()
{
    if (!attach_function1())
        HostInfo(HOSTINFO::EmuWarning, TR[EMUVERSIONTOOOLD]);
    return true;
}
