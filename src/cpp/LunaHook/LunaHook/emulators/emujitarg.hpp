#pragma once
#ifdef _WIN64
namespace PCSX2Types
{
    // https://github.com/PCSX2/pcsx2/blob/master/pcsx2/R5900.h
    using s8 = int8_t;
    using s16 = int16_t;
    using s32 = int32_t;
    using s64 = int64_t;

    using u8 = uint8_t;
    using u16 = uint16_t;
    using u32 = uint32_t;
    using u64 = uint64_t;

    using uptr = uintptr_t;
    using sptr = intptr_t;

    using uint = unsigned int;

    struct s128
    {
        s64 lo;
        s64 hi;

        // explicit conversion from s64, with sign extension.
        static s128 From64(s64 src)
        {
            s128 retval = {src, (src < 0) ? -1 : 0};
            return retval;
        }

        // explicit conversion from s32, with sign extension.
        static s128 From64(s32 src)
        {
            s128 retval = {src, (src < 0) ? -1 : 0};
            return retval;
        }

        operator u32() const { return (s32)lo; }
        operator u16() const { return (s16)lo; }
        operator u8() const { return (s8)lo; }

        bool operator==(const s128 &right) const
        {
            return (lo == right.lo) && (hi == right.hi);
        }

        bool operator!=(const s128 &right) const
        {
            return (lo != right.lo) || (hi != right.hi);
        }
    };

    union u128
    {
        struct
        {
            u64 lo;
            u64 hi;
        };

        u64 _u64[2];
        u32 _u32[4];
        u16 _u16[8];
        u8 _u8[16];

        // Explicit conversion from u64. Zero-extends the source through 128 bits.
        static u128 From64(u64 src)
        {
            u128 retval;
            retval.lo = src;
            retval.hi = 0;
            return retval;
        }

        // Explicit conversion from u32. Zero-extends the source through 128 bits.
        static u128 From32(u32 src)
        {
            u128 retval;
            retval._u32[0] = src;
            retval._u32[1] = 0;
            retval.hi = 0;
            return retval;
        }

        operator u32() const { return _u32[0]; }
        operator u16() const { return _u16[0]; }
        operator u8() const { return _u8[0]; }

        bool operator==(const u128 &right) const
        {
            return (lo == right.lo) && (hi == right.hi);
        }

        bool operator!=(const u128 &right) const
        {
            return (lo != right.lo) || (hi != right.hi);
        }
    };

    union GPR_reg
    { // Declare union type GPR register
        u128 UQ;
        s128 SQ;
        u64 UD[2]; // 128 bits
        s64 SD[2];
        u32 UL[4];
        s32 SL[4];
        u16 US[8];
        s16 SS[8];
        u8 UC[16];
        s8 SC[16];
    };
    struct __named_regs__
    {
        GPR_reg r0, at, v0, v1, a0, a1, a2, a3,
            t0, t1, t2, t3, t4, t5, t6, t7,
            s0, s1, s2, s3, s4, s5, s6, s7,
            t8, t9, k0, k1, gp, sp, s8, ra;
    };
    union GPRregs
    {
        __named_regs__ n;
        GPR_reg r[32];
    };

    union CP0regs
    {
        struct
        {
            u32 Index, Random, EntryLo0, EntryLo1,
                Context, PageMask, Wired, Reserved0,
                BadVAddr, Count, EntryHi, Compare;
            union
            {
                struct
                {
                    u32 IE : 1;  // Bit 0: Interrupt Enable flag.
                    u32 EXL : 1; // Bit 1: Exception Level, set on any exception not covered by ERL.
                    u32 ERL : 1; // Bit 2: Error level, set on Resetm NMI, perf/debug exceptions.
                    u32 KSU : 2; // Bits 3-4: Kernel [clear] / Supervisor [set] mode
                    u32 unused0 : 3;
                    u32 IM : 8;   // Bits 10-15: Interrupt mask (bits 12,13,14 are unused)
                    u32 EIE : 1;  // Bit 16: IE bit enabler.  When cleared, ints are disabled regardless of IE status.
                    u32 _EDI : 1; // Bit 17: Interrupt Enable (set enables ints in all modes, clear enables ints in kernel mode only)
                    u32 CH : 1;   // Bit 18: Status of most recent cache instruction (set for hit, clear for miss)
                    u32 unused1 : 3;
                    u32 BEV : 1; // Bit 22: if set, use bootstrap for TLB/general exceptions
                    u32 DEV : 1; // Bit 23: if set, use bootstrap for perf/debug exceptions
                    u32 unused2 : 2;
                    u32 FR : 1; // (?)
                    u32 unused3 : 1;
                    u32 CU : 4; // Bits 28-31: Co-processor Usable flag
                } b;
                u32 val;
            } Status;
            u32 Cause, EPC, PRid,
                Config, LLAddr, WatchLO, WatchHI,
                XContext, Reserved1, Reserved2, Debug,
                DEPC, PerfCnt, ErrCtl, CacheErr,
                TagLo, TagHi, ErrorEPC, DESAVE;
        } n;
        u32 r[32];
    };

