#include "yuzu.h"
#include "mages/mages.h"
namespace
{
    auto isFastMem = true;

    auto isVirtual = true; // Process.arch === 'x64' && Process.platform === 'windows';
    auto idxDescriptor = isVirtual == true ? 2 : 1;
    auto idxEntrypoint = idxDescriptor + 1;

    uintptr_t getDoJitAddress()
    {
        // Dynarmic::Backend::X64::EmitX64::RegisterBlock
        auto RegisterBlockSig1 = "E8 ?? ?? ?? ?? 4? 8B ?? 4? 8B ?? 4? 8B ?? E8 ?? ?? ?? ?? 4? 89?? 4? 8B???? ???????? 4? 89?? ?? 4? 8B?? 4? 89";
        auto RegisterBlock = find_pattern(RegisterBlockSig1, processStartAddress, processStopAddress);
        if (RegisterBlock)
        {
            auto beginSubSig1 = "CC 40 5? 5? 5?";
            auto lookbackSize = 0x400;
            auto address = RegisterBlock - lookbackSize;
            auto subs = find_pattern(beginSubSig1, address, address + lookbackSize);
            if (subs)
            {
                return subs + 1;
            }
        }

        auto PatchSig1 = "4????? 4????? 4????? FF?? ?? 4????? ?? 4????? 75 ?? 4????? ?? 4????? ?? 4?";
        auto Patch = find_pattern(PatchSig1, processStartAddress, processStopAddress);
        if (Patch)
        {
            auto beginSubSig1 = "4883EC ?? 48";
            auto lookbackSize = 0x80;
            auto address = Patch - lookbackSize;
            auto subs = find_pattern(beginSubSig1, address, address + lookbackSize);
            if (subs)
            {
                idxDescriptor = 1;
                idxEntrypoint = 2;
                return subs;
            }
        }
        return 0;
    }

    struct emfuncinfo
    {
        uint64_t type;
        int offset;
        int padding;
        decltype(HookParam::text_fun) hookfunc;
        decltype(HookParam::filter_fun) filterfun;
        uint64_t _id;
        const char *_version;
    };
    std::unordered_map<uint64_t, emfuncinfo> emfunctionhooks;

    struct GameInfo
    {
        std::string name{""};
        uint64_t id{0};
        std::string version{""};
    } game_info;
    bool checkiscurrentgame(const emfuncinfo &em)
    {
        if ((game_info.version.size()) && game_info.name.size() && (game_info.id != 0))
        {
            // 判断是有效的info
            auto checkversion = (em._version == 0) || (std::string(em._version) == (game_info.version));
            auto checkid = em._id == game_info.id;
            return checkid && checkversion;
        }
        else
        {
            // 加载游戏后在hook，没有办法获取id。
            // 标题里没有id，只有version，没啥必要判断了，直接true得了。
            return true;
        }
    }
}
std::string ull2hex(uint64_t u)
{
    std::stringstream num;
    num << std::uppercase
        << std::hex
        << std::setw(16)
        << std::setfill('0')
        << u;
    return num.str();
}
bool Hook_Network_RoomMember_SendGameInfo()
{
    // void RoomMember::SendGameInfo(const GameInfo& game_info) {
    //     room_member_impl->current_game_info = game_info;
    //     if (!IsConnected())
    //         return;

    //     Packet packet;
    //     packet.Write(static_cast<u8>(IdSetGameInfo));
    //     packet.Write(game_info.name);
    //     packet.Write(game_info.id);
    //     packet.Write(game_info.version);
    //     room_member_impl->Send(std::move(packet));
    // }
    BYTE pattern[] = {
        0x49, 0x8B, XX,
        0x0F, 0xB6, 0x81, 0x28, 0x01, 0x00, 0x00,
        0x90,
        0x3C, 0x02,
        0x74, 0x1C,
        0x0F, 0xB6, 0x81, 0x28, 0x01, 0x00, 0x00,
        0x90,
        0x3C, 0x03,
        0x74, 0x10,
        0x0F, 0xB6, 0x81, 0x28, 0x01, 0x00, 0x00,
        0x90,
        0x3C, 0x04,
        0x0F, 0x85, XX4};
    for (auto addr : Util::SearchMemory(pattern, sizeof(pattern), PAGE_EXECUTE, processStartAddress, processStopAddress))
    {
        addr = MemDbg::findEnclosingAlignedFunction_strict(addr, 0x100);
        // 有两个，但另一个离起始很远
        if (addr == 0)
            continue;
        HookParam hp;
        hp.address = addr;
        hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
        {
            // void __fastcall Network::RoomMember::SendGameInfo(
            //     Network::RoomMember *this,
            //     const AnnounceMultiplayerRoom::GameInfo *game_info)
            game_info = *(GameInfo *)context->rdx;
            if (game_info.id)
            {
                HostInfo(HOSTINFO::EmuGameName, "%s %s %s", game_info.name.c_str(), ull2hex(game_info.id).c_str(), game_info.version.c_str());
            }
            jitaddrclear();
        };
        return NewHook(hp, "yuzuGameInfo");
    }
    return false;
}
namespace
{
    void trygetgameinwindowtitle()
    {
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
            if (game.size())
            {
                return HostInfo(HOSTINFO::EmuGameName, WideStringToString(game).c_str());
            }
        }
    }
}
bool yuzu::attach_function()
{
    ConsoleOutput("[Compatibility] Yuzu 1616+");
    auto DoJitPtr = getDoJitAddress();
    if (!DoJitPtr)
        return false;
    trygetgameinwindowtitle();
    Hook_Network_RoomMember_SendGameInfo();
    spDefault.isjithook = true;
    spDefault.minAddress = 0;
    spDefault.maxAddress = -1;
    HookParam hp;
    hp.address = DoJitPtr;
    hp.text_fun = [](hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto descriptor = context->argof(idxDescriptor + 1); // r8
        auto entrypoint = context->argof(idxEntrypoint + 1); // r9
        auto em_address = *(uint64_t *)descriptor;
        if (!entrypoint)
            return;
        jitaddraddr(em_address, entrypoint, JITTYPE::YUZU);
        [&]()
        {
            if (emfunctionhooks.find(em_address) == emfunctionhooks.end())
                return;
            auto op = emfunctionhooks.at(em_address);
            if (!(checkiscurrentgame(op)))
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
            hpinternal.jittype = JITTYPE::YUZU;
            NewHook(hpinternal, ull2hex(op._id).c_str());
        }();
        delayinsertNewHook(em_address);
    };
    return NewHook(hp, "YuzuDoJit");
}

