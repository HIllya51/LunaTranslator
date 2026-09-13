#include "mages/mages.h"

namespace
{
    int offset = -1;
    int gametype = 0;
}
template <int filter>
static void SpecialHookMAGES(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
{
    auto addr = *(uintptr_t *)(context->base + offset);

    auto s = mages::readString(addr, gametype);

    if (filter)
    {
        static std::wstring last = L"";
        if (last == s)
            return;
        last = s;
    }
    buffer->from(s);
}

#ifndef _WIN64
static void MAGES_mail()
{
    BYTE sig1[] = {
        0xe8, XX, XX, XX, 0x00, 0x6a, 0x18, 0x50, 0x68, XX, 0x01, 0x00, 0x00, 0xe8, XX4, 0x8b};
    auto sigsize = sizeof(sig1);
    auto addr = MemDbg::findBytes(sig1, sizeof(sig1), processStartAddress, processStopAddress);
    if (!addr)
    {
        BYTE sig2[] = {
            0xe8, XX, XX, XX, 0x00, 0x6a, 0x18, XX, XX, 0xb9, XX, 0x01, 0x00, 0x00, 0xe8, XX4, 0x8b};
        sigsize = sizeof(sig2);
        addr = MemDbg::findBytes(sig2, sizeof(sig2), processStartAddress, processStopAddress);
    }
    if (!addr)
        return;
    addr += sigsize - 6;
    addr += *(int *)(addr + 1) + 5;
    HookParam hp;
    hp.address = addr;
    hp.text_fun = SpecialHookMAGES<0>;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    NewHook(hp, "MAGES_mail");
}
#endif

#ifndef _WIN64
bool hookmages::MAGES()
{
    auto dialogSigOffset = 2;
    BYTE dialogSig1[] = {
        0x85, XX, 0x74, XX, 0x83, XX, 0x01, 0x74, XX, 0x83, XX, 0x04, 0x74, XX, 0xc7, 0x05, XX, XX, XX, XX, 0x01, 0x00, 0x00, 0x00};
    auto addr = MemDbg::findBytes(dialogSig1, sizeof(dialogSig1), processStartAddress, processStopAddress);
    if (!addr)
    {
        dialogSigOffset = 3;
        BYTE dialogSig2[] = {
            0x57, 0x85, XX, 0x74, XX, 0x83, XX, 0x01, 0x74, XX, 0x83, XX, 0x04};
        addr = MemDbg::findBytes(dialogSig2, sizeof(dialogSig2), processStartAddress, processStopAddress);
    }
    if (!addr)
        return false;
    auto pos = addr + dialogSigOffset;
    //.text:00431D3F 74 16                         jz      short loc_431D57
    auto jzoff = *(BYTE *)(pos + 1);
    pos += jzoff + 2;
    auto hookaddr = pos;
    for (int i = 0; i < 0x200; i++)
    {
        if (((*(BYTE *)(pos)) == 0x8a))
        {

            switch (((*(BYTE *)(pos + 1))))
            {
                // case 0:reg=pusha_eax_off;break;
                // YU-NO
                //.text:00431D63 89 0D 20 A9 BF 00             mov     dword_BFA920, ecx
                // 在加载到内存后，有时变成89 0d 20 a9 8a 00，导致崩溃，且这个没有遇到过，故注释掉。
            case 3:
                offset = regoffset(ebx);
                break;
            case 1:
                offset = regoffset(ecx);
                break;
            case 2:
                offset = regoffset(edx);
                break;
            case 6:
                offset = regoffset(esi);
                break;
            case 7:
                offset = regoffset(edi);
                break;
            default:
                offset = -1;
            }
            if (offset != -1)
                break;
        }
        pos += 1;
    }
    if (offset == -1)
        return false;
    Msg::Log("%p", pos - processStartAddress);
    switch (pos - processStartAddress)
    {
    case 0x6e69b: // SG My Darling's Embrace 破解版
    case 0x6e77b: // SG My Darling's Embrace
        gametype = 5;
        break;
    case 0x4ef60: // STEINS;GATE: Linear Bounded Phenogram
        gametype = 6;
        break;
    case 0x498b0: // STEINS;GATE
        gametype = 7;
        break;
    case 0x9f723: // Robotics;Notes-Elite
        gametype = 1;
        break;
    case 0xf70a6: // Robotics;Notes-Dash
        gametype = 2;
        break;

    default:
        // YU-NO
        // 测试无效：
        // Steins;Gate-0
        // Steins;Gate
        // 未测试：
        // Steins;Gate-Elite
        // Chaos;Child
        // CHAOS;HEAD_NOAH
        // Memories_Off_-Innocent_Fille
        // Memories_Off_-Innocent_Fille-_for_Dearest
        gametype = 0;
    }
    // Msg::Log ("%x",pos-processStartAddress);
    HookParam hp;
    // hp.address = hookaddr;
    hp.address = hookaddr;
    // 想い出にかわる君 ～メモリーズオフ～ 想君：秋之回忆3在hookaddr上无法正确读取。
    // hookaddr上是没有重复的，pos上是都能读到但有重复。
    hp.text_fun = SpecialHookMAGES<0>;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    auto _ = NewHook(hp, "MAGES_text");
    hp.address = pos;
    hp.text_fun = SpecialHookMAGES<1>;
    _ |= NewHook(hp, "MAGES_text");
    Msg::Log("%p %p", hookaddr, pos);
    if (_)
        MAGES_mail();
    return _;
}
#else

static bool dohooksinternal(uintptr_t usestart, uintptr_t useend, bool MyMerryMayWithbe)
{
    BYTE sig1[] = {
        /*
*((_DWORD *)&qword_140B21E28 + v17) = (unsigned int)v18 / 0xBB80;
v19 = v12 / 0x3E8;
.text:0000000140066EA4 B8 F1 19 76 05                                mov     eax, 57619F1h
.text:0000000140066EA9 F7 E1                                         mul     ecx
.text:0000000140066EAB C1 EA 0A                                      shr     edx, 0Ah
.text:0000000140066EAE 43 89 94 82 28 1E B2 00                       mov     dword ptr rva qword_140B21E28[r10+r8*4], edx
.text:0000000140066EB6 B8 D3 4D 62 10                                mov     eax, 10624DD3h
.text:0000000140066EBB 41 F7 E7                                      mul     r15d
.text:0000000140066EBE C1 EA 06                                      shr     edx, 6
        */
        0xb8, 0xf1, 0x19, 0x76, 0x05,
        0xf7, XX,
        0xc1, 0xea, 0x0a,
        XX, 0x89, 0x94, 0x82, XX4,
        0xb8, 0xd3, 0x4d, 0x62, 0x10,
        0x41, 0xf7, XX,
        0xc1, XX, 0x06};

    BYTE sig1_2[] = {
        // Never7
        /*
  dword_141140860[4 * dword_14113F418 + 2] = v30 * v20 / 0xBB80;
  dword_141140860[4 * dword_14113F418 + 3] = (int)v30 / 1000;
.text:00000001400AFBA6 B9 80 BB 00 00                                mov     ecx, 0BB80h
.text:00000001400AFBAB F7 F1                                         div     ecx
.text:00000001400AFBAD 8B 0D 65 F8 08 01                             mov     ecx, cs:dword_14113F418
.text:00000001400AFBB3 8D 0C 8D 02 00 00 00                          lea     ecx, ds:2[rcx*4]
.text:00000001400AFBBA 8B C9                                         mov     ecx, ecx
.text:00000001400AFBBC 48 8D 15 9D 0C 09 01                          lea     rdx, dword_141140860
.text:00000001400AFBC3 89 04 8A                                      mov     [rdx+rcx*4], eax
.text:00000001400AFBC6 33 D2                                         xor     edx, edx
.text:00000001400AFBC8 8B 44 24 38                                   mov     eax, [rsp+118h+var_E0]
.text:00000001400AFBCC B9 E8 03 00 00                                mov     ecx, 3E8h
.text:00000001400AFBD1 F7 F1                                         div     ecx
        */
        0xB9, 0x80, 0xBB, 0x00, 0x00,
        0xF7, XX,
        0x8B, 0x0D, XX4,
        0x8D, 0x0C, 0x8D, 0x02, 0x00, 0x00, 0x00,
        0x8B, 0xC9,
        0x48, 0x8D, 0x15, XX4,
        0x89, 0x04, 0x8A,
        0x33, 0xD2,
        0x8B, 0x44, 0x24, XX,
        0xB9, 0xE8, 0x03, 0x00, 0x00,
        0xF7, XX};
    BYTE sig1_1[] = {
        0xb8, 0xf1, 0x19, 0x76, 0x05,
        0xf7, XX,
        0xc1, 0xea, 0x0a,
        0x41, 0x8d, 0x40, 0x02,
        XX, 0x89, 0x94, 0x82, XX4,
        0xb8, 0xd3, 0x4d, 0x62, 0x10,
        0x41, 0xf7, XX,
        0xc1, XX, 0x06};
    BYTE sig2[] = {
        /*
      if ( i < 0 && (v32 = *v30 & 0x60, (*v30 & 0x60) != 0) )
      {
        switch ( v32 )
        {
          case ' ':
            v30 += 3;
            break;
          case '@':
            v30 += 4;
            break;
          case '`':
            v30 += 6;
            break;
        }
      }
.text:00000001400670DC 0F B6 03                                      movzx   eax, byte ptr [rbx]
.text:00000001400670DF 83 E0 60                                      and     eax, 60h
.text:00000001400670E2 74 21                                         jz      short loc_140067105
.text:00000001400670E4 83 F8 20                                      cmp     eax, 20h ; ' '
.text:00000001400670E7 74 16                                         jz      short loc_1400670FF
.text:00000001400670E9 83 F8 40                                      cmp     eax, 40h ; '@'
.text:00000001400670EC 74 0B                                         jz      short loc_1400670F9
.text:00000001400670EE 83 F8 60                                      cmp     eax, 60h ; '`'
.text:00000001400670F1 75 16                                         jnz     short loc_140067109
.text:00000001400670F3 48 83 C3 06                                   add     rbx, 6
        */
        0x0f, 0xb6, XX,
        0x83, 0xe0, 0x60,
        0x74, XX,
        0x83, 0xf8, 0x20,
        0x74, XX,
        0x83, 0xf8, 0x40,
        0x74, XX,
        0x83, 0xf8, 0x60,
        0x75, XX,
        0x48, 0x83, 0xc3, 0x06};
    BYTE sig3[] = {
        /*
v60 = v26[1] + ((v28 & 0x7F) << 8);
.text:00000001400676B5 41 83 E1 7F                                   and     r9d, 7Fh
.text:00000001400676B9 41 C1 E1 08                                   shl     r9d, 8
.text:00000001400676BD 0F B6 43 01                                   movzx   eax, byte ptr [rbx+1]
.text:00000001400676C1 44 03 C8                                      add     r9d, eax
        */
        0x41, 0x83, 0xe1, 0x7f,
        0x41, 0xc1, 0xe1, 0x08,
        0x0f, 0xb6, 0x43, 0x01,
        0x44, 0x03, 0xc8};
    BYTE sig3_1[] = {
        0x44, 0x0f, 0xb6, 0x5b, 0x01,
        0x41, 0xc1, 0xe3, 0x08,
        0x0f, 0xb6, 0x43, 0x02,
        0x44, 0x03, 0xd8};
    for (auto [_sig, sz, off] : {
             std::make_tuple(sig1, sizeof(sig1), 0x200),
             std::make_tuple(sig1_2, sizeof(sig1_2), 0x340),
             std::make_tuple(sig1_1, sizeof(sig1_1), 0x200),
             std::make_tuple(sig2, sizeof(sig2), 0x450),
             std::make_tuple(sig3, sizeof(sig3), 0xa00),
             std::make_tuple(sig3_1, sizeof(sig3_1), 0xa00),
         })
    {
        auto addr1 = MemDbg::findBytes(_sig, sz, usestart, useend);
        if (!addr1)
            continue;
        BYTE start[] = {
            XX, 0x89, XX, 0x24, XX,
            XX, 0x89, XX, 0x24, 0x18};
        auto func = reverseFindBytes(start, sizeof(start), addr1 - off, addr1, 0, true);
        if (!func)
            continue;
        switch (func - usestart)
        {
        case 0x66CE0: // 岩倉アリア
        case 0xAF970: // Never 7 - The End of Infinity
        case 0x6C180: // Ever17 -the out of infinity-
            gametype = 8;
            break;
        case 0xC8D60: // メモリーズオフ 双想 ～Not always true～
            gametype = 9;
            break;
        default:
            gametype = 8;
        }
        if (MyMerryMayWithbe) // My Merry May with be
            gametype = 9;
        HookParam hp;
        hp.address = func;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            auto edx = **(uintptr_t **)context->rcx;
            auto s = mages::readString(edx, gametype);
            buffer->from(s);
        };
        hp.type = CODEC_UTF16 | USING_STRING | FULL_STRING;
        return NewHook(hp, "MAGES2");
    }
    return false;
}

