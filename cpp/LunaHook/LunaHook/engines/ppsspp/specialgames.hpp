#include <queue>
#include "emujitarg.hpp"

namespace ppsspp
{
	void ULJS00403_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::string result = buffer->strA();
		std::regex newlinePattern(R"((\\n)+)");
		result = std::regex_replace(result, newlinePattern, " ");
		std::regex pattern(R"((\\d$|^\@[a-z]+|#.*?#|\$))");
		result = std::regex_replace(result, pattern, "");
		buffer->from(result);
	}

	void ULJS00339(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto a2 = PPSSPP::emu_arg(stack)[0];

		auto vm = *(DWORD *)(a2 + (0x28));
		vm = *(DWORD *)PPSSPP::emu_addr(stack, vm);
		vm = *(DWORD *)PPSSPP::emu_addr(stack, vm + 8);
		uintptr_t address = PPSSPP::emu_addr(stack, vm);
		auto len1 = *(DWORD *)(address + 4);
		auto p = address + 0x20;
		if (len1 > 4 && *(WORD *)(p + 2) == 0)
		{
			auto p1 = *(DWORD *)(address + 8);
			vm = *(DWORD *)PPSSPP::emu_addr(stack, vm);
			vm = *(DWORD *)PPSSPP::emu_addr(stack, vm + 0xC);
			p = PPSSPP::emu_addr(stack, vm);
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
		pre = s;
		buffer->from(s);
	}

	void NPJH50909_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::string result = buffer->strA();
		auto ws = StringToWideString(result, 932).value();
		// Remove single line markers
		ws = std::regex_replace(ws, std::wregex(L"(\\%N)+"), L" ");

		// Remove scale marker
		ws = std::regex_replace(ws, std::wregex(L"\\%\\@\\%\\d+"), L"");

		// Reformat name
		std::wsmatch match;
		if (std::regex_search(ws, match, std::wregex(L"(^[^「]+)「")))
		{
			std::wstring name = match[1].str();
			ws = std::regex_replace(ws, std::wregex(L"^[^「]+"), L"");
			ws = name + L"\n" + ws;
		}
		buffer->from(WideStringToString(ws, 932));
	}

	void ULJM06119_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::string s = buffer->strA();

		std::regex pattern(R"(/\[[^\]]+./g)");
		s = std::regex_replace(s, pattern, "");

		std::regex tagPattern(R"(/\\k|\\x|%C|%B)");
		s = std::regex_replace(s, tagPattern, "");

		std::regex colorPattern(R"(/\%\d+\#[0-9a-fA-F]*\;)");
		s = std::regex_replace(s, colorPattern, "");

		std::regex newlinePattern(R"(/\n+)");
		s = std::regex_replace(s, newlinePattern, " ");
		buffer->from(s);
	}

	void ULJM06036_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::wstring result = buffer->strW();
		std::wregex pattern(LR"(<R([^\/]+).([^>]+).>)");
		result = std::regex_replace(result, pattern, L"$2");
		std::wregex tagPattern(LR"(<[A-Z]+>)");
		result = std::regex_replace(result, tagPattern, L"");
		buffer->from(result);
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
			while ((c = *(uint8_t *)(address + i)) != 0)
			{
				if (c == 0x1b)
				{
					if (*haveName)
						return s; // (1) skip junk after name

					c = *(uint8_t *)(address + (i + 1));
					if (c == 0x7f)
						i += 5;
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

	void ULJM05428(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto address = PPSSPP::emu_arg(stack)[1];
		bool haveNamve;
		auto s = Corda::readBinaryString(address, &haveNamve);
		*split = haveNamve;
		buffer->from(s);
	}
	void ULJM05054(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto address = PPSSPP::emu_arg(stack)[1];
		bool haveNamve;
		auto s = Corda::readBinaryString(address, &haveNamve);
		*split = haveNamve;
		buffer->from(s);
	}

	void ULJM05943F(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		strReplace(s, "#n", "");
		s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*\\.)?\\d+\\]+"), "");
		buffer->from(s);
	}

	void FULJM05603(TextBuffer *buffer, HookParam *)
	{
		StringCharReplacer(buffer, "%N", 2, ' ');
		StringFilter(buffer, "%K", 2);
		StringFilter(buffer, "%P", 2);
	}

	void ULJM05810(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto data = PPSSPP::emu_arg(stack)[0] + 0x0f;
		data = data + 400;
		std::string s;
		while (true)
		{
			std::string sub = (char *)data;
			s += sub;
			data += sub.size() + 1;
			if (!*(char *)data)
				break;
		}
		strReplace(s, "\n", "");
		buffer->from(s);
	}
	namespace NPJH50530
	{
		std::string current;
		void T(TextBuffer *buffer, HookParam *)
		{
			current = buffer->strA();
		}
		void N(TextBuffer *buffer, HookParam *)
		{
			auto current1 = buffer->strA();
			if(current == current1)
				buffer->clear();
		}
	}
	void FNPJH50243(TextBuffer *buffer, HookParam *)
	{
		auto s = buffer->strW();
		s = std::regex_replace(s, std::wregex(LR"(<(.*?)\|(.*?)>)"), L"$1");
		buffer->from(s);
	}
	void FNPJH50459(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(#SCL\((.*?)\)(.*?)#ECL)"), "$2");
		strReplace(s, "\n\r\n", "\n");
		buffer->from(s);
	}
	void FNPJH50127(TextBuffer *buffer, HookParam *hp)
	{
		StringCharReplacer(buffer, "\\n", 2, '\n');
	}
	void ULJM06145(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(#Ruby\[(.*?),(.*?)\])"), "$1");
		s = std::regex_replace(s, std::regex("#[A-Za-z]+\\[(\\d*\\.)?\\d+\\]+"), "");
		strReplace(s, "#n", "");
		strReplace(s, "\x84\xbd", "!?");
		buffer->from(s);
	}
	void FULJM05690(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(#Kana\[(.*?),(.*?)\])"), "$1");
		strReplace(s, "#n", "");
		buffer->from(s);
	}
	void FULJM05889(TextBuffer *buffer, HookParam *)
	{
		auto text = reinterpret_cast<LPSTR>(buffer->buff);
		for (size_t i = 0; i < buffer->size;)
		{
			if (IsShiftjisLeadByte(text[i]))
			{
				i += 2;
				continue;
			}
			if (text[i] == '^')
				text[i] = '\n';

			i += 1;
		}
	}

	void NPJH50619F(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		std::regex pattern1("[\\r\\n]+");
		std::string replacement1 = "";
		std::string result1 = std::regex_replace(s, pattern1, replacement1);
		std::regex pattern2("^(.*?)\\)+");
		std::string replacement2 = "";
		std::string result2 = std::regex_replace(result1, pattern2, replacement2);
		std::regex pattern3("#ECL+");
		std::string replacement3 = "";
		std::string result3 = std::regex_replace(result2, pattern3, replacement3);
		std::regex pattern4("(#.+?\\))+");
		std::string replacement4 = "";
		std::string result4 = std::regex_replace(result3, pattern4, replacement4);
		buffer->from(result4);
	}

	void NPJH50505F(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();

		std::regex pattern2("#RUBS(#[A-Z0-9]+)*[^#]+");
		std::string replacement2 = "";
		std::string result2 = std::regex_replace(s, pattern2, replacement2);

		std::regex pattern3("#FAMILY");
		std::string replacement3 = "$FAMILY";
		std::string result3 = std::regex_replace(result2, pattern3, replacement3);

		std::regex pattern4("#GIVE");
		std::string replacement4 = "$GIVE";
		std::string result4 = std::regex_replace(result3, pattern4, replacement4);

		std::regex pattern5("(#[A-Z0-9\\-]+)+");
		std::string replacement5 = "";
		std::string result5 = std::regex_replace(result4, pattern5, replacement5);

		std::regex pattern6("\\n+");
		std::string replacement6 = " ";
		std::string result6 = std::regex_replace(result5, pattern6, replacement6);
		buffer->from(result6);
	}

	void QNPJH50909(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto data = PPSSPP::emu_arg(stack)[0];
		uintptr_t addr = PPSSPP::emu_addr(stack, 0x08975110);
		if (0x6e87 == *(WORD *)data)
			return;
		if (0x000a == *(WORD *)data)
			return;
		buffer->from(addr + 0x20, *(DWORD *)(addr + 0x14) * 2);
	}
	std::unordered_map<uintptr_t, emfuncinfo> emfunctionhooks = {
		// Shinigami to Shoujo
		{0x883bf34, {0, 1, 0, 0, ULJS00403_filter, "ULJS00403"}},
		// Amagami
		{0x0886775c, {0, 0, 0, ULJS00339, 0, "ULJS00339"}}, // String.length()
		// Sekai de Ichiban Dame na Koi
		{0x8814adc, {0, 0, 0, 0, NPJH50909_filter, "ULJM05878"}}, // name + dialouge
		{0x8850b2c, {0, 0, 0, 0, NPJH50909_filter, "ULJM05878"}}, // onscreen toast
		// Dunamis15
		{0x0891D72C, {CODEC_UTF8, 0, 0, 0, ULJM06119_filter, "ULJM06119"}},
		// Princess Evangile Portable
		{0x88506d0, {CODEC_UTF16, 2, 0, 0, ULJM06036_filter, "ULJM06036"}}, // [0x88506d0(2)...0x088507C0(?)] // name text text (line doubled)
		// Kin'iro no Corda 2f
		{0x89b59dc, {0, 0, 0, ULJM05428, 0, "ULJM05428"}},
		// Kin'iro no Corda
		{0x886162c, {0, 0, 0, ULJM05054, 0, "ULJM05054"}}, // dialogue: 0x886162c (x1), 0x889d5fc-0x889d520(a2) fullLine
		{0x8899e90, {0, 0, 0x3c, 0, 0, "ULJM05054"}},	   // name 0x88da57c, 0x8899ca4 (x0, oneTime), 0x8899e90
		// Sol Trigger
		{0x8952cfc, {CODEC_UTF8, 0, 0, 0, NPJH50619F, "NPJH50619"}}, // dialog
		{0x884aad4, {CODEC_UTF8, 0, 0, 0, NPJH50619F, "NPJH50619"}}, // description
		{0x882e1b0, {CODEC_UTF8, 0, 0, 0, NPJH50619F, "NPJH50619"}}, // system
		{0x88bb108, {CODEC_UTF8, 2, 0, 0, NPJH50619F, "NPJH50619"}}, // battle tutorial
		{0x89526a0, {CODEC_UTF8, 0, 0, 0, NPJH50619F, "NPJH50619"}}, // battle info
		{0x88bcef8, {CODEC_UTF8, 1, 0, 0, NPJH50619F, "NPJH50619"}}, // battle talk
		// Fate/EXTRA CCC
		{0x8958490, {0, 0, 0, 0, NPJH50505F, "NPJH50505"}},
		// Kamigami no Asobi InFinite
		{0x088630f8, {0, 0, 0, QNPJH50909, 0, "NPJH50909"}}, // text, choice (debounce trailing 400ms), TODO: better hook
		{0x0887813c, {0, 3, 4, 0, 0, "NPJH50909"}},			 // Question YN
		// Gekka Ryouran Romance
		{0x88eeba4, {0, 0, 0, 0, ULJM05943F, "ULJM05943"}}, // a0 - monologue text
		{0x8875e0c, {0, 1, 6, 0, ULJM05943F, "ULJM05943"}}, // a1 - dialogue text
		// My Merry May with be
		{0x886F014, {0, 3, 0, 0, FULJM05603, "ULJM05603"}},
		// Corpse Party -The Anthology- Sachiko no Ren'ai Yuugi ♥ Hysteric Birthday 2U - Regular Edition
		{0x88517C8, {0, 1, 0, 0, FULJM05603, "ULJM06114"}},
		// Himawari_no_Kyoukai_to_Nagai_Natsuyasumi_Extra_Vacation_JPN_PSP-MOEMOE
		{0x881c444, {FULL_STRING, 0, 0, 0, 0, "ULJM06321"}}, // name+text,sjit,FULL_STRING to split name and text
		// ましろ色シンフォニー *mutsu-no-hana
		{0x8868AB8, {0, 0, 0, 0, FULJM05889, "ULJM05889"}},
		// シャイニング・ブレイド
		{0x8AA3B70, {0, 0xC, 0, 0, NPJH50530::T, "NPJH50530"}}, // text only
		{0x884DB44, {0, 1, 0, 0, NPJH50530::N, "NPJH50530"}},	// text+name
		// ティアーズ・トゥ・ティアラ 外伝 アヴァロンの謎 ＰＯＲＴＡＢＬＥ
		{0x890A4BC, {CODEC_UTF16, 1, 0, 0, FNPJH50243, "NPJH50243"}},
		// 薔薇ノ木ニ薔薇ノ花咲ク
		{0x881E560, {0, 1, 0, 0, 0, "ULJM05802"}},
		// D.C. Girl's Symphony Pocket ～ダ・カーポ～ ガールズシンフォニーポケット
		{0x883C77C, {0, 0, 0, 0, FULJM05690, "ULJM05690"}},
		// Ever17 -the out of infinity- Premium Edition
		{0x881AD64, {0, 0xd, 0, 0, 0, "ULJM05437"}},
		// １２時の鐘とシンデレラ～Halloween Wedding～
		{0x882A650, {0, 1, 0, 0, 0, "ULJM06023"}},
		// 0時の鐘とシンデレラ～Halloween Wedding～ (instance: 2)
		{0x8855CA0, {0, 1, 0, 0, 0, "ULJM06272"}},
		// セブンスドラゴン２０２０
		{0x88847A0, {CODEC_UTF8, 1, 0, 0, FNPJH50459, "NPJH50459"}},
		// セブンスドラゴン２０２０-Ⅱ
		{0x8889CCC, {CODEC_UTF8, 1, 0, 0, FNPJH50459, "NPJH50716"}}, // 会有两三条后续文本都被一次性提取到。
		// マイナスエイト
		{0x88DC218, {0, 0, 0, 0, FULJM05690, "ULJM06341"}},
		// Tokimeki Memorial 4
		{0x899a510, {0, 2, 0, 0, FNPJH50127, "NPJH50127"}},
		{0x88719dc, {0, 1, 0, 0, FNPJH50127, "NPJH50127"}},
		// オメルタ～沈黙の掟～ THE LEGACY
		{0x88861C8, {0, 3, 0, 0, 0, "ULJM06393"}},
		// L.G.S～新説 封神演義～
		{0x888A358, {0, 0, 0, 0, ULJM05943F, "ULJM06131"}}, // NAME+TEXT
		{0x88DB214, {0, 0, 0, 0, ULJM05943F, "ULJM06131"}}, // TEXT
		{0x889E970, {0, 0, 0, 0, ULJM05943F, "ULJM06131"}}, // NAME
		// 源狼 GENROH
		{0x8940DA8, {0, 1, 0, 0, ULJM06145, "ULJM06145"}}, // TEXT
		// 遙かなる時空の中で４ 愛蔵版
		{0x8955CE0, {0, 0, 0, ULJM05810, 0, " ULJM05810"}},
	};

}