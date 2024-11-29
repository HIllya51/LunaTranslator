#include <queue>
#include "emujitarg.hpp"

namespace ppsspp
{
	void ULJS00403_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::string result = buffer->strA();
		result = std::regex_replace(result, std::regex(R"((\\n)+)"), " ");
		result = std::regex_replace(result, std::regex(R"((\\d$|^\@[a-z]+|#.*?#|\$))"), "");
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
		auto ws = StringToWideString(buffer->viewA(), 932).value();
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
		s = std::regex_replace(s, std::regex(R"(/\[[^\]]+./g)"), "");
		s = std::regex_replace(s, std::regex(R"(/\\k|\\x|%C|%B)"), "");
		s = std::regex_replace(s, std::regex(R"(/\%\d+\#[0-9a-fA-F]*\;)"), "");
		s = std::regex_replace(s, std::regex(R"(/\n+)"), " ");
		buffer->from(s);
	}

	void ULJM06036_filter(TextBuffer *buffer, HookParam *hp)
	{
		std::wstring result = buffer->strW();
		result = std::regex_replace(result, std::wregex(LR"(<R([^\/]+).([^>]+).>)"), L"$2");
		result = std::regex_replace(result, std::wregex(LR"(<[A-Z]+>)"), L"");
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

	void ULJM05943F(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		strReplace(s, "#n", "");
		s = std::regex_replace(s, std::regex(R"((#[A-Za-z]+\[(\d*[.])?\d+\])+)"), "");
		buffer->from(s);
	}

	void FULJM05603(TextBuffer *buffer, HookParam *)
	{
		StringCharReplacer(buffer, "%N", 2, ' ');
		StringFilter(buffer, "%K", 2);
		StringFilter(buffer, "%P", 2);
		StringFilter(buffer, "%O030", 5);
	}

	void ULJM05810(hook_stack *stack, HookParam *hp, TextBuffer *buffer, uintptr_t *split)
	{
		auto data = PPSSPP::emu_arg(stack)[0x0f];
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
			StringCharReplacer(buffer, "\\n", 2, '\n');
		}
		void N(TextBuffer *buffer, HookParam *)
		{
			auto current1 = buffer->strA();
			if (current == current1)
				buffer->clear();
			else
			{
				StringCharReplacer(buffer, "\\n", 2, '\n');
			}
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
	void ULJM05756(TextBuffer *buffer, HookParam *hp)
	{
		static std::string last;
		auto s = buffer->strA();
		if (s == last)
		{
			last = s;
			return buffer->clear();
		}
		last = s;
		strReplace(s, "<D>", u8"ー");
		buffer->from(s);
	}
	void NPJH50535(TextBuffer *buffer, HookParam *hp)
	{
		static std::string last;
		auto s = buffer->strA();
		if (s == last)
		{
			last = s;
			return buffer->clear();
		}
		last = s;
		s = std::regex_replace(s, std::regex(R"(@\d{2})"), "");
		buffer->from(s);
	}
	void ULJS00354(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		static lru_cache<std::string> last(2);
		if (last.touch(s))
			return buffer->clear();
		strReplace(s, "#n", "");
		s = std::regex_replace(s, std::regex(R"(#R(.*?)\((.*?)\))"), "$1");
		buffer->from(s);
	}
	void ULJM05458(TextBuffer *buffer, HookParam *hp)
	{
		static int i = 0;
		if ((i++ % 2) || all_ascii((char *)buffer->buff, buffer->size))
			return buffer->clear();
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(\[(.*?)\*(.*?)\])"), "$1");
		buffer->from(s);
	}
	void ULJM05796(TextBuffer *buffer, HookParam *hp)
	{
		static std::wstring last;
		auto ws = StringToWideString(buffer->viewA(), 932).value();
		strReplace(ws, L"\\", L"");
		if (last == ws)
		{
			buffer->clear();
			last = ws;
		}
		else
		{
			if (endWith(last, ws))
				buffer->clear();
			else
			{
				buffer->from(WideStringToString(ws, 932));
				last = ws;
			}
		}
	}
	void NPJH50900(TextBuffer *buffer, HookParam *hp)
	{
		auto ws = StringToWideString(buffer->viewA(), 932).value();
		strReplace(ws, L"^", L"");
		static std::wstring last;
		if (startWith(ws, last))
		{
			auto _ = ws.substr(last.size(), ws.size() - last.size());
			last = ws;
			ws = _;
		}
		else
			last = ws;
		buffer->from(WideStringToString(ws, 932));
	}
	void ULJM06129(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(#\w+?\[\d\])"), "");
		strReplace(s, "#n", "");
		buffer->from(s);
	}
	void FNPJH50247(TextBuffer *buffer, HookParam *hp)
	{
		static lru_cache<std::string> cache(3);
		auto s = buffer->strA();
		if (cache.touch(s))
			buffer->clear();
		else
		{
			s = std::regex_replace(s, std::regex("#C[0-9]{9}"), "");
			s = std::regex_replace(s, std::regex("#RUBS(.*?)#RUBE(.*?)#REND"), "$2");
			s = std::regex_replace(s, std::regex("#CDEF"), "");
			buffer->from(s);
		}
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
		s = std::regex_replace(s, std::regex("[\\r\\n]+"), "");
		s = std::regex_replace(s, std::regex("^(.*?)\\)+"), "");
		s = std::regex_replace(s, std::regex("#ECL+"), "");
		s = std::regex_replace(s, std::regex("(#.+?\\))+"), "");
		buffer->from(s);
	}

	void NPJH50505F(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex("#RUBS(#[A-Z0-9]+)*[^#]+"), "");
		s = std::regex_replace(s, std::regex("#FAMILY"), "$FAMILY");
		s = std::regex_replace(s, std::regex("#GIVE"), "$GIVE");
		s = std::regex_replace(s, std::regex("(#[A-Z0-9\\-]+)+"), "");
		s = std::regex_replace(s, std::regex("\\n+"), "");
		buffer->from(s);
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
	void ULJM05433(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		static std::string last;
		if (startWith(s, last))
		{
			auto _ = s.substr(last.size(), s.size() - last.size());
			last = s;
			s = _;
		}
		else
			last = s;
		buffer->from(s);
	}
	void ULJM06289(TextBuffer *buffer, HookParam *hp)
	{
		StringFilter(buffer, "#n", 2);
		StringFilter(buffer, "\x81\x40", 2);
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex("(#[A-Za-z]+\\[(\\d*[.])?\\d+\\])+"), "");
		buffer->from(s);
	}
	void ULJM06040_2(TextBuffer *buffer, HookParam *hp)
	{
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(\x81k(.*?)\x81l(.*))"), "$1");
		buffer->from(s);
	}
	void ULJM06040_1(TextBuffer *buffer, HookParam *hp)
	{
		StringFilter(buffer, "%K%P", 4);
		StringFilterBetween(buffer, "\x81k", 2, "\x81l", 2);
		StringReplacer(buffer, "\x84\xa5", 2, "\x81\x5b", 2);
		StringReplacer(buffer, "\x84\xa7", 2, "\x81\x5b", 2);
		auto s = buffer->strA();
		s = std::regex_replace(s, std::regex(R"(\{(.*?)\}\[(.*?)\])"), "$1");
		buffer->from(s);
	}
	void ULJS00169(TextBuffer *buffer, HookParam *hp)
	{
		CharFilter(buffer, '\n');
		static std::string last;
		auto s = buffer->strA();
		if (s == last)
			return buffer->clear();
		last = s;
	}
	void ULJM05477(TextBuffer *buffer, HookParam *hp)
	{
		StringFilter(buffer, "@c", 2);
		auto s = buffer->strA();
		buffer->from(s.substr(1, s.size() - 2));
	}
	void ULJM05456(TextBuffer *buffer, HookParam *hp)
	{
		static std::string last;
		auto s = buffer->strA();
		if (endWith(last, s))
		{
			buffer->clear();
			last = s;
		}
		else
		{
			last = s;
			s = s.substr(0, s.size() - 1);
			s = std::regex_replace(s, std::regex(R"(\$\w\d{5})"), "$1");
			buffer->from(s);
		}
	}
	void NPJH50380(TextBuffer *buffer, HookParam *hp)
	{
		static std::wstring last;
		static int lastj = 0;
		auto s = buffer->strW();
		if (!last.size())
		{
			buffer->clear();
		}
		else
		{
			if (s[0] != last[0])
				lastj = 0;
			int j = s.size() - 1;
			for (; (j >= 0) && (last[j] == s[j]); j--)
				;
			j += 1;
			buffer->from(s.substr(lastj, j - lastj));
			lastj = j;
		}
		last = s;
	}
	namespace
	{
		void ULJM05823_1(TextBuffer *buffer, HookParam *hp)
		{
			StringFilter(buffer, "#n", 2);
			auto s = buffer->strA();
			s = std::regex_replace(s, std::regex("(#[A-Za-z]+\\[(\\d*[.])?\\d+\\])+"), "");
			buffer->from(s);
		}
		void ULJM05823_2(TextBuffer *buffer, HookParam *hp)
		{
			auto s = buffer->viewA();
			if (s.find("#n") != s.npos)
				return buffer->clear();
		}
	}
	std::unordered_map<uintptr_t, emfuncinfo> emfunctionhooks = {
		// 死神と少女
		{0x883bf34, {0, 1, 0, 0, ULJS00403_filter, "ULJS00403"}},
		// アマガミ
		{0x0886775c, {0, 0, 0, ULJS00339, 0, "ULJS00339"}}, // String.length()
		// 世界でいちばんNG（だめ）な恋
		{0x8814adc, {0, 0, 0, 0, NPJH50909_filter, "ULJM05878"}}, // name + dialouge
		{0x8850b2c, {0, 0, 0, 0, NPJH50909_filter, "ULJM05878"}}, // onscreen toast
		// Dunamis15
		{0x0891D72C, {CODEC_UTF8, 0, 0, 0, ULJM06119_filter, "ULJM06119"}},
		// Princess Evangile
		{0x88506d0, {CODEC_UTF16, 2, 0, 0, ULJM06036_filter, "ULJM06036"}}, // [0x88506d0(2)...0x088507C0(?)] // name text text (line doubled)
		// 金色のコルダ３
		{0x896C3B8, {0, 0, 0, ULJM05428, 0, "ULJM05624"}},
		// 金色のコルダ2 f
		{0x89b59dc, {0, 0, 0, ULJM05428, 0, "ULJM05428"}},
		// 金色のコルダ
		{0x886162c, {0, 0, 0, ULJM05428, 0, "ULJM05054"}}, // dialogue: 0x886162c (x1), 0x889d5fc-0x889d520(a2) fullLine
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
		// Fate/EXTRA
		{0x88B87F0, {0, 6, 0, 0, FNPJH50247, "NPJH50247"}},
		// 神々の悪戯 InFinite
		{0x088630f8, {0, 0, 0, QNPJH50909, 0, "NPJH50909"}}, // text, choice (debounce trailing 400ms), TODO: better hook
		{0x0887813c, {0, 3, 4, 0, 0, "NPJH50909"}},			 // Question YN
		// 月華繚乱ROMANCE
		{0x88eeba4, {0, 0, 0, 0, ULJM05943F, "ULJM05943"}}, // a0 - monologue text
		{0x8875e0c, {0, 1, 6, 0, ULJM05943F, "ULJM05943"}}, // a1 - dialogue text
		// My Merry May with be
		{0x886F014, {0, 3, 0, 0, FULJM05603, "ULJM05603"}},
		// コープスパーティー -THE ANTHOLOGY- サチコの恋愛遊戯♥Hysteric Birthday 2U
		{0x88517C8, {0, 1, 0, 0, FULJM05603, "ULJM06114"}},
		// 向日葵の教会と長い夏休み
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
		// ときめきメモリアル4
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
		{0x8955CE0, {0, 0, 0, ULJM05810, 0, "ULJM05810"}},
		// 十鬼の絆
		{0x891AAAC, {0, 0, 0, 0, ULJM06129, "ULJM06129"}}, // text
		{0x886E094, {0, 0, 0, 0, ULJM06129, "ULJM06129"}}, // name+text
		// ティンクル☆くるせいだーす STARLIT BRAVE!!
		{0x88A94BC, {0, 4, 0, 0, 0, "ULJS00315"}}, // text
		// ティンクル☆くるせいだーす GoGo!
		{0x8822F24, {0, 0xe, 0, 0, 0, "ULJS00316"}}, // text
		// 明治東亰恋伽 トワヰライト・キス
		{0x884DE44, {0, 0, 0, 0, NPJH50900, "NPJH50900"}}, // text
		// Never7 -the end of infinity-
		{0x88196F0, {0, 0xe, 0, 0, ULJM05433, "ULJM05433"}},
		// 青春はじめました！
		{0x880a744, {0, 0, 0, 0, ULJM05943F, "ULJM0630[23]"}}, // ULJM06302 & ULJM06303
		// アーメン・ノワール ポータブル
		{0x883b6a8, {0, 0, 0, 0, ULJM05943F, "ULJM06064"}},
		// デス・コネクション　ポータブル
		{0x882AEF4, {0, 0, 0, 0, ULJM05823_1, "ULJM05823"}},
		{0x88B2464, {0, 0, 0, 0, ULJM05823_2, "ULJM05823"}}, // text+name->name
		// しらつゆの怪
		{0x888A26C, {0, 0, 0, 0, ULJM06289, "ULJM06289"}},
		// 新装版クローバーの国のアリス～Wonderful Wonder World～
		{0x8875E50, {0, 1, 0, 0, 0, "NPJH50894"}},
		// ダイヤの国のアリス～Wonderful Wonder World～
		{0x8857E3C, {0, 0, 0, 0, 0, "ULJM06216"}},
		// ダイヤの国のアリス～ Wonderful Mirror World ～
		{0x8855AE4, {0, 1, 0, 0, 0, "ULJM06295"}},
		// ハートの国のアリス～Wonderful Twin World～
		{0x8881CAC, {0, 1, 0, 0, 0, "NPJH50872"}},
		// 新装版 ハートの国のアリス～Wonderful Wonder World～
		{0x886B610, {0, 1, 0, 0, 0, "ULJM06332"}},
		// S・Y・K ～新説西遊記～ ポータブル
		{0x88DD918, {0, 0, 0, 0, ULJM05823_2, "ULJM05697"}}, // text+name->name
		{0x88DA420, {0, 4, 0, 0, ULJM05823_1, "ULJM05697"}},
		// Glass Heart Princess
		{0x885FA30, {0, 0, 0, 0, ULJM05823_1, "ULJM06196"}},
		// Glass Heart Princess:PLATINUM
		{0x885D4F0, {0, 0, 0, 0, ULJM05823_1, "ULJM06309"}},
		// ウィル・オ・ウィスプ ポータブル
		{0x885DD04, {0, 0, 0, 0, ULJM05823_1, "ULJM05447"}},
		// 華鬼 ～恋い初める刻 永久の印～
		{0x8829F14, {0, 4, 0, 0, ULJM05823_1, "ULJM05847"}},
		{0x886D270, {0, 0, 0, 0, ULJM05823_2, "ULJM05847"}},
		// 華鬼 ～夢のつづき～
		{0x88406CC, {0, 0, 0, 0, ULJM05823_1, "ULJM06048"}}, // text
		{0x885B7BC, {0, 0, 0, 0, ULJM05823_1, "ULJM06048"}}, // name+text
		// サモンナイト３
		{0x89DCF90, {0, 6, 0, 0, NPJH50380, "NPJH50380"}},
		// Steins;Gate 比翼恋理のだーりん
		{0x8856968, {0, 4, 0, 0, ULJM06040_1, "ULJM06040"}},
		{0x889AD70, {0, 1, 0, 0, ULJM06040_2, "ULJM06040"}},
		// 鋼鉄のガールフレンド特別編ポータブル
		{0x882AAA4, {0, 1, 0, 0, ULJM05456, "ULJM05456"}},
		// 鋼鉄のガールフレンド2ndポータブル
		{0x8807FAC, {0, 1, 0, 0, ULJM05477, "ULJM05477"}},
		// アイドルマスターSP パーフェクトサン
		{0x8951A7C, {0, 1, 0, 0, ULJS00169, "ULJS00167"}},
		// アイドルマスターSP ワンダリングスター
		{0x8955E54, {0, 0, 0, 0, ULJS00169, "ULJS00168"}},
		// アイドルマスターSP ミッシングムーン
		{0x8951AE0, {0, 1, 0, 0, ULJS00169, "ULJS00169"}},
		// カヌチ 二つの翼
		{0x88158A0, {0, 0, 0, 0, ULJM05796, "ULJM0579[67]"}}, // ULJM05796 & ULJM05797
		// うたわれるもの PORTABLE
		{0x881CC54, {0, 0, 0, 0, ULJM05458, "ULJM05458"}},
		// とある科学の超電磁砲
		{0x88363A8, {FULL_STRING, 1, 0, 0, ULJS00354, "ULJS00354"}},
		// 幻想水滸伝　紡がれし百年の時
		{0x893FF00, {0, 0, 0, 0, NPJH50535, "NPJH50535"}},
		// アンチェインブレイズ レクス
		{0x88FD624, {CODEC_UTF8, 4, 0, 0, ULJM05756, "ULJM05756"}},
	};

}