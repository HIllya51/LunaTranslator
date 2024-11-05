#include "extension.h"

bool ProcessSentence(std::wstring& sentence, SentenceInfo sentenceInfo)
{
	if (sentenceInfo["text number"] == 0) return false;

	std::vector<int> repeatNumbers(sentence.size() + 1, 0);
	for (int i = 0; i < sentence.size(); ++i)
	{
		if (sentence[i] != sentence[i + 1])
		{
			int j = i;
			while (sentence[j] == sentence[i] && --j >= 0);
			repeatNumbers[i - j] += 1;
		}
	}
	int repeatNumber = std::distance(repeatNumbers.begin(), std::max_element(repeatNumbers.rbegin(), repeatNumbers.rend()).base() - 1);
	if (repeatNumber < 2) return false;

	std::wstring newSentence;
	for (int i = 0; i < sentence.size();)
	{
		newSentence.push_back(sentence[i]);
		for (int j = i; j <= sentence.size(); ++j)
		{
			if (j == sentence.size() || sentence[i] != sentence[j])
			{
				i += (j - i) % repeatNumber == 0 ? repeatNumber : 1;
				break;
			}
		}
	}
	sentence = newSentence;
	return true;
}

TEST(
	{
		InfoForExtension nonConsole[] = { { "text number", 1 }, {} };

		std::wstring repeatedChars = L"aaaaaaaaaaaabbbbbbcccdddaabbbcccddd";
		std::wstring someRepeatedChars = L"abcdefaabbccddeeff";
		ProcessSentence(repeatedChars, { nonConsole });
		ProcessSentence(someRepeatedChars, { nonConsole });
		assert(repeatedChars.find(L"aaaabbcd") == 0);
		assert(someRepeatedChars == L"abcdefabcdef");

		std::wstring empty = L"", one = L" ", normal = L"This is a normal sentence. はい";
		ProcessSentence(empty, { nonConsole });
		ProcessSentence(one, { nonConsole });
		ProcessSentence(normal, { nonConsole });
		assert(empty == L"" && one == L" " && normal == L"This is a normal sentence. はい");
	}
);