    union PERFregs
    {
        struct
        {
            union
            {
                struct
                {
                    u32 pad0 : 1;   // LSB should always be zero (or undefined)
                    u32 EXL0 : 1;   // enable PCR0 during Level 1 exception handling
                    u32 K0 : 1;     // enable PCR0 during Kernel Mode execution
                    u32 S0 : 1;     // enable PCR0 during Supervisor mode execution
                    u32 U0 : 1;     // enable PCR0 during User-mode execution
                    u32 Event0 : 5; // PCR0 event counter (all values except 1 ignored at this time)

                    u32 pad1 : 1; // more zero/undefined padding [bit 10]

                    u32 EXL1 : 1;   // enable PCR1 during Level 1 exception handling
                    u32 K1 : 1;     // enable PCR1 during Kernel Mode execution
                    u32 S1 : 1;     // enable PCR1 during Supervisor mode execution
                    u32 U1 : 1;     // enable PCR1 during User-mode execution
                    u32 Event1 : 5; // PCR1 event counter (all values except 1 ignored at this time)

                    u32 Reserved : 11;
                    u32 CTE : 1; // Counter enable bit, no counting if set to zero.
                } b;

                u32 val;
            } pccr;

            u32 pcr0, pcr1, pad;
        } n;
        u32 r[4];
    };
    struct cpuRegisters
    {
        GPRregs GPR; // GPR regs
        // NOTE: don't change order since recompiler uses it
        GPR_reg HI;
        GPR_reg LO;      // hi & log 128bit wide
        CP0regs CP0;     // is COP0 32bit?
        u32 sa;          // shift amount (32bit), needs to be 16 byte aligned
        u32 IsDelaySlot; // set true when the current instruction is a delay slot.
        u32 pc;          // Program counter, when changing offset in struct, check iR5900-X.S to make sure offset is correct
        u32 code;        // current instruction
        PERFregs PERF;
        u32 eCycle[32];
        u32 sCycle[32]; // for internal counters
        u32 cycle;      // calculate cpucycles..
        u32 interrupt;
        int branch;
        int opmode; // operating mode
        u32 tempcycles;
        u32 dmastall;
        u32 pcWriteback;

        // if cpuRegs.cycle is greater than this cycle, should check cpuEventTest for updates
        u32 nextEventCycle;
        u32 lastEventCycle;
        u32 lastCOP0Cycle;
        u32 lastPERFCycle[2];
    };
    struct cpuRegistersPack
    {
        alignas(16) cpuRegisters cpuRegs;
        //   alignas(16) fpuRegisters fpuRegs;
    };

    static constexpr sptr _1kb = 1024 * 1;
    static constexpr sptr _4kb = _1kb * 4;
    static constexpr sptr _16kb = _1kb * 16;
    static constexpr sptr _32kb = _1kb * 32;
    static constexpr sptr _64kb = _1kb * 64;
    static constexpr sptr _128kb = _1kb * 128;
    static constexpr sptr _256kb = _1kb * 256;

    static constexpr s64 _1mb = 1024 * 1024;
    static constexpr s64 _8mb = _1mb * 8;
    static constexpr s64 _16mb = _1mb * 16;
    static constexpr s64 _32mb = _1mb * 32;
    static constexpr s64 _64mb = _1mb * 64;
    static constexpr s64 _256mb = _1mb * 256;
    static constexpr s64 _1gb = _1mb * 1024;
    static constexpr s64 _4gb = _1gb * 4;

    namespace Ps2MemSize
    {
        static constexpr u32 MainRam = _32mb;       // 32 MB main memory.
        static constexpr u32 ExtraRam = _1mb * 96;  // 32+96 MB devkit memory.
        static constexpr u32 TotalRam = _1mb * 128; // 128 MB total memory.
        static constexpr u32 Rom = _1mb * 4;        // 4 MB main rom
        static constexpr u32 Rom1 = _1mb * 4;       // DVD player
        static constexpr u32 Rom2 = _1mb * 4;       // Chinese rom extension
        static constexpr u32 Hardware = _64kb;
        static constexpr u32 Scratch = _16kb;

        static constexpr u32 IopRam = _1mb * 2; // 2MB main ram on the IOP.
        static constexpr u32 IopHardware = _64kb;

        static constexpr u32 GSregs = 0x00002000; // 8k for the GS registers and stuff.

        extern u32 ExposedRam;
    } // namespace Ps2MemSize