namespace
{
    int readu8(BYTE *addr)
    {
        int numBytes = 0;
        auto firstByte = *addr;
        if (firstByte <= 0x7F)
        {
            numBytes = 1;
        }
        else if ((firstByte & 0xE0) == 0xC0)
        {
            numBytes = 2;
        }
        else if ((firstByte & 0xF0) == 0xE0)
        {
            numBytes = 3;
        }
        else if ((firstByte & 0xF8) == 0xF0)
        {
            numBytes = 4;
        }
        return numBytes;
    }
    void T010012A017F18000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[2];
        std::string s, bottom;
        uint32_t c;
        while (true)
        {
            c = *(BYTE *)(address);
            if (c == 0)
                break;
            if (c >= 0x20)
            {
                auto l = readu8((BYTE *)address);
                s += std::string((char *)address, l);
                address += l;
            }
            else
            {
                address += 1;
                if (c == 1)
                {
                    bottom = "";
                    while (true)
                    {
                        auto l = readu8((BYTE *)address);
                        auto ss = std::string((char *)address, l);
                        address += l;
                        if (ss[0] < 0xa)
                            break;
                        bottom += ss;
                        s += ss;
                    }
                }
                else if (c == 3)
                {
                    while (true)
                    {
                        auto l = readu8((BYTE *)address);
                        auto ss = std::string((char *)address, l);
                        address += l;
                        if (ss[0] < 0xa)
                            break;
                    }
                }
                else if (c == 7)
                {
                    address += 1;
                }
                else if (c == 0xa)
                {
                    return;
                }
                else if (c == 0xd)
                {
                    c = *(uint32_t *)address;
                    auto count = c & 0xFF;
                    c = c & 0xFFFFFF00;
                    if (c == 0x0692c500)
                    {
                        for (int _ = 0; _ < count; _++)
                            s += '-';
                        address += 4;
                    }
                }
            }
        }
        buffer->from(s);
    }

    void ReadTextAndLenDW(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[hp->offset];
        buffer->from(address + 0x14, (*(DWORD *)(address + 0x10)) * 2);
    }

    void ReadTextAndLenW(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[hp->offset];
        buffer->from(address + 0x14, (*(WORD *)(address + 0x10)) * 2);
    }
    void mages_readstring(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto s = mages::readString(YUZU::emu_arg(context)[0], hp->offset);
        buffer->from(s);
    }

    void F0100A3A00CC7E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(^\`([^\@]+).)"), L"$1: ");
        s = std::regex_replace(s, std::wregex(LR"(\$[A-Z]\d*(,\d*)*)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\$\[([^$]+)..([^$]+)..)"), L"$1");
        buffer->from(s);
    }

    void F010045C0109F2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#[^\]]*\])"), "");
        s = std::regex_replace(s, std::regex(R"(#[^n]*n)"), "");
        s = std::regex_replace(s, std::regex(u8"　"), "");
        s = std::regex_replace(s, std::regex(u8R"(Save[\s\S]*データ)"), "");
        buffer->from(s);
    }

    void F0100A1E00BFEA000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"(.+? \")"), L"");
        s = std::regex_replace(s, std::wregex(L"(\",.*)"), L"");
        s = std::regex_replace(s, std::wregex(L"(\" .*)"), L"");
        buffer->from(s);
    }

    void F0100A1200CA3C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\$d"), L"\n");
        s = std::regex_replace(s, std::wregex(L"＿"), L" ");
        s = std::regex_replace(s, std::wregex(L"@"), L" ");
        s = std::regex_replace(s, std::wregex(L"\\[([^\\/\\]]+)\\/[^\\/\\]]+\\]"), L"$1");
        s = std::regex_replace(s, std::wregex(L"[~^$❝.❞'?,(-)!—:;-❛ ❜]"), L"");
        s = std::regex_replace(s, std::wregex(L"[A-Za-z0-9]"), L"");
        s = std::regex_replace(s, std::wregex(L"^\\s+"), L"");
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        buffer->from(s);
    }

    void F0100F6A00A684000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        auto r = std::regex("(?=@.)");
        std::sregex_token_iterator it(s.begin(), s.end(), r, -1);
        std::sregex_token_iterator end;
        std::vector<std::string> parts(it, end);
        s = "";
        for (auto part : parts)
        {
            if (startWith(part, "@") == false)
            {
                s += part;
                continue;
            }
            std::string tag = part.substr(0, 2);
            std::string content = part.substr(2);
            if (tag == "@r")
            {
                if (s == "")
                    s = content;
                else
                    s += '\n' + content;
            }
            else if (tag == "@u" || tag == "@v" || tag == "@w" || tag == "@o" || tag == "@a" || tag == "@z" || tag == "@c" || tag == "@s")
            {
                auto splited = strSplit(content, ".");
                if (splited.size() == 2)
                    s += splited[1];
            }
            else if (tag == "@b")
            {
            }
            else
            {
                s += content;
            }
        }
        static auto katakanaMap = std::map<std::wstring, std::wstring>{
            {L"｢", L"「"}, {L"｣", L"」"}, {L"ｧ", L"ぁ"}, {L"ｨ", L"ぃ"}, {L"ｩ", L"ぅ"}, {L"ｪ", L"ぇ"}, {L"ｫ", L"ぉ"}, {L"ｬ", L"ゃ"}, {L"ｭ", L"ゅ"}, {L"ｮ", L"ょ"}, {L"ｱ", L"あ"}, {L"ｲ", L"い"}, {L"ｳ", L"う"}, {L"ｴ", L"え"}, {L"ｵ", L"お"}, {L"ｶ", L"か"}, {L"ｷ", L"き"}, {L"ｸ", L"く"}, {L"ｹ", L"け"}, {L"ｺ", L"こ"}, {L"ｻ", L"さ"}, {L"ｼ", L"し"}, {L"ｽ", L"す"}, {L"ｾ", L"せ"}, {L"ｿ", L"そ"}, {L"ﾀ", L"た"}, {L"ﾁ", L"ち"}, {L"ﾂ", L"つ"}, {L"ﾃ", L"て"}, {L"ﾄ", L"と"}, {L"ﾅ", L"な"}, {L"ﾆ", L"に"}, {L"ﾇ", L"ぬ"}, {L"ﾈ", L"ね"}, {L"ﾉ", L"の"}, {L"ﾊ", L"は"}, {L"ﾋ", L"ひ"}, {L"ﾌ", L"ふ"}, {L"ﾍ", L"へ"}, {L"ﾎ", L"ほ"}, {L"ﾏ", L"ま"}, {L"ﾐ", L"み"}, {L"ﾑ", L"む"}, {L"ﾒ", L"め"}, {L"ﾓ", L"も"}, {L"ﾔ", L"や"}, {L"ﾕ", L"ゆ"}, {L"ﾖ", L"よ"}, {L"ﾗ", L"ら"}, {L"ﾘ", L"り"}, {L"ﾙ", L"る"}, {L"ﾚ", L"れ"}, {L"ﾛ", L"ろ"}, {L"ﾜ", L"わ"}, {L"ｦ", L"を"}, {L"ﾝ", L"ん"}, {L"ｰ", L"ー"}, {L"ｯ", L"っ"}, {L"､", L"、"}, {L"ﾟ", L"？"}, {L"ﾞ", L"！"}, {L"･", L"…"}, {L"?", L"　"}, {L"｡", L"。"}, {L"\uF8F0", L""}, {L"\uFFFD", L""} // invalid (shift_jis A0 <=> EF A3 B0) | FF FD - F8 F0)
        };

        auto remap = [](std::string &s)
        {
            std::wstring result;
            auto ws = StringToWideString(s, 932).value();
            for (auto _c : ws)
            {
                std::wstring c;
                c.push_back(_c);
                if (katakanaMap.find(c) != katakanaMap.end())
                {
                    result += katakanaMap[c];
                }
                else
                    result += c;
            }
            return WideStringToString(result, 932);
        };
        buffer->from(remap(s));
    }
    void F01006590155AC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        auto r = std::regex("(?=@.)");
        std::sregex_token_iterator it(s.begin(), s.end(), r, -1);
        std::sregex_token_iterator end;

        std::vector<std::string> parts(it, end);
        s = "";
        int counter = 0;
        while (counter < parts.size())
        {
            std::string part = parts[counter];
            if (part[0] != '@')
            {
                s += part;
                counter++;
                continue;
            }
            std::string tag = part.substr(0, 2);
            std::string content = part.substr(2);
            if (tag == "@s" || tag == "@t")
            {
                s += content.substr(4);
                counter++;
                continue;
            }
            else if (tag == "@m")
            {
                s += content.substr(2);
                counter++;
                continue;
            }
            else if (tag == "@n")
            {
                s += '\n' + content;
                counter++;
                continue;
            }
            else if (tag == "@b" || tag == "@a" || tag == "@p" || tag == "@k")
            {
                s += content;
                counter++;
                continue;
            }
            else if (tag == "@v" || tag == "@h")
            {
                s += std::regex_replace(content, std::regex("[\\w_-]+"), "");
                counter++;
                continue;
            }
            else if (tag == "@r")
            {
                s += content + parts[counter + 2].substr(1);
                counter += 3;
                continue;
            }
            else if (tag == "@I")
            {
                if (content == "@" || parts[counter + 1].substr(0, 2) == "@r")
                {
                    counter++;
                    continue;
                }
                s += std::regex_replace(content, std::regex(u8"[\\d+─]"), "");
                counter += 3;
                continue;
            }
            else
            {
                s += content;
                counter++;
                continue;
            }
        }
        buffer->from(s);
    }
    void F01000200194AE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string readString_savedSentence = "";
        static bool readString_playerNameFlag = false;
        static std::string readString_playerName = u8"ラピス";
        auto r = std::regex("(?=@.)");
        std::sregex_token_iterator it(s.begin(), s.end(), r, -1);
        std::sregex_token_iterator end;

        std::vector<std::string> parts(it, end);
        s = "";
        size_t counter = 0;

        while (counter < parts.size())
        {
            const std::string &part = parts[counter];

            if (part.empty() || part[0] != '@')
            {
                s += part;
                counter++;
                continue;
            }

            std::string tag = part.substr(0, 2);
            std::string content = part.substr(2);

            if (tag == "@*")
            {
                if (content.find("name") == 0)
                {
                    if (readString_playerName == u8"ラピス")
                    {
                        s += content.substr(4) + readString_playerName + parts[counter + 4].substr(1);
                    }
                    else
                    {
                        s += content.substr(4) + parts[counter + 3].substr(1) + parts[counter + 4].substr(1);
                    }
                    counter += 5;
                    continue;
                }
            }
            else if (tag == "@s" || tag == "@t")
            {
                s += content.substr(4);
                counter++;
                continue;
            }
            else if (tag == "@m")
            {
                s += content.substr(2);
                counter++;
                continue;
            }
            else if (tag == "@u")
            {
                readString_playerNameFlag = true;
                readString_savedSentence = "";
                counter++;
                return buffer->clear();
            }
            else if (tag == "@n" || tag == "@b" || tag == "@a" || tag == "@p" || tag == "@k")
            {
                s += content;
                counter++;
                continue;
            }
            else if (tag == "@v" || tag == "@h")
            {
                s += std::regex_replace(content, std::regex("[\\w_-]+"), "");
                counter++;
                continue;
            }
            else if (tag == "@r")
            {
                s += content + parts[counter + 2].substr(1);
                counter += 3;
                continue;
            }
            else if (tag == "@I")
            {
                if (content == "@" || parts[counter + 1].substr(0, 2) == "@r")
                {
                    counter++;
                    continue;
                }
                s += std::regex_replace(content, std::regex(u8"[\\d+─]"), "");
                counter += 3;
                continue;
            }
            else
            {
                s += content;
                counter++;
                continue;
            }
        }

        if (!readString_playerNameFlag)
        {
            ;
        }
        else if (readString_savedSentence.empty())
        {
            readString_savedSentence = s;
            s = "";
        }
        else
        {
            std::string savedSentence = readString_savedSentence;
            readString_playerNameFlag = false;
            readString_savedSentence = "";
            readString_playerName = s;
            s = s + "\n" + savedSentence;
        }
        buffer->from(s);
    }
    void F0100EA001A626000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        if (s == L"　　")
        {
            return buffer->clear();
        }
        s = std::regex_replace(s, std::wregex(L"\n+"), L" ");

        s = std::regex_replace(s, std::wregex(L"\\$\\{FirstName\\}"), L"ナーヤ");

        if (startWith(s, L"#T"))
        {
            s = std::regex_replace(s, std::wregex(L"#T2[^#]+"), L"");
            s = std::regex_replace(s, std::wregex(L"#T\\d"), L"");
        }
        buffer->from(utf16_to_utf32(s));
    }
    void F010093800DB1C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(L"\\n+"), L" ");
        s = std::regex_replace(s, std::wregex(L"\\$\\{FirstName\\}"), L"シリーン");
        if (startWith(s, L"#T"))
        {
            s = std::regex_replace(s, std::wregex(L"\\#T2[^#]+"), L"");
            s = std::regex_replace(s, std::wregex(L"\\#T\\d"), L"");
        }
        buffer->from(utf16_to_utf32(s));
    }
    void F0100F7E00DFC8000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L" ");
        s = std::regex_replace(s, std::wregex(L"#KW"), L"");
        s = std::regex_replace(s, std::wregex(L"#C\\(TR,0xff0000ff\\)"), L"");
        s = std::regex_replace(s, std::wregex(L"#P\\(.*\\)"), L"");
        buffer->from(utf16_to_utf32(s));
    }

    void F0100982015606000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\n+|(\\\\n)+"), L" ");
        buffer->from(s);
    }
    void F0100C4E013E5E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\\\n"), L" ");
        buffer->from(s);
    }

    void F01004EB01A328000(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, "#n", 2);
        char name[] = u8"雪村";
        StringReplacer(buffer, "#Name[1]", 8, name, strlen(name));
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#Color\[\d+?\])"), "");
        buffer->from(s);
    }
    void F0100CF90151E0000(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = StringToWideString(buffer->viewA(), 932).value();
        strReplace(ws, L"^", L"");
        ws = std::regex_replace(ws, std::wregex(LR"(@c\d)"), L"");
        ws = std::regex_replace(ws, std::wregex(LR"(@v\(\d+\))"), L"");
        buffer->from(WideStringToString(ws, 932));
    }
    void F010052300F612000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#r(.*?)\|(.*?)#)"), "$1");
        strReplace(s, R"(\c)", "");
        strReplace(s, R"(\n)", "");
        buffer->from(s);
    }
    template <int _1>
    void F010053F0128DC000(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        auto s = buffer->strA();
        char __[] = "$1";
        __[1] += _1 - 1;
        s = std::regex_replace(s, std::regex(R"(<CLY2>(.*?)<CLNA>([\s\S]*))"), __);
        buffer->from(s);
    }
    namespace
    {
        static std::string F0100FB50156E6000;
        void F0100FB50156E6000_1(TextBuffer *buffer, HookParam *hp)
        {
            auto s = buffer->strA();
            s = std::regex_replace(s, std::regex(R"(@v\(\d+\))"), "");
            F0100FB50156E6000 = s;
            s = std::regex_replace(s, std::regex("@r(.*?)@(.*?)@"), "$1");
            s = std::regex_replace(s, std::regex("@n"), "");
            buffer->from(s);
        }
        void F0100FB50156E6000_2(TextBuffer *buffer, HookParam *hp)
        {
            auto s = buffer->viewA();
            if (s == F0100FB50156E6000)
                return buffer->clear();
        }
    }
    void F010001D015260000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewA();
        if (startWith(s, "#Key"))
            return buffer->clear();
        StringFilter(buffer, "#n", 2);
    }
    void F0100E1E00E2AE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("#n"), "\n");
        s = std::regex_replace(s, std::regex("[A-Za-z0-9]"), "");
        s = std::regex_replace(s, std::regex("[~^,\\-\\[\\]#]"), "");
        buffer->from(s);
    }
    void F0100DE200C0DA000(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, "#n", 2, " ", 1);
        StringReplacer(buffer, "\n", 1, " ", 1);
    }
    void F0100AEC013DDA000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string ss;
        if (ss == s)
            return buffer->clear();
        ss = std::move(s);
    }

    void F0100F7801B5DC000(TextBuffer *buffer, HookParam *hp)
    {
        if (!all_ascii((wchar_t *)buffer->buff, buffer->size / 2))
            return buffer->clear(); // chaos on first load.
        StringReplacer(buffer, L"<br>", 4, L"\n", 1);
    }

    void F01006CC015ECA000(TextBuffer *buffer, HookParam *hp)
    {
        StringCharReplacer(buffer, L"#<br>", 5, L'\n');
    }
    void F0100925014864000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("(#n)+"), " ");
        s = std::regex_replace(s, std::regex("(#[A-Za-z]+\\[(\\d*[.])?\\d+\\])+"), "");
        buffer->from(s);
    }

    void F0100936018EB4000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(L"<[^>]+>"), L"");
        s = std::regex_replace(s, std::wregex(L"\n+"), L" ");
        buffer->from(utf16_to_utf32(s));
    }
    void T01000BB01CB8A000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[hp->offset];
        std::wstring s;
        while (auto c = *(uint16_t *)address)
        {
            if (c == 0x0 || c == 0xcccc)
            {
                break;
            }
            else if (c == 0xa || c == 0xd)
                ;
            else
            {
                s += c;
            }
            address += 4;
        }
        buffer->from(s);
    }
    std::unordered_map<std::wstring, std::wstring> T0100DEF01D0C6000_dict;

    void T0100DEF01D0C6000_2(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address1 = YUZU::emu_arg(context)[0] + 0x14;
        auto address2 = YUZU::emu_arg(context)[1] + 0x14;
        auto word = std::wstring((wchar_t *)address1);
        auto meaning = std::wstring((wchar_t *)address2);
        T0100DEF01D0C6000_dict[word] = meaning;
    }
    void T010061300DF48000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address1 = YUZU::emu_arg(context)[0];
        auto address2 = YUZU::emu_arg(context)[1];
        auto word = std::string((char *)address1);
        word = std::regex_replace(word, std::regex(R"(\w+\.\w+)"), "");
        while (!(*(BYTE *)address2))
            address2 += 1;
        auto meaning = std::string((char *)address2);
        meaning = std::regex_replace(meaning, std::regex(R"(%\w+)"), "");
        auto s = word + '\n' + meaning;
        buffer->from(s);
    }

    void T0100B0100E26C000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[hp->offset];
        if (hp->padding == 2)
            address += 0xA;
        auto length = (*(DWORD *)(address + 0x10)) * 2;
        buffer->from(address + 0x14, length);
    }

    void F010045C014650000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"((@(\/)?[a-zA-Z#](\(\d+\))?|)+|[\*<>]+)"), "");
        buffer->from(s);
    }

    void F0100AB100E2FA000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\n)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(<[^>]*>)"), L"");
        buffer->from(s);
    }
    void F0100B5801D7CE000(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, LR"(\n)", 2);
    }
    void F01008C0016544000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]+>"), L" ");
        buffer->from(s);
    }
    void F0100FB7019ADE000(TextBuffer *buffer, HookParam *hp)
    {
        static int idx = 0;
        if ((idx++) % 2)
            buffer->clear();
    }
    void F01006F000B056000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\[.*?\\]"), L" ");
        buffer->from(s);
    }
    void F010019C0155D8000_1(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->viewW();
        if (ws.find(L"@n") != ws.npos)
            buffer->clear();
    }
    void F010019C0155D8000_2(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = buffer->strW();
        if (ws.find(L"@n") == ws.npos)
            buffer->clear();
        else
        {
            strReplace(ws, L"@n", L"");
            strReplace(ws, L"%dts", L"");
            strReplace(ws, L"%dte", L"");
            ws = std::regex_replace(ws, std::wregex(LR"(%rbs(.*?)\{(.*?)\}%rbe)"), L"$1");
            buffer->from(ws);
        }
    }
    void F0100068019996000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("%N"), "\n");
        buffer->from(s);
    }
    void F0100ADC014DA0000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[~^$(,)]"), L"");
        s = std::regex_replace(s, std::wregex(L"[A-Za-z0-9]"), L"");
        s = std::regex_replace(s, std::wregex(L"@"), L" ");
        s = std::regex_replace(s, std::wregex(L"^\\s+"), L"");
        buffer->from(s);
    }
    void F0100AFA01750C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"((\\n)+)"), " ");
        s = std::regex_replace(s, std::regex(R"(\\d$|^\@[a-z]+|#.*?#|\$)"), "");
        buffer->from(s);
    }
    void F0100C1E0102B8000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("#N"), "\n");
        s = std::regex_replace(s, std::regex("#Color\\[[\\d]+\\]"), "");
        buffer->from(s);
    }
    void F0100BD700E648000(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, "*", 1, " ", 1);
        StringReplacer(buffer, u8"ゞ", sizeof(u8"ゞ"), u8"！？", sizeof(u8"！？"));
    }
    void F0100D9500A0F6000(TextBuffer *buffer, HookParam *hp)
    {
        StringReplacer(buffer, u8"㊤", sizeof(u8"㊤"), u8"―", sizeof(u8"―"));
        StringReplacer(buffer, u8"㊥", sizeof(u8"㊥"), u8"―", sizeof(u8"―"));
        StringReplacer(buffer, u8"^㌻", sizeof(u8"^㌻"), u8" ", sizeof(u8" ")); // \n
    }

    void F0100DA201E0DA000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        buffer->from(s);
    }
    void F01002C0008E52000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("(YUR)"), u8"ユーリ");
        s = std::regex_replace(s, std::regex("(FRE)"), u8"フレン");
        s = std::regex_replace(s, std::regex("(RAP)"), u8"ラピード");
        s = std::regex_replace(s, std::regex("(EST|ESU)"), u8"エステル");
        s = std::regex_replace(s, std::regex("(KAR)"), u8"カロル");
        s = std::regex_replace(s, std::regex("(RIT)"), u8"リタ");
        s = std::regex_replace(s, std::regex("(RAV|REI)"), u8"レイヴン");
        s = std::regex_replace(s, std::regex("(JUD)"), u8"ジュディス");
        s = std::regex_replace(s, std::regex("(PAT)"), u8"パティ");
        s = std::regex_replace(s, std::regex("(DUK|DYU)"), u8"デューク");
        s = std::regex_replace(s, std::regex("[A-Za-z0-9]"), "");
        s = std::regex_replace(s, std::regex("[,(-)_]"), "");
        s = std::regex_replace(s, std::regex("^\\s+"), "");
        while (std::regex_search(s, std::regex("^\\s*$")))
        {
            s = std::regex_replace(s, std::regex("^\\s*$"), "");
        }
        buffer->from(s);
    }

    void F01005940182EC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\s"), L"");
        s = std::regex_replace(s, std::wregex(L"<color=.*?>(.*?)<\\/color>"), L"$1");
        buffer->from(s);
    }
    void F0100AE90109A2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        static std::wstring last;
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        s = std::regex_replace(s, std::wregex(LR"(%co[\de])"), L"");
        buffer->from(s);
    }
    void F010015600D814000(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, L"\\n", 2);
        auto s = buffer->viewW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void F0100B0601852A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void F010027100C79A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->viewA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void F010027400BD24000(TextBuffer *buffer, HookParam *hp)
    {
        static int i = 0;
        if (i++ % 2)
            return buffer->clear();
        CharFilter(buffer, '\n');
    }
    void F010027400BD24000_1(TextBuffer *buffer, HookParam *hp)
    {
        CharFilter(buffer, '\n');
        if (buffer->buff[0] == 0x2a || buffer->buff[0] == 0x24 || buffer->buff[0] == 0x18)
        {
            memmove(buffer->buff, buffer->buff + 1, buffer->size - 1);
            buffer->size -= 1;
        }
    }
    void F0100FD4016528000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (endWith(last, s))
        {
            buffer->clear();
            last = s;
            return;
        }
        last = s;
        s = std::regex_replace(s, std::regex(R"(@v\d+)"), "");
        s = std::regex_replace(s, std::regex(R"(@t\d+)"), "");
        s = std::regex_replace(s, std::regex(R"(@\w+)"), "");
        buffer->from(s);
    }
    void F01001BB01E8E2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        buffer->from(s);
    }
    void F0100B0C016164000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"[A-Za-z0-9]"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }

    void F010043B013C5C000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010055D009F78000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\d+"), "");
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }

    void F010080C01AA22000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("#\\d+R.*?#"), "");
        s = std::regex_replace(s, std::regex("[A-Za-z0-9]"), "");
        s = std::regex_replace(s, std::regex(u8"[().%,_!#©&:?/]"), "");
        buffer->from(s);
    }
    void F0100CB700D438000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(<RUBY><RB>(.*?)<\/RB><RT>(.*?)<\/RT><\/RUBY>)"),
                               "$1");
        s = std::regex_replace(s, std::regex("<[^>]*>"), "");
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F01005C301AC5E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(".*_.*_.*"), ""); // SIR_C01_016,ERU_C00_000
        s = std::regex_replace(s, std::regex("\\.mp4"), "");
        s = std::regex_replace(s, std::regex("@v"), "");
        s = std::regex_replace(s, std::regex("@n"), "\n");
        buffer->from(s);
    }
    void F0100815019488000_text(TextBuffer *buffer, HookParam *hp)
    {
        //@n@vaoi_s01_0110「うんうん、そうかも！」
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("@.*_.*_\\d+"), "");
        s = std::regex_replace(s, std::regex("@n"), "");
        buffer->from(s);
    }
    void F0100815019488000_name(TextBuffer *buffer, HookParam *hp)
    {
        //  あおい@n@vaoi_s01_0110「うんうん、そうかも！」
        auto s = buffer->strA();
        if (s.find("@n") == s.npos)
            return buffer->clear();
        s = std::regex_replace(s, std::regex("(.*)@n.*"), "$1");
        buffer->from(s);
    }
    void F010072000BD32000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(\[~\])"), "\n");
        s = std::regex_replace(s, std::regex(R"(rom:[\s\S]*$)"), "");
        s = std::regex_replace(s, std::regex(R"(\[[\w\d]*\[[\w\d]*\].*?\[\/[\w\d]*\]\])"), "");
        s = std::regex_replace(s, std::regex(R"(\[.*?\])"), "");
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F01009B50139A8000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"\\b\\d{2}:\\d{2}\\b"), L"");

        auto _ = L"^(?:スキップ|むしる|取り出す|話す|選ぶ|ならびかえ|閉じる|やめる|undefined|決定|ボロのクワ|拾う)$(\\r?\\n|\\r)?";
        while (std::regex_search(s, std::wregex(_)))
        {
            s = std::regex_replace(s, std::wregex(_), L"");
        }
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010032300C562000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        s = std::regex_replace(s, std::regex(R"((#Ruby\[)([^,]+),(#\w+\[.\])?(.+?]))"), "$2");
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        s = std::regex_replace(s, std::regex(u8"　"), "");
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010088B01A8FC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        s = std::regex_replace(s, std::regex(u8"　"), "");
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void FF010061300DF48000_2(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
    }
    void F0100DEF01D0C6000_2(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        if (T0100DEF01D0C6000_dict.find(s) == T0100DEF01D0C6000_dict.end())
            return buffer->clear();
        s += L'\n' + T0100DEF01D0C6000_dict[s];
        buffer->from(s);
    }
    void F0100CEF0152DE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(u8"　"), "");
        s = std::regex_replace(s, std::regex(R"(#n)"), "");
        s = std::regex_replace(s, std::regex(R"(#\w.+?])"), "");
        buffer->from(s);
    }
    void F010061300DF48000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(%\w+)"), "");
        s = std::regex_replace(s, std::regex(u8"　"), "");
        buffer->from(s);
    }
    void F0100E4000F616000(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = StringToWideString(buffer->viewA(), 932).value();
        ws = std::regex_replace(ws, std::wregex(LR"(\\\w)"), L"");
        buffer->from(WideStringToString(ws, 932));
    }
    void F01005A401D766000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(\\n)"), "");
        s = std::regex_replace(s, std::regex(R"(\|(.*?)\|(.*?)\|)"), "$1");
        buffer->from(s);
    }
    void F01005A401D766000_2(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"((#Ruby\[)([^,]+).([^\]]+).)"), "$2");
        s = std::regex_replace(s, std::regex(R"((\\n)+)"), "");
        s = std::regex_replace(s, std::regex(R"((#[A-Za-z]+\[(\d*[.])?\d+\])+)"), "");
        s = std::regex_replace(s, std::regex(R"((<color=.*>(.*)<\/color>)"), "$1");
        buffer->from(s);
    }
    void F010027300A660000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(u8R"(#n(　)*)"), "");
        buffer->from(s);
    }
    void F0100FA10185B0000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#.+?])"), "");
        buffer->from(s);
    }
    void F010095E01581C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(\n)"), "");
        s = std::regex_replace(s, std::regex(R"(\\\w+)"), "");
        buffer->from(s);
    }
    void F0100943010310000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, u8"❞", "\"");
        strReplace(s, u8"❝", "\"");
        s = std::regex_replace(s, std::regex("@(.*?)@"), "$1\n");
        buffer->from(s);
    }
    template <bool choice>
    void F010027401A2A2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\[dic.*?text="), L"");
        s = std::regex_replace(s, std::wregex(L"\\[|'.*?\\]"), L"");
        s = std::regex_replace(s, std::wregex(L"\\]"), L"");
        if (choice)
        {
            s = std::regex_replace(s, std::wregex(LR"([ \t\r\f\v]|　)"), L"");
        }
        else
        {
            s = std::regex_replace(s, std::wregex(L"\\s|　"), L"");
        }
        buffer->from(s);
    }
    void F010027401A2A2000_2(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        static std::wstring last;
        auto x = endWith(last, s);
        last = s;
        if (x)
            return buffer->clear();
        F010027401A2A2000<false>(buffer, hp);
    }

    void F0100BD4014D8C000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L".*?_"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F01007FD00DB20000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(LR"(\n+)"), L" ");
        s = std::regex_replace(s, std::wregex(LR"(\#T1[^#]+)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\#T\d)"), L"");
        if (s == L"　　")
            return buffer->clear();
        buffer->from(utf16_to_utf32(s));
    }
    void F010021D01474E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(LR"(#\w\(.+?\)|#\w{2})"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\n)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(utf16_to_utf32(s));
    }
    void F010021D01474E000_2(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(#\w.+?\)|#\w+)"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(utf16_to_utf32(s));
    }
    void F01002C00177AE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\n)"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(utf16_to_utf32(s));
    }
    void F0100EA100DF92000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static std::string last;
        if (last.find(s) != last.npos)
            return buffer->clear();
        last = s;
        s = std::regex_replace(s, std::regex(R"([~^$(,)R])"), "");
        s = std::regex_replace(s, std::regex(R"(\\n)"), "");
        buffer->from(s);
    }
    template <int i>
    void F010079200C26E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#n)"), "");
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010037500DF38000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\n)"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F0100C7400CFB4000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\d"), L"");
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F0100CB9018F5A000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"\\{([^{}]+):[^{}]+\\}"), L"$1");
        buffer->from(s);
    }

    void F010028D0148E6000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("{|\\/.*?}|\\[.*?]", std::regex_constants::grep), "");
        s = std::regex_replace(s, std::regex("(\\\\\\\\c|\\\\\\\\n)+"), " ");
        s = std::regex_replace(s, std::regex(",.*$"), " ");
        buffer->from(s);
    }

    void F0100F4401940A000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\r\\n]+"), L"");
        s = std::regex_replace(s, std::wregex(L"<[^>]+>|\\[\\[[^]]+\\]\\]"), L"");
        buffer->from(s);
    }

    void F0100B5500CA0C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\\\"), "");
        s = std::regex_replace(s, std::regex("\\$"), "");
        buffer->from(s);
    }
    void T0100B5500CA0C000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context, hp->emu_addr)[6];
        buffer->from(address, *(WORD *)(address - 2));
    }
    void F0100A8401A0A8000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\r\n]+"), L"");
        s = std::regex_replace(s, std::wregex(L"(<.+?>)+"), L"\r\n");
        strReplace(s, L"", L"(L)");
        strReplace(s, L"", L"(ZL)");
        strReplace(s, L"", L"(Y)");
        strReplace(s, L"", L"(X)");
        strReplace(s, L"", L"(A)");
        strReplace(s, L"", L"(B)");
        strReplace(s, L"", L"(+)");
        strReplace(s, L"", L"(-)");
        strReplace(s, L"", L"(DPAD_DOWN)");
        strReplace(s, L"", L"(DPAD_LEFT)");
        strReplace(s, L"", L"(LSTICK)");
        strReplace(s, L"", L"(L3)");
        buffer->from(s);
    }
    void F0100BC0018138000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>([^<]*)<\\/[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"<sprite name=L>"), L"L");
        s = std::regex_replace(s, std::wregex(L"<sprite name=R>"), L"R");
        s = std::regex_replace(s, std::wregex(L"<sprite name=A>"), L"A");
        s = std::regex_replace(s, std::wregex(L"<sprite name=B>"), L"B");
        s = std::regex_replace(s, std::wregex(L"<sprite name=X>"), L"X");
        s = std::regex_replace(s, std::wregex(L"<sprite name=Y>"), L"Y");
        s = std::regex_replace(s, std::wregex(L"<sprite name=PLUS>"), L"+");
        s = std::regex_replace(s, std::wregex(L"<sprite name=MINUS>"), L"-");
        s = std::regex_replace(s, std::wregex(L"<[^>]+>"), L"");
        buffer->from(s);
    }
    void F0100D7800E9E0000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[A-Za-z0-9]"), L"");
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"^二十五字二.*(\r?\n|\r)?"), L"");
        s = std::regex_replace(s, std::wregex(L"^操作を割り当てる.*(\r?\n|\r)?"), L"");
        s = std::regex_replace(s, std::wregex(L"^上記アイコンが出.*(\r?\n|\r)?"), L"");
        s = std::regex_replace(s, std::wregex(L"[()~^,ö.!]"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void TF0100AA1013B96000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto ptr = (char *)(YUZU::emu_arg(context, hp->emu_addr)[0] + 0xb);
        std::string collect;
        while (*ptr || *(ptr - 1))
            ptr--;
        while (!(*ptr && *(ptr + 1)))
            ptr++;
        do
        {
            if (!(*ptr))
            {
                ptr++;
            }
            else
            {
                collect += std::string(ptr);
                ptr += strlen(ptr);
            }
        } while (*ptr || *(ptr + 1));
        strReplace(collect, "\x87\x85", "\x81\x5c");
        strReplace(collect, "\x87\x86", "\x81\x5c");
        strReplace(collect, "\x87\x87", "\x81\x5c");
        strReplace(collect, "\n", "");
        strReplace(collect, "\x81\x40", "");
        buffer->from(collect);
    }
    void T0100CF400F7CE000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[hp->offset];
        std::string s;
        int i = 0;
        while (1)
        {
            auto c = *(BYTE *)(address + i);
            if (c == 0)
                break;
            if (c < 0x20 && c > 0x10)
            {
                auto command = *(BYTE *)(address + i + 1);
                if (command == 0x80)
                    i += 3;
                else if (command == 0xb8)
                    i += 4;
                else
                {
                    auto sz = *(BYTE *)(address + i + 2);
                    i += 3 + sz;
                }
            }
            else if (c == 0xaa)
            {
                i += 1;
            }
            else if (c == 0xff)
            {
                i += 0x30;
            }
            else
            {
                auto l = 1 + IsShiftjisLeadByte(c);
                s += std::string((char *)(address + i), l);
                i += l;
            }
        }
        buffer->from(s);
    }
    void T0100DB300B996000(hook_context *context, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
    {
        auto address = YUZU::emu_arg(context)[8] + 1;
        std::string s;
        int i = 0;
        while (1)
        {
            auto c = *(BYTE *)(address + i);
            if (c == 0)
                break;
            if (c < 0x20 && c > 0x10)
            {
                auto sz = *(BYTE *)(address + i + 2);
                i += 3 + sz;
            }
            else
            {
                auto l = 1 + IsShiftjisLeadByte(c);
                s += std::string((char *)(address + i), l);
                i += l;
            }
        }
        buffer->from(s);
    }
    void F0100CBA014014000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(u8"《.*?》"), "");
        s = std::regex_replace(s, std::regex("<[^>]*>"), "");
        buffer->from(s);
    }
    template <int idx>
    void F0100CC401A16C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("<[^>]*>"), "");
        s = std::regex_replace(s, std::regex("\\d+"), "");
        if (s == "")
            return buffer->clear();
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F0100BDD01AAE4000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("(#Ruby\\[)([^,]+).([^\\]]+)."), "$2");
        s = std::regex_replace(s, std::regex("(#n)+"), " ");
        s = std::regex_replace(s, std::regex("(#[A-Za-z]+[(\\d*[.])?\\d+])+"), "");
        buffer->from(s);
    }
    void F0100C310110B4000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("(#Ruby\\[)([^,]+).([^\\]]+)."), "$2");
        s = std::regex_replace(s, std::regex("#Color\\[[\\d]+\\]"), "");
        s = std::regex_replace(s, std::regex(u8"(　#n)+"), "#n");
        s = std::regex_replace(s, std::regex("#n+"), " ");
        buffer->from(s);
    }
    void F010003F003A34000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"([\s\S]*$)"), L"");
        s = std::regex_replace(s, std::wregex(L"\n+"), L" ");
        s = std::regex_replace(s, std::wregex(L"\\s"), L"");
        s = std::regex_replace(s, std::wregex(L"[＀븅]"), L"");
        buffer->from(s);
    }

    void F01007B601C608000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"\\[.*?\\]"), L"");
        std::vector<std::wstring> lines = strSplit(s, L"\n");
        std::wstring result;
        for (const std::wstring &line : lines)
        {
            if (result.empty() == false)
                result += L"\n";
            s = std::regex_replace(s, std::wregex(L"^(?:メニュー|システム|Ver\\.)$(\\r?\\n|\\r)?"), L"");
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }

    void F010046601125A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(L"<rb>(.+?)</rb><rt>.+?</rt>"), L"$1");
        s = std::regex_replace(s, std::wregex(L"\n+"), L" ");
        buffer->from(utf16_to_utf32(s));
    }
    void F0100771013FA8000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<br>"), L"\n");
        s = std::regex_replace(s, std::wregex(L"^(\\s+)"), L"");
        buffer->from(s);
    }
    void F0100556015CCC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[[^\\]]+."), "");
        s = std::regex_replace(s, std::regex("\\\\k|\\\\x|%C|%B|%p-1;"), "");
        s = std::regex_replace(s, std::regex("#[0-9a-fA-F]+;([^%#]+)(%r)?"), "$1");
        static std::set<std::string> dump;
        if (dump.find(s) != dump.end())
            return buffer->clear();
        dump.insert(s);
        buffer->from(s);
    }
    void F0100CC80140F8000_1(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"^(?:スキップ|メニュー|バックログ|ズームイン|ズームアウト|ガイド OFF|早送り|オート|人物情報|ユニット表示切替|カメラリセット|ガイド表示切替|ページ切替|閉じる|コマンド選択|詳細|シミュレーション|移動)$([\\r?\\n|\\r])?"), L"");

        s = std::regex_replace(s, std::wregex(L"[A-Za-z0-9]"), L"");
        s = std::regex_replace(s, std::wregex(L"[().%,_!#©&:?/]"), L"");
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        buffer->from(s);
    }

    template <int i>
    void F0100CC80140F8000(TextBuffer *buffer, HookParam *hp)
    {
        F0100CC80140F8000_1(buffer, hp);
        auto s = buffer->viewW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
    }

    void F0100D9A01BD86000_0(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> cache(5);
        auto s = buffer->strA();
        if (cache.touch(s))
            return buffer->clear();
    }
    void F0100D9A01BD86000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"\\\\n"), L"");
        buffer->from(s);
    }
    void F010042300C4F6000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"(.+?/)"), L"");
        s = std::regex_replace(s, std::wregex(L"(\" .*)"), L"");
        s = std::regex_replace(s, std::wregex(L"^(.+?\")"), L"");
        buffer->from(s);
    }
    void F010044800D2EC000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\n+"), L" ");
        s = std::regex_replace(s, std::wregex(L"\\<PL_N\\>"), L"???");
        s = std::regex_replace(s, std::wregex(L"<.+?>"), L"");
        buffer->from(s);
    }
    template <int i>
    void F010021300F69E000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\$[a-z]"), L"");
        s = std::regex_replace(s, std::wregex(L"@"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010050000705E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\s"), "");
        s = std::regex_replace(s, std::regex("<br>"), "\n");
        s = std::regex_replace(s, std::regex("<([^:>]+):[^>]+>"), "$1");
        s = std::regex_replace(s, std::regex("<[^>]+>"), "");
        buffer->from(s);
    }
    void F01001B900C0E2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\s"), "");
        s = std::regex_replace(s, std::regex("#[A-Za-z]+(\\[(\\d*\\.)?\\d+\\])+"), "");
        s = std::regex_replace(s, std::regex("#[a-z]"), "");
        s = std::regex_replace(s, std::regex("[a-z]"), "");
        buffer->from(s);
    }

    void F0100217014266000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        s = std::regex_replace(s, std::wregex(L"｛([^｛｝]+)：[^｛｝]+｝"), L"$1");
        while (std::regex_search(s, std::wregex(L"^\\s+")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s+"), L"");
        }
        buffer->from(s);
    }
    void F010007500F27C000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        auto _ = L"^(?:決定|進む|ページ移動|ノート全体図|閉じる|もどる|セーブ中)$(\\r?\\n|\\r)?";
        while (std::regex_search(s, std::wregex(_)))
        {
            s = std::regex_replace(s, std::wregex(_), L"");
        }
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F0100874017BE2000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\n+|(\\\\n)+"), L" ");
        s = std::regex_replace(s, std::wregex(L"#n"), L"");
        buffer->from(s);
    }
    void F010094601D910000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\<.*?\\>"), L"");
        s = std::regex_replace(s, std::wregex(L"\\[.*?\\]"), L"");
        s = std::regex_replace(s, std::wregex(L"\\s"), L"");
        buffer->from(s);
    }
    void F010079201BD88000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"\\\\n"), L"");
        buffer->from(s);
    }
    void F010086C00AF7C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[([^\\]]+)\\/[^\\]]+\\]"), "$1");
        s = std::regex_replace(s, std::regex("\\s+"), " ");
        s = std::regex_replace(s, std::regex("\\\\n"), " ");
        s = std::regex_replace(s, std::regex("<[^>]+>|\\[[^\\]]+\\]"), "");
        buffer->from(s);
    }
    void F010079C017B98000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = utf32_to_utf16(buffer->viewU());
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"#KW"), L"");
        s = std::regex_replace(s, std::wregex(L"#C\\(TR,0xff0000ff\\)"), L"");
        s = std::regex_replace(s, std::wregex(L"【SW】"), L"");
        s = std::regex_replace(s, std::wregex(L"【SP】"), L"");
        s = std::regex_replace(s, std::wregex(L"#P\\(.*\\)"), L"");
        buffer->from(utf16_to_utf32(s));
    }
    void F010061A01C1CE000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[\\s]"), L"");
        s = std::regex_replace(s, std::wregex(L"sound"), L" ");
        buffer->from(s);
    }
    void F0100F7401AA74000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("[\\s]"), "");
        s = std::regex_replace(s, std::regex("@[a-z]"), "");
        s = std::regex_replace(s, std::regex("@[0-9]"), "");
        buffer->from(s);
    }
    void F010069E01A7CE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "\"", "");
        strReplace(s, "#", "");
        buffer->from(s);
    }
    void F0100509013040000(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = StringToWideString(buffer->viewA(), 932).value();
        strReplace(ws, L"^", L"");
        buffer->from(WideStringToString(ws, 932));
    }
    void F01002BB00A662000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "#n", "");
        strReplace(s, "\x81\x40", "");
        s = std::regex_replace(s, std::regex(R"(#Ruby\[(.*?),(.*?)\])"), "$1");
        s = std::regex_replace(s, std::regex(R"(#(\w+?)\[[\d,\.]+?\])"), ""); // #Pos[0,42]#Speed[5]#Effect[0]#Scale[1] #Scale[0.9]
        buffer->from(s);
    }
    void F01008BA00F172000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "[n]", "\n");
        strReplace(s, "[#]", ""); // 分两段显示
        buffer->from(s);
    }
    void F01007A901E728000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"((\\n)+)"), L"");
        s = std::regex_replace(s, std::wregex(LR"([^ \t\r\n\f\v]+＠)"), L""); // c++ regex\S对中文字符支持有问题
        s = std::regex_replace(s, std::wregex(LR"(\\)"), L"");
        s = std::regex_replace(s, std::wregex(LR"((\@)+)"), L"");
        buffer->from(s);
    }
    void F01003E601E324000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(<[^>]*>)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\[[^\]]*\])"), L"");
        buffer->from(s);
    }
    void F01000EA00B23C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"[`@](.*?)@"), L"$1");
        s = std::regex_replace(s, std::wregex(L"\\$\\[(.*?)\\$/(.*?)\\$\\]"), L"$1");
        s = std::regex_replace(s, std::wregex(L"\\$K\\d+(.*?)\\$K\\d+"), L"$1");
        s = std::regex_replace(s, std::wregex(L"\\$A\\d+"), L"");
        strReplace(s, L"$2", L"花");
        strReplace(s, L"$1", L"山田");
        strReplace(s, L"$(3)", L"花");
        buffer->from(s);
    }
    void F010060301588A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        static lru_cache<std::string> cache(4);
        static std::string last;
        if (cache.touch(s))
            return buffer->clear();
        if (startWith(s, last))
        {
            buffer->from(s.substr(last.size(), s.size() - last.size()));
        }
        last = s;
    }
    template <bool name>
    void F0100D8B019FC0000(TextBuffer *buffer, HookParam *hp)
    {
        const char *start;
        if constexpr (name)
        {
            auto v = buffer->viewA();
            if (!startWith(v, "<name"))
                return buffer->clear();
            buffer->from(v.substr(6, v.size() - 6 - 1));
        }
        else
        {
            if (!startWith(buffer->viewA(), "<text"))
                return buffer->clear();
            auto s = buffer->strA();
            buffer->from(std::regex_replace(s.substr(6, s.size() - 6 - 1), std::regex("/ruby:(.*?)&(.*?)/"), "$1"));
        }
    }
    void F0100F7700CB82000(TextBuffer *buffer, HookParam *hp)
    {
        static std::string last;
        static lru_cache<std::string> lastx(10);
        auto s = buffer->strA();
        if (endWith(last, s))
            return buffer->clear();
        last = s;
        if (lastx.touch(last))
            return buffer->clear();
    }

    void F010005F00E036000_1(TextBuffer *buffer, HookParam *hp)
    {
        static lru_cache<std::string> cache(5);
        static std::string last;
        auto s = buffer->strA();

        if (endWith(last, s))
        {
            last = s;
            return buffer->clear();
        }
        if (cache.touch(s))
        {
            last = s;
            return buffer->clear();
        }
        last = s;
        buffer->from(s);
    }
    void F010005F00E036000(TextBuffer *buffer, HookParam *hp)
    {
        F010005F00E036000_1(buffer, hp);
        if (!buffer->size)
            return;
        static std::string last;
        auto s = buffer->strA();

        auto parse = [](std::string &s)
        {
            strReplace(s, u8"㊤", u8"―");
            strReplace(s, u8"㊥", u8"―");
            strReplace(s, u8"㊦", u8"―");
            return s;
        };
        if (startWith(s, last))
        {
            buffer->from(parse(s.substr(last.size(), s.size() - last.size())));
            last = s;
            return;
        }
        last = s;
        buffer->from(parse(s));
    }
    void F0100FC2019346000(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, "#n", 2);
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"((#[A-Za-z]+\[(\d*[.])?\d+\])+)"), "");
        buffer->from(s);
    }
    template <bool choice>
    void F0100E5200D1A2000(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = StringToWideString(buffer->viewA(), 932).value();
        ws = std::regex_replace(ws, std::wregex(LR"((\\n)+)"), L" ");
        ws = std::regex_replace(ws, std::wregex(LR"(\\d$|^\@[a-z]+|#.*?#|\$)"), L"");
        ws = std::regex_replace(ws, std::wregex(LR"(\u3000+)"), L"");
        if (choice)
            ws = std::regex_replace(ws, std::wregex(LR"(, ?\w+)"), L"");
        buffer->from(WideStringToString(ws, 932));
    }
    void F010028D0148E6000_2(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, "@w", 2);
    }
    namespace
    {
#pragma optimize("", off)
        // 必须禁止优化这个函数，或者引用一下参数，否则参数被优化没了。
        void F01009E600FAF6000_collect(const char *_) {}
#pragma optimize("", on)
        void F01009E600FAF6000(TextBuffer *buffer, HookParam *hpx)
        {
            auto s = buffer->strA();
            HookParam hp;
            hp.address = (uintptr_t)F01009E600FAF6000_collect;
            hp.offset = GETARG1;
            hp.type = USING_STRING;
            hp.filter_fun = [](TextBuffer *buffer, HookParam *hp)
            {
                StringFilter(buffer, "@1r", 3);
                StringFilter(buffer, "@-1r", 4);
            };
            static auto _ = NewHook(hp, "01009E600FAF6000");
            static std::map<uint64_t, uintptr_t> mp;
            // 这个address会被触发两次。
            if (mp.find(hpx->emu_addr) == mp.end())
                mp[hpx->emu_addr] = hpx->address;
            if (mp[hpx->emu_addr] != hpx->address)
                return buffer->clear();
            F01009E600FAF6000_collect(s.c_str());
            buffer->clear();
        }
    }
    template <bool choice>
    void F0100EFE0159C6000(TextBuffer *buffer, HookParam *hp)
    {
        auto ws = StringToWideString(buffer->viewA(), 932).value();
        ws = std::regex_replace(ws, std::wregex(LR"((\\n)+)"), L" ");
        ws = std::regex_replace(ws, std::wregex(LR"(\\d$|^\@[a-z]+|#.*?#|\$)"), L"");
        ws = std::regex_replace(ws, std::wregex(LR"(\u3000+)"), L"");
        ws = std::regex_replace(ws, std::wregex(LR"(@w|\\c)"), L"");
        if (choice)
            ws = std::regex_replace(ws, std::wregex(LR"(, ?\w+)"), L"");
        buffer->from(WideStringToString(ws, 932));
    }

    void F0100FDB00AA80000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[([^\\]]+)\\/[^\\]]+\\]"), "$1");
        s = std::regex_replace(s, std::regex("<[^>]*>"), "");
        buffer->from(s);
    }
    void F0100FF500E34A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[.*?\\]"), "");
        s = std::regex_replace(s, std::regex("\\n+"), " ");
        buffer->from(s);
    }
    void F010076501DAEA000(TextBuffer *buffer, HookParam *hp)
    {
        StringFilter(buffer, "\\n", 2);
    }
    void F01005E9016BDE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(\[[^\]]+.)"), "");
        s = std::regex_replace(s, std::regex("\\\\k|\\\\x|%C|%B|%p-1;"), "");
        s = std::regex_replace(s, std::regex("#[0-9a-fA-F]+;([^%#]+)(%r)?"), "$1");
        s = std::regex_replace(s, std::regex("\\\\n"), " ");
        buffer->from(s);
    }

    void F010065301A2E0000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"<WaitFrame>\\d+</WaitFrame>"), L"");
        s = std::regex_replace(s, std::wregex(L"<[^>]*>"), L"");
        buffer->from(s);
    }
    void F01002AE00F442000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\[([^\]\/]+)\/[^\]]+\])"), L"$1");
        s = std::regex_replace(s, std::wregex(LR"(([^ \t\r\n\f\v]*)@)"), L"$1");
        s = std::regex_replace(s, std::wregex(LR"(\$)"), L"");
        buffer->from(s);
    }
    void F01000A400AF2A000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"@[a-zA-Z]|%[a-zA-Z]+"), L"");
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }

    void F01006B5014E2E000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("@r(.*?)@(.*?)@"), "$1");
        s = std::regex_replace(s, std::regex("@n"), "");
        s = std::regex_replace(s, std::regex("@v"), "");
        s = std::regex_replace(s, std::regex("TKY[0-9]{6}_[A-Z][0-9]{2}"), "");
        buffer->from(s);
    }
    void F0100CF400F7CE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\n+"), " ");
        buffer->from(s);
    }
    void F01000AE01954A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("[A-Za-z0-9]"), "");
        s = std::regex_replace(s, std::regex("[~^(-).%,!:#@$/*&;+_]"), "");
        buffer->from(s);
    }
    void F01003BD013E30000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("{|\\/.*?}|\\[.*?]"), "");
        buffer->from(s);
    }
    void F010074F013262000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[.*?]"), "");
        buffer->from(s);
    }
    void F010057E00AC56000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("<[^>]*>"), "");
        s = std::regex_replace(s, std::regex(u8"ズーム|回転|身長|体重"), "");
        s = std::regex_replace(s, std::regex("[A-Za-z0-9]"), "");
        s = std::regex_replace(s, std::regex("[().%,!#/]"), "");
        while (std::regex_search(s, std::regex("^\\s*$")))
        {
            s = std::regex_replace(s, std::regex("^\\s*$"), "");
        }
        static std::string last;
        if (last == s)
            return buffer->clear();
        last = s;
        buffer->from(s);
    }
    void F010051D010FC2000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex("\\[([^\\]]+)\\/[^\\]]+\\]"), "$1");
        s = std::regex_replace(s, std::regex("\\s+"), " ");
        s = std::regex_replace(s, std::regex("\\\\n"), " ");
        s = std::regex_replace(s, std::regex("<[^>]+>|\\[[^\\]]+\\]"), "");
        buffer->from(s);
    }

    void F010096000CA38000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\$\w{1,2})"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\$\[|\$\/.+?])"), L"");
        buffer->from(s);
    }
    void F0100EC001DE7E000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(<\w+=[^>]+>|<\/\w+>)"), L"");
        buffer->from(s);
    }
    void F0100DEF01D0C6000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\n)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(<.+?>)"), L"");
        buffer->from(s);
    }
    void F01005AF00E9DC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        s = std::regex_replace(s, std::regex(R"(#n)"), "");
        s = std::regex_replace(s, std::regex(R"(#\w+(\[.+?\])?)"), "");
        buffer->from(s);
    }
    void F010031C01F410000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s += L"\n";
        buffer->from(s);
    }
    namespace
    {
#pragma optimize("", off)
        void TT0100A4700BC98000(const char *_) {}
#pragma optimize("", on)

        void T0100A4700BC98000(TextBuffer *buffer, HookParam *)
        {
            auto s = buffer->strA();
            HookParam hp;
            hp.address = (uintptr_t)TT0100A4700BC98000;
            hp.offset = GETARG1;
            hp.type = CODEC_UTF8 | USING_STRING;
            static auto _ = NewHook(hp, "0100A4700BC98000");
            TT0100A4700BC98000(s.c_str());
            // buffer->clear();
        }
    }
    namespace
    {
#pragma optimize("", off)
        void F01006530151F0000_collect(const wchar_t *_) {}
#pragma optimize("", on)
        void F01006530151F0000(TextBuffer *buffer, HookParam *)
        {

            auto s = buffer->strW();
            strReplace(s, L"/player", L"");
            HookParam hp;
            hp.address = (uintptr_t)F01006530151F0000_collect;
            hp.offset = GETARG1;
            hp.type = CODEC_UTF16 | USING_STRING;
            static auto _ = NewHook(hp, "01006530151F0000");
            F01006530151F0000_collect(s.c_str());
            buffer->clear();
        }
    }
    void F010043901E972000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        strReplace(s, L"<br>", L"\n");
        buffer->from(s);
    }
    void wF0100A9B01D4AE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(@(.*?)@)"), L"$1\n");
        buffer->from(s);
    }
    void aF0100A9B01D4AE000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, u8"❛", "'");
        strReplace(s, u8"❜", "'");
        strReplace(s, u8"❝", "\"");
        strReplace(s, u8"❞", "\"");
        s = std::regex_replace(s, std::regex(R"(@(.*?)@)"), "$1\n");
        s = std::regex_replace(s, std::regex(R"(\$s\(i?\))"), "");
        s = std::regex_replace(s, std::regex(R"(\$[<>]\d+)"), "");
        buffer->from(s);
    }
    void F0100FB301E70A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        if (s == L"\uc5d0\u4bad\u0012")
            buffer->clear();
    }
    void F0100F0A01F112000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        s = std::regex_replace(s, std::wregex(LR"(\$\[(.*?)\$/(.*?)\$\])"), L"$1");
        buffer->from(s);
    }
    void F0100C9001E10C000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(<(.*?)>)"), L""); //<indent=3.5%>
        buffer->from(s);
    }
    void F01001BA01EBFC000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(#n)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(#\w+(\[.+?\])?)"), L"");
        buffer->from(s);
    }
    void F01000BB01CB8A000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strW();
        static std::wstring last;
        if (last == s)
            return buffer->clear();
        last = s;
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        buffer->from(s);
    }
    void F010044701E9BC000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\<.*?\>)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\s)"), L"");
        buffer->from(s);
    }
    void F01003BB01DF54000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\\\u3000*)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\$)"), L"");
        buffer->from(s);
    }
    void F01004E5017C54000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(<.+?>)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        buffer->from(s);
    }
    void F0100FA001E160000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"(\r\n)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(\u3000)"), L"");
        buffer->from(s);
    }
    template <bool choice>
    void F0100A250191E8000(TextBuffer *buffer, HookParam *hp)
    {
        auto s = buffer->strA();
        strReplace(s, "\n", "");
        s = std::regex_replace(s, std::regex(R"(\\d$|^\@[a-z]+|#.*?#|\$)"), "");
        strReplace(s, "\x81\x40", "");
        s = std::regex_replace(s, std::regex(R"(@w|\\c)"), "");
        if (choice)
            s = std::regex_replace(s, std::regex(R"(, ?\w+)"), "");
        buffer->from(s);
    }
    void F0100B1F0123B6000(TextBuffer *buffer, HookParam *hp)
    {
        if (all_ascii((wchar_t *)buffer->buff))
            return buffer->clear();
        F010096000CA38000(buffer, hp);
    }
    void F0100A62019078000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(LR"([\s])"), L"");
        s = std::regex_replace(s, std::wregex(LR"($$R)"), L"");
        s = std::regex_replace(s, std::wregex(LR"(%)"), L"");
        buffer->from(s);
    }
    void F01001EF017BE6000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        while (std::regex_search(s, std::wregex(L"^\\s*$")))
        {
            s = std::regex_replace(s, std::wregex(L"^\\s*$"), L"");
        }
        buffer->from(s);
    }
    void F01000EA00D2EE000(TextBuffer *buffer, HookParam *hp)
    {

        auto s = buffer->strW();
        s = std::regex_replace(s, std::wregex(L"\\n+"), L" ");
        s = std::regex_replace(s, std::wregex(L"\\<PL_Namae\\>"), L"???");
        s = std::regex_replace(s, std::wregex(L"\\<chiaki_washa\\>"), L"chiaki_washa");
        s = std::regex_replace(s, std::wregex(L"<.+?>"), L"");
        buffer->from(s);
    }

    void NewLineCharFilterW(TextBuffer *buffer, HookParam *)
    {
        CharFilter(buffer, L'\n');
    }
    auto _ = []()
    {
        emfunctionhooks = {
            // Memories Off
            {0x8003eeac, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100978013276000ull, "1.0.0"}},
            {0x8003eebc, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100978013276000ull, "1.0.1"}},
            // Memories Off ～それから～
            {0x8003fb7c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100B4A01326E000ull, "1.0.0"}},
            {0x8003fb8c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100B4A01326E000ull, "1.0.1"}},
            // ファミコン探偵倶楽部 消えた後継者
            {0x80052a10, {CODEC_UTF16, 3, 0, mages_readstring, 0, 0x0100B4500F7AE000ull, "1.0.0"}},
            // ファミコン探偵倶楽部PartII うしろに立つ少女
            {0x8004cb30, {CODEC_UTF16, 3, 0, mages_readstring, 0, 0x010078400F7B0000ull, "1.0.0"}},
            // Memories Off 2nd
            {0x8003ee0c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100D31013274000ull, "1.0.0"}},
            {0x8003ee1c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100D31013274000ull, "1.0.1"}},
            // 想い出にかわる君 ～メモリーズオフ～
            {0x8003ef6c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100FFA013272000ull, "1.0.0"}},
            {0x8003ef7c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100FFA013272000ull, "1.0.1"}},
            // メモリーズオフ6 ～T-wave～
            {0x80043d7c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x010047A013268000ull, "1.0.0"}},
            {0x80043d5c, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x010047A013268000ull, "1.0.1"}},
            // メモリーズオフ ゆびきりの記憶
            {0x800440ec, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x010079C012896000ull, "1.0.0"}},
            // Memories Off #5 とぎれたフィルム
            {0x8003f6ac, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x010073901326C000ull, "1.0.0"}},
            {0x8003f5fc, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x010073901326C000ull, "1.0.1"}},
            // シンスメモリーズ 星天の下で
            {0x80048cc8, {CODEC_UTF16, 4, 0, mages_readstring, 0, 0x0100E94014792000ull, 0}}, // line + name => join
            {0x8004f44c, {CODEC_UTF16, 4, 0, mages_readstring, 0, 0x0100E94014792000ull, 0}}, // fast trophy
            {0x8004f474, {CODEC_UTF16, 4, 0, mages_readstring, 0, 0x0100E94014792000ull, 0}}, // prompt
            {0x80039dc0, {CODEC_UTF16, 4, 0, mages_readstring, 0, 0x0100E94014792000ull, 0}}, // choice
            // やはりゲームでも俺の青春ラブコメはまちがっている。
            {0x8005DFB8, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100E0D0154BC000ull, "1.0.0"}},
            // CHAOS;HEAD NOAH
            {0x80046700, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100957016B90000ull, "1.0.0"}},
            {0x8003A2c0, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100957016B90000ull, "1.0.0"}}, // choice
            {0x8003EAB0, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100957016B90000ull, "1.0.0"}}, // TIPS list (menu)
            {0x8004C648, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100957016B90000ull, "1.0.0"}}, // system message
            {0x80050374, {CODEC_UTF16, 0, 0, mages_readstring, 0, 0x0100957016B90000ull, "1.0.0"}}, // TIPS (red)
            // 白と黒のアリス
            {0x80013f20, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            {0x80013f94, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            {0x8001419c, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            // 白と黒のアリス -Twilight line-
            {0x80014260, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            {0x800142d4, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            {0x800144dc, {CODEC_UTF8, 0, 0, 0, NewLineCharFilterW, 0x0100A460141B8000ull, "1.0.0"}},
            // CLANNAD
            {0x80072d00, {CODEC_UTF16 | FULL_STRING, 1, 0, 0, F0100A3A00CC7E000, 0x0100A3A00CC7E000ull, "1.0.0"}},
            {0x80072d30, {CODEC_UTF16 | FULL_STRING, 1, 0, 0, F0100A3A00CC7E000, 0x0100A3A00CC7E000ull, "1.0.7"}},
            // VARIABLE BARRICADE NS
            {0x800e3424, {CODEC_UTF8, 0, 0, 0, F010045C0109F2000, 0x010045C0109F2000ull, "1.0.1"}}, //"System Messages + Choices"), //Also includes the names of characters,
            {0x800fb080, {CODEC_UTF8, 3, 0, 0, F010045C0109F2000, 0x010045C0109F2000ull, "1.0.1"}}, // Main Text
            // AMNESIA for Nintendo Switch
            {0x805bba5c, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, F0100A1E00BFEA000, 0x0100A1E00BFEA000ull, "1.0.1"}}, // dialogue
            {0x805e9930, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100A1E00BFEA000, 0x0100A1E00BFEA000ull, "1.0.1"}}, // choice
            {0x805e7fd8, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100A1E00BFEA000, 0x0100A1E00BFEA000ull, "1.0.1"}}, // name
            // 蝶の毒 華の鎖
            {0x80095010, {CODEC_UTF16, 1, 0, 0, F0100A1200CA3C000, 0x0100A1200CA3C000ull, "2.0.1"}}, // Main Text + Names
            // Live a Live
            {0x80a05170, {CODEC_UTF16, 0, 0, 0, F0100982015606000, 0x0100C29017106000ull, "1.0.0"}},
            // さくらの雲＊スカアレットの恋
            {0x804e4858, {CODEC_UTF8, 3, 1, 0, F01006590155AC000, 0x01006590155AC000ull, "1.0.0"}}, // name
            {0x804e4870, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01006590155AC000ull, "1.0.0"}}, // dialogue
            // マジェスティック☆マジョリカル
            {0x80557408, {CODEC_UTF8, 0, 0, 0, F01000200194AE000, 0x01000200194AE000ull, "1.0.0"}}, // name
            {0x8059ee94, {CODEC_UTF8, 3, 0, 0, F01000200194AE000, 0x01000200194AE000ull, "1.0.0"}}, // player name
            {0x80557420, {CODEC_UTF8, 0, 0, 0, F01000200194AE000, 0x01000200194AE000ull, "1.0.0"}}, // dialogue
            // マツリカの炯-kEi- 天命胤異伝
            {0x8017ad54, {CODEC_UTF32, 1, 0, 0, F0100EA001A626000, 0x0100EA001A626000ull, "1.0.0"}}, // text
            {0x80174d4c, {CODEC_UTF32, 1, 0, 0, F0100EA001A626000, 0x0100EA001A626000ull, "1.0.0"}}, // name
            // キューピット・パラサイト
            {0x80057910, {CODEC_UTF32, 2, 0, 0, F0100F7E00DFC8000, 0x0100F7E00DFC8000ull, "1.0.1"}}, // name + text
            {0x80169df0, {CODEC_UTF32, 0, 0, 0, F0100F7E00DFC8000, 0x0100F7E00DFC8000ull, "1.0.1"}}, // choice
            // ラディアンテイル
            {0x80075190, {CODEC_UTF8, 1, 0, 0, F0100925014864000, 0x0100925014864000ull, "1.0.0"}}, // prompt
            {0x8002fb18, {CODEC_UTF8, 0, 0, 0, F0100925014864000, 0x0100925014864000ull, "1.0.0"}}, // name
            {0x8002fd7c, {CODEC_UTF8, 0, 0, 0, F0100925014864000, 0x0100925014864000ull, "1.0.0"}}, // text
            {0x8004cf28, {CODEC_UTF8, 1, 0, 0, F0100925014864000, 0x0100925014864000ull, "1.0.0"}}, // text
            // MUSICUS
            {0x80462DD4, {CODEC_UTF8, 0, 1, 0, F01006590155AC000, 0x01000130150FA000ull, "1.0.0"}}, // name
            {0x80462DEC, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01000130150FA000ull, "1.0.0"}}, // dialogue 1
            {0x80480d4c, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01000130150FA000ull, "1.0.0"}}, // dialogue 2
            {0x804798e0, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01000130150FA000ull, "1.0.0"}}, // choice
            // Story of Seasons a Wonderful Life
            {0x80ac4d88, {CODEC_UTF32, 0, 0, 0, F0100936018EB4000, 0x0100936018EB4000ull, "1.0.3"}}, // Main text
            {0x808f7e84, {CODEC_UTF32, 0, 0, 0, F0100936018EB4000, 0x0100936018EB4000ull, "1.0.3"}}, // Item name
            {0x80bdf804, {CODEC_UTF32, 0, 0, 0, F0100936018EB4000, 0x0100936018EB4000ull, "1.0.3"}}, // Item description
            // 乙女ゲームの破滅フラグしかない悪役令嬢に転生してしまった… 〜波乱を呼ぶ海賊〜
            {0x81e75940, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100982015606000ull, "1.0.0"}}, // Hamekai.TalkPresenter$$AddMessageBacklog
            {0x81c9ae60, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100982015606000ull, "1.0.0"}}, // Hamekai.ChoicesText$$SetText
            {0x81eb7dc0, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100982015606000ull, "1.0.0"}}, // Hamekai.ShortStoryTextView$$AddText
            // Death end re;Quest
            {0x80241088, {CODEC_UTF8, 8, 0, 0, F0100AEC013DDA000, 0x0100AEC013DDA000ull, "1.0.0"}}, // english ver
            // Death end re;Quest 2
            {0x80225C3C, {CODEC_UTF8, 8, 0, 0, F010001D015260000, 0x010001D015260000ull, "1.0.0"}},
            // Death end re;Quest Code Z
            {0x82349188, {CODEC_UTF16, 1, 0, 0, 0, 0x010054B01BE90000ull, "1.0.0"}},
            {0x823DC128, {CODEC_UTF16, 1, 0, 0, 0, 0x010054B01BE90000ull, "1.0.2"}},
            // ――ッ違う!!!
            {0x81DD6010, {CODEC_UTF16, 1, -32, 0, 0, 0x01009A401C1B0000ull, "1.02"}}, // english ver, only long string, short string can't find.
            // あかやあかしやあやかしの 綴
            {0x8176D78C, {CODEC_UTF16, 3, 0, 0, 0, 0x0100F7801B5DC000ull, "1.0.0"}},
            // 13 Sentinels: Aegis Rim
            {0x80057d18, {CODEC_UTF8, 0, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // cutscene text
            {0x8026fec0, {CODEC_UTF8, 1, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // prompt
            {0x8014eab4, {CODEC_UTF8, 0, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // name (combat)
            {0x801528ec, {CODEC_UTF8, 3, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // dialogue (combat)
            {0x80055acc, {CODEC_UTF8, 0, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // dialogue 2 (speech bubble)
            {0x802679c8, {CODEC_UTF8, 1, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // notification
            {0x8025e210, {CODEC_UTF8, 2, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // scene context example: 数日前 咲良高校 １年Ｂ組 教室 １９８５年５月"
            {0x8005c518, {CODEC_UTF8, 0, 0, 0, F010045C014650000, 0x010045C014650000ull, "1.0.0"}}, // game help
            // Sea of Stars
            {0x83e93ca0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01008C0016544000, 0x01008C0016544000ull, "1.0.45861"}}, // Main text
            {0x820c3fa0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01008C0016544000, 0x01008C0016544000ull, "1.0.47140"}}, // Main text
            // Final Fantasy I
            {0x81e88040, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01000EA014150000ull, "1.0.1"}}, // Main text
            {0x81cae54c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01000EA014150000ull, "1.0.1"}}, // Intro text
            {0x81a3e494, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01000EA014150000ull, "1.0.1"}}, // battle text
            {0x81952c28, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01000EA014150000ull, "1.0.1"}}, // Location
            // Final Fantasy II
            {0x8208f4cc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01006B7014156000ull, "1.0.1"}}, // Main text
            {0x817e464c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01006B7014156000ull, "1.0.1"}}, // Intro text
            {0x81fb6414, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01006B7014156000ull, "1.0.1"}}, // battle text
            // Final Fantasy III
            {0x82019e84, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01002E2014158000ull, "1.0.1"}}, // Main text1
            {0x817ffcfc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01002E2014158000ull, "1.0.1"}}, // Main text2
            {0x81b8b7e4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01002E2014158000ull, "1.0.1"}}, // battle text
            {0x8192c4a8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01002E2014158000ull, "1.0.1"}}, // Location
            // Final Fantasy IV
            {0x81e44bf4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01004B301415A000ull, "1.0.2"}}, // Main text
            {0x819f92c4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01004B301415A000ull, "1.0.2"}}, // Rolling text
            {0x81e2e798, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01004B301415A000ull, "1.0.2"}}, // Battle text
            {0x81b1e6a8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01004B301415A000ull, "1.0.2"}}, // Location
            // Final Fantasy V
            {0x81d63e24, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA201415C000ull, "1.0.2"}}, // Main text
            {0x81adfb3c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA201415C000ull, "1.0.2"}}, // Location
            {0x81a8fda8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA201415C000ull, "1.0.2"}}, // Battle text
            // Final Fantasy VI
            {0x81e6b350, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA001415E000ull, "1.0.2"}}, // Main text
            {0x81ab40ec, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA001415E000ull, "1.0.2"}}, // Location
            {0x819b8c88, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100AA001415E000ull, "1.0.2"}}, // Battle text
            // Final Fantasy IX
            {0x80034b90, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Main Text
            {0x802ade64, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Battle Text
            {0x801b1b84, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Descriptions
            {0x805aa0b0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Key Item Name
            {0x805a75d8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Key Item Content
            {0x8002f79c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Menu
            {0x80ca88b0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Tutorial1
            {0x80ca892c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Tutorial2
            {0x80008d88, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01006F000B056000, 0x01006F000B056000ull, "1.0.1"}}, // Location
            // Norn9 Var Commons
            {0x8003E874, {CODEC_UTF8, 0, 0, 0, F0100068019996000, 0x0100068019996000ull, "1.0.0"}}, // English
            // 薄桜鬼 真改 遊戯録　隊士達の大宴会 for Nintendo Switch   三合一
            {0x80016730, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其一
            {0x8013AAA0, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其二
            {0x8009C8A0, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其三
            {0x800167B0, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其一
            {0x8013AFA0, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其二
            {0x8009CCE0, {CODEC_UTF8, 0, 0, 0, F01002BB00A662000, 0x010046601C024000ull, "1.0.0"}}, // name+text 其三
            // 薄桜鬼SSL ～sweet school life～ for Nintendo Switch
            {0x8004E71C, {CODEC_UTF8, 1, 0, 0, F01004EB01A328000, 0x01004EB01A328000ull, "1.0.0"}},
            {0x8004EAEC, {CODEC_UTF8, 1, 0, 0, F01004EB01A328000, 0x01004EB01A328000ull, "1.0.1"}},
            // 薄桜鬼 真改 万葉ノ抄
            {0x8004E8F0, {CODEC_UTF8, 1, 0, 0, F010001D015260000, 0x0100EA601A0A0000ull, "1.0.0"}},
            // 薄桜鬼 真改 天雲ノ抄
            {0x8004CACC, {CODEC_UTF8, 1, 0, 0, F010001D015260000, 0x0100997017690000ull, "1.0.0"}},
            // 薄桜鬼 真改 銀星ノ抄
            {0x80047F00, {CODEC_UTF8, 1, 0, 0, F010001D015260000, 0x0100C49010598000ull, "1.0.0"}},
            // 薄桜鬼 真改 月影ノ抄
            {0x8019ecd0, {CODEC_UTF8, 1, 0, 0, F0100E1E00E2AE000, 0x0100E1E00E2AE000ull, "1.0.0"}}, // Text
            // 薄桜鬼　黎明録
            {0x8002e94c, {CODEC_UTF8, 0, 0, 0, F0100925014864000, 0x0100D57014692000ull, "1.0.0"}}, // Text
            {0x8004c3f4, {CODEC_UTF8, 1, 0, 0, F0100925014864000, 0x0100D57014692000ull, "1.0.0"}},
            {0x8005389c, {CODEC_UTF8, 0, 0, 0, F0100925014864000, 0x0100D57014692000ull, "1.0.0"}},
            {0x80059b68, {CODEC_UTF8, 0, 0, 0, F0100925014864000, 0x0100D57014692000ull, "1.0.0"}},
            // Chrono Cross: The Radical Dreamers Edition
            {0x802b1254, {CODEC_UTF32, 1, 0, 0, 0, 0x0100AC20128AC000ull, "1.0.2"}}, // Text
            // AIR
            {0x800a6b10, {CODEC_UTF16, 1, 0, 0, F0100ADC014DA0000, 0x0100ADC014DA0000ull, "1.0.1"}}, // Text + Name
            // 死神と少女
            {0x21cb08, {0, 1, 0, 0, F0100AFA01750C000, 0x0100AFA01750C000ull, "1.0.2"}}, // Text,sjis
            // Octopath Traveler II
            {0x8088a4d4, {CODEC_UTF16, 0, 0, 0, 0, 0x0100A3501946E000ull, "1.0.0"}}, // main text
            // NieR:Automata The End of YoRHa Edition
            {0x808e7068, {CODEC_UTF16, 3, 0, 0, 0, 0x0100B8E016F76000ull, "1.0.2"}}, // Text
            // レンドフルール
            {0x80026434, {CODEC_UTF8, 0, 0, 0, 0, 0x0100B5800C0E4000ull, "1.0.0"}}, // Dialogue text
            // Code：Realize ～彩虹の花束～
            {0x80019c14, {CODEC_UTF8, 0, 0x1c, 0, F010088B01A8FC000, 0x0100B6900A668000ull, "1.0.0"}},
            {0x80041560, {CODEC_UTF8, 1, 0, 0, F010088B01A8FC000, 0x0100B6900A668000ull, "1.0.0"}},
            {0x800458c8, {CODEC_UTF8, 0, 0, 0, F010088B01A8FC000, 0x0100B6900A668000ull, "1.0.0"}},
            // Diabolik Lovers Grand Edition
            {0x80041080, {CODEC_UTF8, 1, 0, 0, F0100BD700E648000, 0x0100BD700E648000ull, "1.0.0"}}, // name
            {0x80041080, {CODEC_UTF8, 0, 0, 0, F0100BD700E648000, 0x0100BD700E648000ull, "1.0.0"}}, // dialogue
            {0x80041080, {CODEC_UTF8, 2, 0, 0, F0100BD700E648000, 0x0100BD700E648000ull, "1.0.0"}}, // choice1
            // DIABOLIK LOVERS CHAOS LINEAGE
            {0x80033A00, {CODEC_UTF8, 0, 0, 0, F010027400BD24000, 0x010027400BD24000ull, "1.0.0"}},
            {0x8001EEB8, {CODEC_UTF8, 0, 0, 0, F010027400BD24000_1, 0x010027400BD24000ull, "1.0.2"}},
            // 忍び、恋うつつ
            {0x8002aca0, {CODEC_UTF8, 0, 0, 0, F0100C1E0102B8000, 0x0100C1E0102B8000ull, "1.0.0"}}, // name
            {0x8002aea4, {CODEC_UTF8, 0, 0, 0, F0100C1E0102B8000, 0x0100C1E0102B8000ull, "1.0.0"}}, // dialogue1
            {0x8001ca90, {CODEC_UTF8, 2, 0, 0, F0100C1E0102B8000, 0x0100C1E0102B8000ull, "1.0.0"}}, // dialogue2
            {0x80049dbc, {CODEC_UTF8, 1, 0, 0, F0100C1E0102B8000, 0x0100C1E0102B8000ull, "1.0.0"}}, // choice
            // 夜、灯す
            {0xe2748eb0, {CODEC_UTF32, 1, 0, 0, 0, 0x0100C2901153C000ull, "1.0.0"}}, // text1
            // Closed Nightmare
            {0x800c0918, {CODEC_UTF8, 0, 0, 0, F0100D9500A0F6000, 0x0100D9500A0F6000ull, "1.0.0"}}, // line + name
            {0x80070b98, {CODEC_UTF8, 0, 0, 0, F0100D9500A0F6000, 0x0100D9500A0F6000ull, "1.0.0"}}, // fast trophy
            {0x800878fc, {CODEC_UTF8, 0, 0, 0, F0100D9500A0F6000, 0x0100D9500A0F6000ull, "1.0.0"}}, // prompt
            {0x80087aa0, {CODEC_UTF8, 0, 0, 0, F0100D9500A0F6000, 0x0100D9500A0F6000ull, "1.0.0"}}, // choice
            // ゆるキャン△ Have a nice day!
            {0x816d03f8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100982015606000, 0x0100D12014FC2000ull, "1.0.0"}}, // dialog / backlog
            // 悪役令嬢は隣国の王太子に溺愛される
            {0x817b35c4, {CODEC_UTF8, 1, 0, 0, F0100DA201E0DA000, 0x0100DA201E0DA000ull, "1.0.0"}}, // Dialogue
            // ゆのはなSpRING！～Mellow Times～
            {0x80028178, {CODEC_UTF8, 0, 0, 0, F0100DE200C0DA000, 0x0100DE200C0DA000ull, "1.0.0"}}, // name
            {0x8001b9d8, {CODEC_UTF8, 2, 0, 0, F0100DE200C0DA000, 0x0100DE200C0DA000ull, "1.0.0"}}, // dialogue1
            {0x8001b9b0, {CODEC_UTF8, 2, 0, 0, F0100DE200C0DA000, 0x0100DE200C0DA000ull, "1.0.0"}}, // dialogue2
            {0x8004b940, {CODEC_UTF8, 2, 0, 0, F0100DE200C0DA000, 0x0100DE200C0DA000ull, "1.0.0"}}, // dialogue3
            {0x8004a8d0, {CODEC_UTF8, 1, 0, 0, F0100DE200C0DA000, 0x0100DE200C0DA000ull, "1.0.0"}}, // choice
            // サマータイムレンダ Another Horizon
            {0x818ebaf0, {CODEC_UTF16, 0, 0x14, 0, F01005940182EC000, 0x01005940182EC000ull, "1.0.0"}}, // dialogue
            // あくありうむ。
            {0x8051a990, {CODEC_UTF8, 0, 1, 0, F01006590155AC000, 0x0100D11018A7E000ull, "1.0.0"}}, // name
            {0x8051a9a8, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x0100D11018A7E000ull, "1.0.0"}}, // dialogue
            {0x80500178, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x0100D11018A7E000ull, "1.0.0"}}, // choice
            // AKA
            {0x8166eb80, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Main text
            {0x817d44a4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Letter
            {0x815cb0f4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Mission title
            {0x815cde30, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Mission description
            {0x8162a910, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Craft description
            {0x817fdca8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0601852A000, 0x0100B0601852A000ull, "1.0.0"}}, // Inventory item name
            // Etrian Odyssey I HD
            {0x82d57550, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x01008A3016162000ull, "1.0.2"}}, // Text
            {0x824ff408, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x01008A3016162000ull, "1.0.2"}}, // Config Description
            {0x8296b4e4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x01008A3016162000ull, "1.0.2"}}, // Class Description
            {0x81b2204c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x01008A3016162000ull, "1.0.2"}}, // Item Description
            // Etrian Odyssey II HD
            {0x82f24c70, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100B0C016164000ull, "1.0.2"}}, // Text
            {0x82cc0988, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100B0C016164000ull, "1.0.2"}}, // Config Description
            {0x8249acd4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100B0C016164000ull, "1.0.2"}}, // Class Description
            {0x81b27644, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100B0C016164000ull, "1.0.2"}}, // Item Description
            // Etrian Odyssey III HD
            {0x83787f04, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100D32015A52000ull, "1.0.2"}}, // Text
            {0x8206915c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100D32015A52000ull, "1.0.2"}}, // Config Description
            {0x82e6d1d4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100D32015A52000ull, "1.0.2"}}, // Class Description
            {0x82bf5d48, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100B0C016164000, 0x0100D32015A52000ull, "1.0.2"}}, // Item Description
            // Fire Emblem Engage
            {0x8248c550, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, 0, 0x0100A6301214E000ull, "1.3.0"}}, // App.Talk3D.TalkLog$$AddLog
            {0x820C6530, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, 0, 0x0100A6301214E000ull, "2.0.0"}}, // App.Talk3D.TalkLog$$AddLog
            // AMNESIA LATER×CROWD for Nintendo Switch
            {0x800ebc34, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100B5700CDFC000ull, "1.0.0"}}, // waterfall
            {0x8014dc64, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100B5700CDFC000ull, "1.0.0"}}, // name
            {0x80149b10, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100B5700CDFC000ull, "1.0.0"}}, // dialogue
            {0x803add50, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100982015606000, 0x0100B5700CDFC000ull, "1.0.0"}}, // choice
            // Natsumon! 20th Century Summer Vacation
            {0x80db5d34, {CODEC_UTF16, 0, 0, 0, F0100A8401A0A8000, 0x0100A8401A0A8000ull, "1.1.0"}}, // tutorial
            {0x846fa578, {CODEC_UTF16, 0, 0, 0, F0100A8401A0A8000, 0x0100A8401A0A8000ull, "1.1.0"}}, // choice
            {0x8441e800, {CODEC_UTF16, 0, 0, 0, F0100A8401A0A8000, 0x0100A8401A0A8000ull, "1.1.0"}}, // examine + dialog
            // Super Mario RPG
            {0x81d78c58, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Main Text
            {0x81dc9cf8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Name
            {0x81c16b80, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Cutscene
            {0x821281f0, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Special/Item/Menu/Objective Description
            {0x81cd8148, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Special Name
            {0x81fc2820, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Item Name Battle
            {0x81d08d28, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Item Name Off-battle
            {0x82151aac, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Shop Item Name
            {0x81fcc870, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Objective Title
            {0x821bd328, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Monster List - Name
            {0x820919b8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Monster List - Description
            {0x81f56518, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Info
            {0x82134ce0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Help Category
            {0x82134f30, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Help Name
            {0x821372e4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Help Description 1
            {0x82137344, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Help Description 2
            {0x81d0ee80, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Location
            {0x82128f64, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Album Title
            {0x81f572a0, {CODEC_UTF16, 3, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Load/Save Text
            {0x81d040a8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Levelup First Part
            {0x81d043fc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Levelup Second Part
            {0x81d04550, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Levelup New Ability Description
            {0x81fbfa18, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Yoshi Mini-Game Header
            {0x81fbfa74, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Yoshi Mini-Game Text
            {0x81cf41b4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BC0018138000, 0x0100BC0018138000ull, "1.0.0"}}, // Enemy Special Attacks
            // Trials of Mana
            {0x800e8abc, {CODEC_UTF16, 1, 0, 0, F0100D7800E9E0000, 0x0100D7800E9E0000ull, "1.1.1"}}, // Text
            // 空蝉の廻
            {0x821b452c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100DA101D9AA000ull, "1.0.0"}}, // text1
            {0x821b456c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100DA101D9AA000ull, "1.0.0"}}, // text2
            {0x821b45ac, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x0100DA101D9AA000ull, "1.0.0"}}, // text3
            // バディミッション BOND
            {0x80046dd0, {0, 0, 0, T0100DB300B996000, 0, 0x0100DB300B996000ull, 0}}, // 1.0.0, 1.0.1,sjis
            {0x80046de0, {0, 0, 0, T0100DB300B996000, 0, 0x0100DB300B996000ull, 0}},
            // Bravely Default II
            {0x80b97700, {CODEC_UTF16, 0, 0, 0, 0, 0x010056F00C7B4000ull, "1.0.0"}}, // Main Text
            {0x80bb8d3c, {CODEC_UTF16, 0, 0, 0, 0, 0x010056F00C7B4000ull, "1.0.0"}}, // Main Ptc Text
            {0x810add68, {CODEC_UTF16, 0, 0, 0, 0, 0x010056F00C7B4000ull, "1.0.0"}}, // Secondary Text
            // 探偵撲滅
            {0x8011c340, {CODEC_UTF8, 1, 0, 0, F0100CBA014014000, 0x0100CBA014014000ull, "1.0.0"}}, // Text
            {0x80064f20, {CODEC_UTF8, 1, 0, 0, F0100CBA014014000, 0x0100CBA014014000ull, "1.0.0"}}, // Choices
            // Ys X: Nordics
            {0x80817758, {CODEC_UTF8, 1, 0, 0, F0100CC401A16C000<0>, 0x0100CC401A16C000ull, "1.0.4"}}, // Main Text
            {0x80981e3c, {CODEC_UTF8, 0, 0, 0, F0100CC401A16C000<1>, 0x0100CC401A16C000ull, "1.0.4"}}, // Secondary Text
            // 9 R.I.P
            {0x80025360, {CODEC_UTF8, 2, 0, 0, F0100BDD01AAE4000, 0x0100BDD01AAE4000ull, "1.0.0"}}, // name
            {0x80023c60, {CODEC_UTF8, 0, 0, 0, F0100BDD01AAE4000, 0x0100BDD01AAE4000ull, "1.0.0"}}, // text
            {0x8005388c, {CODEC_UTF8, 1, 0, 0, F0100BDD01AAE4000, 0x0100BDD01AAE4000ull, "1.0.0"}}, // choice
            {0x80065010, {CODEC_UTF8, 0, 0, 0, F0100BDD01AAE4000, 0x0100BDD01AAE4000ull, "1.0.0"}}, // character description
            {0x8009c780, {CODEC_UTF8, 0, 0, 0, F0100BDD01AAE4000, 0x0100BDD01AAE4000ull, "1.0.0"}}, // prompt
            // キスベル
            {0x8049d958, {CODEC_UTF8, 1, 0, 0, F01006590155AC000, 0x0100BD7015E6C000ull, "1.0.0"}}, // text
            // ピオフィオーレの晩鐘 -Ricordo-  CN
            {0x80015fa0, {CODEC_UTF8, 2, 0, 0, F0100C310110B4000, 0x0100C310110B4000ull, "1.0.0"}}, // handlerMsg
            {0x80050d50, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x0100C310110B4000ull, "1.0.0"}}, // handlerName
            {0x8002F430, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x0100C310110B4000ull, "1.0.0"}}, // handlerPrompt
            {0x8002F4F0, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x0100C310110B4000ull, "1.0.0"}}, // handlerPrompt
            {0x8002F540, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x0100C310110B4000ull, "1.0.0"}}, // handlerPrompt
            // ピオフィオーレの晩鐘 -Ricordo-
            {0x800141d0, {CODEC_UTF8, 2, 0, 0, F0100C310110B4000, 0x01005F700DC56000ull, "1.0.0"}}, // handlerMsg
            {0x8004ce20, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01005F700DC56000ull, "1.0.0"}}, // handlerName
            {0x8002be90, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01005F700DC56000ull, "1.0.0"}}, // handlerPrompt
            {0x8002bf50, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01005F700DC56000ull, "1.0.0"}}, // handlerPrompt
            {0x8002bfa0, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01005F700DC56000ull, "1.0.0"}}, // handlerPrompt
            // ピオフィオーレの晩鐘 -Episodio1926-
            {0x80019630, {CODEC_UTF8, 2, 0, 0, F0100C310110B4000, 0x01009E30120F4000ull, "1.0.0"}}, // handlerMsg
            {0x8005B7B0, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01009E30120F4000ull, "1.0.0"}}, // handlerName
            {0x80039230, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01009E30120F4000ull, "1.0.0"}}, // handlerPrompt
            {0x800392F0, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01009E30120F4000ull, "1.0.0"}}, // handlerPrompt
            {0x80039340, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01009E30120F4000ull, "1.0.0"}}, // handlerPrompt
            // Pokémon Let’s Go, Pikachu!
            {0x8067d9fc, {CODEC_UTF16, 0, 0, 0, F010003F003A34000, 0x010003F003A34000ull, "1.0.2"}}, // Text
            // イケメン戦国◆時をかける恋 新たなる出逢い
            {0x813e4fb4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01008BE016CE2000ull, "1.0.0"}}, // Main Text
            {0x813e4c60, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01008BE016CE2000ull, "1.0.0"}}, // Name
            {0x813b5360, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x01008BE016CE2000ull, "1.0.0"}}, // Choices
            {0x81bab9ac, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, 0, 0x01008BE016CE2000ull, "1.0.0"}}, // Info
            // Shin Megami Tensei V
            {0x80ce01a4, {CODEC_UTF16, 0, 0, 0, 0, 0x01006BD0095F4000ull, "1.0.2"}}, // Text
            // The Legend of Zelda: Link's Awakening
            {0x80f57910, {CODEC_UTF8, 1, 0, 0, 0, 0x01006BB00C6F0000ull, "1.0.1"}}, // Main Text
            // Cendrillon palikA
            {0x8001ab8c, {CODEC_UTF8, 2, 0, 0, F0100DE200C0DA000, 0x01006B000A666000ull, "1.0.0"}}, // name
            {0x80027b30, {CODEC_UTF8, 0, 0, 0, F0100DE200C0DA000, 0x01006B000A666000ull, "1.0.0"}}, // dialogue
            // Crayon Shin-chan Shiro of Coal Town
            {0x83fab4bc, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F01007B601C608000, 0x01007B601C608000ull, "1.0.1"}},
            // 風雨来記4
            {0x80008c80, {CODEC_UTF32, 1, 0, 0, F010046601125A000, 0x010046601125A000ull, "1.0.0"}}, // Main
            {0x80012b1c, {CODEC_UTF32, 1, 0, 0, F010046601125A000, 0x010046601125A000ull, "1.0.0"}}, // Wordpad
            {0x80012ccc, {CODEC_UTF32, 1, 0, 0, F010046601125A000, 0x010046601125A000ull, "1.0.0"}}, // Comments
            {0x80009f74, {CODEC_UTF32, 1, 0, 0, F010046601125A000, 0x010046601125A000ull, "1.0.0"}}, // Choices
            {0x80023d64, {CODEC_UTF32, 0, 0, 0, F010046601125A000, 0x010046601125A000ull, "1.0.0"}}, // Location
            // 剣が君 for S
            {0x81477128, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100771013FA8000, 0x0100771013FA8000ull, "1.1"}}, // Main Text
            {0x81470e38, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100771013FA8000, 0x0100771013FA8000ull, "1.1"}}, // Secondary Text
            // ANONYMOUS;CODE
            {0x80011608, {CODEC_UTF8, 1, 0, 0, F0100556015CCC000, 0x0100556015CCC000ull, "1.0.0"}}, // dialouge, menu
            // Sugar * Style
            {0x800ccbc8, {0, 0, 0, 0, 0, 0x0100325012B70000ull, "1.0.0"}}, // ret x0 name + text (readShiftJisString), filter is to complex, quit.
            // Nightshade／百花百狼
            {0x802999c8, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010042300C4F6000, 0x010042300C4F6000ull, "1.0.1"}}, // dialogue
            {0x8015b544, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010042300C4F6000, 0x010042300C4F6000ull, "1.0.1"}}, // name
            {0x802a2fd4, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010042300C4F6000, 0x010042300C4F6000ull, "1.0.1"}}, // choice1
            {0x802b7900, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010042300C4F6000, 0x010042300C4F6000ull, "1.0.1"}}, // choice2
            // 囚われのパルマ
            {0x8015b7a8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010044800D2EC000, 0x010044800D2EC000ull, "1.0.0"}}, // text x0
            {0x8015b46c, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010044800D2EC000, 0x010044800D2EC000ull, "1.0.0"}}, // name x1
            // Brothers Conflict: Precious Baby
            {0x8016aecc, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100982015606000, 0x010037400DAAE000ull, "1.0.0"}}, // name
            {0x80126b9c, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100982015606000, 0x010037400DAAE000ull, "1.0.0"}}, // dialogue
            {0x80129160, {CODEC_UTF16, 2, 0, ReadTextAndLenW, F0100982015606000, 0x010037400DAAE000ull, "1.0.0"}}, // choice
            // 絶対階級学園 ~Eden with roses and phantasm~
            {0x80067b5c, {CODEC_UTF16, 1, 0, 0, F010021300F69E000<0>, 0x010021300F69E000ull, "1.0.0"}}, // name+ dialogue main(ADV)+choices
            {0x80067cd4, {CODEC_UTF16, 1, 0, 0, F010021300F69E000<1>, 0x010021300F69E000ull, "1.0.0"}}, // dialogueNVL
            // Dragon Quest Builders 2
            {0x805f8900, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Main text textbox
            {0x8068a698, {CODEC_UTF8, 0, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Not press to continue text
            {0x806e4118, {CODEC_UTF8, 3, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Character creation text
            {0x8067459c, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Objective progress1
            {0x800a4f90, {CODEC_UTF8, 0, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Objective progress2
            {0x8060a1c0, {CODEC_UTF8, 0, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Infos1
            {0x805f6130, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Infos2
            {0x80639b6c, {CODEC_UTF8, 2, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Item description
            {0x807185ac, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Mission1
            {0x80657e4c, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Mission2
            {0x80713be0, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Mission3
            {0x8076ab04, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Tutorial header
            {0x8076ab2c, {CODEC_UTF8, 1, 0, 0, F010050000705E000, 0x010050000705E000ull, "1.7.3"}}, // Tutorial explanation
            // BUSTAFELLOWS シーズン2
            {0x819ed3e4, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010037400DAAE000ull, "1.0.0"}}, // dialogue
            {0x82159cd0, {CODEC_UTF16, 1, 0, ReadTextAndLenW, F0100874017BE2000, 0x010037400DAAE000ull, "1.0.0"}}, // textmessage
            {0x81e17530, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010037400DAAE000ull, "1.0.0"}}, // option
            {0x81e99d64, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010037400DAAE000ull, "1.0.0"}}, // choice
            {0x8186f81c, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010037400DAAE000ull, "1.0.0"}}, // archives
            // 5分後に意外な結末　モノクロームの図書館
            {0x81fa4890, {CODEC_UTF16, 1, 0X14, 0, F010094601D910000, 0x010094601D910000ull, "1.0.1"}}, // book text
            {0x81fa5250, {CODEC_UTF16, 1, 0X14, 0, F010094601D910000, 0x010094601D910000ull, "1.0.1"}}, // book text
            {0x81b1c68c, {CODEC_UTF16, 0, 0X14, 0, F010094601D910000, 0x010094601D910000ull, "1.0.1"}}, // choice1
            {0x81b1c664, {CODEC_UTF16, 0, 0X14, 0, F010094601D910000, 0x010094601D910000ull, "1.0.1"}}, // choice2
            {0x81b1e5b0, {CODEC_UTF16, 3, 0X14, 0, F010094601D910000, 0x010094601D910000ull, "1.0.1"}}, // dialogue
            // うたの☆プリンスさまっ♪ Repeat LOVE
            {0x800374a0, {0, 0, 0, 0, F0100068019996000, 0x010024200E00A000ull, "1.0.0"}}, // Main Text + Name,sjis
            {0x8002ea08, {0, 0, 0, 0, F0100068019996000, 0x010024200E00A000ull, "1.0.0"}}, // Choices,sjis
            // ワンド オブ フォーチュン Ｒ～ for Nintendo Switch
            {0x81ed0580, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01000C7019E1C000ull, "1.0.0"}}, // dialogue
            {0x81f96bac, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01000C7019E1C000ull, "1.0.0"}}, // name
            {0x8250ac28, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01000C7019E1C000ull, "1.0.0"}}, // choice
            // ワンド オブ フォーチュン Ｒ２ ～時空に沈む黙示録～ for Nintendo Switch
            {0x821540c4, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100DA201E0DA000, 0x010088A01A774000ull, "1.0.0"}}, // dialogue
            {0x8353e674, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100DA201E0DA000, 0x010088A01A774000ull, "1.0.0"}}, // choice
            {0x835015e8, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100DA201E0DA000, 0x010088A01A774000ull, "1.0.0"}}, // name
            // Yo-kai Watch 4++
            {0x80a88080, {CODEC_UTF8, 1, 0, 0, F010086C00AF7C000, 0x010086C00AF7C000ull, "2.2.0"}}, // All Text
            // キューピット・パラサイト -Sweet & Spicy Darling.-
            {0x80138150, {CODEC_UTF32, 2, 0, 0, F010079C017B98000, 0x010079C017B98000ull, "1.0.0"}}, // name + text
            {0x801a1bf0, {CODEC_UTF32, 0, 0, 0, F010079C017B98000, 0x010079C017B98000ull, "1.0.0"}}, // choice
            // DesperaDrops
            {0x8199c95c, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010061A01C1CE000, 0x010061A01C1CE000ull, "1.0.0"}}, // text1
            {0x81d5c900, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010061A01C1CE000, 0x010061A01C1CE000ull, "1.0.0"}}, // text2
            {0x820d6324, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010061A01C1CE000, 0x010061A01C1CE000ull, "1.0.0"}}, // choice
            // Dragon Ball Z: Kakarot
            {0x812a8e28, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Main Text
            {0x812a8c90, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Name
            {0x80bfbff0, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Ptc Text
            {0x80bfbfd4, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Ptc Name
            {0x8126a538, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Info
            {0x8106fcbc, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // More Info
            {0x80fad204, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Hint Part1
            {0x80fad2d0, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Hint Part2
            {0x80facf1c, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Loading Title
            {0x80fad018, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Loading Description
            {0x81250c50, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Tutorial h1
            {0x81250df0, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Tutorial h2
            {0x81251e80, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Tutorial Description1
            {0x81252214, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Tutorial Description2
            {0x810ae1c4, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Config Description
            {0x812a9bb8, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Menu Talk
            {0x812a9b78, {CODEC_UTF16, 0, 0, 0, F01008C0016544000, 0x0100EF00134F4000ull, "1.50"}}, // Menu Name
            // Harvestella
            {0x80af7abc, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Main Text
            {0x80c0beb8, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Tutorial + News
            {0x80b87f94, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Tutorial Part 2
            {0x80e1c378, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Mission Title
            {0x80a7d7f4, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Mission Description
            {0x80e39130, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Item Name
            {0x80e38f80, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Item Description Part1
            {0x80e38ea8, {CODEC_UTF16, 0, 0, 0, F0100B0601852A000, 0x0100EDD018032000ull, "1.0.1"}}, // Item Description Part2
            // 千の刃濤、桃花染の皇姫
            {0x8003fc90, {CODEC_UTF8, 1, 0, 0, 0, 0x0100F8A017BAA000ull, "1.0.0"}}, // text1
            {0x8017a740, {CODEC_UTF8, 0, 0, 0, 0, 0x0100F8A017BAA000ull, "1.0.0"}}, // text2
            // オランピアソワレ
            {0x8002ad60, {CODEC_UTF8, 31, 0, 0, F0100C310110B4000, 0x0100F9D00C186000ull, "1.0.0"}},
            {0x8004b9e0, {CODEC_UTF8, 1, 0, 0, F0100C310110B4000, 0x0100F9D00C186000ull, "1.0.0"}},
            // 月影の鎖 -錯乱パラノイア-
            {0x21801c, {0, 2, 0, 0, F0100F7401AA74000, 0x0100F7401AA74000ull, "1.0.0"}}, // text,sjis
            {0x228fac, {0, 1, 0, 0, F0100F7401AA74000, 0x0100F7401AA74000ull, "1.0.0"}}, // choices
            {0x267f24, {0, 1, 0, 0, F0100F7401AA74000, 0x0100F7401AA74000ull, "1.0.0"}}, // dictionary
            // Xenoblade Chronicles 2
            {0x8010b180, {CODEC_UTF8, 1, 0, 0, F01006F000B056000, 0x0100F3400332C000ull, "2.0.2"}}, // Text
            // Kanon
            {0x800dc524, {CODEC_UTF16, 0, 0, 0, F0100FB7019ADE000, 0x0100FB7019ADE000ull, "1.0.0"}}, // Text
            // Princess Arthur
            {0x80066e10, {0, 2, 0, 0, F0100FC2019346000, 0x0100FC2019346000ull, "1.0.0"}}, // Dialogue text ,sjis
            {0x8001f7d0, {0, 0, 0, 0, F0100FC2019346000, 0x0100FC2019346000ull, "1.0.0"}}, // Name
            // Layton’s Mystery Journey: Katrielle and the Millionaires’ Conspiracy
            {0x8025d520, {0, 2, 0, 0, F0100FDB00AA80000, 0x0100FDB00AA80000ull, "1.1.0"}}, // All Text ,sjis
            // Xenoblade Chronicles: Definitive Edition
            {0x808a5670, {CODEC_UTF8, 1, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Main Text
            {0x80305968, {CODEC_UTF8, 1, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Choices
            {0x8029edc8, {CODEC_UTF8, 0, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Item Name
            {0x8029ede8, {CODEC_UTF8, 0, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Item Description
            {0x8026a454, {CODEC_UTF8, 0, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Acquired Item Name
            {0x803c725c, {CODEC_UTF8, 0, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Acquired Item Notification
            {0x802794cc, {CODEC_UTF8, 0, 0, 0, F0100FF500E34A000, 0x0100FF500E34A000ull, "1.1.2"}}, // Location Discovered
            // Unicorn Overlord -国王的假日-
            {0x805ae1f8, {CODEC_UTF8, 1, 0, 0, F01000AE01954A000, 0x01000AE01954A000ull, "1.00"}}, // Text
            // Octopath Traveler
            {0x8005ef78, {CODEC_UTF32, 0, 0, 0, 0, 0x01000E200DC58000ull, "1.0.0"}}, // Text
            // The World Ends with You: Final Remix
            {0x80706ab8, {CODEC_UTF16, 2, 0, 0, F01006F000B056000, 0x01001C1009892000ull, "1.0.0"}}, // Text
            // JackJanne
            {0x81f02cd8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100982015606000, 0x01001DD010A2E800ull, "1.0.5"}}, // Text
            {0x821db028, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100982015606000, 0x01001DD010A2E800ull, "1.0.5"}}, // choice
            // Collar x Malice
            {0x800444c4, {CODEC_UTF8, 0, 0, 0, 0, 0x01002B400E9DA000ull, "1.0.0"}}, // Text
            // 神田アリスも推理スル。
            {0x80041db0, {0, 0, 0, 0, F01003BD013E30000, 0x01003BD013E30000ull, "1.0.0"}}, // sjis
            // Rune Factory 3 Special
            {0x81fb3364, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Main Text
            {0x826c0f20, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Aproach
            {0x81fb3320, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Choices
            {0x821497e8, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Calendar
            {0x826ba1a0, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Info
            {0x823f6200, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // More Info
            {0x826c381c, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01001EF017BE6000, 0x01001EF017BE6000ull, "1.0.4"}}, // Item Select Name
            // 囚われのパルマ Refrain
            {0x80697300, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01000EA00D2EE000, 0x01000EA00D2EE000ull, "1.0.0"}}, // text x1
            {0x806f43c0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01000EA00D2EE000, 0x01000EA00D2EE000ull, "1.0.0"}}, // name x0
            {0x80d2aca4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01000EA00D2EE000, 0x01000EA00D2EE000ull, "1.0.0"}}, // choice x0
            {0x804b04c8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01000EA00D2EE000, 0x01000EA00D2EE000ull, "1.0.0"}}, // alert x0
            {0x804b725c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01000EA00D2EE000, 0x01000EA00D2EE000ull, "1.0.0"}}, // prompt x0
            // 穢翼のユースティア
            {0x804BEFD0, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01001CC017BB2000ull, "1.0.0"}}, // x0 - name
            {0x804BEFE8, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01001CC017BB2000ull, "1.0.0"}}, // x0 - dialogue
            {0x804d043c, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x01001CC017BB2000ull, "1.0.0"}}, // x0 - choice
            // 蛇香のライラ ～Allure of MUSK～
            {0x80167100, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x1 text + name (unformated), #T1 #T2, #T0  1. European night
            {0x801589a0, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x0=x1=choice (sig=SltAdd)
            {0x801b4300, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x1 text + name (unformated), #T1 #T2, #T0  2. Asian night
            {0x802a9170, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x0=x1=choice (sig=SltAdd)
            {0x80301e80, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x1 text + name (unformated), #T1 #T2, #T0  3. Arabic night
            {0x803f7a90, {CODEC_UTF32, 1, 0, 0, F010093800DB1C000, 0x010093800DB1C000ull, "1.0.0"}}, // x0=x1=choice (sig=SltAdd)
            // ガレリアの地下迷宮と魔女ノ旅団
            {0x8002f64c, {CODEC_UTF8, 0, 0, 0, 0, 0x01007010157B4000ull, "1.0.1"}}, // Main Text
            // Dragon's Dogma: Dark Arisen
            {0x81023a80, {CODEC_UTF8, 1, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Main Text
            {0x8103e140, {CODEC_UTF8, 1, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Allies + Cutscene Text
            {0x8103bb10, {CODEC_UTF8, 1, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // NPC Text
            {0x80150720, {CODEC_UTF8, 0, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Intro Message
            {0x80df90a8, {CODEC_UTF8, 0, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Info1
            {0x80ce2bb8, {CODEC_UTF8, 0, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Info2
            {0x80292d84, {CODEC_UTF8, 0, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Info Popup1
            {0x80cfac6c, {CODEC_UTF8, 0, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Info Popup2
            {0x8102d460, {CODEC_UTF8, 1, 0, 0, F010057E00AC56000, 0x010057E00AC56000ull, "1.0.1"}}, // Description
            // Yo-kai Watch Jam - Yo-kai Academy Y: Waiwai Gakuen
            {0x80dd0cec, {CODEC_UTF8, 0, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Dialogue text
            {0x80e33450, {CODEC_UTF8, 3, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Other Dialogue text
            {0x80c807c0, {CODEC_UTF8, 0, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Item description etc text
            {0x808d9a30, {CODEC_UTF8, 0, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Tutorial Text
            {0x811b95ac, {CODEC_UTF8, 3, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Menu screen
            {0x80e20290, {CODEC_UTF8, 3, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Opening Song Text etc
            {0x80c43680, {CODEC_UTF8, 3, 0, 0, F010051D010FC2000, 0x010051D010FC2000ull, "4.0.0"}}, // Cutscene Text
            // NEO: The World Ends With You
            {0x81581d6c, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Text
            {0x818eb248, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Objective
            {0x81db84a4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Menu: Collection Item Name
            {0x81db8660, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Menu: Collection Item Description
            {0x81c71a48, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Tutorial Title
            {0x81c71b28, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010043B013C5C000, 0x010043B013C5C000ull, "1.03"}}, // Tutorial Description
            // Eiyuden Chronicle: Rising
            {0x82480190, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Main Text
            {0x824805d0, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Name
            {0x81f05c44, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Intro Text
            {0x82522ac4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Character Info
            {0x81b715f4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Info
            {0x825274d0, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Info2
            {0x825269b0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Tutorial Title
            {0x82526a0c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Tutorial Description
            {0x82523e04, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Objective Title
            {0x82524160, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Objective Description
            {0x81f0351c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Location Selection Title
            {0x81f0358c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Location Selection Description
            {0x81f0d520, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Quest Title
            {0x81f0d58c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Quest Description
            {0x81f00318, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Help Title
            {0x81f00368, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Help Description
            {0x81f0866c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, 0, 0x010039B015CB6000ull, "1.02"}}, // Config Description
            // Ghost Trick: Phantom Detective
            {0x81448898, {CODEC_UTF16, 0, 0, 0, F010043B013C5C000, 0x010029B018432000ull, "1.0.0"}}, // Main Text
            {0x80c540d4, {CODEC_UTF16, 0, 0, 0, F010043B013C5C000, 0x010029B018432000ull, "1.0.0"}}, // Secondary Text
            {0x80e50dd4, {CODEC_UTF16, 0, 0, 0, F010043B013C5C000, 0x010029B018432000ull, "1.0.0"}}, // Object Name
            {0x80f91c08, {CODEC_UTF16, 0, 0, 0, F010043B013C5C000, 0x010029B018432000ull, "1.0.0"}}, // Language Selection
            {0x805c9014, {CODEC_UTF16, 0, 0, 0, F010043B013C5C000, 0x010029B018432000ull, "1.0.0"}}, // Story/Character Info
            // ひぐらしのなく頃に奉
            {0x800bd6c8, {0, 0, 0, 0, F0100F6A00A684000, 0x0100F6A00A684000ull, "1.0.0"}}, // sjis
            {0x800c2d20, {0, 0, 0, 0, F0100F6A00A684000, 0x0100F6A00A684000ull, "1.2.0"}}, // sjis
            // うみねこのなく頃に咲 ～猫箱と夢想の交響曲～
            {0x800b4560, {CODEC_UTF8, 0, 0, 0, 0, 0x01006A300BA2C000ull, "1.0.0"}}, // x0 name + text (bottom, center) - whole line. filter is to complex, quit.
            {0x801049c0, {CODEC_UTF8, 0, 0, 0, 0, 0x01006A300BA2C000ull, "1.0.0"}}, // x0 prompt, bottomLeft
            {0x80026378, {CODEC_UTF8, 0, 0, 0, 0, 0x01006A300BA2C000ull, "1.0.0"}}, // x0 Yes|No
            {0x801049a8, {CODEC_UTF8, 0, 0, 0, 0, 0x01006A300BA2C000ull, "1.0.0"}}, // x0 topLeft (double: ♪ + text)
            // 殺し屋とストロベリー
            {0x81322cec, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F010042300C4F6000, 0x0100E390145C8000ull, "1.0.0"}}, // dialogue
            {0x819b1a78, {CODEC_UTF16, 2, 0, ReadTextAndLenW, F010042300C4F6000, 0x0100E390145C8000ull, "1.0.0"}}, // dialogue
            {0x81314e8c, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F010042300C4F6000, 0x0100E390145C8000ull, "1.0.0"}}, // dialogue
            // ときめきメモリアル Girl's Side
            {0x822454a4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // dialogue1
            {0x82247138, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // dialogue2
            {0x822472e0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // dialogue3
            {0x82156988, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // choice
            {0x82642200, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // option1
            {0x81ecd758, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // option2
            {0x823185e4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // mail
            {0x823f2edc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // roomDescript
            {0x821e3cf0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // dateDescript
            {0x81e20050, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // characterDesc1
            {0x81e1fe50, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // characterDesc2
            {0x81e1feb0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // characterDesc3
            {0x81e1ff04, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // characterDesc4
            {0x821d03b0, {CODEC_UTF16, 3, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // news
            {0x82312008, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100D9A01BD86000, 0x0100D9A01BD86000ull, "1.0.1"}}, // luckyitem
            {0x8093F4F4, {CODEC_UTF8, 1, 0, 0, F0100D9A01BD86000_0, 0x0100D9A01BD86000ull, "1.0.0"}},               // text
            // ときめきメモリアル Girl’s Side 2nd Kiss
            {0x82058848, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // dialogue1
            {0x82058aa0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // dialogue2
            {0x8205a244, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // dialogue3
            {0x826ee1d8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // choice
            {0x8218e258, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // news
            {0x823b61d4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // mail
            {0x82253454, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // luckyitem
            {0x82269240, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // profile1
            {0x82269138, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // profile2
            {0x822691ec, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // profile3
            {0x82269198, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F010079201BD88000, 0x010079201BD88000ull, "1.0.1"}}, // profile4
            // ときめきメモリアル Girl's Side 4th Heart
            {0x817e7da8, {CODEC_UTF16, 2, 0, T0100B0100E26C000, F0100982015606000, 0x0100B0100E26C000ull, "1.0.0"}}, // name (x1) + dialogue (x2)
            {0x81429f54, {CODEC_UTF16, 0, 1, T0100B0100E26C000, F0100982015606000, 0x0100B0100E26C000ull, "1.0.0"}}, // choice (x0)
            {0x8180633c, {CODEC_UTF16, 1, 2, T0100B0100E26C000, F0100982015606000, 0x0100B0100E26C000ull, "1.0.0"}}, // help (x1)
            // Triangle Strategy
            {0x80aadebc, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<0>, 0x0100CC80140F8000ull, "1.1.0"}}, // Main Text
            {0x81358ce4, {CODEC_UTF16, 3, 0, 0, F0100CC80140F8000<1>, 0x0100CC80140F8000ull, "1.1.0"}}, // Secondary Text
            {0x80a38988, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<2>, 0x0100CC80140F8000ull, "1.1.0"}}, // Info Contents
            {0x80aa4aec, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<3>, 0x0100CC80140F8000ull, "1.1.0"}}, // Info
            {0x80b1f300, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<4>, 0x0100CC80140F8000ull, "1.1.0"}}, // Difficulty Selection Part1
            {0x80b1f670, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<5>, 0x0100CC80140F8000ull, "1.1.0"}}, // Difficulty Selection Part2
            {0x80aa48f0, {CODEC_UTF16, 0, 0, 0, F0100CC80140F8000<6>, 0x0100CC80140F8000ull, "1.1.0"}}, // PopUp Message
            // Xenoblade Chronicles 3
            {0x80cf6ddc, {CODEC_UTF8, 0, 0, 0, F010074F013262000, 0x010074F013262000ull, "2.2.0"}}, // Main Text
            {0x80e76150, {CODEC_UTF8, 0, 0, 0, F010074F013262000, 0x010074F013262000ull, "2.2.0"}}, // Secondary Text
            {0x807b4ee4, {CODEC_UTF8, 1, 0, 0, F010074F013262000, 0x010074F013262000ull, "2.2.0"}}, // Tutorial Description
            {0x80850218, {CODEC_UTF8, 0, 0, 0, F010074F013262000, 0x010074F013262000ull, "2.2.0"}}, // Objective
            // CLOCK ZERO 〜終焉の一秒〜
            {0x8003c290, {0, 0, 0, 0, F0100BDD01AAE4000, 0x01008C100C572000ull, "1.0.0"}}, // name,sjis
            {0x8003c184, {0, 0, 0, 0, F0100BDD01AAE4000, 0x01008C100C572000ull, "1.0.0"}}, // dialogue
            {0x8001f6d0, {0, 0, 0, 0, F0100BDD01AAE4000, 0x01008C100C572000ull, "1.0.0"}}, // prompt
            // 終遠のヴィルシュ -ErroR:salvation-
            {0x8001f594, {CODEC_UTF8, 0, 0x1C, 0, F0100C310110B4000, 0x01005B9014BE0000ull, "1.0.0"}}, // dialog
            {0x8001f668, {CODEC_UTF8, 0, 0x1C, 0, F0100C310110B4000, 0x01005B9014BE0000ull, "1.0.0"}}, // center
            {0x8003d540, {CODEC_UTF8, 0, 0, 0, F0100C310110B4000, 0x01005B9014BE0000ull, "1.0.0"}},    // choice
            // 終遠のヴィルシュ -EpiC:lycoris-
            {0x8002bf6c, {CODEC_UTF8, 0, 0x1c, 0, FF010061300DF48000_2, 0x01004D601B0AA000ull, "1.0.1"}},
            {0x8004e720, {CODEC_UTF8, 1, 0, 0, FF010061300DF48000_2, 0x01004D601B0AA000ull, "1.0.1"}},
            // スペードの国のアリス ～Wonderful White World～
            {0x8135d018, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01008C0016544000, 0x01003FE00E2F8000ull, "1.0.0"}}, // Text + Name
            // スペードの国のアリス ～Wonderful Black World～
            {0x819dbdc8, {CODEC_UTF16, 0, 0x14, 0, F0100AB100E2FA000, 0x0100AB100E2FA000ull, "1.0.0"}},
            {0x81f8e564, {CODEC_UTF16, 1, 0x14, 0, F0100AB100E2FA000, 0x0100AB100E2FA000ull, "1.0.0"}},
            // 十三支演義 偃月三国伝1・2 for Nintendo Switch (Juuzaengi ~Engetsu Sangokuden~)
            {0x82031f20, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01003D2017FEA000ull, "1.0.0"}}, // name
            {0x82ef9550, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01003D2017FEA000ull, "1.0.0"}}, // dialogue
            {0x83252e0c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100DA201E0DA000, 0x01003D2017FEA000ull, "1.0.0"}}, // choice
            // Tales of Vesperia: Definitive Edition
            {0x802de170, {CODEC_UTF8, 2, 0, 0, F01002C0008E52000, 0x01002C0008E52000ull, "1.0.2"}}, // Ptc Text
            {0x802cf170, {CODEC_UTF8, 3, 0, 0, F01002C0008E52000, 0x01002C0008E52000ull, "1.0.2"}}, // Cutscene
            {0x8019957c, {CODEC_UTF8, 0, 0, 0, F01002C0008E52000, 0x01002C0008E52000ull, "1.0.2"}}, // Conversation
            {0x802c0600, {CODEC_UTF8, 2, 0, 0, F01002C0008E52000, 0x01002C0008E52000ull, "1.0.2"}}, // Info
            {0x801135fc, {CODEC_UTF8, 0, 0, 0, F01002C0008E52000, 0x01002C0008E52000ull, "1.0.2"}}, // Post Battle Text
            // Nil Adminari no Tenbin Irodori Nadeshiko
            {0x8005fd5c, {CODEC_UTF8, 0, 0, 0, F0100BDD01AAE4000, 0x01002BB00A662000ull, "1.0.0"}},  // name
            {0x800db0d8, {CODEC_UTF8, 0, 20, 0, F0100BDD01AAE4000, 0x01002BB00A662000ull, "1.0.0"}}, // name
            // 華ヤカ哉、我ガ一族 モダンノスタルジィ
            {0x2509ac, {CODEC_UTF8, 0, 0, T0100B5500CA0C000, F0100B5500CA0C000, 0x01008DE00C022000ull, "1.0.0"}},
            // 華ヤカ哉、我ガ一族 幻燈ノスタルジィ
            {0x27ca10, {CODEC_UTF8, 0, 0, T0100B5500CA0C000, F0100B5500CA0C000, 0x0100B5500CA0C000ull, "1.0.0"}}, // x3 (double trigged), name+text, onscreen
            // 超探偵事件簿 レインコード
            {0x80bf2034, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Dialogue text
            {0x80c099d4, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Cutscene text
            {0x80cbf1f4, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Menu
            {0x80cbc11c, {CODEC_UTF16, 0, 0, 0, F0100DA201E0DA000, 0x0100F4401940A000ull, "1.3.3"}}, // Menu Item Description
            {0x80cacc14, {CODEC_UTF16, 0, 0, 0, F0100DA201E0DA000, 0x0100F4401940A000ull, "1.3.3"}}, // Menu Item Description 2
            {0x80cd6410, {CODEC_UTF16, 0, 0, 0, F0100DA201E0DA000, 0x0100F4401940A000ull, "1.3.3"}}, // Menu Item Description 3
            {0x80c214d4, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Description
            {0x80cc9908, {CODEC_UTF16, 0, 0, 0, F0100DA201E0DA000, 0x0100F4401940A000ull, "1.3.3"}}, // Mini game item description
            {0x80bce36c, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Tutorial
            {0x80bcb7d4, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Loading Screen information
            {0x80bf32d8, {CODEC_UTF16, 0, 0, 0, F0100F4401940A000, 0x0100F4401940A000ull, "1.3.3"}}, // Choices
            // Fire Emblem: Three Houses
            {0x8041e6bc, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Main Text
            {0x805ca570, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Cutscene Text
            {0x8049f1e8, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Cutscene Text Scroll
            {0x805ee730, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Info
            {0x805ee810, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Info Choice
            {0x80467a60, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Location First Part
            {0x805f0340, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Location Second Part
            {0x801faae4, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Action Location
            {0x803375e8, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Objective
            {0x805fd870, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Tutorial
            {0x804022f8, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Request
            {0x802f7df4, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Quest Description
            {0x8031af0c, {CODEC_UTF8, 0, 0, 0, F010055D009F78000, 0x010055D009F78000ull, "1.2.0"}}, // Aproach Text
            // SWEET CLOWN ~午前三時のオカシな道化師~
            {0x20dbfc, {0, 0, 0x28, 0, F010028D0148E6000, 0x010028D0148E6000ull, "1.2.0"}},          // dialog, sjis
            {0x214978, {0, 2, 0xC, 0, F010028D0148E6000, 0x010028D0148E6000ull, "1.2.0"}},           // choices
            {0x218B40, {FULL_STRING, 1, 0, 0, F010028D0148E6000_2, 0x010028D0148E6000ull, "1.0.1"}}, // TEXT
            {0x20D420, {0, 0, 0, 0, 0, 0x010028D0148E6000ull, "1.0.1"}},                             // NAME+TEXT
            // アナザーコード リコレクション：２つの記憶 / 記憶の扉
            {0x82dcad30, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Main Text
            {0x82f2cfb0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Item Description
            {0x82dcc5fc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Tutorial PopUp Header
            {0x82dcc61c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Tutorial PopUp Description
            {0x82f89e78, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Aproach Text
            {0x82973300, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Chapter
            {0x82dd2604, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Location
            {0x82bcb77c, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Save Message
            {0x828ccfec, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Acquired Item
            {0x83237b14, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Question Options
            {0x82dcee10, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Tutorial Header
            {0x82dcee38, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Tutorial Description
            {0x82e5cadc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Character Info Name
            {0x82e5cc38, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Character Info Description
            {0x82871ac8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Letter Message
            {0x82e4dad4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // アナザーキー
            {0x82bd65d0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Message Title
            {0x82bd65f0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Message Content
            {0x82c1ccf0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Decision Header
            {0x82c1d218, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Decision1
            {0x82c1e43c, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100CB9018F5A000, 0x0100CB9018F5A000ull, "1.0.0"}}, // Decision2
            // AI：ソムニウム ファイル
            {0x8165a9a4, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100C7400CFB4000, 0x0100C7400CFB4000ull, "1.0.2"}}, // Main Text + Tutorial
            {0x80320dd4, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100C7400CFB4000, 0x0100C7400CFB4000ull, "1.0.2"}}, // Menu Interface Text1
            {0x80320e20, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F0100C7400CFB4000, 0x0100C7400CFB4000ull, "1.0.2"}}, // Menu Interface Text2
            // AI: ソムニウムファイル ニルヴァーナイニシアチブ
            {0x8189ae64, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // Main Text + Tutorial
            {0x81813428, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // Hover Investigation Text
            {0x82e122b8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // Info
            {0x82cffff8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // Config Description
            {0x818c3cd8, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // File: Names
            {0x82ea1a38, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // File: Contents
            {0x82cbb1fc, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F0100BD4014D8C000, 0x0100BD4014D8C000ull, "1.0.1"}}, // Investigation Choices
            // ファタモルガーナの館 -DREAMS OF THE REVENANTS EDITION-
            {0x8025a998, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01008C0016544000, 0x0100BE40138B8000ull, "1.0.1"}}, // Main Text
            {0x801d6050, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01008C0016544000, 0x0100BE40138B8000ull, "1.0.1"}}, // Choices
            // Ni no Kuni II: Revenant Kingdom
            {0x80ac651c, {CODEC_UTF8, 0, 0, 0, F0100C4E013E5E000, 0x0100C4E013E5E000ull, "1.0.0"}}, // Main Text
            {0x80335ea0, {CODEC_UTF8, 0, 0, 0, F0100C4E013E5E000, 0x0100C4E013E5E000ull, "1.0.0"}}, // Name
            // 遙かなる時空の中で7
            {0x800102bc, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100CF400F7CE000ull, "1.0.0"}}, // name, sjis
            {0x80051f90, {0, 1, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100CF400F7CE000ull, "1.0.0"}}, // text
            {0x80010b48, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100CF400F7CE000ull, "1.0.0"}}, // prompt
            {0x80010c80, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100CF400F7CE000ull, "1.0.0"}}, // choice
            // アンジェリーク ルミナライズ
            {0x80046c04, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100D11018A7E000ull, "1.0.0"}}, // ingameDialogue, sjis
            {0x80011284, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100D11018A7E000ull, "1.0.0"}}, // choice
            {0x80011140, {0, 0, 0, T0100CF400F7CE000, F0100CF400F7CE000, 0x0100D11018A7E000ull, "1.0.0"}}, // prompt first
            // Star Ocean The Second Story R
            {0x81d5e4d0, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Main Text + Tutorial
            {0x81d641b4, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Intro Cutscene
            {0x824b1f00, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Character Selection Name
            {0x81d4c670, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Character Selection Lore
            {0x8203a048, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // General Description
            {0x82108cd0, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Unique Spot Title
            {0x827a9848, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Chest Item
            {0x82756890, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Info
            {0x82241410, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Menu Talk
            {0x81d76404, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Secondary Talk
            {0x821112e0, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Location
            {0x82111320, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Location Interior
            {0x81d6ea24, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Special Arts/Spells Name
            {0x81d6ea68, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Special Arts/Spells Description
            {0x81d6ed48, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Special Arts/Spells Range
            {0x81d6eb3c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Special Arts/Spells Effect
            {0x81d6f880, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Special Arts/Spells Bonus
            {0x8246d81c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Tactics Name
            {0x8246d83c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Tactics Description
            {0x8212101c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Achievements Name
            {0x82121088, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Achievements Description
            {0x81d6c480, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Acquired Item1
            {0x821143f0, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Acquired Item2
            {0x81d6fb18, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Skill Name
            {0x81d6fb4c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Skill Description
            {0x81d6fb7c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Skill Bonus Description
            {0x8212775c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Item Name
            {0x82127788, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Item Description
            {0x821361ac, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Ability Name
            {0x821361f4, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Ability Range
            {0x82136218, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Ability Effect
            {0x8238451c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Strategy Name
            {0x82134610, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Battle Acquired Item
            {0x824b5eac, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Item Name
            {0x824b5f04, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Item Description
            {0x824b5f54, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Item Effect
            {0x81d71790, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Item Factor Title
            {0x824b62c0, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Item Factor Description
            {0x824c2e2c, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Skills Name
            {0x824c2e54, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Skills Description
            {0x824c2fbc, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Skills Level
            {0x823e7230, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Name
            {0x823e94bc, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Description
            {0x823e9980, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Talent
            {0x823ea9c4, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // IC/Specialty Support Item
            {0x82243b18, {0, 1, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Enemy Info Skills
            {0x81d64540, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Guild Mission Description
            {0x823b4f6c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Guild Mission Reward
            {0x826facd8, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Challenge Mission Description
            {0x826f98f8, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Challenge Mission Reward
            {0x8244af2c, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Formation Name
            {0x8244ae90, {0, 0, 0, ReadTextAndLenDW, F010065301A2E0000, 0x010065301A2E0000ull, "1.0.2"}}, // Formation Description
            // 魔法使いの夜 通常版
            {0x80086ba0, {CODEC_UTF8, 0, 0, T010012A017F18000, 0, 0x010012A017F18000ull, "1.0.0"}},
            {0x80086e70, {CODEC_UTF8, 0, 0, T010012A017F18000, 0, 0x010012A017F18000ull, "1.0.2"}},
            // 月姫 -A piece of blue glass moon-
            {0x800ac290, {CODEC_UTF8, 0, 0, T010012A017F18000, 0, 0x01001DC01486A000ull, 0}}, // 1.0.1,1.0.2
            // 映画 五等分の花嫁　～君と過ごした五つの思い出～ (JP)
            {0x80011688, {CODEC_UTF8, 1, 0, 0, F01005E9016BDE000, 0x01005E9016BDE000ull, "1.0.0"}}, // dialogue, menu, choice, name
            // FLOWERS 四季
            {0x8006f940, {CODEC_UTF16, 1, 0, 0, F01002AE00F442000, 0x01002AE00F442000ull, "1.0.1"}},
            // 最悪なる災厄人間に捧ぐ
            {0x8034EB44, {CODEC_UTF16, 8, 0, 0, F01000A400AF2A000, 0x01000A400AF2A000ull, "1.0.0"}}, // text
            // 神様のような君へ
            {0x80487CD0, {CODEC_UTF8, 0, 0, 0, F01006B5014E2E000, 0x01006B5014E2E000ull, "1.0.0"}}, // text
            // BUSTAFELLOWS
            {0x80191b18, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010060800B7A8000ull, "1.1.3"}}, // Dialogue
            {0x80191f88, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010060800B7A8000ull, "1.1.3"}}, // Choice
            {0x801921a4, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010060800B7A8000ull, "1.1.3"}}, // Choice 2
            {0x801935f0, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F0100874017BE2000, 0x010060800B7A8000ull, "1.1.3"}}, // option
            // 猛獣使いと王子様 ～Flower ＆ Snow～ for Nintendo Switch
            {0x800a1a10, {CODEC_UTF8, 1, 0, 0, F01001B900C0E2000, 0x01001B900C0E2000ull, "1.0.0"}}, // Dialogue 1
            {0x80058f80, {CODEC_UTF8, 1, 0, 0, F01001B900C0E2000, 0x01001B900C0E2000ull, "1.0.0"}}, // Dialogue 2
            // Detective Pikachu Returns
            {0x81585750, {CODEC_UTF16, 2, 0, ReadTextAndLenDW, F010007500F27C000, 0x010007500F27C000ull, "1.0.0"}}, // All Text
            // Dragon Quest Treasures
            {0x80bd62c4, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Cutscene
            {0x80a74b64, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Ptc Text
            {0x80a36d18, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Info
            {0x80c43878, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Tutorial Title
            {0x80c43d50, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Tutorial Description
            {0x80a72598, {CODEC_UTF16, 0, 0, 0, F0100217014266000, 0x0100217014266000ull, "1.0.1"}}, // Aproach Text
            // Rune Factory 4 Special
            {0x48b268, {CODEC_UTF8, 3, 0, 0, F010027100C79A000, 0x010027100C79A000ull, "1.0.1"}}, // All Text
            // The Legend of Zelda: Skyward Sword HD
            {0x80dc36dc, {CODEC_UTF16 | FULL_STRING, 3, 0, 0, F01001EF017BE6000, 0x01002DA013484000ull, "1.0.1"}}, // All Text
            // World of Final Fantasy Maxima
            {0x8068fea0, {CODEC_UTF8, 0, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Cutscene
            {0x802c6a48, {CODEC_UTF8, 0, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Action Text
            {0x803a523c, {CODEC_UTF8, 1, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Location
            {0x8041ed64, {CODEC_UTF8, 0, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Info
            {0x802c9f1c, {CODEC_UTF8, 0, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Chapter First Part
            {0x802c9f6c, {CODEC_UTF8, 0, 0, 0, F010072000BD32000, 0x010072000BD32000ull, "1.0.0"}}, // Chapter Second Part
            // Tokyo Xanadu eX+
            {0x8025135c, {CODEC_UTF8, 1, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Name
            {0x80251068, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Main Text
            {0x802ac86c, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Action Text
            {0x802b04b4, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Choices
            {0x8013243c, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Location
            {0x802b1f3c, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Info
            {0x802ab46c, {CODEC_UTF8, 0, 0, 0, F010080C01AA22000, 0x010080C01AA22000ull, "1.0.0"}}, // Documents
            // DORAEMON STORY OF SEASONS: Friends of the Great Kingdom
            {0x839558e4, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01009B50139A8000, 0x01009B50139A8000ull, "1.1.1"}}, // Text
            {0x8202a9b0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01009B50139A8000, 0x01009B50139A8000ull, "1.1.1"}}, // Tutorial
            // Monster Hunter Stories 2: Wings of Ruin
            {0x8042fe60, {CODEC_UTF8, 1, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Cutscene
            {0x804326c0, {CODEC_UTF8, 1, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Ptc Text
            {0x804d3d44, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Info
            {0x8045e7c8, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Info Choice
            {0x805cec4c, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Config Header
            {0x8078c2d0, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Config Name+
            {0x805d0858, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Config Description
            {0x807612d4, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Notice
            {0x807194a0, {CODEC_UTF8, 1, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Update Content + Tutorial
            {0x804d687c, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Objective Title
            {0x804d6a7c, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Objective Description
            {0x80509900, {CODEC_UTF8, 0, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Aproach Text
            {0x8060ee90, {CODEC_UTF8, 1, 0, 0, F0100CB700D438000, 0x0100CB700D438000ull, "1.5.2"}}, // Acquired Item
            // ２０４５、月より。
            {0x80016334, {CODEC_UTF8, 1, 0, 0, F01005C301AC5E000, 0x01005C301AC5E000ull, "1.0.1"}},
            // ヤマノススメ Next Summit ～あの山に、もう一度～
            {0x806E1444, {CODEC_UTF8, 0, 0, 0, F0100815019488000_text, 0x0100815019488000ull, "1.0.0"}},
            {0x80659EE0, {CODEC_UTF8, 1, 0, 0, F0100815019488000_name, 0x0100815019488000ull, "1.0.0"}},
            // プリズンプリンセス
            {0x800eba00, {CODEC_UTF16, 2, 0x14, 0, 0, 0x0100F4800F872000ull, "1.0.0"}},
            // 泡沫のユークロニア
            {0x8180de40, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F010027401A2A2000<false>, 0x010027401A2A2000ull, "1.0.0"}}, // text box
            {0x816b61c0, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F010027401A2A2000<false>, 0x010027401A2A2000ull, "1.0.0"}}, // dictionary
            {0x815fe594, {CODEC_UTF16, 0, 0, ReadTextAndLenW, F010027401A2A2000<true>, 0x010027401A2A2000ull, "1.0.0"}},  // choices
            {0x81836E0C, {CODEC_UTF16, 1, 0, 0, F010027401A2A2000_2, 0x010027401A2A2000ull, "1.0.1"}},
            // リトルバスターズ！Converted Edition
            {0x800A97C8, {CODEC_UTF8, 9, 0, 0, F0100943010310000, 0x0100943010310000ull, "1.0.0"}},
            // GrimGrimoire OnceMore
            {0x80020bd4, {CODEC_UTF8, 0, 0, 0, 0, 0x01003F5017760000ull, "1.0.0"}},
            {0x800375a0, {CODEC_UTF8, 2, 0, 0, 0, 0x01003F5017760000ull, "1.0.0"}}, // tutorial
            {0x800781dc, {CODEC_UTF8, 0, 0, 0, 0, 0x01003F5017760000ull, "1.0.0"}}, // Chapter
            // テミラーナ国の強運姫と悲運騎士団
            {0x82457970, {CODEC_UTF16, 0, 0x14, 0, F0100A62019078000, 0x0100A62019078000ull, "1.0.1"}},
            // 慟哭 そして…
            {0x8008171c, {0, 0, 0, 0, 0, 0x01007F000EB36000ull, "1.0.0"}},
            // ミストニアの翅望 -The Lost Delight-
            {0x8246c4ac, {CODEC_UTF16, 0, 0, 0, 0, 0x01007AD01CB42000ull, "1.0.0"}},
            // even if TEMPEST 連なるときの暁
            {0x80031008, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x0100DEF01D0C2000ull, "1.0.2"}},
            {0x8002e2cc, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x0100DEF01D0C2000ull, "1.0.2"}},
            {0x8002e2cc, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x0100DEF01D0C2000ull, "1.0.2"}},
            // even if TEMPEST 宵闇にかく語りき魔女
            {0x8001cf80, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x010095E01581C000ull, "1.0.8"}},
            {0x800297d0, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x010095E01581C000ull, "1.0.8"}},
            {0x8000edcc, {CODEC_UTF8, 0, 0, 0, F010095E01581C000, 0x010095E01581C000ull, "1.0.8"}},
            // 大正×対称アリス all in one
            {0x80064ab8, {CODEC_UTF16, 1, 0, 0, F010096000CA38000, 0x010096000CA38000ull, "1.0.2"}},
            {0x80064bd4, {CODEC_UTF16, 1, 0, 0, F010096000CA38000, 0x010096000CA38000ull, "1.0.2"}},
            {0x8015f968, {CODEC_UTF16, 0, 0, 0, F010096000CA38000, 0x010096000CA38000ull, "1.0.2"}},
            // 大正×対称アリス HEADS&TAILS
            {0x8009bb3c, {CODEC_UTF16, 1, 0, 0, F0100B1F0123B6000, 0x0100B1F0123B6000ull, "2.0.0"}},
            {0x8009bc58, {CODEC_UTF16, 1, 0, 0, F0100B1F0123B6000, 0x0100B1F0123B6000ull, "2.0.0"}},
            // 緋色の欠片 玉依姫奇譚 ～おもいいろの記憶～
            {0x81922ce8, {CODEC_UTF16, 0, 0x14, 0, F0100EC001DE7E000, 0x0100EC001DE7E000ull, "1.0.0"}},
            // 幻想マネージュ
            {0x8124f690, {CODEC_UTF16, 0, 0x14, 0, F010037500DF38000, 0x010037500DF38000ull, "1.0.4"}},
            {0x811f63f0, {CODEC_UTF16, 0, 0x14, 0, F010037500DF38000, 0x010037500DF38000ull, "1.0.4"}},
            {0x811917f4, {CODEC_UTF16, 0, 0x14, 0, F010037500DF38000, 0x010037500DF38000ull, "1.0.4"}},
            {0x81595f90, {CODEC_UTF16, 0, 0x14, 0, F010037500DF38000, 0x010037500DF38000ull, "1.0.4"}},
            // 幻奏喫茶アンシャンテ
            {0x8002863c, {CODEC_UTF8, 0, 0, 0, 0, 0x010079200C26E000ull, "1.0.0"}},
            {0x80044360, {CODEC_UTF8, 1, 0, 0, 0, 0x010079200C26E000ull, "1.0.0"}},
            {0x8004a1a4, {CODEC_UTF8, 0, 0, 0, F010079200C26E000<0>, 0x010079200C26E000ull, "1.0.0"}},
            {0x8004a394, {CODEC_UTF8, 0, 0, 0, F010079200C26E000<1>, 0x010079200C26E000ull, "1.0.0"}},
            // 天獄ストラグル -strayside-
            {0x801bc678, {CODEC_UTF32, 0, 0, 0, F01002C00177AE000, 0x01002C00177AE000ull, "1.0.0"}},
            {0x8016a05c, {CODEC_UTF32, 0, 0, 0, F01002C00177AE000, 0x01002C00177AE000ull, "1.0.0"}},
            {0x80140cac, {CODEC_UTF32, 1, 0, 0, F01002C00177AE000, 0x01002C00177AE000ull, "1.0.0"}},
            {0x800e08dc, {CODEC_UTF32, 0, 0, 0, F01002C00177AE000, 0x01002C00177AE000ull, "1.0.0"}},
            // 明治活劇 ハイカラ流星組 －成敗しませう、世直し稼業－
            {0x802ab2fc, {CODEC_UTF8, 6, 0, 0, F0100EA100DF92000, 0x0100EA100DF92000ull, "1.0.0"}},
            // 7'scarlet
            {0x8177ec00, {CODEC_UTF16, 0, 0x14, 0, F0100FA001E160000, 0x0100FA001E160000ull, "1.0.0"}},
            {0x817754ac, {CODEC_UTF16, 0, 0x14, 0, F0100FA001E160000, 0x0100FA001E160000ull, "1.0.0"}},
            // SympathyKiss (JP)
            {0x80037d90, {CODEC_UTF8, 0, 0, 0, F0100FA10185B0000, 0x0100FA10185B0000ull, "1.0.0"}},
            {0x80030f24, {CODEC_UTF8, 0, 0, 0, F0100FA10185B0000, 0x0100FA10185B0000ull, "1.0.0"}},
            {0x80054804, {CODEC_UTF8, 1, 0, 0, F0100FA10185B0000, 0x0100FA10185B0000ull, "1.0.0"}},
            {0x80054290, {CODEC_UTF8, 1, 0, 0, F0100FA10185B0000, 0x0100FA10185B0000ull, "1.0.0"}},
            // 君は雪間に希う
            {0x8013a0f0, {CODEC_UTF32, 0, 0, 0, F010021D01474E000, 0x010021D01474E000ull, "1.0.0"}},
            {0x800319f8, {CODEC_UTF32, 0, 0, 0, F010021D01474E000_2, 0x010021D01474E000ull, "1.0.0"}},
            {0x800488e4, {CODEC_UTF32, 1, 0, 0, F010021D01474E000, 0x010021D01474E000ull, "1.0.0"}},
            {0x800bdb84, {CODEC_UTF32, 0, 0, 0, F010021D01474E000, 0x010021D01474E000ull, "1.0.0"}},
            {0x800e4540, {CODEC_UTF32, 0, 0, 0, F010021D01474E000, 0x010021D01474E000ull, "1.0.0"}},
            // DAIROKU：AYAKASHIMORI
            {0x800e35ec, {CODEC_UTF8, 0, 0, 0, F010061300DF48000, 0x010061300DF48000ull, "1.0.1"}},
            {0x800d103c, {CODEC_UTF8, 0, 0, 0, F010061300DF48000, 0x010061300DF48000ull, "1.0.1"}},
            {0x800f1320, {CODEC_UTF8, 0, 0, T010061300DF48000, FF010061300DF48000_2, 0x010061300DF48000ull, "1.0.1"}},
            // Charade Maniacs
            {0x8001c460, {CODEC_UTF8, 0, 0x5c, 0, F0100CEF0152DE000, 0x0100CEF0152DE000ull, "1.0.0"}},
            {0x8004c390, {CODEC_UTF8, 1, 0, 0, F0100CEF0152DE000, 0x0100CEF0152DE000ull, "1.0.0"}},
            {0x80050d60, {CODEC_UTF8, 0, 0, 0, F0100CEF0152DE000, 0x0100CEF0152DE000ull, "1.0.0"}},
            {0x8007ee20, {CODEC_UTF8, 0, 0, 0, F0100CEF0152DE000, 0x0100CEF0152DE000ull, "1.0.0"}},
            // 花笑む彼と & bloom
            {0x833e4d84, {CODEC_UTF16, 0, 0x14, 0, F0100DEF01D0C6000, 0x0100DEF01D0C6000ull, "1.0.0"}},
            {0x8335f650, {CODEC_UTF16, 0, 0x14, 0, F0100DEF01D0C6000, 0x0100DEF01D0C6000ull, "1.0.0"}},
            {0x81729520, {CODEC_UTF16, 1, 0x14, 0, F0100DEF01D0C6000_2, 0x0100DEF01D0C6000ull, "1.0.0"}},
            {0x83375938, {CODEC_UTF16, 0, 0, T0100DEF01D0C6000_2, 0, 0x0100DEF01D0C6000ull, "1.0.0"}},
            // Dance with Devils
            {0x81616034, {CODEC_UTF16, 0, 0x14, 0, F01004E5017C54000, 0x01004E5017C54000ull, "1.0.0"}},
            {0x8185a800, {CODEC_UTF16, 0, 0x14, 0, F01004E5017C54000, 0x01004E5017C54000ull, "1.0.0"}},
            // My9Swallows TOPSTARS LEAGUE
            {0x818554ac, {CODEC_UTF16, 0, 0x14, 0, F01003BB01DF54000, 0x01003BB01DF54000ull, "1.0.0"}},
            {0x817b76d4, {CODEC_UTF16, 0, 0x14, 0, F01003BB01DF54000, 0x01003BB01DF54000ull, "1.0.0"}},
            {0x8187882c, {CODEC_UTF16, 0, 0x14, 0, F01003BB01DF54000, 0x01003BB01DF54000ull, "1.0.1"}},
            {0x817b8f64, {CODEC_UTF16, 0, 0x14, 0, F01003BB01DF54000, 0x01003BB01DF54000ull, "1.0.1"}},
            // 時計仕掛けのアポカリプス
            {0x8001d9c4, {CODEC_UTF8, 0, 0x1c, 0, F01005AF00E9DC000, 0x01005AF00E9DC000ull, "1.0.0"}},
            {0x8004ca84, {CODEC_UTF8, 1, 0, 0, F01005AF00E9DC000, 0x01005AF00E9DC000ull, "1.0.0"}},
            {0x8005b304, {CODEC_UTF8, 0, 0, 0, F01005AF00E9DC000, 0x01005AF00E9DC000ull, "1.0.0"}},
            {0x8005b310, {CODEC_UTF8, 0, 0, 0, F01005AF00E9DC000, 0x01005AF00E9DC000ull, "1.0.0"}},
            // ラディアンテイル ～ファンファーレ！～
            {0x8003a880, {CODEC_UTF8, 0, 0, 0, F010088B01A8FC000, 0x010088B01A8FC000ull, "1.0.1"}},
            {0x8004eb08, {CODEC_UTF8, 1, 0, 0, F010088B01A8FC000, 0x010088B01A8FC000ull, "1.0.1"}},
            {0x8005bff4, {CODEC_UTF8, 0, 0, 0, F010088B01A8FC000, 0x010088B01A8FC000ull, "1.0.1"}},
            {0x8005f0d4, {CODEC_UTF8, 3, 0, 0, F010088B01A8FC000, 0x010088B01A8FC000ull, "1.0.1"}},
            // Lover Pretend
            {0x80034ad0, {CODEC_UTF8, 0, 0, 0, F010032300C562000, 0x010032300C562000ull, "1.0.0"}},
            {0x8004e950, {CODEC_UTF8, 1, 0, 0, F010032300C562000, 0x010032300C562000ull, "1.0.0"}},
            {0x8002e6c4, {CODEC_UTF8, 0, 0, 0, F010032300C562000, 0x010032300C562000ull, "1.0.0"}},
            {0x8005f6ec, {CODEC_UTF8, 0, 0, 0, F010032300C562000, 0x010032300C562000ull, "1.0.0"}},
            // NORN9 ~ノルン+ノネット~ LOFN for Nintendo Switch
            {0x8002b200, {CODEC_UTF8, 1, 0x18, 0, F010061300DF48000, 0x01001A500AD6A000ull, "1.0.0"}},
            {0x8003d83c, {CODEC_UTF8, 0, 0, 0, F010061300DF48000, 0x01001A500AD6A000ull, "1.0.0"}},
            {0x80047850, {CODEC_UTF8, 0, 0, 0, F010061300DF48000, 0x01001A500AD6A000ull, "1.0.0"}},
            // 私立ベルばら学園 ～ベルサイユのばらRe*imagination～
            {0x8001b68c, {CODEC_UTF8, 0, 0x1c, 0, F010027300A660000, 0x010027300A660000ull, "1.0.0"}},
            {0x800460f0, {CODEC_UTF8, 1, 0, 0, F010027300A660000, 0x010027300A660000ull, "1.0.0"}},
            // ひめひび Another Princess Days – White or Black –
            {0x219ed0, {0, 0, 0, 0, F0100E4000F616000, 0x0100E4000F616000ull, "1.0.0"}},
            {0x21a3e0, {0, 0, 0, 0, F0100E4000F616000, 0x0100E4000F616000ull, "1.0.0"}},
            // ひめひび -Princess Days-
            {0x20d7b8, {0, 0, 0, 0, F0100E4000F616000, 0x0100F8D0129F4000ull, "1.0.0"}},
            {0x20da9c, {0, 0, 0, 0, F0100E4000F616000, 0x0100E4000F616000ull, "1.0.0"}},
            {0x20d834, {0, 0, 0, 0, F0100E4000F616000, 0x0100F8D0129F4000ull, "1.0.1"}},
            {0x20dae8, {0, 0, 0, 0, F0100E4000F616000, 0x0100E4000F616000ull, "1.0.1"}},
            // オホーツクに消ゆ ～追憶の流氷・涙のニポポ人形～
            {0x83d4bda0, {CODEC_UTF16, 1, 0x14, 0, F010044701E9BC000, 0x010044701E9BC000ull, "1.2.0"}},
            {0x83d59320, {CODEC_UTF16, 0, 0x14, 0, F010044701E9BC000, 0x010044701E9BC000ull, "1.2.0"}},
            {0x83d22530, {CODEC_UTF16, 0, 0x14, 0, F010044701E9BC000, 0x010044701E9BC000ull, "1.2.0"}},
            {0x83d225c0, {CODEC_UTF16, 0, 0x14, 0, F010044701E9BC000, 0x010044701E9BC000ull, "1.2.0"}},
            {0x83d26fd8, {CODEC_UTF16, 0, 0x14, 0, F010044701E9BC000, 0x010044701E9BC000ull, "1.2.0"}},
            // トラブル・マギア ～訳アリ少女は未来を勝ち取るために異国の魔法学校へ留学します～
            {0x8017e6b0, {CODEC_UTF16, 1, 0, T01000BB01CB8A000, F01000BB01CB8A000, 0x01000BB01CB8A000ull, "1.0.0"}},
            {0x80177ae0, {CODEC_UTF16, 0, 0, T01000BB01CB8A000, F01000BB01CB8A000, 0x01000BB01CB8A000ull, "1.0.0"}},
            {0x80122a4c, {CODEC_UTF16, 0, 0, T01000BB01CB8A000, F01000BB01CB8A000, 0x01000BB01CB8A000ull, "1.0.0"}},
            {0x800ba088, {CODEC_UTF16, 0, 0, T01000BB01CB8A000, F01000BB01CB8A000, 0x01000BB01CB8A000ull, "1.0.0"}},
            // 燃えよ！ 乙女道士 ～華遊恋語～
            {0x8005c698, {CODEC_UTF16, 1, 0x20, 0, F01001BA01EBFC000, 0x01001BA01EBFC000ull, "1.0.0"}},
            {0x80051cd0, {CODEC_UTF16, 1, 0, 0, F01001BA01EBFC000, 0x01001BA01EBFC000ull, "1.0.0"}},
            // planetarian～雪圏球～
            {0x800F32A0, {CODEC_UTF16 | FULL_STRING, 1, 0, 0, 0, 0x010031C01F410000ull, "1.0.0"}}, // 各种语言一起都提取出来了
            // planetarian～ちいさなほしのゆめ＆雪圏球～ パッケージ版 英文版
            {0x801253EC, {CODEC_UTF16, 0xA, 0, 0, 0, 0x0100F0A01F112000ull, nullptr}},               // 1.0.0 && 1.0.1 // 中文
            {0x8012441C, {CODEC_UTF16, 8, 0, 0, F0100F0A01F112000, 0x0100F0A01F112000ull, nullptr}}, // 1.0.0 && 1.0.1 // 日文
            // 贄の町
            {0x818B6078, {CODEC_UTF16, 1, 0, 0, F0100C9001E10C000, 0x0100C9001E10C000ull, "1.0.0"}},
            // Honey Vibes
            {0x81845F80, {CODEC_UTF16 | FULL_STRING, 1, 0, 0, F0100FB301E70A000, 0x0100FB301E70A000ull, "1.0.0"}},
            // ワールドエンド・シンドローム
            {0x805F5F04, {CODEC_UTF16, 2, 0, 0, 0, 0x01008A30083E2000ull, "1.0.0"}},
            {0x800FBA84, {CODEC_UTF16, 2, 0, 0, 0, 0x01008A30083E2000ull, "1.0.1"}},
            // 果つることなき未来ヨリ
            {0x8017BE0C, {CODEC_UTF8, 8, 0, 0, aF0100A9B01D4AE000, 0x0100A9B01D4AE000ull, "1.0.0"}},  // 英文
            {0x8017C0B4, {CODEC_UTF16, 8, 0, 0, wF0100A9B01D4AE000, 0x0100A9B01D4AE000ull, "1.0.0"}}, // 日文
            // 明治東亰恋伽
            {0x81898840, {CODEC_UTF16, 3, 0, 0, F010043901E972000, 0x010043901E972000ull, "1.0.0"}}, // 日文
            // 月影の鎖～狂爛モラトリアム～
            {0x2170B4, {0, 1, 0, 0, F010076501DAEA000, 0x010076501DAEA000ull, "1.0.0"}}, // text
            {0x2179A8, {0, 2, 0, 0, 0, 0x010076501DAEA000ull, "1.0.0"}},                 // name+text
            {0x217950, {0, 0, 0, 0, F0100A250191E8000<false>, 0x010076501DAEA000ull, "1.0.0"}},
            {0x217f64, {0, 0, 0, 0, F0100A250191E8000<true>, 0x010076501DAEA000ull, "1.0.0"}},
            // 神々の悪戯 Unite Edition
            {0x812BFF40, {CODEC_UTF16, 1, -2, 0, F01006530151F0000, 0x01006530151F0000ull, "1.0.0"}}, // 只有第一行
            {0x812BCEB8, {CODEC_UTF16, 1, -2, 0, F01006530151F0000, 0x01006530151F0000ull, "1.0.0"}}, // 只有2&3行
            // 新宿羅生門 ―Rashomon of Shinjuku―
            {0x80062158, {CODEC_UTF8, 0, 0, 0, F01005A401D766000, 0x01005A401D766000ull, "1.0.0"}},
            {0x80062a74, {CODEC_UTF8, 0, 0, 0, F01005A401D766000_2, 0x01005A401D766000ull, "1.0.0"}},
            {0x800629f4, {CODEC_UTF8, 0, 0, 0, F01005A401D766000_2, 0x01005A401D766000ull, "1.0.0"}},
            {0x800ea870, {CODEC_UTF8, 1, 0, 0, F01005A401D766000_2, 0x01005A401D766000ull, "1.0.0"}},
            // 夏空のモノローグ ～Another Memory～
            {0x8006007c, {0, 0, 0, 0, F0100FC2019346000, 0x01000E701DAE8000ull, "1.0.0"}},
            {0x800578c4, {0, 1, 0, 0, F0100FC2019346000, 0x01000E701DAE8000ull, "1.0.0"}},
            // 真紅の焔 真田忍法帳 for Nintendo Switch
            {0x800170a0, {CODEC_UTF8, 0, 0, 0, F0100FC2019346000, 0x01008A001C79A000ull, "1.0.0"}},
            {0x800220a0, {CODEC_UTF8, 2, 0, 0, F0100FC2019346000, 0x01008A001C79A000ull, "1.0.0"}},
            {0x8004bbd0, {CODEC_UTF8, 1, 0, 0, F0100FC2019346000, 0x01008A001C79A000ull, "1.0.0"}},
            {0x80062a20, {CODEC_UTF8, 0, 0, 0, F0100FC2019346000, 0x01008A001C79A000ull, "1.0.0"}},
            {0x80064c48, {CODEC_UTF8, 3, 0, 0, F0100FC2019346000, 0x01008A001C79A000ull, "1.0.0"}},
            // 神さまと恋ゴコロ
            {0x20D838, {0, 7, 0, 0, 0, 0x0100612019F12000ull, "1.0.0"}}, // name+text
            {0x20D030, {0, 1, 0, 0, 0, 0x0100612019F12000ull, "1.0.0"}},
            // KLAP!! for Nintendo Switch
            {0x8004a2d0, {CODEC_UTF8, 1, 0, 0, F0100FC2019346000, 0x0100E8E016D82000ull, "1.0.0"}},
            {0x8004970c, {CODEC_UTF8, 1, 0, 0, F0100FC2019346000, 0x0100E8E016D82000ull, "1.0.0"}},
            {0x800da5e0, {CODEC_UTF8, 0, 0, 0, F0100FC2019346000, 0x0100E8E016D82000ull, "1.0.0"}},
            {0x8003dfac, {CODEC_UTF8, 0, 0, 0, F0100FC2019346000, 0x0100E8E016D82000ull, "1.0.0"}},
            // PSYCHIC ECLIPSE-サイキックイクリプス- reload
            {0x8091B41C, {CODEC_UTF8, 8, 0, 0, 0, 0x0100A0001B9F0000ull, "1.0.0"}},               // 提取不到短字符串
            {0x804FAF5C, {CODEC_UTF8 | FULL_STRING, 1, 0, 0, 0, 0x0100A0001B9F0000ull, "1.1.0"}}, // 提取不到短字符串 text+name
            {0x80887ABC, {CODEC_UTF8, 8, 0, 0, 0, 0x0100A0001B9F0000ull, "1.1.0"}},               // 提取不到短字符串
            // アイ★チュウ
            {0x824865C4, {CODEC_UTF16, 3, 0, 0, F01006CC015ECA000, 0x01006CC015ECA000ull, "1.14"}},
            // カエル畑DEつかまえて☆彡
            {0x2206bc, {0, 0, 0, 0, F0100E5200D1A2000<false>, 0x0100E5200D1A2000ull, "1.0.0"}},
            {0x220cfc, {0, 0, 0, 0, F0100E5200D1A2000<true>, 0x0100E5200D1A2000ull, "1.0.0"}},
            {0x2372b0, {0, 1, 0, 0, F0100E5200D1A2000<false>, 0x0100E5200D1A2000ull, "1.0.0"}},
            // カエル畑DEつかまえて・夏 千木良参戦!
            {0x2210d0, {0, 0, 0, 0, F0100EFE0159C6000<false>, 0x0100EFE0159C6000ull, "1.0.0"}},
            {0x221768, {0, 0, 0, 0, F0100EFE0159C6000<false>, 0x0100EFE0159C6000ull, "1.0.0"}},
            // 片恋いコントラスト ―collection of branch―
            {0x8004ba20, {CODEC_UTF32, 0, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            {0x800c6eb0, {CODEC_UTF32, 1, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            {0x8017e560, {CODEC_UTF32, 0, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            {0x801f67c0, {CODEC_UTF32, 1, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            {0x802a76c0, {CODEC_UTF32, 0, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            {0x8031fc80, {CODEC_UTF32, 1, 0, 0, F01007FD00DB20000, 0x01007FD00DB20000ull, "1.0.0"}},
            // ジュエリー・ハーツ・アカデミア -We will wing wonder world-
            {0x805b0714, {CODEC_UTF8, 1, 0, 0, F01006590155AC000, 0x010064701F37A000ull, "1.0.0"}},
            {0x805b0704, {CODEC_UTF8, 0, 0, 0, F01006590155AC000, 0x010064701F37A000ull, "1.0.0"}},
            // 真 流行り神１・２パック
            {0x80072720, {CODEC_UTF8, 1, 0, 0, F010005F00E036000, 0x010005F00E036000ull, "1.0.0"}},
            // 真流行り神3
            {0x80082F70, {0, 0, 0, TF0100AA1013B96000, 0, 0x0100AA1013B96000ull, nullptr}}, //"1.0.0", "1.0.1"
            // NG
            {0x228AA4, {0, 6, 0, 0, F01009E600FAF6000, 0x01009E600FAF6000ull, "1.0.0"}},
            {0x228C0C, {0, 6, 0, 0, F01009E600FAF6000, 0x01009E600FAF6000ull, "1.0.0"}},
            // アサツグトリ
            {0x8012C824, {CODEC_UTF8, 1, 0, 0, F010060301588A000, 0x010060301588A000ull, "1.0.0"}},
            {0x80095370, {CODEC_UTF8, 4, 0, 0, F010060301588A000, 0x010060301588A000ull, "1.0.2"}}, // text only
            // Money Parasite〜嘘つきな女〜
            {0x2169ac, {0, 0, 0, 0, F0100A250191E8000<false>, 0x0100A250191E8000ull, "1.0.0"}},
            {0x217030, {0, 0, 0, 0, F0100A250191E8000<true>, 0x0100A250191E8000ull, "1.0.0"}},
            // 三国恋戦記～オトメの兵法！～
            {0x800644A0, {CODEC_UTF16, 1, 0, 0, F01000EA00B23C000, 0x01000EA00B23C000ull, "1.0.0"}},
            // 三国恋戦記～思いでがえし～＋学園恋戦記
            {0x80153B20, {CODEC_UTF16, 8, 0, 0, F01000EA00B23C000, 0x01003B6014B38000ull, "1.0.0"}},
            // 殺人探偵ジャック・ザ・リッパー
            {0x8000ED30, {CODEC_UTF8, 0, 0, 0, T0100A4700BC98000, 0x0100A4700BC98000ull, "1.0.0"}}, // 1.0.0有漏的
            {0x8000ED1C, {CODEC_UTF8, 0, 0, 0, T0100A4700BC98000, 0x0100A4700BC98000ull, "1.0.0"}},
            {0x8000ED3C, {CODEC_UTF8, 0, 0, 0, T0100A4700BC98000, 0x0100A4700BC98000ull, "1.0.0"}},
            {0x8003734C, {CODEC_UTF8, 2, 0, 0, F010027100C79A000, 0x0100A4700BC98000ull, "1.0.2"}}, // 完整
            // サスペクツルーム -警視庁門前署取調班-
            {0x81397F6C, {CODEC_UTF8, 1, 0, 0, F010069E01A7CE000, 0x010069E01A7CE000ull, "1.0.0"}},
            // Dragon Quest III Hd-2D Remake
            {0x80c4b094, {CODEC_UTF16, 0, 0, 0, F01003E601E324000, 0x01003E601E324000ull, "1.0.1"}},
            // EVE rebirth terror
            {0x8002CC40, {0, 1, 0, 0, F01008BA00F172000, 0x01008BA00F172000ull, "1.0.0"}},
            {0x80045918, {0, 0, 0, 0, F01008BA00F172000, 0x01008BA00F172000ull, "1.0.2"}},
            {0x80045798, {0, 0, 0, 0, F01008BA00F172000, 0x01008BA00F172000ull, "1.0.3"}},
            // EVE ghost enemies
            {0x80053900, {0, 1, 0, 0, F01008BA00F172000, 0x01007BE0160D6000ull, "1.0.0"}},
            {0x80052440, {0, 1, 0, 0, F01008BA00F172000, 0x01007BE0160D6000ull, "1.0.1"}},
            // ニル・アドミラリの天秤 色ドリ撫子，二合一，其一
            {0x8000BDD0, {0, 8, 0, 0, F01002BB00A662000, 0x01002BB00A662000ull, "1.0.0"}}, // text
            {0x80019260, {0, 0, 0, 0, F01002BB00A662000, 0x01002BB00A662000ull, "1.0.0"}}, // name+text
            // 其二
            {0x8006BCC0, {0, 8, 0, 0, F01002BB00A662000, 0x01002BB00A662000ull, "1.0.0"}}, // text
            {0x8007C1D4, {0, 0, 0, 0, F01002BB00A662000, 0x01002BB00A662000ull, "1.0.0"}}, // name+text 这个两作都能提到。实际上只留这一个也行，但它显示完才有，速度慢。
            // 八剱伝
            {0x819ade74, {CODEC_UTF16, 1, 0, ReadTextAndLenDW, F01007A901E728000, 0x01007A901E728000ull, "1.0.1"}},
            // 大正メビウスライン大全 三合一
            {0x800C43D4, {0, 0, 0, 0, F0100509013040000, 0x0100509013040000ull, "1.0.0"}}, // text
            {0x800C4468, {0, 0, 0, 0, F0100509013040000, 0x0100509013040000ull, "1.0.1"}}, // text
            // 猛獣たちとお姫様 for Nintendo Switch  二合一
            {0x80115C70, {CODEC_UTF8, 0, 0, 0, F010001D015260000, 0x010035001D1B2000ull, "1.0.0"}}, // text
            {0x80115F20, {CODEC_UTF8, 0, 0, 0, F010001D015260000, 0x010035001D1B2000ull, "1.0.1"}}, // text
            // BEAST Darling! ～けもみみ男子と秘密の寮～
            {0x80424D50, {CODEC_UTF16, 8, 0, 0, F0100B0601852A000, 0x010045F00BF64000ull, "1.0.0"}}, // text
            // 恋の花咲く百花園
            {0x211464, {0, 0, 0, 0, F010052300F612000, 0x010052300F612000ull, "1.0.0"}}, // text
            // 東京24区 -祈-
            {0x8006F100, {0, 0, 0, 0, F0100CF90151E0000, 0x0100CF90151E0000ull, "1.0.0"}}, // text
            // ディアマジ -魔法少年学科-
            {0x802B1270, {CODEC_UTF16, 8, 0, 0, F010015600D814000, 0x010015600D814000ull, "1.0.0"}}, // text
            {0x802B19E0, {CODEC_UTF16, 8, 0, 0, F010015600D814000, 0x010015600D814000ull, "1.0.1"}}, // text
            // デスマッチラブコメ！
            {0x800FB41C, {CODEC_UTF16, 1, -2, 0, F0100AE90109A2000, 0x0100AE90109A2000ull, "1.0.0"}},
            // CROSS†CHANNEL ～For all people～
            {0x80033250, {0, 0, 0, 0, F0100068019996000, 0x0100735012AAE000ull, "1.0.0"}}, // text
            // フルキス
            {0x804988A0, {CODEC_UTF8, 0, 0, 0, F0100FB50156E6000_1, 0x0100FB50156E6000ull, "1.0.0"}}, // text
            {0x804FECD4, {CODEC_UTF8, 1, 0, 0, F0100FB50156E6000_2, 0x0100FB50156E6000ull, "1.0.0"}}, // text+name->name
            // フルキスS  1.0.0 & 1.0.1
            {0x804E7AF0, {CODEC_UTF8, 0, 0, 0, F0100FB50156E6000_1, 0x0100BEE0156D8000ull, nullptr}}, // text
            {0x804FF454, {CODEC_UTF8, 1, 0, 0, F0100FB50156E6000_2, 0x0100BEE0156D8000ull, nullptr}}, // text+name->name
            // アーキタイプ・アーカディア
            {0x817FAC88, {CODEC_UTF16, 8, 0, 0, F010019C0155D8000_1, 0x010019C0155D8000ull, "1.0.0"}}, // text+name,->name
            {0x817FAC90, {CODEC_UTF16, 8, 0, 0, F010019C0155D8000_2, 0x010019C0155D8000ull, "1.0.0"}}, // text+name,->text
            {0x817E5818, {CODEC_UTF16, 8, 0, 0, F010019C0155D8000_1, 0x010019C0155D8000ull, "1.0.2"}}, // text+name,->name
            {0x817E5820, {CODEC_UTF16, 8, 0, 0, F010019C0155D8000_2, 0x010019C0155D8000ull, "1.0.2"}}, // text+name,->text
            // 神凪ノ杜
            {0x8205e150, {CODEC_UTF16, 0, 0x14, 0, F0100B5801D7CE000, 0x0100B5801D7CE000ull, "1.0.0"}},
            {0x820e2e6c, {CODEC_UTF16, 0, 0x14, 0, 0, 0x0100B5801D7CE000ull, "1.0.0"}},
            // シェルノサージュ ～失われた星へ捧ぐ詩～ DX
            {0x801A1140, {CODEC_UTF8, 1, 0, 0, F010053F0128DC000<1>, 0x010053F0128DC000ull, "1.0.0"}},
            {0x801A10A4, {CODEC_UTF8, 1, 0, 0, F010053F0128DC000<2>, 0x010053F0128DC000ull, "1.0.0"}},
            {0x801A04F4, {CODEC_UTF8, 1, 0, 0, F010053F0128DC000<1>, 0x010053F0128DC000ull, "1.0.1"}},
            {0x801A0590, {CODEC_UTF8, 1, 0, 0, F010053F0128DC000<2>, 0x010053F0128DC000ull, "1.0.1"}},
            // 遙かなる時空の中で６ DX
            {0x80193FAC, {0, 0, 0, 0, F0100F7700CB82000, 0x0100F7700CB82000ull, "1.0.0"}},
            // フローラル・フローラブ
            {0x80020974, {0, 0, 0, 0, F0100D8B019FC0000<true>, 0x0100D8B019FC0000ull, "1.0.0"}},
            {0x80020958, {0, 0, 0, 0, F0100D8B019FC0000<false>, 0x0100D8B019FC0000ull, "1.0.0"}},
            // FANTASIAN Neo Dimension
            {0x81719ea0, {CODEC_UTF16, 0, 0, ReadTextAndLenDW, F01001BB01E8E2000, 0x01001BB01E8E2000ull, "1.0.0"}},
            // アイキス3cute
            {0x804C18C4, {CODEC_UTF8, 1, 0, 0, F0100FD4016528000, 0x0100FD4016528000ull, nullptr}}, // 1.0.0 && 1.0.2

        };
        return 1;
    }();
}