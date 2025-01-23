#include "extension.h"

bool ProcessSentence(std::wstring &sentence, SentenceInfo sentenceInfo);

/*
	You shouldn't mess with this or even look at it unless you're certain you know what you're doing.
	Param sentence: pointer to sentence received by Textractor (UTF-16).
	This can be modified. Textractor uses the modified sentence for future processing and display. If empty (starts with null terminator), Textractor will destroy it.
	Textractor will display the sentence after all extensions have had a chance to process and/or modify it.
	The buffer is allocated using HeapAlloc(). If you want to make it larger, please use HeapReAlloc().
	Param sentenceInfo: pointer to array containing misc info about the sentence. End of array is marked with name being nullptr.
	Return value: the buffer used for the sentence. Remember to return a new pointer if HeapReAlloc() gave you one.
	This function may be run concurrently with itself: please make sure it's thread safe.
	It will not be run concurrently with DllMain.
*/
extern "C" __declspec(dllexport) wchar_t *OnNewSentence(wchar_t *sentence, const InfoForExtension *sentenceInfo)
{
	try
	{
		std::wstring sentenceCopy(sentence);
		int oldSize = sentenceCopy.size();
		if (ProcessSentence(sentenceCopy, SentenceInfo{sentenceInfo}))
		{
			if (sentenceCopy.size() > oldSize)
				sentence = (wchar_t *)HeapReAlloc(GetProcessHeap(), HEAP_GENERATE_EXCEPTIONS, sentence, (sentenceCopy.size() + 1) * sizeof(wchar_t));
			wcscpy_s(sentence, sentenceCopy.size() + 1, sentenceCopy.c_str());
		}
	}
	catch (SKIP)
	{
		*sentence = L'\0';
	}
	return sentence;
}

/*
This API is not necessary, but when the plugin contains a configuration window, this API allows the user to show or hide the configuration window, which can greatly improve the user experience.
*/
/*
extern "C" __declspec(dllexport) void VisSetting(bool vis)
{

}
*/