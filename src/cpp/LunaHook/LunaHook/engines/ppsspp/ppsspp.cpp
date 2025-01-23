#include "ppsspp.h"
#include "specialgames.hpp"
// See: https://github.com/hrydgard/ppsspp

// Core/HLE (High Level Emulator)
// - sceCcc
//   #void sceCccSetTable(u32 jis2ucs, u32 ucs2jis)
//   int sceCccUTF8toUTF16(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccUTF8toSJIS(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccUTF16toUTF8(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccUTF16toSJIS(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccSJIStoUTF8(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccSJIStoUTF16(u32 dstAddr, u32 dstSize, u32 srcAddr)
//   int sceCccStrlenUTF8(u32 strAddr)
//   int sceCccStrlenUTF16(u32 strAddr)
//   int sceCccStrlenSJIS(u32 strAddr)
//   u32 sceCccEncodeUTF8(u32 dstAddrAddr, u32 ucs)
//   void sceCccEncodeUTF16(u32 dstAddrAddr, u32 ucs)
//   u32 sceCccEncodeSJIS(u32 dstAddrAddr, u32 jis)
//   u32 sceCccDecodeUTF8(u32 dstAddrAddr)
//   u32 sceCccDecodeUTF16(u32 dstAddrAddr)
//   u32 sceCccDecodeSJIS(u32 dstAddrAddr)
//   int sceCccIsValidUTF8(u32 c)
//   int sceCccIsValidUTF16(u32 c)
//   int sceCccIsValidSJIS(u32 c)
//   int sceCccIsValidUCS2(u32 c)
//   int sceCccIsValidUCS4(u32 c)
//   int sceCccIsValidJIS(u32 c)
//   int sceCccIsValidUnicode(u32 c)
//   #u32 sceCccSetErrorCharUTF8(u32 c)
//   #u32 sceCccSetErrorCharUTF16(u32 c)
//   #u32 sceCccSetErrorCharSJIS(u32 c)
//   u32 sceCccUCStoJIS(u32 c, u32 alt)
//   u32 sceCccJIStoUCS(u32 c, u32 alt)
// - sceFont: search charCode
//   int sceFontGetCharInfo(u32 fontHandle, u32 charCode, u32 charInfoPtr)
//   int sceFontGetShadowInfo(u32 fontHandle, u32 charCode, u32 charInfoPtr)
//   int sceFontGetCharImageRect(u32 fontHandle, u32 charCode, u32 charRectPtr)
//   int sceFontGetShadowImageRect(u32 fontHandle, u32 charCode, u32 charRectPtr)
//   int sceFontGetCharGlyphImage(u32 fontHandle, u32 charCode, u32 glyphImagePtr)
//   int sceFontGetCharGlyphImage_Clip(u32 fontHandle, u32 charCode, u32 glyphImagePtr, int clipXPos, int clipYPos, int clipWidth, int clipHeight)
//   #int sceFontSetAltCharacterCode(u32 fontLibHandle, u32 charCode)
//   int sceFontGetShadowGlyphImage(u32 fontHandle, u32 charCode, u32 glyphImagePtr)
//   int sceFontGetShadowGlyphImage_Clip(u32 fontHandle, u32 charCode, u32 glyphImagePtr, int clipXPos, int clipYPos, int clipWidth, int clipHeight)
// - sceKernelInterrupt
//   u32 sysclib_strcat(u32 dst, u32 src)
//   int sysclib_strcmp(u32 dst, u32 src)
//   u32 sysclib_strcpy(u32 dst, u32 src)
//   u32 sysclib_strlen(u32 src)
//
// Sample debug string:
//     006EFD8E   PUSH PPSSPPWi.00832188                    ASCII "sceCccEncodeSJIS(%08x, U+%04x)"
// Corresponding source code in sceCcc:
//     ERROR_LOG(HLE, "sceCccEncodeSJIS(%08x, U+%04x): invalid pointer", dstAddrAddr, jis);

