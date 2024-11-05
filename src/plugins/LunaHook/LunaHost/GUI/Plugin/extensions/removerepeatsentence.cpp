#include "extension.h"

int sentenceCacheSize = 30;

BOOL WINAPI DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	{
		wchar_t filePath[MAX_PATH];
		GetModuleFileNameW(hModule, filePath, MAX_PATH);
		if (wchar_t* fileName = wcsrchr(filePath, L'\\')) swscanf_s(fileName, L"\\Remove %d Repeated Sentences.xdll", &sentenceCacheSize);
	}
	break;
	case DLL_PROCESS_DETACH:
	{
	}
	break;
	}
	return TRUE;
}

bool ProcessSentence(std::wstring& sentence, SentenceInfo sentenceInfo)
{
	uint64_t textNumber = sentenceInfo["text number"];
	if (textNumber == 0) return false;

	static std::deque<Synchronized<std::vector<std::wstring>>> cache;
	static std::mutex m;
	m.lock();
	if (textNumber + 1 > cache.size()) cache.resize(textNumber + 1);
	auto prevSentences = cache[textNumber].Acquire();
	m.unlock();
	auto& inserted = prevSentences->emplace_back(sentence);
	auto firstLocation = std::find(prevSentences->begin(), prevSentences->end(), sentence);
	if (&*firstLocation != &inserted)
	{
		prevSentences->erase(firstLocation);
		sentence.clear();
	}
	if (prevSentences->size() > sentenceCacheSize) prevSentences->erase(prevSentences->begin());
	return sentence.empty();
}
