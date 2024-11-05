#include "extension.h"
#include "blockmarkup.h"
#include <cwctype>
#include <fstream>
#include <sstream>
#include <process.h>

extern const wchar_t* REPLACER_INSTRUCTIONS;

constexpr auto REPLACE_SAVE_FILE = u8"SavedReplacements.txt";

std::atomic<std::filesystem::file_time_type> replaceFileLastWrite = {};
concurrency::reader_writer_lock m;

class Trie
{
public:
	Trie(const std::istream& replacementScript)
	{
		BlockMarkupIterator replacementScriptParser(replacementScript, Array<std::wstring_view>{ L"|ORIG|", L"|BECOMES|" });
		while (auto read = replacementScriptParser.Next())
		{
			const auto& [original, replacement] = read.value();
			Node* current = &root;
			for (auto ch : original) if (!Ignore(ch)) current = Next(current, ch);
			if (current != &root)
				current->value = charStorage.insert(charStorage.end(), replacement.c_str(), replacement.c_str() + replacement.size() + 1) - charStorage.begin();
		}
	}

	std::wstring Replace(const std::wstring& sentence) const
	{
		std::wstring result;
		for (int i = 0; i < sentence.size();)
		{
			std::wstring_view replacement(sentence.c_str() + i, 1);
			int originalLength = 1;

			const Node* current = &root;
			for (int j = i; current && j <= sentence.size(); ++j)
			{
				if (current->value >= 0)
				{
					replacement = charStorage.data() + current->value;
					originalLength = j - i;
				}
				if (!Ignore(sentence[j])) current = Next(current, sentence[j]) ? Next(current, sentence[j]) : Next(current, L'^');
			}

			result += replacement;
			i += originalLength;
		}
		return result;
	}

	bool Empty()
	{
		return root.charMap.empty();
	}

private:
	static bool Ignore(wchar_t ch)
	{
		return ch <= 0x20 || iswspace(ch);
	}

	template <typename Node>
	static Node* Next(Node* node, wchar_t ch)
	{
		auto it = std::lower_bound(node->charMap.begin(), node->charMap.end(), ch, [](const auto& one, auto two) { return one.first < two; });
		if (it != node->charMap.end() && it->first == ch) return it->second.get();
		if constexpr (!std::is_const_v<Node>) return node->charMap.insert(it, { ch, std::make_unique<Node>() })->second.get();
		return nullptr;
	}

	struct Node
	{
		std::vector<std::pair<wchar_t, std::unique_ptr<Node>>> charMap;
		ptrdiff_t value = -1;
	} root;

	std::vector<wchar_t> charStorage;
} trie = { std::istringstream("") };

void UpdateReplacements()
{
	try
	{
		if (replaceFileLastWrite.exchange(std::filesystem::last_write_time(REPLACE_SAVE_FILE)) == std::filesystem::last_write_time(REPLACE_SAVE_FILE)) return;
		std::scoped_lock lock(m);
		trie = Trie(std::ifstream(REPLACE_SAVE_FILE, std::ios::binary));
	}
	catch (std::filesystem::filesystem_error) { replaceFileLastWrite.store({}); }
}

BOOL WINAPI DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	{
		UpdateReplacements();
		if (trie.Empty())
		{
			auto file = std::ofstream(REPLACE_SAVE_FILE, std::ios::binary) << "\xff\xfe";
			for (auto ch : std::wstring_view(REPLACER_INSTRUCTIONS))
				file << (ch == L'\n' ? std::string_view("\r\0\n", 4) : std::string_view((char*)&ch, 2));
			SpawnThread([] { _spawnlp(_P_DETACH, "notepad", "notepad", REPLACE_SAVE_FILE, NULL); }); // show file to user
		}
	}
	break;
	case DLL_PROCESS_DETACH:
	{
	}
	break;
	}
	return TRUE;
}

bool ProcessSentence(std::wstring& sentence, SentenceInfo)
{
	UpdateReplacements();

	concurrency::reader_writer_lock::scoped_lock_read readLock(m);
	sentence = trie.Replace(sentence);
	return true;
}

TEST(
	{
		std::wstring replacementScript = LR"(
|ORIG|さよなら|BECOMES|goodbye |END|Ignore this text
And this text ツ　　
|ORIG|バカ|BECOMES|idiot|END|
|ORIG|こんにちは |BECOMES| hello|END||ORIG|delet^this|BECOMES||END|)";
		Trie replacements(std::istringstream(std::string{ (const char*)replacementScript.c_str(), replacementScript.size() * sizeof(wchar_t) }));
		std::wstring original = LR"(Don't replace this　
 さよなら バカ こんにちは delete this)";
		std::wstring replaced = Trie(std::move(replacements)).Replace(original);
		assert(replaced == L"Don't replace thisgoodbye idiot hello");
	}
);