static bool ff2()
{
    bool succ = dohooksinternal(processStartAddress, processStopAddress, false);

    // 游戏启动时，先加载MyMerryMaySel_WIN_Master用于选择哪个真正的游戏
    // MyMerryMay_WIN_Master和MyMerryMaybe_WIN_Master是真正有用的
    // 如果已经加载过，则立即hook，否则，ldr等待加载。
    static auto hookmm = []()
    {
        static bool touch[] = {false, false};
        bool ss = false;
        int i = 0;
        for (auto m : {L"MyMerryMay_WIN_Master.dll", L"MyMerryMaybe_WIN_Master.dll"})
        {
            if (!touch[i])
            {
                if (auto h = GetModuleHandle(m))
                {
                    auto [s, e] = Util::QueryModuleLimits(h);
                    if (dohooksinternal(s, e, true))
                    {
                        touch[i] = true;
                        ss = true;
                    }
                }
            }
            i += 1;
        }
        return ss;
    };
    if (GetModuleHandle(L"MyMerryMaySel_WIN_Master.dll"))
    {
        // 用于检测dll加载。懒得用ldrregister了
        HookParam hp;
        hp.address = 0x1998;
        hp.type = DIRECT_READ;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            hookmm();
        };
        succ |= NewHook(hp, "waiter");
    }
    return succ | hookmm();
};

