#include "mages/mages.h"

namespace mages
{

    std::map<WORD, std::wstring> createTable(int _idx)
    {
        auto compound_charsA = LoadResData(std::vector<const wchar_t *>{
                                               L"compound_chars_default",
                                               L"compound_chars_Robotics_Notes_Elite",
                                               L"compound_chars_Robotics_Notes_Dash",
                                               L"",
                                               L"",
                                               L"",
                                               L"compound_chars_SGHD",
                                           }[_idx],
                                           L"COMPOUND_CHARS");
        auto charsetA = LoadResData(std::vector<const wchar_t *>{
                                        L"charset_default",
                                        L"charset_Robotics_Notes_Elite",
                                        L"charset_Robotics_Notes_Dash",
                                        L"charset_Famicom_Tantei_Club",
                                        L"charset_SINce_Memories",
                                        L"charset_SG_My_Darlings_Embrace",
                                        L"charset_SG_Linear_Bounded_Phenogram",
                                        L"charset_SGHD"}[_idx],
                                    L"CHARSET");

        auto compound_chars = StringToWideString(compound_charsA);
        auto charset = StringToWideString(charsetA);
        strReplace(charset, L"\n");
        strReplace(charset, L"\r");
        std::map<WORD, std::wstring> table = {};

        for (auto line : strSplit(compound_chars, L"\n"))
        {
            auto pair = strSplit(line, L"=");
            if (pair.size() != 2)
                continue;
            auto key = pair[0].substr(1, pair[0].size() - 2);
            auto val = pair[1];
            auto keys = strSplit(key, L"-");
            if (keys.size() == 1)
                keys.push_back(key);
            size_t _;
            auto start = std::stoi(keys[0], &_, 16);
            auto end = std::stoi(keys[1], &_, 16);
            for (auto i = start; i <= end; i++)
            {
                auto charCode = ((i & 0xFF) << 8) | i >> 8; // swap endian
                table[charCode] = val;
            }
        }

        WORD charCode;
        for (auto i = 0; i < charset.size(); i++)
        {
            charCode = 0x8000 + i;
            charCode = ((charCode & 0xFF) << 8) | charCode >> 8; // swap endian (0x8001 -> 0x0180)
            table[charCode] = charset[i];
        }
        return table;
    }

