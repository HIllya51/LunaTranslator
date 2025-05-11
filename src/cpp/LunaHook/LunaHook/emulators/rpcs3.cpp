#include "rpcs3.h"
namespace
{
#if 0 // only support0.0.20-0.0.27
    int emoffset;
    int jitoffset;
    uintptr_t getDoJitAddress_() {
        auto installFunctionPatt1 = "0F8? ???????? 488D?? ?00?0000 E8 ???????? 4?83C? 68"; // MSVC
        auto DoJitMatch = find_pattern(installFunctionPatt1,processStartAddress,processStopAddress); 
        if(DoJitMatch)return DoJitMatch;
        
        auto installFunctionPatt2 = "660F 1F440000 488D?? ?00?0000 E8 ???????? 4?83C? 68"; // patched
        DoJitMatch = find_pattern(installFunctionPatt2,processStartAddress,processStopAddress); 
        if(DoJitMatch)return DoJitMatch;
        return 0;
    }
    uintptr_t getDoJitAddress() {
        auto DoJitPtr=getDoJitAddress_();
        if(!DoJitPtr)return 0;
        //<--DoJitPtr
        //0f85 1b050000 // jbe 0x00 ; long jump
        //48 8d 8d 40020000 // lea r?x, ss:[rbp+0x1?0]
        //e8 cc39acff //call
        //48 83 c3 68 // add r?x, 0x68
        auto checkaddr=DoJitPtr+0x6+7+5;
        switch (*(BYTE*)checkaddr)
        {
            case 0x48:{
                switch(*(BYTE*)(checkaddr+2)){
                    case 0xc0:emoffset=regoffset(rax);break;
                    case 0xc3:emoffset=regoffset(rbx);break;
                    case 0xc1:emoffset=regoffset(rcx);break;
                    case 0xc2:emoffset=regoffset(rdx);break;
                    case 0xc4:emoffset=regoffset(rsp);break;
                    case 0xc5:emoffset=regoffset(rbp);break;
                    case 0xc6:emoffset=regoffset(rsi);break;
                    case 0xc7:emoffset=regoffset(rdi);break;
                    default:emoffset=0;
                }  
            }
            break;
            case 0x49:{
                switch(*(BYTE*)(checkaddr+2)){
                    case 0xc0:emoffset=regoffset(r8);break;
                    case 0xc1:emoffset=regoffset(r9);break;
                    case 0xc2:emoffset=regoffset(r10);break;
                    case 0xc3:emoffset=regoffset(r11);break;
                    case 0xc4:emoffset=regoffset(r12);break;
                    case 0xc5:emoffset=regoffset(r13);break;
                    case 0xc6:emoffset=regoffset(r14);break;
                    case 0xc7:emoffset=regoffset(r15);break;
                    default:emoffset=0;
                }
            }
            break;
            default:emoffset=0;
        }
        ConsoleOutput("emoffset %d",emoffset);
        if(emoffset==0)return 0;

        auto isPPUDebugIfPtr = find_pattern("84C0 ???? 8B",DoJitPtr-0x40,DoJitPtr); // je
        //84 c0 //test al,al
        //74 21 //je
        //8b 0b //mov ecx[rbx]
        //48 8b 05 XX4 // mov rax[]
        //4c 8d 34 48 //lea r14,[rax+rcx*2]
        if(isPPUDebugIfPtr==0)return 0;
         
        checkaddr= isPPUDebugIfPtr+2+2+2+7;
        switch (*(BYTE*)checkaddr)
        {
            case 0x48:{
                switch(*(BYTE*)(checkaddr+2)){
                    case 0x14:jitoffset=regoffset(rdx);break;
                    case 0x04:jitoffset=regoffset(rax);break;
                    case 0x1c:jitoffset=regoffset(rbx);break;
                    case 0x0c:jitoffset=regoffset(rcx);break;
                    case 0x24:jitoffset=regoffset(rsp);break;
                    case 0x2c:jitoffset=regoffset(rbp);break;
                    case 0x34:jitoffset=regoffset(rsi);break;
                    case 0x3c:jitoffset=regoffset(rdi);break;
                    default:jitoffset=0;
                }  
            }
            break;
            case 0x4c:{
                switch(*(BYTE*)(checkaddr+2)){
                    case 0x04:jitoffset=regoffset(r8);break;
                    case 0x0c:jitoffset=regoffset(r9);break;
                    case 0x14:jitoffset=regoffset(r10);break;
                    case 0x1c:jitoffset=regoffset(r11);break;
                    case 0x24:jitoffset=regoffset(r12);break;
                    case 0x2c:jitoffset=regoffset(r13);break;
                    case 0x34:jitoffset=regoffset(r14);break;
                    case 0x3c:jitoffset=regoffset(r15);break;
                    default:jitoffset=0;
                }
            }
            break;
            default:jitoffset=0;
        }
        ConsoleOutput("jitoffset %d",jitoffset);
        if(jitoffset==0)return 0;
        
        DWORD _;
        BYTE bs1[]={0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00};
        VirtualProtect((void*)DoJitPtr,sizeof(bs1),PAGE_EXECUTE_READWRITE,&_);
        memcpy((void*)DoJitPtr,bs1,sizeof(bs1));
        BYTE bs2[]={0x66, 0x90};
        VirtualProtect((void*)(isPPUDebugIfPtr+2),sizeof(bs2),PAGE_EXECUTE_READWRITE,&_);
        memcpy((void*)(isPPUDebugIfPtr+2),bs2,sizeof(bs2));
        
        return DoJitPtr+6;
    }
#endif

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

    bool checkiscurrentgame(const emfuncinfo &em)
    {
        auto wininfos = get_proc_windows();
        for (auto &&info : wininfos)
        {
            if (info.title.find(acastw(em._id)) != info.title.npos)
                return true;
        }
        return false;
    }

    static std::set<std::pair<uintptr_t, uintptr_t>> timeoutbreaks;

    void dohookemaddr(uintptr_t em_address, uintptr_t ret)
    {
        jitaddraddr(em_address, ret, JITTYPE::RPCS3);
        auto found = emfunctionhooks.find(em_address);
        if (found == emfunctionhooks.end())
            return;
        auto op = found->second;
        if (!(checkiscurrentgame(op)))
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
        NewHook(hpinternal, op._id);
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
bool rpcs3::attach_function()
{
    auto DoJitPtr = getDoJitAddress();
    if (DoJitPtr == 0)
        return false;
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

namespace
{

    void FBLJM61131(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\[[^\]]+.)");
        s = re::sub(s, R"(\\k|\\x|%C|%B)");
        s = re::sub(s, R"(\%\d+\#[0-9a-fA-F]*\;)");
        s = re::sub(s, R"(\n+)");
        buffer->from(s);
    }
    auto _ = []()
    {
        emfunctionhooks = {
            // ‘＆’ - 空の向こうで咲きますように -
            {0x46328, {CODEC_UTF8, 1, 0, 0, FBLJM61131, "BLJM61131"}},
            // Dunamis15
            {0x42c90, {CODEC_UTF8, 1, 0, 0, FBLJM61131, "BLJM60347"}},

        };
        return 1;
    }();
}