static bool ff()
{
    auto dialogSigOffset = 2;
    BYTE dialogSig1[] = {
        0x85, XX, 0x74, XX, 0x41, 0x83, XX, 0x01, 0x74, XX, 0x41, 0x83, XX, 0x04, 0x74, XX, 0x41};
    auto addr = MemDbg::findBytes(dialogSig1, sizeof(dialogSig1), processStartAddress, processStopAddress);
    if (!addr)
        return false;
    auto pos = addr + dialogSigOffset;
    auto jzoff = *(BYTE *)(pos + 1);
    pos += jzoff + 2;
    auto hookaddr = pos;
    //
    for (int i = 0; i < 0x200; i++)
    {
        //.text:000000014004116B 0F B6 13                      movzx   edx, byte ptr [rbx]
        //->rbx
        if ((((*(DWORD *)(pos)) & 0xffffff) == 0x13b60f))
        {
            offset = regoffset(rbx); // rbx
            // Msg::Log ("%p",pos-processStartAddress);
            break;
        }
        pos += 1;
    }
    if (offset == -1)
        return false;
    switch (pos - processStartAddress)
    {

    default:
        // CHAOS;HEAD_NOAH
        gametype = 0;
    }
    HookParam hp;
    hp.address = hookaddr;
    hp.text_fun = SpecialHookMAGES<0>;
    hp.type = CODEC_UTF16 | USING_STRING | NO_CONTEXT;
    return NewHook(hp, "MAGES");
};

bool hookmages::MAGES()
{
    return ff2() | ff();
}
#endif
