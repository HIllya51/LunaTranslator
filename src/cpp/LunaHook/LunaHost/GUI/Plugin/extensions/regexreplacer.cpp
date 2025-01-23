#include "extension.h"
#include "blockmarkup.h"
#include <fstream>
#include <process.h>

extern const wchar_t *REGEX_REPLACER_INSTRUCTIONS;

const char *REPLACE_SAVE_FILE = "SavedRegexReplacements.txt";

std::atomic<std::filesystem::file_time_type> replaceFileLastWrite = {};
concurrency::reader_writer_lock m;
std::vector<std::tuple<std::wregex, std::wstring, std::regex_constants::match_flag_type>> replacements;

void UpdateReplacements()
{
	try
	{
		if (replaceFileLastWrite.exchange(std::filesystem::last_write_time(REPLACE_SAVE_FILE)) == std::filesystem::last_write_time(REPLACE_SAVE_FILE))
			return;
		std::scoped_lock lock(m);
		replacements.clear();
		std::ifstream stream(REPLACE_SAVE_FILE, std::ios::binary);
		BlockMarkupIterator savedFilters(stream, Array<std::wstring_view>{L"|REGEX|", L"|BECOMES|", L"|MODIFIER|"});
		while (auto read = savedFilters.Next())
		{
			const auto &[regex, replacement, modifier] = read.value();
			try
			{
				replacements.emplace_back(
					std::wregex(regex, modifier.find(L'i') == std::string::npos ? std::regex::ECMAScript : std::regex::icase),
					replacement,
					modifier.find(L'g') == std::string::npos ? std::regex_constants::format_first_only : std::regex_constants::format_default);
			}
			catch (std::regex_error)
			{
			}
		}
	}
	catch (std::filesystem::filesystem_error)
	{
		replaceFileLastWrite.store({});
	}
}

BOOL WINAPI DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	{
		UpdateReplacements();
		if (replacements.empty())
		{
			auto file = std::ofstream(REPLACE_SAVE_FILE, std::ios::binary) << "\xff\xfe";
			for (auto ch : std::wstring_view(REGEX_REPLACER_INSTRUCTIONS))
				file << (ch == L'\n' ? std::string_view("\r\0\n", 4) : std::string_view((char *)&ch, 2));
			SpawnThread([]
						{ _spawnlp(_P_DETACH, "notepad", "notepad", REPLACE_SAVE_FILE, NULL); }); // show file to user
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

bool ProcessSentence(std::wstring &sentence, SentenceInfo sentenceInfo)
{
	UpdateReplacements();

	concurrency::reader_writer_lock::scoped_lock_read readLock(m);
	for (const auto &[regex, replacement, flags] : replacements)
		sentence = std::regex_replace(sentence, regex, replacement, flags);
	return true;
}
