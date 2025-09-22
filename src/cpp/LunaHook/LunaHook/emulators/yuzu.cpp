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
    bool Hook_Network_RoomMember_SendGameInfo_at(uintptr_t addr)
    {
        HookParam hp;
        hp.address = addr;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            // void __fastcall Network::RoomMember::SendGameInfo(
            // Network::RoomMember *this,
            // const AnnounceMultiplayerRoom::GameInfo *game_info)
            game_info = *(GameInfo *)context->rdx;
            if (game_info.id)
            {
                HostInfo(HOSTINFO::EmuGameName, "%s %s %s", game_info.name.c_str(), ull2hex(game_info.id).c_str(), game_info.version.c_str());
            }
            jitaddrclear();
        };
        return NewHook(hp, "yuzuGameInfo");
    }
    uintptr_t find_Network_RoomMember_SendGameInfo_1()
    {
        // void RoomMember::SendGameInfo(const GameInfo& game_info) {
        //     room_member_impl->current_game_info = game_info;
        //     if (!IsConnected())
        //         return;

        //     Packet packet;
        //     packet.Write(static_cast<u8>(IdSetGameInfo));
        //     packet.Write(game_info.name);
        //     packet.Write(game_info.id);
        //     packet.Write(game_info.version);
        //     room_member_impl->Send(std::move(packet));
        // }
        BYTE pattern[] = {
            0x49, 0x8B, XX,
            0x0F, 0xB6, 0x81, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x02,
            0x74, 0x1C,
            0x0F, 0xB6, 0x81, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x03,
            0x74, 0x10,
            0x0F, 0xB6, 0x81, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x04,
            0x0F, 0x85, XX4};
        for (auto addr : Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, processStartAddress, processStopAddress))
        {
            // Citron-Windows-Canary-Refresh_0.6.1为0x20，其他为0x28
            if (!(((((BYTE *)addr)[3 + 3] == 0x20) &&
                   (((BYTE *)addr)[3 + 7 + 1 + 2 + 2 + 3] == 0x20) &&
                   (((BYTE *)addr)[3 + 7 + 1 + 2 + 2 + 7 + 1 + 2 + 2 + 3] == 0x20)) ||
                  ((((BYTE *)addr)[3 + 3] == 0x28) &&
                   (((BYTE *)addr)[3 + 7 + 1 + 2 + 2 + 3] == 0x28) &&
                   (((BYTE *)addr)[3 + 7 + 1 + 2 + 2 + 7 + 1 + 2 + 2 + 3] == 0x28))))
                continue;
            addr = MemDbg::findEnclosingAlignedFunction_strict(addr, 0x100);
            // 有两个，但另一个离起始很远
            if (addr)
                return addr;
        }
        BYTE pattern2[] = {
            // Citron v0.7.0
            0xe8, XX4,
            0x4c, 0x8B, 0x06,
            0x41, 0x0F, 0xB6, 0x80, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x02,
            0x74, 0x1e,
            0x41, 0x0F, 0xB6, 0x80, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x03,
            0x74, 0x11,
            0x41, 0x0F, 0xB6, 0x80, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x04,
            0x0F, 0x85, XX4};
        for (auto addr : Util::SearchMemory(pattern2, sizeof(pattern2), PAGE_EXECUTE, processStartAddress, processStopAddress))
        {

            if (!(0 ||
                  ((((BYTE *)addr)[5 + 3 + 4] == 0x28) &&
                   (((BYTE *)addr)[5 + 3 + 8 + 1 + 2 + 2 + 4] == 0x28) &&
                   (((BYTE *)addr)[5 + 3 + 8 + 1 + 2 + 2 + 8 + 1 + 2 + 2 + 4] == 0x28))))
                continue;
            addr = MemDbg::findEnclosingAlignedFunction_strict(addr, 0x100);
            if (addr)
                return addr;
        }
        return 0;
    }
    uintptr_t find_Network_RoomMember_SendGameInfo()
    {
        auto addr = find_Network_RoomMember_SendGameInfo_1();
        if (addr)
            return addr;
        // sumi-gen-signed-0.9.4-win-x64
        BYTE pattern[] = {
            0x48, 0x89, XX, 0x24, 0x08,
            0x48, 0x89, XX, 0x24, 0x10,
            0x48, 0x89, XX, 0x24, 0x18,
            0x57,
            0x48, 0x83, XX, XX,
            0x48, 0x8b, XX,
            0x48, 0x8b, XX,
            0x48, 0x8b, XX,
            0x48, XX, XX, XX4,
            0xe8, XX4,
            0x3e, 0x48, XX, XX, XX,
            0x48, 0x89, XX, XX4,
            0x48, 0x8d, XX, XX4,
            0x48, 0x8d, XX, XX,
            0xe8, XX4,
            0x48, 0x8b, 0x0e,
            0x0f, 0xb6, 0x81, XX4,
            0x90,
            0x3C, 0x02,
            0x74, 0x20,
            XX4,
            0x0F, 0xB6, 0x81, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x03,
            0x74, 0x10,
            0x0F, 0xB6, 0x81, XX, 0x01, 0x00, 0x00,
            0x90,
            0x3C, 0x04,
            0x0F, 0x85, XX4};
        addr = MemDbg::findBytes(pattern, sizeof(pattern), processStartAddress, processStopAddress);
        if (addr)
            return addr;
        return 0;
    }
    bool Hook_Network_RoomMember_SendGameInfo()
    {
        auto addr = find_Network_RoomMember_SendGameInfo_1();
        if (!addr)
            return false;
        return Hook_Network_RoomMember_SendGameInfo_at(addr);
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
    if (!Hook_Network_RoomMember_SendGameInfo())
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
        HostInfo(HOSTINFO::Warning, TR[EMUVERSIONTOOOLD]);
    return true;
}