    std::wstring mages_decode(WORD charCode, int _idx)
    {
        static auto table = createTable(_idx);
        auto found = table.find(charCode);
        if (found == table.end())
        {
            std::wstringstream _;
            _ << std::hex << charCode;
            return L"[" + _.str() + L"]";
        }
        else
        {
            return found->second;
        }
    }
    std::wstring readString(uintptr_t address, int _idx)
    {
        auto edx = address;
        std::wstring s = L"", bottom = L"";
        while (1)
        {
            auto c = *(BYTE *)edx;
            if (c == 0xff)
                break; // terminated
            if (c >= 0xb0)
            { // b4: next page?
                edx += 1;
                continue;
            }
            if (c >= 0x80)
            { // readChar
                auto charCode = *(WORD *)edx;
                edx += 2;
                s += mages_decode(charCode, _idx);
            }
            else
            { // readControl
                edx += 1;
                if (c == 0)
                {
                    s += L' ';
                }
                else if (c == 1)
                { // speaker
                    bottom = L"";
                    while (1)
                    {
                        auto c2 = *(BYTE *)edx;
                        if (c2 == 2)
                        {
                            edx += 1;
                            break;
                        }
                        else if (c2 < 0x20)
                            edx += 1;
                        else
                        {
                            auto charCode = *(WORD *)edx;
                            edx += 2;
                            bottom += mages_decode(charCode, _idx);
                        }
                    }
                    if (bottom.size())
                        s = s + bottom + L": ";
                }
                else if (c == 2)
                { // line
                  // do nothing -> back to readChar
                }
                else if (c == 4 || c == 0x15)
                { // SetColor, EvaluateExpression => SKIP
                    ////if (c !== 4) console.warn('Warning: ', c, hexdump(address));
                    // https://github.com/CommitteeOfZero/SciAdv.Net/blob/32489cd21921079975291dbdce9151ad66f1b06a/src/SciAdvNet.SC3/Text/SC3StringDecoder.cs#L98
                    //   https://github.com/CommitteeOfZero/SciAdv.Net/blob/32489cd21921079975291dbdce9151ad66f1b06a/src/SciAdvNet.SC3/Text/StringSegmentCodes.cs#L3
                    // https://github.com/shiiion/steinsgate_textractor/blob/master/steinsgatetextractor/sg_text_extractor.cpp#L46
                    auto token = *(BYTE *)edx; // BYTE token = read_single<BYTE>(cur_index);
                    if (!token)
                    {
                        edx += 1; // return cur_index + 1;
                    }
                    else
                    {
                        do
                        {
                            if (token & 0x80)
                            {
                                switch (token & 0x60)
                                {
                                case 0:
                                    edx += 2; // cur_index += 2;
                                    break;
                                case 0x20:
                                    edx += 3; // cur_index += 3;
                                    break;
                                case 0x40:
                                    edx += 4; // cur_index += 4;
                                    break;
                                case 0x60:
                                    edx += 5; // cur_index += 5;
                                    break;
                                default:
                                    // impossible
                                    break;
                                }
                            }
                            else
                            {
                                edx += 2; // cur_index += 2;
                            }
                            token = *(BYTE *)edx; // token = read_single<BYTE>(cur_index);
                        } while (token);
                    }
                }
                else if (c == 0x0C    // SetFontSize
                         || c == 0x11 // SetTopMargin
                         || c == 0x12 // SetLeftMargin
                         || c == 0x13 // STT_GetHardcodedValue: https://github.com/CommitteeOfZero/impacto/blob/master/src/text.cpp#L43
                )
                {
                    edx += 2;
                }
                else if (c == 9)
                { // ruby (09_text_0A_rubi_0B)
                    std::wstring rubi = L"";
                    bottom = L"";
                    while (true)
                    {
                        auto c2 = *(BYTE *)edx;
                        if (c2 == 0x0A)
                        { // rubi
                            edx += 1;
                            while (true)
                            {
                                c2 = *(BYTE *)edx;
                                if (c2 == 0x0B)
                                { // end rubi
                                    // address = address.add(1);
                                    break; // break lv2 loop
                                }
                                else if (c2 < 0x20)
                                { // another control
                                    edx += 1;
                                }
                                else
                                { // rubi
                                    auto charCode = *(WORD *)edx;
                                    edx += 2;

                                    rubi += mages_decode(charCode, _idx);
                                }
                            } // end while
                        }
                        else if (c2 == 0x0B)
                        { // end rubi
                            edx += 1;
                            break; // break lv1 loop
                        }
                        else if (c2 < 0x20)
                        { // another control (color?)
                            edx += 1;
                        }
                        else
                        { // char (text)
                            auto charCode = *(WORD *)edx;
                            edx += 2;

                            auto cc = mages_decode(charCode, _idx);
                            bottom += cc;
                            s += cc;
                        }
                    }
                    if (rubi != L"")
                    {
                        // console.log('rubi: ', rubi);
                        // console.log('char: ', bottom);
                    }
                }
                else
                {
                    // do nothing (one byte control)
                }
            }
        }
        return s;
    }

}

namespace hookmages
{

    int offset = -1;
    int gametype = 0;

    template <int filter>
    void SpecialHookMAGES(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto edx = *(uintptr_t *)(context->base + offset); // regof(edx, esp_base);

        auto s = mages::readString(edx, gametype);

        if (filter)
        {
            static std::wstring last = L"";
            if (last == s)
                return;
            last = s;
        }
        buffer->from(s);
    }

    bool MAGES_text()
    {
#ifndef _WIN64
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
        ConsoleOutput("%p", pos - processStartAddress);
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
        // ConsoleOutput("%x",pos-processStartAddress);
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
        ConsoleOutput("%p %p", hookaddr, pos);
        return _;

#else

        auto dialogSigOffset = 2;
        BYTE dialogSig1[] = {
            0x85, XX, 0x74, XX, 0x41, 0x83, XX, 0x01, 0x74, XX, 0x41, 0x83, XX, 0x04, 0x74, XX, 0x41};
        auto addr = MemDbg::findBytes(dialogSig1, sizeof(dialogSig1), processStartAddress, processStopAddress);
        ConsoleOutput("%p", addr);
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
                // ConsoleOutput("%p",pos-processStartAddress);
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

#endif
    }

    void MAGES_mail()
    {
#ifndef _WIN64
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
#endif
    }
    bool MAGES()
    {
        auto succ = MAGES_text();
        if (succ)
            MAGES_mail();
        return succ;
    }
}