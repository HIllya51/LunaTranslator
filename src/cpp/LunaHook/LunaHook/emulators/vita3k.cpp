#include "vita3k.h"
#include "vita3k_1.h"
#include "JIT_Keeper.hpp"
namespace
{
    auto isVirtual = true;
    auto idxDescriptor = isVirtual == true ? 2 : 1;
    auto idxEntrypoint = idxDescriptor + 1;
    struct GameInfo
    {
        std::wstring game;
        std::string Vita3KGameID;
        std::wstring lastcheck;
    } game_info;
    uintptr_t getDoJitAddress()
    {
        // Vita3K\external\dynarmic\src\dynarmic\backend\x64\emit_x64.h
        // BlockDescriptor EmitX64::RegisterBlock(const IR::LocationDescriptor& location_descriptor, CodePtr entrypoint, size_t size);
        BYTE RegisterBlockSig1[] = {0x40, 0x55, 0x53, 0x56, 0x57, 0x41, 0x54, 0x41, 0x56, 0x41, 0x57, 0x48, 0x8D, 0x6C, 0x24, 0xE9, 0x48, 0x81, 0xEC, 0x90, 0x00, 0x00, 0x00, 0x48, 0x8B, XX, XX, XX, XX, XX, 0x48, 0x33, 0xC4, 0x48, 0x89, 0x45, 0x07, 0x4D, 0x8B, 0xF1, 0x49, 0x8B, 0xF0, 0x48, 0x8B, 0xFA, 0x48, 0x8B, 0xD9, 0x4C, 0x8B, 0x7D, 0x77, 0x48, 0x8B, 0x01, 0x48, 0x8D, 0x55, 0xC7, 0xFF, 0x50, 0x10};
        auto first = MemDbg::findBytes(RegisterBlockSig1, sizeof(RegisterBlockSig1), processStartAddress, processStopAddress);
        if (first)
            return first;

        BYTE PatchBlockSig1[] = {0x4C, 0x8B, 0xDC, 0x49, 0x89, 0x5B, 0x10, 0x49, 0x89, 0x6B, 0x18, 0x56, 0x57, 0x41, 0x54, 0x41, 0x56, 0x41, 0x57};
        BYTE PatchBlockSig2[] = {0x4C, 0x8B, 0xDC, 0x49, 0x89, 0x5B, XX, 0x49, 0x89, 0x6B, XX, 0x56, 0x57, 0x41, 0x54, 0x41, 0x56, 0x41, 0x57};
        first = MemDbg::findBytes(PatchBlockSig1, sizeof(PatchBlockSig1), processStartAddress, processStopAddress);
        if (!first)
            first = MemDbg::findBytes(PatchBlockSig2, sizeof(PatchBlockSig2), processStartAddress, processStopAddress); // 0.1.9 3339
        if (first)
        {
            idxDescriptor = 1;
            idxEntrypoint = 2;
            return first;
        }
        return 0;
    }
    std::unordered_map<DWORD, emfuncinfo> emfunctionhooks;
}

namespace
{
    void trygetgameinwindowtitle()
    {
        HookParam hp;
        hp.address = 0x3000;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            // vita3k Vulkan模式GetWindowText会卡住
            auto getSecondSubstring = [](const std::wstring &str) -> std::wstring
            {
                size_t firstPos = str.find(L'|');
                if (firstPos == std::wstring::npos)
                    return L"";
                size_t nextPos = str.find(L'|', firstPos + 1);
                if (nextPos == std::wstring::npos)
                    return L"";
                size_t start = firstPos + 1;
                size_t end = nextPos;
                return str.substr(start, end - start);
            };
            auto wininfos = get_proc_windows();
            for (auto &&info : wininfos)
            {
                auto game = getSecondSubstring(info.title);
                if (!game.size())
                    continue;
                auto match = re::search(game, L"\\((.*?)\\)");
                if (!match)
                    return;
                auto curr = match.value()[1].str();
                if (game_info.lastcheck == curr)
                    return;
                game_info.Vita3KGameID = wcasta(curr);
                game_info.lastcheck = curr;
                game_info.game = game;
                return HostInfo(HOSTINFO::EmuGameName, game_info.game.c_str());
            }
        };
        hp.type = DIRECT_READ;
        NewHook(hp, "Vita3KGameInfo");
    }
    auto MatchGameId = [](const auto &idsv) -> const char *
    {
        if (const auto *id = std::get_if<const char *>(&idsv))
        {
            if (game_info.Vita3KGameID == *id)
                return *id;
            return nullptr;
        }
        else if (const auto *ids = std::get_if<std::vector<const char *>>(&idsv))
        {
            if (!game_info.Vita3KGameID.size())
                return nullptr;
            for (auto &&id : *ids)
            {
                if (game_info.Vita3KGameID == id)
                {
                    return id;
                }
            }
            return nullptr;
        }
        return nullptr;
    };
    void CheckEmAddrHOOKable(uint64_t em_address, uintptr_t entrypoint)
    {
        auto found = emfunctionhooks.find(em_address);
        if (found == emfunctionhooks.end())
            return;
        auto op = found->second;
        auto getmatched = MatchGameId(op._id);
        if (!getmatched)
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
        hpinternal.jittype = JITTYPE::VITA3K;
        NewHook(hpinternal, getmatched);
    }
    struct IDremember
    {
        GameInfo info;
        bool load()
        {
            if (info.Vita3KGameID.size())
            {
                game_info = std::move(info);
                HostInfo(HOSTINFO::EmuGameName, game_info.game.c_str());
            }
            return true;
        }
        void save()
        {
            info = std::move(game_info);
        }
    };
}

bool vita3k::attach_function1()
{
    auto minver = std::make_tuple(0u, 1u, 9u, 3339u);
    auto version = queryversion();
    if (version && version < minver)
        return false;
    auto DoJitPtr = getDoJitAddress();
    if (!DoJitPtr)
        return false;
    vita3k_load_functions(emfunctionhooks);
    JIT_Keeper<IDremember>::CreateStatic(CheckEmAddrHOOKable);
    trygetgameinwindowtitle();
    HookParam hp;
    hp.address = DoJitPtr;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto descriptor = context->argof(idxDescriptor + 1); // r8
        auto entrypoint = context->argof(idxEntrypoint + 1); // r9
        auto em_address = *(uint32_t *)descriptor;
        if (em_address < 0x80000000)
            em_address += 0x80000000; // 0.1.9 3339
        if (!entrypoint)
            return;
        // ConsoleOutput("%p",em_address);
        CheckEmAddrHOOKable(em_address, entrypoint);
        jitaddraddr(em_address, entrypoint, JITTYPE::VITA3K);

        delayinsertNewHook(em_address);
    };
    return NewHook(hp, "vita3kjit");
}
bool vita3k::attach_function()
{
    if (!attach_function1())
        HostInfo(HOSTINFO::Warning, TR[EMUVERSIONTOOOLD]);
    return true;
}