    struct EEVM_MemoryAllocMess
    {
        u8 Main[Ps2MemSize::MainRam];         // Main memory (hard-wired to 32MB)
        u8 ExtraMemory[Ps2MemSize::ExtraRam]; // Extra memory (32MB up to 128MB => 96MB).
        u8 Scratch[Ps2MemSize::Scratch];      // Scratchpad!
        u8 ROM[Ps2MemSize::Rom];              // Boot rom (4MB)
        u8 ROM1[Ps2MemSize::Rom1];            // DVD player (4MB)
        u8 ROM2[Ps2MemSize::Rom2];            // Chinese extensions

        // Two 1 megabyte (max DMA) buffers for reading and writing to high memory (>32MB).
        // Such accesses are not documented as causing bus errors but as the memory does
        // not exist, reads should continue to return 0 and writes should be discarded.
        // Probably.

        u8 ZeroRead[_1mb];
        u8 ZeroWrite[_1mb];
    };

    enum BreakPointCpu
    {
        BREAKPOINT_EE = 0x01,
        BREAKPOINT_IOP = 0x02,
        BREAKPOINT_IOP_AND_EE = 0x03
    };
    // alignas(16) extern cpuRegistersPack _cpuRegistersPack;
    inline cpuRegistersPack *_cpuRegistersPack = nullptr;
    inline EEVM_MemoryAllocMess *eeMem = nullptr;
    inline uintptr_t emu_addr(uint32_t addr)
    {
        return (uintptr_t)eeMem->Main + addr;
    }
    inline uintptr_t argsof(int idx)
    {
        return emu_addr(((DWORD *)(&_cpuRegistersPack->cpuRegs.GPR.r[idx].UQ))[0]);
    }
}
#define PCSX2_REG_OFFSET(reg) (offsetof(__named_regs__, reg) / sizeof(GPR_reg))
#define PCSX2_REG(reg) ((uintptr_t)eeMem->Main + ((DWORD *)(&_cpuRegistersPack->cpuRegs.GPR.n.reg.UQ))[0])

namespace RPCS3
{
    class emu_arg
    {
        hook_context *context;

    public:
        emu_arg(hook_context *context) : context(context) {};
        uintptr_t operator[](int idx)
        {
            auto base = context->rbx;
            auto args = (uintptr_t *)(context->rbp + 0x18 + 8 * 3);
            return base + args[idx];
        }
    };
}
namespace YUZU
{
    class emu_arg
    {
        hook_context *context;
        bool is64;

    public:
        emu_arg(hook_context *context, uint64_t em_addr = 0) : context(context), is64(em_addr == 0 || em_addr > 0x80004000) {};
        uintptr_t value(int idx)
        {
            if (is64)
            {
                auto args = (uintptr_t *)context->r15;
                return args[idx];
            }
            else
            {
                // 0x204000
                auto args = (DWORD *)context->r15;
                return args[idx];
            }
        }
        uintptr_t operator[](int idx)
        {
            auto base = context->r13;
            return base + value(idx);
        }
    };
}
namespace VITA3K
{
    class emu_addr
    {
        hook_context *context;
        DWORD addr;

    public:
        emu_addr(hook_context *context, DWORD addr_) : context(context), addr(addr_) {};
        operator uintptr_t()
        {
            auto base = context->r13;
            return base + addr;
        }
        operator DWORD *()
        {
            return (DWORD *)(uintptr_t)*this;
        }
    };
    class emu_arg
    {
        hook_context *context;

    public:
        emu_arg(hook_context *context) : context(context) {};
        uintptr_t value(int idx)
        {
            auto args = (uint32_t *)context->r15;
            return args[idx];
        }
        uintptr_t operator[](int idx)
        {
            return emu_addr(context, value(idx));
        }
    };
}
#endif
namespace PPSSPP
{
    inline DWORD x86_baseaddr;
    class emu_addr
    {
        hook_context *context;
        DWORD addr;

    public:
        emu_addr(hook_context *context, DWORD addr_) : context(context), addr(addr_) {};
        operator uintptr_t()
        {
#ifndef _WIN64
            auto base = x86_baseaddr;
#else
            auto base = context->rbx;
#endif
            return base + addr;
        }
        operator DWORD *()
        {
            return (DWORD *)(uintptr_t)*this;
        }
    };
    class emu_arg
    {
        hook_context *context;

    public:
        emu_arg(hook_context *context) : context(context) {};
        uintptr_t operator[](int idx)
        {
#ifndef _WIN64
            auto args = context->ebp;
#else
            auto args = context->r14;
#endif
            auto offR = -0x80;
            auto offset = offR + 0x10 + idx * 4;
            return (uintptr_t)emu_addr(context, *(uint32_t *)(args + offset));
        }
    };
}