struct PPSSPPFunction
{
    const char *hookName; // hook name
    int argIndex;         // argument index
    uint64_t hookType;    // hook parameter type
    int hookSplit;        // hook parameter split, positive: stack, negative: registers
    const char *pattern;  // debug string used within the function
};

namespace PPSSPP
{
    uintptr_t findleapushalignfuncaddr(uintptr_t addr)
    {
#ifndef _WIN64
        addr = MemDbg::findPushAddress(addr, processStartAddress, processStopAddress);
        if (!addr)
            return NULL;
        addr = SafeFindEnclosingAlignedFunction(addr, 0x200);
#else
        addr = MemDbg::findleaaddr(addr, processStartAddress, processStopAddress);

        if (!addr)
            return NULL;

        BYTE sig1[] = {
            0xCC,
            0x48, 0x89, XX, 0x24, XX};
        BYTE sig2[] = {
            0xC3,
            0x48, 0x89, XX, 0x24, XX};
        BYTE sig3[] = {
            0xCC,
            0x89, XX, 0x24, XX4};
        BYTE sig4[] = {
            0xC3,
            0x89, XX, 0x24, XX};
        int idx = 0;
        uintptr_t maxaddr = 0;
        for (auto sig : {sig1, sig2, sig3, sig4})
        {
            idx += 1;
            maxaddr = max(maxaddr, reverseFindBytes(sig, (idx > 2) ? 5 : 6, addr - 0x500, addr, 1, true));
        }
        maxaddr = max(maxaddr, MemDbg::findEnclosingAlignedFunction_strict(addr, 0x500));

        addr = maxaddr;
#endif
        return addr;
    }
}

