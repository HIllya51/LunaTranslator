#include "PCSX2.h"
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
    using namespace PCSX2Types;
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
        0x4c, 0x89, 0xc7,
        0x89, 0xd3,
        0x48, 0x89, 0xce,
        0x48, 0x8b, 0x01,
        0x48, 0x8d, 0x50, 0x08,
        0x4c, 0x8b, 0x40, 0x08,
        0x41, 0x80, 0x78, 0x19, 0x00};
    constexpr BYTE sig_recRecompile[] = {
        0x89, 0xcd,
        0x48, 0x8b, 0x05, XX4,
        0x48, 0x3b, 0x05, XX4,
        0x72, 0x07,
        0xc6, 0x05, XX4, 0x01,
        XX, 0x89, XX,
        0x41, 0xc1, XX, 0x10,
        0x4c, 0x8d, XX, XX4};
    constexpr BYTE sig_AddBreakPoint[] = {
        0x89, 0xd0,
        0x25, 0x00, 0x00, 0x00, 0x60,
        0x3d, 0x00, 0x00, 0x00, 0x20,
        0xb8, 0xff, 0xff, 0xff, 0x0f,
        0xb9, 0xff, 0xff, 0xff, 0x7f};
    BYTE sig_OpCodeImpl_CACHE[] = {
        0x48, 0x83, 0xec, XX,
        0x8b, 0x05, XX4,
        0x89, 0xc2,
        0xc1, 0xea, 0x10,
        0x83, 0xe2, 0x1f,
        0x8d, 0x4a, 0xf9,
        0x83, 0xf9, 0x15,
        0x0f, 0x87, XX4};
#define FINDALIGN(X)                                                     \
    X = (decltype(X))MemDbg::findEnclosingAlignedFunction((uintptr_t)X); \
    if (!X)                                                              \
        return false;
#define FINDFUNCTION(X)                                                                                    \
    X = (decltype(X))MemDbg::findBytes(sig_##X, sizeof(sig_##X), processStartAddress, processStopAddress); \
    if (!X)                                                                                                \
        return false;
    bool findstartGameListEntry()
    {
        char fmtstr[] = "This save state does not exist.";
        auto fmtstrptr = MemDbg::findBytes(fmtstr, sizeof(fmtstr), processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        fmtstrptr = MemDbg::findleaaddr(fmtstrptr, processStartAddress, processStopAddress);
        if (!fmtstrptr)
            return false;
        startGameListEntry = MemDbg::findEnclosingAlignedFunction(fmtstrptr);
        return startGameListEntry;
    }
    bool hookFunctions()
    {
        if (!findstartGameListEntry())
            return false;
        FINDFUNCTION(dynarecCheckBreakpoint);
        FINDALIGN(dynarecCheckBreakpoint);
        FINDFUNCTION(BaseBlocksNew);
        FINDFUNCTION(recRecompile);
        FINDALIGN(recRecompile);
        FINDFUNCTION(AddBreakPoint);
        FINDALIGN(AddBreakPoint);
        uint64_t OpCodeImpl_CACHE;
        FINDFUNCTION(OpCodeImpl_CACHE);
        _cpuRegistersPack = (decltype(_cpuRegistersPack))(OpCodeImpl_CACHE + 4 + 6 + *(int *)(OpCodeImpl_CACHE + 4 + 2) - 0x2ac);
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
    struct emfuncinfo
    {
        uint64_t type;
        int offset;
        int padding;
        decltype(HookParam::text_fun) hookfunc;
        decltype(HookParam::filter_fun) filterfun;
        const char *_id;
    };
    std::unordered_map<uintptr_t, emfuncinfo> emfunctionhooks;

    void CheckForHook(uint64_t em_address, uintptr_t entrypoint)
    {
        if (emfunctionhooks.find(em_address) == emfunctionhooks.end())
            return;
        auto op = emfunctionhooks.at(em_address);
        if (current_serial.size() && (current_serial != op._id))
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
        NewHook(hpinternal, op._id);
    }
}
bool PCSX2::attach_function()
{
    if (!hookFunctions())
        return false;
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
            return HostInfo(HOSTINFO::EmuGameName, "%s %s", entry->serial.c_str(), entry->title.c_str());
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
                    if (emuaddr2jitaddr.find(startpc) == emuaddr2jitaddr.end())
                        return;
                    auto fnptr = emuaddr2jitaddr[startpc].second;
                    CheckForHook(startpc, fnptr);
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
    for (auto &&hs : emfunctionhooks)
    {
        SafeAddBreakPoint(hs.first);
    }
    return true;
}

namespace
{
    void FSLPM66136(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "#cr0");
        s = re::sub(s, R"((\\n)+)", " ");
        s = re::sub(s, R"(\\d$|^\@[a-z]+|#.*?#|\$)");
        s = re::sub(s, R"(@w|\\c)");
        buffer->from(s);
    }
    void FSLPM65914(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        strReplace(s, L"①ｎ");
        if (startWith(s, L"Ｖ＿") || std::all_of(s.begin(), s.end(), [](wchar_t c)
                                                 { return (c == L'±') || (c == L'-') || (c == L'\\') || (c == L'．') || (c == L'，') || (c == L'－') || (c == L'　') || (c == L' ') || ((c >= L'０') && (c <= L'９')) || ((c >= L'0') && (c <= L'9')); }))
            return buffer->clear();
        s = re::sub(s, LR"(^([±\s]+[０-９０-９，．\-]+|[０-９0-9，．\-]+)$)");
        buffer->fromWA(s);
    }
    void FSLPM66045(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(%\w+\d*\w*)", " ");
        s = re::sub(s, R"(%N+)");
        buffer->from(s);
    }
    void FSLPM66302(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = strSplit(s, L"\");")[0];
        s = re::sub(s, LR"((\\n)+)", L" ");
        s = re::sub(s, LR"(\\d$|^\@[a-z]+|#.*?#|\$)");
        s = re::sub(s, LR"(@w|\\c)");
        strReplace(s, L"＊Ａ", L"岡崎");
        strReplace(s, L"＊Ｂ", L"朋也");
        buffer->fromWA(s);
    }
    void FSLPS25677(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strAW();
        s = re::sub(s, LR"(^\[.*$)");
        s = re::sub(s, LR"(\_0C|\_1_5C|\_1C)");
        s = re::sub(s, LR"(^([a-zA-Z]+)|([a-zA-Z]+)$)");
        buffer->fromWA(s);
    }
    void FSLPS25547(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        FSLPS25677(buffer, hp);
    }
    auto _ = []()
    {
        emfunctionhooks = {
            // アカイイト
            {0x136800, {0, PCSX2_REG_OFFSET(t0), 0, 0, FSLPM66136, "SLPM-65732"}},
            // Nana
            {0x15036C, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM65914, "SLPM-65914"}},
            // My Merry May with be
            {0x1DB7DC, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPM66045, "SLPM-66045"}},
            // CLANNAD - ゲオオンラインストア
            {0x1DB7DC, {0, PCSX2_REG_OFFSET(s4), 0, 0, FSLPM66302, "SLPM-66302"}},
            // 苺ましまろ
            {0x1439F4, {0, PCSX2_REG_OFFSET(s1), 0, 0, FSLPS25547, "SLPS-25547"}},
            // ブラッドプラス ワン ナイト キス
            {0x267B58, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPS25677, "SLPS-25677"}},
            {0x268260, {0, PCSX2_REG_OFFSET(a3), 0, 0, FSLPS25677, "SLPS-25677"}},
        };
        return 0;
    }();
}