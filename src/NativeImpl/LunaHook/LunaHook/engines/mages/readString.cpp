#include "mages/mages.h"

namespace mages
{
    std::map<DWORD, std::wstring> createTable(int _idx)
    {
        auto compound_charsA = LoadResData(std::vector<const wchar_t *>{
                                               L"compound_chars_default",
                                               L"compound_chars_Robotics_Notes_Elite",
                                               L"compound_chars_Robotics_Notes_Dash",
                                               L"",
                                               L"",
                                               L"",
                                               L"compound_chars_SGHD",
                                               L"",
                                               L"",
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
                                        L"charset_SGHD",
                                        L"charset_IwakuraAria",
                                        L"charset_9",
                                    }[_idx],
                                    L"CHARSET");

        auto compound_chars = StringToWideString(compound_charsA);
        auto charset = StringToWideString(charsetA);
        strReplace(charset, L"\n");
        strReplace(charset, L"\r");
        std::map<DWORD, std::wstring> table = {};

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
                auto charCode = ((i & 0xFF) << 8) | i >> 8;
                table[charCode] = val;
            }
        }

        DWORD charCode;
        for (auto i = 0; i < charset.size(); i++)
        {
            if (_idx == 9)
            {
                /*
    while ( *v14 != 255 )
    {
      if ( (*v14 & 0x80) != 0 )
      {
        v55 = v14[3] + (v14[2] << 8) + (v14[1] << 16) + ((*v14 & 0x7F) << 24);
                */
                uint8_t *v14 = (uint8_t *)&i;
                charCode = v14[3] + (v14[2] << 8) + (v14[1] << 16) + 0x80 + ((*v14) << 24);
                table[charCode] = charset[i];
            }
            else
            {
                charCode = 0x8000 + i;
                charCode = ((charCode & 0xFF) << 8) | charCode >> 8;
                table[charCode] = charset[i];
            }
        }
        return table;
    }

    std::wstring mages_decode(int _idx, uintptr_t &addr)
    {
        DWORD charCode;
        if (_idx == 9)
        {
            charCode = *(DWORD *)addr;
            addr += 4;
        }
        else
        {
            charCode = *(WORD *)addr;
            addr += 2;
        }
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
        for (auto i = 0; i < 1000; i++)
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
                s += mages_decode(_idx, edx);
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
                            bottom += mages_decode(_idx, edx);
                        }
                    }
                    if (bottom.size())
                        s = s + L"【" + bottom + L"】";
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
                                    rubi += mages_decode(_idx, edx);
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
                            auto cc = mages_decode(_idx, edx);
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