bool InsertPPSSPPHLEHooks()
{
    auto functions = std::vector<PPSSPPFunction>{

        // https://github.com/hrydgard/ppsspp/blob/master/Core/HLE/sceCcc.cpp
        // {"sceCccStrlenSJIS", GETARG(1), USING_STRING, 0, "sceCccStrlenSJIS("},
        // {"sceCccStrlenUTF8", GETARG(1), CODEC_UTF8 | USING_STRING, 0, "sceCccStrlenUTF8("},
        // {"sceCccStrlenUTF16", GETARG(1), CODEC_UTF16 | USING_STRING, 0, "sceCccStrlenUTF16("},

        // {"sceCccSJIStoUTF8", GETARG(3), USING_STRING, 0, "sceCccSJIStoUTF8("},
        // {"sceCccSJIStoUTF16", GETARG(3), USING_STRING, 0, "sceCccSJIStoUTF16("},
        // {"sceCccUTF8toSJIS", GETARG(3), CODEC_UTF8 | USING_STRING, 0, "sceCccUTF8toSJIS("},
        // {"sceCccUTF8toUTF16", GETARG(3), CODEC_UTF8 | USING_STRING, 0, "sceCccUTF8toUTF16("},
        // {"sceCccUTF16toSJIS", GETARG(3), CODEC_UTF16 | USING_STRING, 0, "sceCccUTF16toSJIS("},
        // {"sceCccUTF16toUTF8", GETARG(3), CODEC_UTF16 | USING_STRING, 0, "sceCccUTF16toUTF8("},

        // https://github.com/hrydgard/ppsspp/blob/master/Core/HLE/sceFont.cpp
        {"sceFontGetCharInfo", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetCharInfo("},
        {"sceFontGetShadowInfo", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetShadowInfo("},
        {"sceFontGetCharImageRect", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetCharImageRect("},
        {"sceFontGetShadowImageRect", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetShadowImageRect("},
        {"sceFontGetCharGlyphImage", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetCharGlyphImage("},
        //{"sceFontGetCharGlyphImage_Clip", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetCharGlyphImage_Clip("},
        {"sceFontGetShadowGlyphImage", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetShadowGlyphImage("},
        //{"sceFontGetShadowGlyphImage_Clip", GETARG(2), CODEC_UTF16, GETARG(1), "sceFontGetShadowGlyphImage_Clip("},

        // https://github.com/hrydgard/ppsspp/blob/master/Core/HLE/sceKernelInterrupt.cpp
        // {"sysclib_strcat", GETARG(2), USING_STRING, 0, "Untested sysclib_strcat("},
        // {"sysclib_strcpy", GETARG(2), USING_STRING, 0, "Untested sysclib_strcpy("},
        // {"sysclib_strlen", GETARG(1), USING_STRING, 0, "Untested sysclib_strlen("}

    };
    auto succ = false;
    for (auto &&function : functions)
    {
        auto addr = MemDbg::findBytes(function.pattern, ::strlen(function.pattern), processStartAddress, processStopAddress);
        if (!addr)
            continue;
        addr = PPSSPP::findleapushalignfuncaddr(addr);

        if (!addr)
            continue;
        HookParam hp;
        hp.address = addr;
        hp.type = function.hookType;
        hp.offset = function.argIndex;
        hp.split = function.hookSplit;
        if (hp.split)
            hp.type |= USING_SPLIT;
        succ |= NewHook(hp, function.hookName);
    }
    return succ;
}
#if 0
bool PPSSPPinithooksearch(){
	bool found = false;
	SYSTEM_INFO systemInfo;
	GetNativeSystemInfo(&systemInfo);
	for (BYTE* probe = NULL; probe < systemInfo.lpMaximumApplicationAddress;)
	{
		MEMORY_BASIC_INFORMATION info;
		if (!VirtualQuery(probe, &info, sizeof(info)))
		{
			probe += systemInfo.dwPageSize;
		}
		else
		{
			if (info.RegionSize == 0x1f00000 && info.Protect == PAGE_READWRITE && info.Type == MEM_MAPPED)
			{
				found = true;
				ConsoleOutput("PPSSPP memory found: searching for hooks should yield working hook codes");
#ifndef _WIN64
                // PPSSPP 1.8.0 compiles jal to sub dword ptr [ebp+0x360],??
				memcpy(spDefault.pattern, Array<BYTE>{ 0x83, 0xAD, 0x60, 0x03, 0x00, 0x00 }, spDefault.length = 6);
#else
				// PPSSPP 1.8.0 compiles jal to sub dword ptr [r14+0x360],??
				memcpy(spDefault.pattern, Array<BYTE>{ 0x41, 0x83, 0xae, 0x60, 0x03, 0x00, 0x00 }, spDefault.length = 7);
#endif
				spDefault.offset = 0;
				spDefault.minAddress = 0;
				spDefault.maxAddress = -1ULL;
				spDefault.padding = (uintptr_t)probe - 0x8000000;
				spDefault.hookPostProcessor = [](HookParam& hp)
				{
					hp.type |= NO_CONTEXT | USING_SPLIT | SPLIT_INDIRECT;
#ifndef _WIN64
                    hp.split = regoffset(ebp);
					hp.split_index =regoffset(eax); // this is where PPSSPP 1.8.0 stores its return address stack
#else
					hp.split = regoffset(r14);
					hp.split_index = -8; // this is where PPSSPP 1.8.0 stores its return address stack
#endif
				};
			}
			probe += info.RegionSize;
		}
	}
	return found;
}
#endif
uintptr_t getDoJitAddress()
{
#ifndef _WIN64
    auto string1 = "Jump target too far away, needs indirect register";
    auto string2 = "Jump target too far away, needs force5Bytes = true";
    auto addr1 = MemDbg::findBytes(string1, ::strlen(string1), processStartAddress, processStopAddress);
    auto addr2 = MemDbg::findBytes(string2, ::strlen(string2), processStartAddress, processStopAddress);

    if (addr1 == 0 || addr2 == 0)
        return 0;
    // 都是被push两次，但是都是第一个
    addr1 = MemDbg::findPushAddress(addr1, processStartAddress, processStopAddress);
    addr2 = MemDbg::findPushAddress(addr2, processStartAddress, processStopAddress);
    if (addr1 == 0 || addr2 == 0)
        return 0;
    addr1 = MemDbg::findEnclosingAlignedFunction_strict(addr1, 0x100);
    addr2 = MemDbg::findEnclosingAlignedFunction_strict(addr2, 0x100);
    if (addr1 == 0 || addr2 == 0 || addr1 != addr2)
        return 0;
    auto xrefs = findxref_reverse_checkcallop(addr1, processStartAddress, processStopAddress, 0xe8);
    if (xrefs.size() < 28)
        return 0;
    addr1 = MemDbg::findEnclosingAlignedFunction_strict(xrefs[xrefs.size() - 1 - 3], 0x400);
    addr2 = MemDbg::findEnclosingAlignedFunction_strict(xrefs[xrefs.size() - 1 - 4], 0x400);
    if (addr1 == 0 || addr2 == 0 || addr1 != addr2)
        return 0;
    return addr1;
#else
    auto DoJitSig1 = "C7 83 ?? 0? 00 00 11 00 00 00 F6 83 ?? 0? 00 00 01 C7 83 ?? 0? 00 00 E4 00 00 00";
    auto first = find_pattern(DoJitSig1, processStartAddress, processStopAddress);
    if (first)
    {
        auto beginSubSig1 = "55 41 ?? 41 ?? 41";
        auto lookbackSize = 0x400;
        auto address = first - lookbackSize;
        auto subs = find_pattern(beginSubSig1, address, address + lookbackSize);
        if (subs)
        {
            return subs;
        }
    }
    else
    {

        auto DoJitSig2 = "C7 83 ?? 0? 00 00 11 00 00 00 F6 83 ?? 0? 00 00 01 ?? ?? ?? ?? ?? ?? ?? C7 83 ?? 0? 00 00 E4 00 00 00";
        first = find_pattern(DoJitSig2, processStartAddress, processStopAddress);
        if (first)
        {
            first = MemDbg::findEnclosingAlignedFunction_strict(first, 0x400);
            return first;
        }
    }
#endif
    return 0;
}

namespace ppsspp
{
    struct GameInfo
    {
        std::string DISC_ID{""};
        std::string TITLE{""};
    } game_info;
    bool checkiscurrentgame(const emfuncinfo &em)
    {
        if (game_info.DISC_ID.size())
        {
            std::smatch match;
            return std::regex_match(game_info.DISC_ID, match, std::regex(em._id));
        }
        else
        {
            auto wininfos = get_proc_windows();
            for (auto &&info : wininfos)
            {
                if (std::regex_search(info.title, std::wregex(acastw(em._id))))
                    return true;
            }
            return false;
        }
    }
    std::unordered_set<uintptr_t> breakpoints;

    inline bool IsValidAddress(const uintptr_t address)
    {
        if ((address & 0x3E000000) == 0x08000000)
        {
            return true;
        }
        else if ((address & 0x3F800000) == 0x04000000)
        {
            return address < 0x80000000; // Let's disallow kernel-flagged VRAM. We don't have it mapped and I am not sure if it's accessible.
        }
        else if ((address & 0xBFFFC000) == 0x00010000)
        {
            return true;
        }
        else if ((address & 0x3F000000) >= 0x08000000)
        { // && (address & 0x3F000000) < 0x08000000 + g_MemorySize) {
            return true;
        }
        else
        {
            return false;
        }
    }
    void dohookemaddr(uintptr_t em_address, uintptr_t ret)
    {
        jitaddraddr(em_address, ret, JITTYPE::PPSSPP);

        if (emfunctionhooks.find(em_address) == emfunctionhooks.end())
            return;
        if (!(checkiscurrentgame(emfunctionhooks.at(em_address))))
            return;

        auto op = emfunctionhooks.at(em_address);
        ConsoleOutput("jit function addr %p", ret);
#ifndef _WIN64
        BYTE sig[] = {
            0x8b, XX2,                    // mov reg,[ebp-off]
            0x8b, 0xc6,                   // mov eax,esi
            0x25, 0xff, 0xff, 0xff, 0x3f, // and eax,0x3fffffff
            0x89, XX, XX4,                // mov [eax+base+off],reg

        };
        auto findbase = MemDbg::findBytes(sig, sizeof(sig), ret, ret + 0x20);
        if (!findbase)
            findbase = MemDbg::findBytes(sig, sizeof(sig), ret - 0x1000, ret + 0x1000);
        if (!findbase)
            ConsoleOutput("can't find emu_baseaddr");
        PPSSPP::x86_baseaddr = (*(DWORD *)(findbase + 12)) & 0xffff0000;
        ConsoleOutput("x86 base addr %p", PPSSPP::x86_baseaddr);
#endif
        HookParam hpinternal;
        hpinternal.address = ret;
        hpinternal.emu_addr = em_address; // 用于生成hcode
        hpinternal.type = NO_CONTEXT | BREAK_POINT | op.type;
        if (!(op.type & USING_CHAR))
            hpinternal.type |= USING_STRING;
        hpinternal.codepage = 932;
        hpinternal.text_fun = op.hookfunc;
        hpinternal.filter_fun = op.filterfun;
        hpinternal.offset = op.offset;
        hpinternal.padding = op.padding;
        hpinternal.jittype = JITTYPE::PPSSPP;
        NewHook(hpinternal, op._id);
    }
    namespace
    {
        typedef DWORD u32;
        typedef BYTE u8;
        typedef WORD u16;
        const int MAX_JIT_BLOCK_EXITS = 8;
        namespace Memory
        {
            struct Opcode
            {
                Opcode()
                {
                }

                explicit Opcode(u32 v) : encoding(v)
                {
                }

                u32 operator&(const u32 &arg) const
                {
                    return encoding & arg;
                }

                u32 operator>>(const u32 &arg) const
                {
                    return encoding >> arg;
                }

                bool operator==(const u32 &arg) const
                {
                    return encoding == arg;
                }

                bool operator!=(const u32 &arg) const
                {
                    return encoding != arg;
                }

                u32 encoding;
            };

        }

        typedef Memory::Opcode MIPSOpcode;

        struct JitBlock
        {
            bool ContainsAddress(u32 em_address) const;

            const u8 *checkedEntry; // const, we have to translate to writable.
            const u8 *normalEntry;

            u8 *exitPtrs[MAX_JIT_BLOCK_EXITS];    // to be able to rewrite the exit jump
            u32 exitAddress[MAX_JIT_BLOCK_EXITS]; // 0xFFFFFFFF == unknown

            u32 originalAddress;
            MIPSOpcode originalFirstOpcode; // to be able to restore
            uint64_t compiledHash;
            u16 codeSize;
            u16 originalSize;
            u16 blockNum;

            bool invalid;
            bool linkStatus[MAX_JIT_BLOCK_EXITS];

#ifdef USE_VTUNE
            char blockName[32];
#endif

            // By having a pointer, we avoid a constructor/destructor being generated and dog slow
            // performance in debug.
            std::vector<u32> *proxyFor;

            bool IsPureProxy() const
            {
                return originalFirstOpcode.encoding == 0x68FF0000;
            }
            void SetPureProxy()
            {
                // Magic number that won't be a real opcode.
                originalFirstOpcode.encoding = 0x68FF0000;
            }
        };
    }

    void unsafeoncegetJitBlockCache(hook_context *context)
    {

// class JitBlockCache : public JitBlockCacheDebugInterface {
//...
// JitBlock *blocks_ = nullptr;
// std::unordered_multimap<u32, int> proxyBlockMap_; ->64
// int num_blocks_ = 0;
#ifdef _WIN64
        auto num_blocks_ = *(uint32_t *)(context->rcx + 72 + 16 + 88);
        auto blocks_ = (JitBlock *)*(uintptr_t *)(context->rcx + 72 + 16 + 88 - 64 - 8);
#else
        auto num_blocks_ = *(uint32_t *)(context->ecx + 88);
        auto blocks_ = (JitBlock *)*(uintptr_t *)(context->ecx + 88 - 32 - 4);
#endif
        int checkvalid = 0;
        num_blocks_ -= 1; // last one is now dojiting
        for (int i = 0; i < num_blocks_; i++)
        {
            if (IsValidAddress(blocks_[i].originalAddress) && blocks_[i].normalEntry)
                checkvalid += 1;
        }
        if (checkvalid < num_blocks_ / 2)
            return;

        for (int i = 0; i < num_blocks_; i++)
        {
            if (IsValidAddress(blocks_[i].originalAddress) && blocks_[i].normalEntry)
            {
                dohookemaddr(blocks_[i].originalAddress, (uintptr_t)blocks_[i].normalEntry);
                delayinsertNewHook(blocks_[i].originalAddress);
            }
        }

        return;
    }
    bool oncegetJitBlockCache(hook_context *context)
    {
        // 在游戏中途hook，获取已compiled jit
        // 虽然只有在每次进行jit时才会触发，不过测试后续触发的也挺频繁的。
        __try
        {
            unsafeoncegetJitBlockCache(context);
        }
        __except (EXCEPTION_EXECUTE_HANDLER)
        {
        }
        return true;
    }
    void Load_PSP_ISO_StringFromFormat()
    {
        /*
        bool Load_PSP_ISO(FileLoader *fileLoader, std::string *error_string) {
    // Mounting stuff relocated to InitMemoryForGameISO due to HD Remaster restructuring of code.

    std::string sfoPath("disc0:/PSP_GAME/PARAM.SFO");
    PSPFileInfo fileInfo = pspFileSystem.GetFileInfo(sfoPath.c_str());
    if (fileInfo.exists) {
        std::vector<u8> paramsfo;
        pspFileSystem.ReadEntireFile(sfoPath, paramsfo);
        if (g_paramSFO.ReadSFO(paramsfo)) {
            std::string title = StringFromFormat("%s : %s", g_paramSFO.GetValueString("DISC_ID").c_str(), g_paramSFO.GetValueString("TITLE").c_str());
            INFO_LOG(Log::Loader, "%s", title.c_str());
            System_SetWindowTitle(title);
        }
    }

    ------>StringFromFormat
        */
        BYTE sig[] = {
#ifndef _WIN64
            0x55, 0x8B, 0xEC, 0x6A, 0xFF, 0x68, XX4, 0x64, 0xA1, 0x00, 0x00, 0x00, 0x00, 0x50, 0x64, 0x89, 0x25, 0x00, 0x00, 0x00, 0x00, 0x83, 0xEC, 0x14, 0x56, 0x8B, 0x75, 0x08, 0x0F, 0x57, 0xC0, 0xC7, 0x45, 0xE8, 0x00, 0x00, 0x00, 0x00, 0x8D, 0x46, 0x10, 0x57, 0x89, 0x45, 0xF0, 0x0F, 0x11, 0x06, 0xC7, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC7, 0x46, 0x14, 0x00, 0x00, 0x00, 0x00, 0xC7, 0x00, 0x00, 0x00, 0x00, 0x00, 0xC7, 0x46, 0x14, 0x0F, 0x00, 0x00, 0x00, 0xC6, 0x06, 0x00, 0xC7, 0x45, 0xFC, 0x00, 0x00, 0x00, 0x00, 0xC7, 0x45, 0xE8, 0x01, 0x00, 0x00, 0x00, 0xE8, XX4, 0x8B, 0xC8, 0x8D, 0x45, 0x10, 0x50, 0x6A, 0x00, 0xFF, 0x75, 0x0C, 0x8B, 0x01, 0x6A, 0x00, 0x6A, 0x00, 0xFF, 0x71, 0x04, 0x83, 0xC8, 0x02, 0x89, 0x4D, 0xE0, 0x50, 0xE8, XX4
#else
            0x48, 0x8B, 0xC4, 0x48, 0x89, 0x50, 0x10, 0x48, 0x89, 0x48, 0x08, 0x4C, 0x89, 0x40, 0x18, 0x4C, 0x89, 0x48, 0x20, 0x53, 0x55, 0x56, 0x57, 0x41, 0x56, 0x41, 0x57, 0x48, 0x83, 0xEC, 0x48, 0x48, 0x8B, 0xDA, 0x48, 0x8B, 0xF9, 0x33, 0xED, 0x89, 0x68, 0xB8, 0x0F, 0x57, 0xC0, 0x0F, 0x11, 0x01, 0x48, 0x89, 0x69, 0x10, 0x48, 0xC7, 0x41, 0x18, 0x0F, 0x00, 0x00, 0x00, 0x40, 0x88, 0x29, 0xC7, 0x40, 0xB8, 0x01, 0x00, 0x00, 0x00, 0x4C, 0x8D, 0x70, 0x18, 0xE8, XX4, 0x48, 0x8B, 0xF0, 0x48, 0x8B, 0x08, 0x48, 0x83, 0xC9, 0x02, 0x4C, 0x89, 0x74, 0x24, 0x28, 0x48, 0x89, 0x6C, 0x24, 0x20, 0x4C, 0x8B, 0xCB, 0x45, 0x33, 0xC0, 0x33, 0xD2, 0xE8, XX4
#endif
        };
        auto addr = MemDbg::findBytes(sig, sizeof(sig), processStartAddress, processStopAddress);
        if (!addr)
            return;
        HookParam hp;
        hp.address = addr;
        hp.text_fun = [](hook_context *context, HookParam *hp, auto *buff, auto *split)
        {
            if (strcmp((char *)context->argof(2), "%s : %s") != 0)
                return;
            game_info.DISC_ID = (char *)context->argof(3);
            game_info.TITLE = (char *)context->argof(4);
            HostInfo(HOSTINFO::EmuGameName, "%s %s", context->argof(3), context->argof(4));
            jitaddrclear();
        };
        NewHook(hp, "PPSSPPGameInfo");
    }
    void trygetgameinwindowtitle()
    {
        auto wininfos = get_proc_windows();
        for (auto &&info : wininfos)
        {
            if (info.title.find(L'-') == info.title.npos)
                continue;
            auto title = WideStringToString(info.title.substr(info.title.find(L'-') + 2));
            game_info.DISC_ID = title.substr(0, title.find(':') - 1);
            game_info.TITLE = title.substr(title.find(':') + 2);
            HostInfo(HOSTINFO::EmuGameName, "%s %s", game_info.DISC_ID.c_str(), game_info.TITLE.c_str());
            return;
        }
    }
    bool hookPPSSPPDoJit()
    {
        auto DoJitPtr = getDoJitAddress();
        if (!DoJitPtr)
            return false;
        trygetgameinwindowtitle();
        Load_PSP_ISO_StringFromFormat();
        HookParam hp;
        hp.address = DoJitPtr; // Jit::DoJit
        hp.user_value = (uintptr_t) new uintptr_t;
        hp.text_fun = [](hook_context *context, HookParam *hp, auto *, auto *)
        {
            static auto once1 = oncegetJitBlockCache(context);
            auto em_address = context->THISCALLARG1;

            *(uintptr_t *)(hp->user_value) = em_address;

            HookParam hpinternal;
            hpinternal.user_value = hp->user_value;
            hpinternal.address = context->retaddr;
            hpinternal.text_fun = [](hook_context *context, HookParam *hp, auto *, auto *)
            {
                auto em_address = *(uintptr_t *)(hp->user_value);
                if (!IsValidAddress(em_address))
                    return;
                [&]()
                {
                    auto ret = context->LASTRETVAL;
                    if (breakpoints.find(ret) != breakpoints.end())
                        return;
                    breakpoints.insert(ret);

                    dohookemaddr(em_address, ret);
                }();
                delayinsertNewHook(em_address);
            };
            static auto once = NewHook(hpinternal, "DoJitPtrRet");
        };

        return NewHook(hp, "PPSSPPDoJit");
    }
}
bool PPSSPPWindows::attach_function()
{
    auto succ = ppsspp::hookPPSSPPDoJit();
    succ |= InsertPPSSPPHLEHooks();
    return succ;
}