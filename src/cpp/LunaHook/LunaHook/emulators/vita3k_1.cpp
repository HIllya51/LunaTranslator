
#include "vita3k_1.h"

namespace
{
    void FPCSG01023(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "<br>");
        s = re::sub(s, "%CF11F");
        s = re::sub(s, "%CFFFF");
        s = re::sub(s, "%K%P");
        s = re::sub(s, "%K%N");
        s = re::sub(s, "\n");
        buffer->from(s);
    }
    void FPCSG01282_1(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "(\\n)+", " ");
        s = re::sub(s, "\\d$|^@[a-z]+|#.*?#|\\$");
        buffer->from(s);
    }
    template <int idx>
    void FPCSG01282(TextBuffer *buffer, HookParam *hp)
    {
        FPCSG01282_1(buffer, hp);
        static std::string last;
        auto s = buffer->viewA();
        if (last == s)
            return buffer->clear();
        last = s;
    }

    void PCSG01235(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[hp->offset];
        buffer->from((char *)(address - 3));
    }

    void PCSG00595(hook_context *context, HookParam *hp1, TextBuffer *buffer, uintptr_t *split)
    {
        hp1->text_fun = nullptr;
        hp1->type |= HOOK_EMPTY;
        HookParam hp;
        hp.emu_addr = VITA3K::emu_arg(context).value(0) + hp1->padding;
        hp.address = VITA3K::emu_addr(context, hp.emu_addr);
        hp.type = DIRECT_READ;
        hp.jittype = JITTYPE ::VITA3K;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            static std::string last;
            std::string collect;
            char *ptr = (char *)hp->address;
            while (*ptr)
            {
                std::string s = ptr;
                collect += s;
                if (endWith(s, "\n"))
                {
                    collect = collect.substr(0, collect.size() - 1);
                }
                ptr += s.size() + 1;
            }
            strReplace(collect, "\x87\x6e");
            if (startWith(collect, last))
                buffer->from(collect.substr(last.size()));
            else
                buffer->from(collect);
            last = collect;
        };
        NewHook(hp, hp1->name);
    }
    void ReadU16TextAndLenDW(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[hp->offset];
        buffer->from(address + 0xC, (*(DWORD *)(address + 0x8)) * 2);
    }

    void FPCSG00410(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "#[A-Za-z]+\\[(\\d*[.])?\\d+\\]");
        s = re::sub(s, "#Pos\\[[\\s\\S]*?\\]");
        s = re::sub(s, "#n", " ");
        // .replaceAll("④", "!?").replaceAll("②", "!!").replaceAll("⑥", "。").replaceAll("⑪", "【")
        // 	.replaceAll("⑫", "】").replaceAll("⑤", "、").replaceAll("①", "・・・")
        strReplace(s, "\x87\x43", "!?");
        strReplace(s, "\x87\x41", "!!");
        strReplace(s, "\x87\x45", "\x81\x42");
        strReplace(s, "\x87\x4a", "\x81\x79");
        strReplace(s, "\x87\x4b", "\x81\x7a");
        strReplace(s, "\x87\x44", "\x81\x41");
        strReplace(s, "\x87\x40", "\x81\x45\x81\x45\x81\x45");
        buffer->from(s);
    }
    void FPCSG00448(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "[\\s]");
        s = re::sub(s, "(#n)+");
        s = re::sub(s, "#[A-Za-z]+\\[(\\d*[.])?\\d+\\]");
        s = re::sub(s, "#Pos\\[[\\s\\S]*?\\]");
        buffer->from(s);
    }
    void PCSG01203(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "#Ruby\\[[-\\d]+,(.*?)\\]");
        buffer->from(s);
    }
    void PCSG00766(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#Ruby\[(.*?),(.*?)\])", "$1");
        s = re::sub(s, R"((\x81\x40)*(#n)*(\x81\x40)*)");
        s = re::sub(s, R"(#[A-Za-z]+\[[\d\-,\.]*\])");
        buffer->from(s);
    }
    void PCSG00935(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        auto _ = re::search(s, R"(#n#Pos[[\d\-,\.]*\](.*))");
        if (_)
        {
            s = strReplace(s, _.value()[0].str());
            s = u8"【" + _.value()[1].str() + u8"】" + s;
        }
        buffer->from(s);
        PCSG00766(buffer, hp);
    }
    void TPCSG00903(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[0];
        buffer->from(address + 0x1C, (*(DWORD *)(address + 0x14)));
    }
    void PCSG00615(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN(L"＿"));
    }
    void PCSG01001(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("@@"));
    }
    void PCSG01247(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\\n"));
    }
    void PCSG01144(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\\n"));
        StringFilter(buffer, TEXTANDLEN("\\c"));
    }
    void FPCSG00903(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "\\\\n", " ");
        buffer->from(s);
    }
    void FPCSG01180(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\\n)", " ");
        s = re::sub(s, R"(,.*$)", " ");
        buffer->from(s);
    }
    void PCSG01002(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, L'\n');
        auto s = buffer->strW();
        s = re::sub(s, L"<.*?>");
        buffer->from(s);
    }
    void FPCSG00839(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = re::sub(s, L"\\[[^\\]]+.");
        s = re::sub(s, L"\\\\k|\\\\x|%C|%B|%p-1;");
        s = re::sub(s, L"#[0-9a-fA-F]+;([^%#]+)(%r)?", L"$1");
        s = re::sub(s, L"\\\\n");
        static std::wstring last;
        if (last.find(s) != last.npos)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void FPCSG00751(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "[\\s]");
        s = re::sub(s, "@[a-z]");
        // s = re::sub(s, "＄"), "");
        strReplace(s, "\x81\x90");
        buffer->from(s);
    }
    void FPCSG00401(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"([\s])");
        s = re::sub(s, R"(\c)");
        s = re::sub(s, R"(\\n)");
        buffer->from(s);
    }
    void PCSG00530(TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN("#n"));
    }
    void PCSG00826(TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN("#n"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
    }
    void PCSG00592(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#Color\[\d+\])");
        buffer->from(s);
    }
    void PCSG00833(TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN(u8"　"));
    }
    void PCSG00855(TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN(u8"#n　"));
        StringFilter(buffer, TEXTANDLEN(u8"#n"));
    }
    void PCSG01150(TextBuffer *buffer, HookParam *hp)
    {
        PCSG00855(buffer, hp);
        PCSG00592(buffer, hp);
    }
    void PCSG01260_T(TextBuffer *buffer, HookParam *)
    {
        StringFilter(buffer, TEXTANDLEN(u8"@n"));
    }
    void PCSG01260(TextBuffer *buffer, HookParam *)
    {
        auto s = buffer->strA();
        if (!startWith(s, u8"【"))
            return buffer->clear();
        buffer->from(s.substr(0, s.find(u8"】") + strlen(u8"】")));
    }
    void PCSG01034(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, L'\n');
        static std::string last;
        auto s = buffer->strA();
        if (s == last)
        {
            buffer->clear();
        }
        last = s;
    }
    void PCSG01284(TextBuffer *buffer, HookParam *)
    {
        static std::string last;
        auto s = buffer->strA();
        if (endWith(last, s))
            buffer->clear();
        last = s;
    }
    void PCSG01204(TextBuffer *buffer, HookParam *)
    {
        CharFilter(buffer, '\n');
        StringFilter(buffer, TEXTANDLEN("@1r"));
        StringFilter(buffer, TEXTANDLEN("@-1r"));
    }
    void PCSG01068(TextBuffer *buffer, HookParam *hp)
    {
        StringCharReplacer(buffer, TEXTANDLEN("\\\\"), '\n');
        CharFilter(buffer, '\\');
        auto s = buffer->viewA();
        if (endWith(s, u8"。!"))
            buffer->from(s.substr(0, s.size() - 1));
    }
    void PCSG00367(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, L'\\');
        CharFilter(buffer, L'#');
    }
    void PCSG01167(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(<(.*?)>(.*?)\|)", "$2");
        buffer->from(s);
    }
    void PCSG00917(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(([^。…？！])　)", "$1");
        s = re::sub(s, u8R"(^　)");
        s = re::sub(s, u8R"(#n)");
        buffer->from(s);
    }
    void PCSG00938(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(([^。…？！])　)", "$1");
        s = re::sub(s, u8R"(^　)");
        s = re::sub(s, u8R"(#n)");
        s = re::sub(s, u8R"(#\w+\[\d+\]|!)");
        buffer->from(s);
    }
    void FPCSG00912(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("%N"));
    }
    void FPCSG00706(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = re::sub(s, L"<br>");
        buffer->from(s);
    }
    void FPCSG00696(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        //.replace(/㌔/g, '⁉')
        //.replace(/㍉/g, '!!')
        strReplace(s, "\x87\x60");
        strReplace(s, "\x87\x5f");
        buffer->from(s);
    }
    void PCSG00472(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "\x81\x55", "!?");
        strReplace(s, "\x81\x54", "!!");
        strReplace(s, "\x81\x40");
        s = re::sub(s, "(#n)+");
        s = re::sub(s, "#[A-Za-z]+\\[(\\d*[.,])?\\d+\\]");
        buffer->from(s);
    }
    void PCSG00272(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if ((!startWith(s, "#n#")) && (s.find("#n#") != s.npos))
        {
            strReplace(s, "#n#", "\x81\x7a#");
            s = "\x81\x79" + s;
        }
        buffer->from(s);
        PCSG00472(buffer, hp);
    }
    void FPCSG00389(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "[\\s]");
        s = re::sub(s, "(#n)+");
        s = re::sub(s, "#[A-Za-z]+\\[(\\d*[.,])?\\d+\\]");
        buffer->from(s);
    }
    void FPCSG00405(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, "[\\s]");
        buffer->from(s);
    }
    void PCSG00172(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"Mﾚ      　ｰ_Mﾚ  ���");
        strReplace(ws, L"u_");
        strReplace(ws, L"ata/data4.dat");
        strReplace(ws, L":data/data4.dat");
        strReplace(ws, L"@");
        strReplace(ws, L"�");
        strReplace(ws, L"∥pp0:d");
        strReplace(ws, L"app0:d:d");
        buffer->fromWA(ws);
    }
    void PCSG00776(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"\x02");
        Trim(ws);
        buffer->fromWA(ws);
    }
    void PCSG00769(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[hp->offset];
        while (true)
        {
            while (*(BYTE *)address)
                address -= 1;
            while (!((*(BYTE *)address) && (*(BYTE *)(1 + address))))
                address += 1;
            if (*(BYTE *)(address - 2))
                address -= 2;
            else
                break;
        }
        std::string collect;
        while (*(BYTE *)address)
        {
            std::string sub = (char *)address;
            collect += sub;
            address += sub.size() + 1;
        }
        strReplace(collect, "\x87\x85", "\x81\x5c");
        strReplace(collect, "\x87\x86", "\x81\x5c");
        strReplace(collect, "\x87\x87", "\x81\x5c");
        strReplace(collect, "\x81\x40");
        strReplace(collect, "\n");
        buffer->from(collect);
    }
    void PCSB00985(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[hp->offset];
        std::wstring str = (WCHAR *)address;
        auto istext = re::search(str, LR"([ \n\.\?!,"'—;:])");
        *split = bool(istext) && (str != L"????");
        str = re::sub(str, LR"(\$\w\[(.*?)\])");
        strReplace(str, L"\n", L" ");
        buffer->from(str);
    }
    void PCSG01046(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto len = (*(DWORD *)(VITA3K::emu_arg(context)[0] + 8)) * 2;
        auto pre = VITA3K::emu_arg(context)[0] + 0xC;
        buffer->from(pre, len);
        StringFilter(buffer, TEXTANDLEN(L"<br>"));
    }
    void PCSG01011(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[7];
        while (*(char *)(address - 1))
            address -= 1;
        buffer->from((char *)address);
        static std::string last;
        auto s = buffer->strA();
        if (s == last)
        {
            buffer->clear();
            last = s;
        }
        else
        {
            last = s;
            strReplace(s, "\n");
            auto pos = s.find(u8"×");
            if (pos != s.npos)
                s = s.substr(pos + strlen(u8"×"));
            buffer->from(s);
        }
    }
    namespace Corda
    {
        std::string readBinaryString(uintptr_t address, bool *haveName)
        {
            *haveName = false;
            if ((*(WORD *)address & 0xF0FF) == 0x801b)
            {
                *haveName = true;
                address = address + 2; // (1)
            }
            std::string s;
            int i = 0;
            uint8_t c;
            if (*(BYTE *)(address + i) == 0xaa)
                i += 1;

            while (true)
            {
                c = *(uint8_t *)(address + i);
                if (!c)
                {
                    if (*(uint8_t *)(address + i + 1) == 0xaa)
                        i += 2;
                    else
                        break;
                }
                else if (c == 0x1b)
                {
                    if (*haveName)
                        return s; // (1) skip junk after name

                    c = *(uint8_t *)(address + (i + 1));
                    if (c == 0x7f)
                        i += 5;
                    else if (c == 0xb4) // 下天の華 夢灯り //NPJH50864
                        i += 6;
                    else
                        i += 2;
                }
                else if (c == 0x0a)
                {
                    s += '\n';
                    i += 1;
                }
                else if (c == 0x20)
                {
                    s += ' ';
                    i += 1;
                }
                else
                {
                    auto len = 1 + (IsShiftjisLeadByte(*(BYTE *)(address + i)));
                    s += std::string((char *)(address + i), len);
                    i += len; // encoder.encode(c).byteLength;
                }
            }
            return s;
        }
    }
    void PCSG01245(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[hp->offset];
        bool haveNamve;
        auto s = Corda::readBinaryString(address, &haveNamve);
        *split = haveNamve;
        buffer->from(s);
    }
    void PCSG00912(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = VITA3K::emu_arg(context)[1];
        std::string final_string = "";
        BYTE pattern[] = {0x47, 0xff, 0xff};
        auto results = MemDbg::findBytes(pattern, sizeof(pattern), address, address + 0x50);
        if (!results)
            return;

        address = results + 5;

        while (true)
        {
            std::string text = (char *)address;
            final_string += text;
            address = address + (text.size() + 1);

            auto bytes = (BYTE *)address;

            if (!(bytes[0] == 0x48 && bytes[1] == 0xFF && bytes[2] == 0xFF))
                break;
            address = address + (3);
            bytes = (BYTE *)address;
            if (!(bytes[0] == 0x47 && bytes[1] == 0xFF && bytes[2] == 0xFF))
                break;

            address = address + (5);
        }
        buffer->from(final_string);
    }
    void TPCSG00291(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto a2 = VITA3K::emu_arg(context)[0];

        auto vm = *(DWORD *)(a2 + (0x28));
        vm = *(DWORD *)VITA3K::emu_addr(context, vm);
        vm = *(DWORD *)VITA3K::emu_addr(context, vm + 8);
        uintptr_t address = VITA3K::emu_addr(context, vm);
        auto len1 = *(DWORD *)(address + 4);
        auto p = address + 0x20;
        if (len1 > 4 && *(WORD *)(p + 2) == 0)
        {
            auto p1 = *(DWORD *)(address + 8);
            vm = *(DWORD *)VITA3K::emu_addr(context, vm);
            vm = *(DWORD *)VITA3K::emu_addr(context, vm + 0xC);
            p = VITA3K::emu_addr(context, vm);
        }
        static int fm = 0;
        static std::string pre;
        auto b = fm;
        auto s = [](uintptr_t address)
        {
            auto frist = *(WORD *)address;
            auto lo = frist & 0xFF; // uppercase: 41->5A
            auto hi = frist >> 8;
            if (hi == 0 && (lo > 0x5a || lo < 0x41) /* T,W,? */)
            {
                return std::string();
            }
            std::string s;
            int i = 0;
            WORD c;
            char buf[3] = {0};
            while ((c = *(WORD *)(address + i)) != 0)
            {
                // reverse endian: ShiftJIS BE => LE
                buf[0] = c >> 8;
                buf[1] = c & 0xFF;

                if (c == 0x815e /* ／ */)
                {
                    s += ' '; // single line
                }
                else if (buf[0] == 0)
                {
                    //// UTF16 LE turned BE: 5700=>0057, 3100, 3500
                    //// 4e00 6d00=>PLAYER
                    // do nothing
                    if (buf[1] == 0x4e)
                    {
                        s += "PLAYER";
                        fm++;
                    }
                }
                else
                {
                    s += buf;
                }
                i += 2;
            }
            return s;
        }(p);
        if (b > 0)
        {
            fm--;
            return;
        }
        if (s == pre)
            return;
        pre = std::move(s);
        buffer->from(pre);
    }

    void FPCSG00468(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(\\n(　)*|\\k)");
        s = re::sub(s, R"(\[|\*[^\]]+])");
        s = re::sub(s, u8"×");
        buffer->from(s);
    }
    void FPCSG00808(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(^\s+|\s+$)");
        s = re::sub(s, R"(\s*(#n)*\s*)");
        s = re::sub(s, R"(#\w+(\[.+?\])?)");
        buffer->from(s);
    }
    void F010088B01A8FC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        s = re::sub(s, R"(#\w+(\[.+?\])?)");
        s = re::sub(s, u8"　");
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void PCSG01036(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        strReplace(s, "#n");
        buffer->from(s);
    }
    void PCSG00402(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"((\x81\x40)*(#n)*(\x81\x40)*)");
        s = re::sub(s, R"(#\w+(\[.+?\])?)");
        buffer->from(s);
    }
    void FPCSG00815(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(\s*(#n)*\s*)");
        s = re::sub(s, R"(#\w+(\[.+?\])?)");
        buffer->from(s);
    }
    void PCSG01250_T(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (!startWith(s, "<text"))
            return buffer->clear();
        s = s.substr(6, s.size() - 6 - 1);
        s = re::sub(s, R"(/ruby:(.*?)&(.*?)/)", "$1");
        s = re::sub(s, R"(#n)");
        buffer->from(s);
    }
    template <int ex = 1>
    void PCSG01250_N(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        if (!startWith(s, "<name"))
            return buffer->clear();
        s = s.substr(6 + ex, s.size() - 6 - 1 - 2 * ex);
        buffer->from(s);
    }
    void PCSG01202(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(/ruby:(.*?)&(.*?)/)", "$1");
        buffer->from(s);
    }
    void PCSG01325(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(@[_\*\d\w]*)");
        buffer->from(s);
    }
    void PCSG00431(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("#n\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("#n"));
        static std::string last;
        auto s = buffer->strA();
        if (startWith(s, last))
        {
            buffer->from(s.substr(last.size()));
        }
        last = s;
    }
    void FPCSG00855(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(#n(　)*)");
        s = re::sub(s, R"(#\w.+?\])");
        buffer->from(s);
    }
    void PCSG01178(TextBuffer *buffer, HookParam *hp)
    {
        FPCSG00855(buffer, hp);
        StringFilter(buffer, TEXTANDLEN("  "));
    }
    void FPCSG00855_2_1(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, u8"Χ", u8"、");
        strReplace(s, u8"Δ", u8"。");
        strReplace(s, u8"Λ", u8"っ");
        strReplace(s, u8"《", u8"（");
        strReplace(s, u8"》", u8"）");
        strReplace(s, u8"∫", u8"「");
        strReplace(s, u8"∨", u8"」");
        strReplace(s, u8"∴", u8"『");
        strReplace(s, u8"∵", u8"』");
        strReplace(s, u8"П", u8"【");
        strReplace(s, u8"Ц", u8"】");
        buffer->from(s);
        FPCSG00855(buffer, hp);
    }
    template <int idx>
    void FPCSG00855_2(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        FPCSG00855_2_1(buffer, hp);
    }
    void FPCSG00477(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#n(\x81\x40)*)");
        s = re::sub(s, R"(#\w.+?\])");
        buffer->from(s);
    }
    void PCSG00654(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW(CP_UTF8);
        strReplace(ws, L"\\");
        strReplace(ws, L"$");
        buffer->fromWA(ws, CP_UTF8);
    }
    void FPCSG00852(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"^");
        buffer->fromWA(ws);
    }
    void PCSG00829(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        strReplace(s, L"\\n　");
        strReplace(s, L"\\n");
        s = re::sub(s, LR"(\[(.*?),\d\])");
        buffer->from(s);
    }
    template <int __>
    void PCSG00451(TextBuffer *buffer, HookParam *hp)
    {
        static int i = 0;
        if (i++ % 2 == 0)
            buffer->clear();
    }
    static std::string PCSG00535;
    void PCSG00535_1(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        PCSG00535 = std::move(buffer->strA());
        StringFilter(buffer, TEXTANDLEN("\\f"));
        StringCharReplacer(buffer, TEXTANDLEN("\\n"), '\n');
        if (last == PCSG00535)
        {
            buffer->clear();
        }
        last = PCSG00535;
    }
    void PCSG00535_2(TextBuffer *buffer, HookParam *hp)
    {
        if (buffer->viewA() == PCSG00535)
            buffer->clear();
    }
    void PCSG01114(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '@');
        StringFilterBetween(buffer, TEXTANDLEN("{"), TEXTANDLEN("}"));
    }
    void PCSG00482(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN(u8"▼"));
        CharFilter(buffer, '\n');
    }
    void PCSG01249(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("[n]"));
    }
    void PCSG00370(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("\n\x81\x40"));
        StringFilter(buffer, TEXTANDLEN("\x81\xa5"));
        StringFilter(buffer, TEXTANDLEN("\x81\x84"));
        CharFilter(buffer, '\n');
    }
    void PCSG01063(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN(u8"\n　"));
        CharFilter(buffer, '\n');
    }
    void PCSG01289(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        ws = remapkatakana(ws);
        ws = re::sub(ws, LR"(\$t(.*?)@)", L"$1");
        ws = re::sub(ws, LR"(\$\[(.*?)\$/(.*?)\$\])", L"$1");
        buffer->fromWA(ws);
    }
    void PCSG01198(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        ws = remapkatakana(ws);
        ws = re::sub(ws, LR"(`(.*?)@)", L"$1");
        ws = re::sub(ws, LR"(\$\[(.*?)\$/(.*?)\$\])", L"$1");
        buffer->fromWA(ws);
    }
    void PCSG00585(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        ws = remapkatakana(ws);
        ws = re::sub(ws, LR"(\$\[(.*?)\$/(.*?)\$\])", L"$1");
        ws = re::sub(ws, LR"(\$C\[ffffff\](.*?)@\$C\[\])", L"$1");
        strReplace(ws, L"\n");
        buffer->fromWA(ws);
    }
    void PCSG01254(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        ws = remapkatakana(ws);
        ws = re::sub(ws, LR"(@[a-zA-Z\d_\.]+)"); // 操了，wregex \w会匹配到unicode字符
        buffer->fromWA(ws);
    }
    void PCSG01196(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"^", L"\n");
        ws = re::sub(ws, LR"(<(.*?)>(.*?)|)", L"$2");
        buffer->fromWA(ws);
    }
    void PCSG00780(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"^");
        ws = re::sub(ws, LR"(<(.*?),(.*?)>)", L"$1");
        buffer->fromWA(ws);
    }
    void PCSG01151(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strAW();
        strReplace(ws, L"^");
        strReplace(ws, L"　");
        buffer->fromWA(ws);
    }
    void FPCSG01066(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, u8R"(\n(　)*)");
        buffer->from(s);
    }
    void FPCSG01075(TextBuffer *buffer, HookParam *hp)
    {
        FPCSG00808(buffer, hp);
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void PCSG01314(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(@r(.*?)@(.*?)@)", "$1");
        s = re::sub(s, R"(@[\w\d_]+)");
        buffer->from(s);
    }
    void F010052300F612000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#r(.*?)\|(.*?)#)", "$1");
        s = re::sub(s, R"(@r(.*?)@\d)", "$1");
        strReplace(s, R"(\c)");
        strReplace(s, R"(\n)");
        buffer->from(s);
    }
    void PCSG01144_1(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("@w"));
        StringFilter(buffer, TEXTANDLEN("@y"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
        auto s = buffer->strA();
        if (!startWith(s, "\x81\x79"))
            buffer->clear();
    }
    void PCSG00449(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, TEXTANDLEN("@w"));
        StringFilter(buffer, TEXTANDLEN("\x81\x40"));
        auto s = buffer->strA();
        if (!startWith(s, "\x81\x79"))
            buffer->clear();
        if (endWith(s, "@"))
            buffer->from(s.substr(0, s.size() - 1));
    }
    void PCSG01197(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(#r(.*?)\|(.*?)#)", "$1");
        strReplace(s, R"(@w)");
        buffer->from(s);
    }
    void PCSG01152(TextBuffer *buffer, HookParam *hp)
    {
        static int idx = 0;
        if (idx++ % 2 == 1)
            return buffer->clear();
        auto s = buffer->strW();
        if (startWith(s, L"<"))
            return buffer->clear();
        if (startWith(s, L"＠"))
        {
            if (s.size() == 1)
                return buffer->clear();
            s = L"【" + s.substr(1) + L"】";
        }
        buffer->from(s);
    }
    void PCSG00433(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, L'\n');
        auto s = buffer->strW();
        s = re::sub(s, LR"(<CLT \d+>(.*?)<CLT>)", L"$1");
        buffer->from(s);
    }
    void PCSG00020(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = re::sub(s, R"(<\w+?>)");
        buffer->from(s);
    }
}

