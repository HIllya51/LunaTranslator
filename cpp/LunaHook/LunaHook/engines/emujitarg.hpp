#pragma once
#ifdef _WIN64
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
        uintptr_t operator[](int idx)
        {
            auto base = context->r13;
            if (is64)
            {
                auto args = (uintptr_t *)context->r15;
                return base + args[idx];
            }
            else
            {
                // 0x204000
                auto args = (DWORD *)context->r15;
                return base + args[idx];
            }
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
            return (DWORD *)(uintptr_t) * this;
        }
    };
    class emu_arg
    {
        hook_context *context;

    public:
        emu_arg(hook_context *context) : context(context) {};
        uintptr_t operator[](int idx)
        {
            auto args = (uint32_t *)context->r15;
            return emu_addr(context, args[idx]);
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
            return (DWORD *)(uintptr_t) * this;
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