struct emfuncinfoX
{
    DWORD addr;
    emfuncinfo info;
};
static const emfuncinfoX emfunctionhooks_1[] = {
    // ヴァルプルガの詩
    {0x8003345A, {0, 1, 0, 0, 0, "PCSG00768"}},
    // アブナイ☆恋の捜査室 ～Eternal Happiness～
    {0x800151A4, {CODEC_UTF16, 4, 0, 0, 0, "PCSG00591"}},
    // 絶対迷宮　秘密のおやゆび姫
    {0x800B9DEA, {0, 3, 0, 0, 0, "PCSG00611"}},
    // フォトカノ Kiss
    {0x81161B0E, {0, 0, 0, 0, NewLineCharFilterA, "PCSG00139"}},
    // POSSESSION MAGENTA
    {0x80016C76, {0, 0, 0, 0, FPCSG00852, "PCSG00509"}},
    // 極限脱出ＡＤＶ 善人シボウデス
    {0x810DE344, {CODEC_UTF8, 6, 0, 0, PCSG00020, "PCSG00020"}},
    // イケメン戦国◆時をかける恋　新たなる出逢い
    {0x8009B496, {CODEC_UTF8, 8, 0, 0, PCSG01063, "PCSG01063"}},
    // ニル・アドミラリの天秤 帝都幻惑綺譚
    {0x80073862, {0, 0, 0, 0, PCSG00766, "PCSG00766"}},
    // ニル・アドミラリの天秤 クロユリ炎陽譚
    {0x80030CC8, {0, 5, 0, 0, PCSG00766, "PCSG01014"}},
    {0x80074F2A, {0, 0, 0, 0, PCSG00766, "PCSG01014"}},
    // BROTHERS CONFLICT　Precious Baby
    {0x800B2C66, {0, 5, 0, 0, PCSG00402, "PCSG00755"}},
    {0x800B4548, {0, 1, 0, 0, PCSG00402, "PCSG00755"}},
    // CLOCK ZERO ～終焉の一秒～ ExTime
    {0x8002BA9C, {CODEC_UTF8, 0, 0, 0, FPCSG00815, "PCSG00469"}},
    // Collar×Malice
    {0x80030250, {CODEC_UTF8, 0, 0, 0, 0, "PCSG00866"}},
    // Side Kicks!
    {0x80020C78, {CODEC_UTF8, 0, 8, 0, PCSG01001, "PCSG01001"}},
    // 俺たちに翼はない
    {0x8003EC88, {0, 7, 0, 0, 0, "PCSG00299"}},
    // シルヴァリオ トリニティ -Beyond the Horizon-
    {0x800B7702, {0, 3, 0, 0, 0, "PCSG01259"}},
    // 追放選挙
    {0x8002e176, {0, 0, 0, 0, FPCSG01023, "PCSG01023"}}, // dialogue+name,sjis
    // 死神と少女
    {0x800204ba, {0, 2, 0, 0, FPCSG01282<0>, "PCSG01282"}}, // dialogueNVL,sjis
    {0x8000f00e, {0, 1, 0, 0, FPCSG01282<1>, "PCSG01282"}}, // dialogue main
    {0x80011f1a, {0, 0, 0, 0, FPCSG01282<2>, "PCSG01282"}}, // Name
    {0x8001ebac, {0, 1, 0, 0, FPCSG01282<3>, "PCSG01282"}}, // choices
    // 神凪ノ杜 五月雨綴り
    {0x828bb50c, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW, 0, "PCSG01268"}}, // dialogue
    {0x828ba9b6, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW, 0, "PCSG01268"}}, // name
    {0x8060D376, {CODEC_UTF8, 0, 0, 0, 0, "PCSG01268"}},                    // vita3k v0.2.0 can't find 0x828bb50c && 0x828ba9b6, unknown reason.
    // 参千世界遊戯 ~MultiUniverse Myself~
    {0x8005ae24, {0, 0, 0, 0, 0, "PCSG01194"}}, // dialouge+name,sjis,need remap jis char,to complex
    // Marginal #4 Road to Galaxy
    {0x8002ff90, {CODEC_UTF8, 0, 0, 0, PCSG00766, "PCSG01008"}}, // text
    // MARGINAL#4 IDOL OF SUPERNOVA
    {0x800718f8, {0, 0, 0, 0, FPCSG00448, "PCSG00448"}}, // dialogue,sjis
    // BLACK WOLVES SAGA  -Weiβ und Schwarz-
    {0x800581a2, {CODEC_UTF8, 0, 0, 0, PCSG00766, "PCSG00935"}}, // text
    {0x800644F6, {CODEC_UTF8, 8, 0, 0, PCSG00935, "PCSG00935"}},
    // New Game! The Challenge Stage!
    {0x8012674c, {CODEC_UTF8, 0, 0, TPCSG00903, FPCSG00903, "PCSG00903"}},
    // 喧嘩番長 乙女
    {0x80009722, {CODEC_UTF16, 0, 0, 0, FPCSG00839, "PCSG00829"}},
    {0x800086C0, {CODEC_UTF16, 0, 0, 0, PCSG00829, "PCSG00829"}}, // 缺少部分
    // アルカナ・ファミリア -La storia della Arcana Famiglia- Ancora
    {0x80070e30, {0, 2, 0, 0, FPCSG00751, "PCSG00751"}}, // all,sjis
    {0x80070cdc, {0, 1, 0, 0, FPCSG00751, "PCSG00751"}}, // text
    // もし、この世界に神様がいるとするならば。
    {0x80c1f270, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW, FPCSG00706, "PCSG00706"}}, // dialogue
    {0x80d48bfc, {CODEC_UTF16, 1, 0, ReadU16TextAndLenDW, FPCSG00706, "PCSG00706"}}, // Dictionary1
    {0x80d48c20, {CODEC_UTF16, 0, 0, ReadU16TextAndLenDW, FPCSG00706, "PCSG00706"}}, // Dictionary2
    // アンジェーリーク ルトゥール
    {0x8008bd1a, {0, 1, 0, 0, FPCSG00696, "PCSG00696"}}, // text1,sjis
    {0x8008cd48, {0, 0, 0, 0, FPCSG00696, "PCSG00696"}}, // text2
    {0x8008f75a, {0, 0, 0, 0, FPCSG00696, "PCSG00696"}}, // choice
    // 月に寄りそう乙女の作法
    {0x8002aefa, {0, 2, 0, 0, 0, "PCSG00648"}}, // dialogue,sjis
    // 熱血異能部活譚 Trigger Kiss
    {0x8004e44a, {0, 0, 0, 0, FPCSG00410, "PCSG00410"}}, // dialogue,sjis
    // バイナリースター
    {0x80058606, {0, 1, 0xd, 0, FPCSG00389, "PCSG00389"}}, // dialogue,sjis
    // アマガミ
    {0x80070658, {0, 0, 0, TPCSG00291, 0, "PCSG00291"}},
    // るいは智を呼ぶ
    {0x81003db0, {CODEC_UTF8, 1, 0, 0, FPCSG00839, "PCSG00216"}}, // dialogue
    // レンドフルール
    {0x8001bff2, {0, 0, 0, 0, FPCSG00405, "PCSG00405"}}, // dialogue,sjis
    // Muv-Luv
    {0x80118f10, {0, 5, 0, 0, PCSG00776, "PCSG00776"}}, // dialogue, choices
    {0x80126e7e, {0, 0, 0, 0, PCSG00776, "PCSG00776"}}, // dialogue
    // Re:BIRTHDAY SONG～恋を唄う死神～
    {0x80033af6, {0, 0, 2, 0, 0, "PCSG00911"}}, // dialogue
    // Un:BIRTHDAY SONG ～愛を唄う死神～
    {0x80038538, {0, 0, 0, PCSG00912, 0, "PCSG00912"}},
    {0x80033d66, {0, 3, 4, 0, FPCSG00912, "PCSG00912"}},
    // ソラ*ユメ
    {0x8000bad4, {0, 1, 0, 0, FPCSG00401, "PCSG00401"}},
    // 天涯ニ舞ウ、粋ナ花
    {0x8006808e, {CODEC_UTF8, 0, 0, 0, FPCSG01180, "PCSG01180"}},
    {0x80089408, {CODEC_UTF8, 0, 0, 0, FPCSG01180, "PCSG01180"}},
    // 黒蝶のサイケデリカ
    {0x80043538, {CODEC_UTF8, 1, 0, 0, FPCSG00468, "PCSG00468"}},
    // 灰鷹のサイケデリカ
    {0x80022c06, {CODEC_UTF8, 4, 0, 0, FPCSG00468, "PCSG00812"}},
    // 悠久のティアブレイド -Lost Chronicle-
    {0x8003542a, {CODEC_UTF8, 10, 0, 0, FPCSG00808, "PCSG00808"}},
    {0x8002a95a, {CODEC_UTF8, 6, 0, 0, FPCSG00808, "PCSG00808"}},
    {0x801a98aa, {CODEC_UTF8, 9, 0, 0, FPCSG00808, "PCSG00808"}},
    {0x801a42bc, {CODEC_UTF8, 9, 0, 0, FPCSG00808, "PCSG00808"}},
    {0x801a42d0, {CODEC_UTF8, 7, 0, 0, FPCSG00808, "PCSG00808"}},
    // 悠久のティアブレイド -Fragments of Memory-
    {0x80035f44, {CODEC_UTF8, 10, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x8000d868, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x8004598e, {CODEC_UTF8, 0, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x801b1d16, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x801ac31e, {CODEC_UTF8, 9, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x801ac33a, {CODEC_UTF8, 7, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x801b879a, {CODEC_UTF8, 5, 0, 0, FPCSG01075, "PCSG01075"}},
    {0x8009f570, {CODEC_UTF8, 5, 0, 0, FPCSG01075, "PCSG01075"}},
    // マジきゅんっ！ルネッサンス
    {0x8008375a, {0, 1, 0, 0, FPCSG00852, "PCSG00852"}},
    {0x8001c194, {0, 1, 0, 0, FPCSG00852, "PCSG00852"}},
    // 蝶々事件ラブソディック
    {0x8008dea2, {CODEC_UTF8, 4, 0, 0, FPCSG01066, "PCSG01066"}},
    {0x8008eb38, {CODEC_UTF8, 0, 0, 0, FPCSG01066, "PCSG01066"}},
    // 百華夜光
    {0x80032b30, {0, 8, 0, 0, 0, "PCSG00477"}},
    {0x80019c5a, {0, 5, 0, 0, 0, "PCSG00477"}},
    {0x80031a46, {0, 6, 0, 0, 0, "PCSG00477"}},
    {0x8003a49a, {0, 0, 0, 0, FPCSG00477, "PCSG00477"}},
    {0x80182532, {0, 7, 0, 0, FPCSG00477, "PCSG00477"}},
    {0x8017d1da, {0, 5, 0, 0, 0, "PCSG00477"}},
    {0x8017d478, {0, 4, 0, 0, 0, "PCSG00477"}},
    {0x8017a6aa, {0, 6, 0, 0, 0, "PCSG00477"}},
    // 花朧 ～戦国伝乱奇～
    {0x80037600, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG00855"}},
    {0x80036580, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG00855"}},
    {0x801a2ada, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<0>, "PCSG00855"}},
    {0x801a2ba8, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<1>, "PCSG00855"}},
    {0x801a2d9e, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<2>, "PCSG00855"}},
    {0x801a2e68, {CODEC_UTF8, 0, 0, 0, FPCSG00855_2<3>, "PCSG00855"}},
    // サイキックエモーション ムー
    {0x80035948, {CODEC_UTF8, 9, 0, 0, FPCSG00815, "PCSG00815"}},
    {0x80034580, {CODEC_UTF8, 6, 0, 0, FPCSG00815, "PCSG00815"}},
    // Code：Realize ～創世の姫君～
    {0x800879DE, {0, 0, 0, 0, PCSG00402, "PCSG00402"}},
    {0x8001A39A, {0, 0, 0x1c, 0, PCSG00402, "PCSG00402"}},
    // Code：Realize ～祝福の未来～
    {0x8008E566, {CODEC_UTF8, 1, 0, 0, FPCSG00815, "PCSG00805"}},
    {0x80024DE0, {CODEC_UTF8, 0xb, 0x1c, 0, FPCSG00815, "PCSG00805"}},
    // Code:Realize ～白銀の奇跡～
    {0x80015bcc, {CODEC_UTF8, 0, 0x1c, 0, F010088B01A8FC000, "PCSG01110"}},
    {0x80038e76, {CODEC_UTF8, 8, 0, 0, F010088B01A8FC000, "PCSG01110"}},
    // オメルタ CODE:TYCOON 戒
    {0x800BC462, {0, 3, 0, 0, F010088B01A8FC000, "PCSG00789"}},
    // 紅色天井艶妖綺譚 二藍
    {0x8003F554, {0, 4, 0, 0, FPCSG00852, "PCSG01221"}},
    // 絶対迷宮 秘密のおやゆび姫
    {0x8003F554, {0, 5, 0, 0, 0, "PCSG00611"}},
    // 鏡界の白雪
    {0x810286C8, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterA, "PCSG00787"}}, // VPK版手动复制安装
    {0x8002BB78, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterA, "PCSG00787"}}, // zip安装版
    {0x80025f0e, {CODEC_UTF8, 5, 0, 0, NewLineCharFilterA, "PCSG00787"}},
    {0x80141978, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00787"}},
    // ニセコイ　ヨメイリ！？
    {0x8189e60c, {CODEC_UTF8, 4, 0, 0, 0, "PCSG00397"}},
    // DIABOLIK LOVERS DARK FATE
    {0x8002CF8E, {0, 1, 0, 0, PCSG00530, "PCSG00530"}},
    // DIABOLIK LOVERS VANDEAD CARNIVAL
    {0x8007300E, {0, 5, 0, 0, PCSG00472, "PCSG00472"}},
    // DIABOLIK LOVERS LOST EDEN
    {0x8007443E, {0, 0, 0, 0, 0, "PCSG00910"}},
    // DIABOLIK LOVERS LUNATIC PARADE
    {0x800579EE, {0, 0, 0, 0, PCSG00826, "PCSG00826"}},
    // DIABOLIK LOVERS LIMITED V EDITION
    {0x8105A176, {0, 5, 0, 0, PCSG00472, "PCSG00272"}}, // prologue+text
    {0x8103416C, {0, 0, 0, 0, PCSG00272, "PCSG00272"}}, // name+text
    // DIABOLIK LOVERS MORE,BLOOD LIMITED V EDITION
    {0x800285BE, {0, 8, 0, 0, PCSG00472, "PCSG00476"}},
    {0x80033F0E, {0, 0, 0, 0, PCSG00272, "PCSG00476"}},
    // Norn9 ~Norn + Nonette~ Act Tune
    {0x8001E288, {CODEC_UTF8, 0, 0, 0, PCSG00833, "PCSG00833"}},
    // NORN9 VAR COMMONS
    {0x80019DFA, {0, 4, 0, 0, PCSG00431, "PCSG00431"}},
    {0x800338AA, {0, 0XD, 0, 0, FPCSG00855, "PCSG00431"}},
    // 空蝉の廻
    {0x82535242, {CODEC_UTF16 | USING_CHAR | DATA_INDIRECT, 1, 0, 0, 0, "PCSG01011"}}, // 后缀有人名，需要额外过滤
    {0x801AE35A, {CODEC_UTF8, 7, 0, PCSG01011, 0, "PCSG01011"}},
    // 真紅の焔 真田忍法帳
    {0x80025064, {CODEC_UTF8, 0, 0, 0, PCSG00833, "PCSG01158"}},
    // 月影の鎖　～狂爛モラトリアム～
    {0x8007AA94, {0, 1, 0, 0, F010052300F612000, "PCSG00991"}},
    // 月影の鎖　～錯乱パラノイア～
    {0x8000E8E0, {0, 0, 0, 0, F010052300F612000, "PCSG00794"}},
    // 源氏恋絵巻
    {0x8002C640, {CODEC_UTF8, 1, 0, 0, 0, "PCSG00619"}},
    // Starry☆Sky ~Spring Stories~ / Starry Sky ~Spring Stories~
    {0x8003542e, {0, 3, 0, 0, FPCSG00912, "PCSG00510"}},
    {0x80033f2e, {0, 0, 0, 0, FPCSG00912, "PCSG00510"}},
    {0x8002c5b8, {0, 0, 8, 0, FPCSG00912, "PCSG00510"}},
    // Starry☆Sky ~Summer Stories~ / Starry Sky ~Summer Stories~
    {0x80035634, {0, 3, 0, 0, FPCSG00912, "PCSG00916"}},
    {0x80034114, {0, 0, 0, 0, FPCSG00912, "PCSG00916"}},
    {0x8002c77a, {0, 0, 8, 0, FPCSG00912, "PCSG00916"}},
    // Starry☆Sky ~Autumn Stories~ / Starry Sky ~Autumn Stories~
    {0x80035b10, {0, 3, 0, 0, FPCSG00912, "PCSG00917"}}, // 1.00
    {0x800345f0, {0, 0, 0, 0, FPCSG00912, "PCSG00917"}},
    {0x8002cc56, {0, 0, 8, 0, FPCSG00912, "PCSG00917"}},
    {0x80035b2c, {0, 3, 0, 0, FPCSG00912, "PCSG00917"}}, // 1.01
    {0x8003460c, {0, 0, 0, 0, FPCSG00912, "PCSG00917"}},
    {0x8002cc72, {0, 0, 8, 0, FPCSG00912, "PCSG00917"}},
    // Starry☆Sky ~Winter Stories~ / Starry Sky ~Winter Stories~
    {0x80035a20, {0, 3, 0, 0, FPCSG00912, "PCSG00918"}},
    {0x80034500, {0, 0, 0, 0, FPCSG00912, "PCSG00918"}},
    {0x8002cb66, {0, 0, 8, 0, FPCSG00912, "PCSG00918"}},
    // ワンドオブフォーチュン R
    {0x8008128a, {CODEC_UTF8, 0, 0, 0, PCSG00917, "PCSG00917"}}, // 1.00
    {0x800345f0, {CODEC_UTF8, 0, 0, 0, PCSG00917, "PCSG00917"}},
    {0x8002cc56, {CODEC_UTF8, 8, 0, 0, PCSG00917, "PCSG00917"}},
    {0x8008134e, {CODEC_UTF8, 0, 0, 0, PCSG00917, "PCSG00917"}}, // 1.01
    {0x80081378, {CODEC_UTF8, 0, 0, 0, PCSG00917, "PCSG00917"}},
    {0x8002cb8c, {CODEC_UTF8, 8, 0, 0, PCSG00917, "PCSG00917"}},
    // ワンド オブ フォーチュン Ｒ２ ～時空に沈む黙示録～
    {0x8006c986, {CODEC_UTF8, 0, 0, 0, PCSG00938, "PCSG00938"}},
    {0x8006c9b0, {CODEC_UTF8, 0, 0, 0, PCSG00938, "PCSG00938"}},
    {0x8001a860, {CODEC_UTF8, 8, 0, 0, PCSG00938, "PCSG00938"}},
    {0x80022bd2, {CODEC_UTF8, 4, 0x14, 0, PCSG00938, "PCSG00938"}},
    {0x80022bf0, {CODEC_UTF8, 5, 0, 0, PCSG00938, "PCSG00938"}},
    // ワンド オブ フォーチュン Ｒ２ ＦＤ ～君に捧げるエピローグ～
    {0x80035B80, {CODEC_UTF8, 6, 0, 0, PCSG00855, "PCSG01208"}},
    // I DOLL U
    {0x8000AC70, {CODEC_UTF8, 0, 0, 0, PCSG00833, "PCSG00592"}}, // 需要自己替换#Name[1] #Name[2]
    {0x8000AE7E, {CODEC_UTF8, 4, 0, 0, PCSG00592, "PCSG00592"}},
    // ピリオドキューブ～鳥籠のアマデウス～
    {0x8000BDF2, {CODEC_UTF8, 5, 0, 0, PCSG00530, "PCSG00853"}},
    // 花朧 ～戦国伝乱奇～
    {0x80024C08, {CODEC_UTF8, 5, 0, 0, PCSG00592, "PCSG00855"}},
    {0x8000D544, {CODEC_UTF8, 0, 0, 0, PCSG00855, "PCSG00855"}},
    // ロミオVSジュリエット 全巻パック
    {0x80017F50, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00618"}},
    // １２時の鐘とシンデレラ～シンデレラシリーズ　トリプル全巻パック～
    {0x8001701C, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00561"}},
    // ハートの国のアリス～Wonderful Wonder World～
    {0x8100F0CA, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00614"}}, // 手动解压
    {0x800173F4, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00614"}},
    // 新装版魔法使いとご主人様～Wizard and The Master～
    {0x8001733C, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00580"}},
    // 円環のメモーリア -カケラ灯し-
    {0x80029AB2, {0, 0, 0, 0, PCSG01167, "PCSG01167"}},
    // ネオ アンジェリーク 天使の涙
    {0x8005426C, {CODEC_UTF8, 0, 0, 0, PCSG01068, "PCSG01068"}},
    // スカーレッドライダーゼクス Rev.
    {0x800BEE38, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterA, "PCSG00745"}},
    // 緋色の欠片 ～おもいいろの記憶～
    {0x8007838c, {CODEC_UTF8, 5, 0, 0, PCSG01036, "PCSG01036"}},
    {0x8001154c, {CODEC_UTF8, 8, 0, 0, PCSG01036, "PCSG01036"}},
    {0x800879ee, {CODEC_UTF8, 2, 0, 0, PCSG01036, "PCSG01036"}},
    // 嘘月シャングリラ
    {0x81e1f5c8, {CODEC_UTF16, 0, 0, PCSG01046, 0, "PCSG01046"}},
    {0x81e4a514, {CODEC_UTF16, 0, 0, PCSG01046, 0, "PCSG01046"}},
    // 罪喰い～千の呪い、千の祈り～ for V
    {0x80080cd0, {0, 0, 0, 0, 0, "PCSG01019"}},
    {0x8001c73e, {0, 1, 0, 0, 0, "PCSG01019"}},
    // LOVE:QUIZ ~恋する乙女のファイナルアンサー~
    {0x8003acba, {CODEC_UTF16, 0, 0, 0, 0, "PCSG00667"}},
    {0x80016dd6, {CODEC_UTF16, 1, 0, 0, 0, "PCSG00667"}},
    // DRAMAtical Murder
    {0x8004630a, {0, 0, 0, 0, FPCSG00852, "PCSG00420"}},
    {0x8003eed2, {0, 0, 0, 0, FPCSG00852, "PCSG00420"}},
    // GALTIA V Edition
    {0x8001B7AA, {0, 0, 0, 0, PCSG01151, "PCSG01151"}},
    // ハナヤマタ　よさこいLIVE！
    {0x810789EE, {CODEC_UTF16, 3, 0, 0, PCSG00451<1>, "PCSG00451"}},
    {0x81078B22, {CODEC_UTF16, 1, 0, 0, PCSG00451<0>, "PCSG00451"}},
    // sweet pool
    {0x8003D5B6, {0, 0, 0, 0, PCSG01196, "PCSG01196"}},
    // 学園CLUB ～ヒミツのナイトクラブ～
    {0x80029854, {0, 1, 0, 0, FPCSG00852, "PCSG01065"}},
    // 学園K -Wonderful School Days- V  Edition
    {0x80059946, {CODEC_UTF8, 5, 0, 0, PCSG00654, "PCSG00654"}},
    // 学園ヘヴン BOY'S LOVE SCRAMBLE!
    {0x80060E58, {0, 2, 0, 0, PCSG00535_1, "PCSG00535"}},
    {0x80083A94, {0, 2, 0, 0, PCSG00535_2, "PCSG00535"}},
    // 学園ヘヴン2 ～DOUBLE SCRAMBLE!～
    {0x80036616, {0, 0xc, 0, 0, PCSG00585, "PCSG00585"}},
    // デュラララ!! 3way standoff -alley- V
    {0x80053BD0, {0, 0, 0, 0, PCSG00370, "PCSG00370"}},
    // デュラララ!! Relay
    {0x80086798, {CODEC_UTF8, 1, 0, 0, PCSG00482, "PCSG00482"}},
    {0x8005F0C4, {CODEC_UTF8, 1, 0, 0, PCSG00482, "PCSG00482"}},
    // 神咒神威神楽
    {0x810a2486, {0, 0, 0, 0, PCSG00172, "PCSG00172"}},
    // ツキトモ。 TSUKIUTA. １２memories
    {0x8004D078, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterA, "PCSG01025"}},
    // アイドリッシュセブン　Twelve Fantasia!
    {0x8011E570, {CODEC_UTF8, 4, 0, 0, 0, "PCSG01094"}}, // 或0x8011e580。映射地址会发生切换，导致用特殊码搜索搜不到，且有好几个杂乱线程，但我也不想改框架了，很烦
    // VARIABLE BARRICADE
    {0x80031CDE, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG01159"}},
    {0x80038874, {CODEC_UTF8, 6, 0, 0, FPCSG00855, "PCSG01159"}},
    // ワールドエンド・シンドローム
    {0x80029E5C, {CODEC_UTF8, 4, 0, 0, PCSG01114, "PCSG01114"}},
    // 添いカノ ～ぎゅっと抱きしめて～
    {0x8007D250, {0, 0, 0, 0, PCSG01254, "PCSG01254"}},
    // アイキス
    {0x80322DDA, {CODEC_UTF8, 5, 0, 0, PCSG01325, "PCSG01325"}},
    {0x801B8F9A, {CODEC_UTF8, 5, 0, 0, PCSG01325, "PCSG01325"}},
    // スキとスキとでサンカク恋愛
    {0x80013ED6, {0, 4, 0, 0, PCSG01250_T, "PCSG01250"}},
    {0x80013EE6, {0, 4, 0, 0, PCSG01250_N, "PCSG01250"}},
    // 戦場の円舞曲
    {0x8006C08C, {0, 5, 0, 0, FPCSG00448, "PCSG00428"}},
    {0x8002B1DE, {0, 7, 0, 0, FPCSG00448, "PCSG00428"}},
    // ピオフィオーレの晩鐘
    {0x80034656, {CODEC_UTF8, 0, 0, 0, 0, "PCSG01139"}},
    // 千の刃濤、桃花染の皇姫
    {0x802D44D4, {CODEC_UTF8, 6, 0, 0, 0, "PCSG01127"}}, // 有注音时有乱码
    // Panic Palette～パニック パレット～
    {0x80010C96, {0, 0, 0, 0, PCSG01247, "PCSG01247"}},
    // ノラと皇女と野良猫ハート2
    {0x80027620, {CODEC_UTF8, 0xb, 0, PCSG01235, 0, "PCSG01235"}}, // 开头少十几句
    // IxSHE Tell
    {0x80027EB0, {CODEC_UTF8, 0xb, 0, PCSG01235, 0, "PCSG01297"}}, // 少很多句
    // NG
    {0x80063E54, {0, 0, 0, 0, PCSG01204, "PCSG01204"}},
    // Making*Lovers
    {0x808E1530, {0, 6, 0, 0, PCSG01284, "PCSG01284"}},
    // LOVE CLEAR
    {0x8031BFA2, {CODEC_UTF8, 5, 0, 0, PCSG01314, "PCSG01314"}},
    // アマツツミ
    {0x800785C8, {0, 2, 0, 0, PCSG01198, "PCSG01198"}},
    // Cafe Cuillere ～カフェ キュイエール～
    {0x8000DF58, {0, 0, 0, 0, PCSG01197, "PCSG01197"}},
    {0x800104FC, {0, 1, 0, 0, PCSG01197, "PCSG01197"}},
    // CharadeManiacs
    {0x800A0264, {CODEC_UTF8, 2, 0, 0, PCSG01150, "PCSG01150"}},
    // Collar×Malice -Unlimited-
    {0x8000D3A4, {CODEC_UTF8, 0, 0, 0, PCSG00530, "PCSG01162"}},
    // D.S.-Dal Segno-
    {0x80014AEC, {0, 0, 0, 0, 0, "PCSG01122"}},
    // ダンジョンに出会いを求めるのは間違っているだろうか インフィニト・コンバーテ
    {0x8232D5C0, {CODEC_UTF16 | FULL_STRING, 2, 0, 0, PCSG01002, "PCSG01002"}},
    // ダンジョントラベラーズ２－２ 闇堕ちの乙女とはじまりの書
    {0x800BE808, {CODEC_UTF8, 3, 0, 0, NewLineCharFilterA, "PCSG00841"}},
    // DYNAMIC CHORD feat.apple-polisher V edition
    {0x80033F6C, {0, 0, 0, 0, FPCSG00912, "PCSG00915"}},
    {0x8003C61E, {0, 0, 0, 0, FPCSG00912, "PCSG00915"}}, // prolog1
    {0x80035924, {0, 6, 0, 0, FPCSG00912, "PCSG00915"}}, // prolog2+name2
    {0x8003548C, {0, 3, 0, 0, FPCSG00912, "PCSG00915"}}, // prolog2
    // フローラル・フローラブ
    {0x80022C9C, {0, 7, 0, 0, PCSG01202, "PCSG01202"}},
    // EVE rebirth terror
    {0x80030CAA, {0, 1, 0, 0, PCSG01249, "PCSG01249"}},
    // フルキス
    {0x801B28C8, {CODEC_UTF8, 5, 0, 0, PCSG01260, "PCSG01260"}},
    {0x801B1FC0, {CODEC_UTF8, 0, 0, 0, PCSG01260_T, "PCSG01260"}},
    // アオナツライン
    {0x8031E464, {CODEC_UTF8, 5, 0, 0, PCSG01314, "PCSG01283"}},
    // 軍靴をはいた猫
    {0x800647D0, {0, 1, 0, 0, PCSG01289, "PCSG01289"}},
    // グリザイア ファントムトリガー ０３＆０４
    {0x80052EFE, {0, 4, 0, 0, PCSG01289, "PCSG01218"}},
    // かりぐらし恋愛
    {0x800444CC, {0, 0, 0, 0, PCSG00530, "PCSG01253"}},
    {0x800443B8, {0, 0, 0, 0, PCSG00530, "PCSG01253"}},
    // カタハネ -An' call Belle-
    {0x8005D784, {0, 1, 0, 0, PCSG01198, "PCSG01153"}},
    // 金色ラブリッチェ
    {0x800154CC, {0, 0, 0, 0, PCSG01250_N<0>, "PCSG01318"}},
    {0x800158B8, {0, 4, 0, 0, PCSG01250_T, "PCSG01318"}},
    // 金色のコルダ オクターヴ
    {0x80022B46, {0, 2, 0, PCSG01245, 0, "PCSG01245"}},
    // 幕末Rock 超魂
    {0x8000BF18, {0, 4, 0, 0, PCSG01247, "PCSG00425"}},
    // your diary +
    {0x800482CE, {0, 0, 0, 0, FPCSG00815, "PCSG01267"}},
    // 絶対絶望少女　ダンガンロンパ Another Episode
    {0x80086CB8, {CODEC_UTF16, 1, 0, 0, PCSG00433, "PCSG00433"}},
    // 夢現Re:Master
    {0x8000CD76, {CODEC_UTF8, 2, 0, 0, 0, "PCSG01266"}},
    // 結城友奈は勇者である　樹海の記憶
    {0x800E954E, {CODEC_UTF16, 0, 0, 0, NewLineCharFilterW, "PCSG00502"}},
    // 終わりのセラフ　運命の始まり
    {0x8028394A, {CODEC_UTF8, 4, 0, 0, NewLineCharFilterA, "PCSG00728"}},
    // Dance with Devils My Carol
    {0x82303AB0, {CODEC_UTF16, 0, 0, 0, PCSG01152, "PCSG01152"}}, // 会超前读取
    // ひめひび　-Princess Days-
    {0x80C5A6EA, {0, 4, 0, 0, PCSG01144_1, "PCSG01092"}},
    {0x80020EA0, {0, 1, 0, 0, PCSG01144, "PCSG01092"}},
    // ひめひび 続！二学期-New Princess Days!!-
    {0x815F96EA, {0, 4, 0, 0, PCSG01144_1, "PCSG01144"}},
    {0x8000D3C2, {0, 8, 0, 0, PCSG01144, "PCSG01144"}},
    // カエル畑 ＤＥ つかまえて・夏　千木良参戦！
    {0x80014488, {0, 6, 0, 0, PCSG01144_1, "PCSG00534"}},
    {0x80011E7A, {0, 0, 0, 0, 0, "PCSG00534"}},
    // カレイドイヴ
    {0x80018748, {0, 0, 0, 0, FPCSG00852, "PCSG00520"}},
    // 神々の悪戯 InFinite
    {0x8009730e, {0, 0, 0x20, PCSG00595, 0, "PCSG00595"}},
    // 神さまと恋ゴコロ
    {0x8000E47A, {0, 0, 0, 0, PCSG01144, "PCSG00449"}},
    {0x80015842, {0, 1, 0, 0, PCSG00449, "PCSG00449"}},
    // キミの瞳にヒットミー
    {0x8006080E, {0, 0, 0, 0, PCSG01254, "PCSG01087"}},
    // 古書店街の橋姫 々
    {0x8000C74A, {0, 0, 0, 0, 0, "PCSG01213"}},
    // ナデレボ！
    {0x80043D1A, {0, 0, 0, 0, PCSG01178, "PCSG01178"}},
    // 猛獣たちとお姫様 ～in blossom～
    {0x8001DD9E, {CODEC_UTF8, 0, 0, 0, 0, "PCSG01096"}},
    // クロガネ回姫譚 －閃夜一夜－
    {0x8003979C, {0, 0, 0, 0, PCSG01249, "PCSG00417"}},
    // スクール・ウォーズ～全巻パック　本編＆卒業戦線～ //PCSG00574
    // ロミオVSジュリエット 全巻パック //PCSG00618
    // スクール・ウォーズ～全巻パック　本編＆卒業戦線～ //PCSG00574
    {0x80017628, {CODEC_UTF8, 1, 0, 0, 0, std::vector<const char *>{"PCSG00574", "PCSG00618", "PCSG00574"}}},
    // 猛獣使いと王子様 ～Flower ＆ Snow～
    {0x80071E3C, {CODEC_UTF8, 0, 0, 0, FPCSG00855, "PCSG00604"}},
    {0x80080BAA, {CODEC_UTF8, 7, 0, 0, FPCSG00855, "PCSG00604"}},
    // 新装版お菓子な島のピーターパン～Sweet Never Land～
    {0x80027140, {CODEC_UTF8, 1, 0, 0, 0, "PCSG00526"}},
    // タユタマ２ -you're the only one-
    {0x8004C0CA, {0, 0, 0, 0, PCSG01203, "PCSG01203"}},
    // 戦極姫７～戦雲つらぬく紅蓮の遺志～
    {0x8276B2CE, {CODEC_UTF16, 0x9, 0, 0, PCSG01034, "PCSG01034"}},
    // 新装版クリムゾン・エンパイア
    {0x800125AE, {CODEC_UTF8, 1, 0, 0, NewLineCharFilterA, "PCSG00481"}},
    // うたの☆プリンスさまっ♪Amazing Aria & Sweet Serenade LOVE
    {0x80052B34, {0, 0, 0x24, PCSG00595, 0, "PCSG01081"}},
    // スカーレッドライダーゼクス
    {0x8000c2d4, {CODEC_UTF8, 12, 8, 0, PCSG01247, "PCSG00745"}},
    // 東京喰種トーキョーグール JAIL
    {0x800714BC, {CODEC_UTF16, 4, 0, 0, PCSG00615, "PCSG00615"}}, // 时断时续
    // PSYCHO-PASS MANDATORY HAPPINESS
    {0x8004D360, {CODEC_UTF16, 0, 0, PCSB00985, 0, "PCSB00985"}},
    // 逢魔が刻～かくりよの縁～
    {0x8003CA08, {0, 3, 0, PCSG00769, 0, "PCSG00769"}},
    // Goes!
    {0x8004D2D4, {CODEC_UTF16, 0xe, 0, 0, PCSG00367, "PCSG00367"}},
    // RE:VICE[D]
    {0x8002D4CA, {0, 0, 0, 0, PCSG00472, "PCSG00382"}},
    // SA7 -Silent Ability Seven-
    {0x800291B2, {CODEC_UTF16, 2, 0, 0, PCSG00367, "PCSG00640"}},
    {0x80045C48, {CODEC_UTF16, 1, 0, 0, PCSG00367, "PCSG00640"}},
    // 赤い砂堕ちる月
    {0x8006DF02, {0, 1, 0, 0, PCSG00780, "PCSG00780"}},
};
extern void vita3k_load_functions(std::unordered_map<DWORD, emfuncinfo> &m)
{
    for (auto i = 0; i < ARRAYSIZE(emfunctionhooks_1); i++)
    {
        m.emplace(emfunctionhooks_1[i].addr, emfunctionhooks_1[i].info);
    }
}