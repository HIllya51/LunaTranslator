#include "qtcommon.h"
#include "translatewrapper.h"
#include "devtools.h"

extern const wchar_t* ERROR_START_CHROME;
extern const wchar_t* TRANSLATION_ERROR;

const char* TRANSLATION_PROVIDER = "DevTools DeepL Translate";
const char* GET_API_KEY_FROM = nullptr;

extern const QStringList languagesTo
{
	"Bulgarian",
	"Chinese (Simplified)",
	"Czech",
	"Danish",
	"Dutch",
	"English (American)",
	"English (British)",
	"Estonian",
	"Finnish",
	"French",
	"German",
	"Greek",
	"Hungarian",
	"Italian",
	"Japanese",
	"Latvian",
	"Lithuanian",
	"Polish",
	"Portuguese",
	"Portuguese (Brazilian)",
	"Romanian",
	"Russian",
	"Slovak",
	"Slovenian",
	"Spanish",
	"Swedish"
},
languagesFrom =
{
	"Bulgarian",
	"Chinese",
	"Czech",
	"Danish",
	"Dutch",
	"English",
	"Estonian",
	"Finnish",
	"French",
	"German",
	"Greek",
	"Hungarian",
	"Italian",
	"Japanese",
	"Latvian",
	"Lithuanian",
	"Polish",
	"Portuguese",
	"Romanian",
	"Russian",
	"Slovak",
	"Slovenian",
	"Spanish",
	"Swedish"
};
extern const std::unordered_map<std::wstring, std::wstring> codes
{
	{ { L"Bulgarian" }, { L"Bulgarian" } },
	{ { L"Chinese" }, { L"Chinese" } },
	{ { L"Chinese (Simplified)" }, { L"Chinese (simplified)" } },
	{ { L"Czech" }, { L"Czech" } },
	{ { L"Danish" }, { L"Danish" } },
	{ { L"Dutch" }, { L"Dutch" } },
	{ { L"English" }, { L"English" } },
	{ { L"English (American)" }, { L"English (American)" } },
	{ { L"English (British)" }, { L"English (British)" } },
	{ { L"Estonian" }, { L"Estonian" } },
	{ { L"Finnish" }, { L"Finnish" } },
	{ { L"French" }, { L"French" } },
	{ { L"German" }, { L"German" } },
	{ { L"Greek" }, { L"Greek" } },
	{ { L"Hungarian" }, { L"Hungarian" } },
	{ { L"Italian" }, { L"Italian" } },
	{ { L"Japanese" }, { L"Japanese" } },
	{ { L"Latvian" }, { L"Latvian" } },
	{ { L"Lithuanian" }, { L"Lithuanian" } },
	{ { L"Polish" }, { L"Polish" } },
	{ { L"Portuguese" }, { L"Portuguese" } },
	{ { L"Portuguese (Brazilian)" }, { L"Portuguese (Brazilian)" } },
	{ { L"Romanian" }, { L"Romanian" } },
	{ { L"Russian" }, { L"Russian" } },
	{ { L"Slovak" }, { L"Slovak" } },
	{ { L"Slovenian" }, { L"Slovenian" } },
	{ { L"Spanish" }, { L"Spanish" } },
	{ { L"Swedish" }, { L"Swedish" } },
	{ { L"?" }, { L"Detect language" } }
};

bool translateSelectedOnly = true, useRateLimiter = true, rateLimitSelected = false, useCache = true, useFilter = true;
int tokenCount = 30, rateLimitTimespan = 60000, maxSentenceSize = 2500;

BOOL WINAPI DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved)
{
	switch (ul_reason_for_call)
	{
	case DLL_PROCESS_ATTACH:
	{
		DevTools::Initialize();
	}
	break;
	case DLL_PROCESS_DETACH:
	{
		DevTools::Close();
	}
	break;
	}
	return TRUE;
}

std::pair<bool, std::wstring> Translate(const std::wstring& text, TranslationParam tlp)
{
	if (!DevTools::Connected()) return { false, FormatString(L"%s: %s", TRANSLATION_ERROR, ERROR_START_CHROME) };
	// DevTools can't handle concurrent translations yet
	static std::mutex translationMutex;
	std::scoped_lock lock(translationMutex);
	std::wstring escaped; // DeepL breaks with slash in input
	for (auto ch : text) ch == '/' ? escaped += L"\\/" : escaped += ch;
	DevTools::SendRequest("Page.navigate", FormatString(LR"({"url":"https://www.deepl.com/en/translator#en/en/%s"})", Escape(escaped)));
	for (int retry = 0; ++retry < 20; Sleep(100))
		if (Copy(DevTools::SendRequest("Runtime.evaluate", LR"({"expression":"document.readyState"})")[L"result"][L"value"].String()) == L"complete") break;

	DevTools::SendRequest("Runtime.evaluate", FormatString(LR"({"expression":"
		document.querySelector('.lmt__language_select--source').querySelector('button').click();
		document.evaluate(`//*[text()='%s']`,document.querySelector('.lmt__language_select__menu'),null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click();
		document.querySelector('.lmt__language_select--target').querySelector('button').click();
		document.evaluate(`//*[text()='%s']`,document.querySelector('.lmt__language_select__menu'),null,XPathResult.FIRST_ORDERED_NODE_TYPE,null).singleNodeValue.click();
	"})", codes.at(tlp.translateFrom), codes.at(tlp.translateTo)));

	for (int retry = 0; ++retry < 100; Sleep(100))
		if (auto translation = Copy(DevTools::SendRequest("Runtime.evaluate",
			LR"({"expression":"document.querySelector('#target-dummydiv').innerHTML.trim() ","returnByValue":true})"
		)[L"result"][L"value"].String())) if (!translation->empty()) return { true, translation.value() };
	if (auto errorMessage = Copy(DevTools::SendRequest("Runtime.evaluate",
		LR"({"expression":"document.querySelector('div.lmt__system_notification').innerHTML","returnByValue":true})"
	)[L"result"][L"value"].String())) return { false, FormatString(L"%s: %s", TRANSLATION_ERROR, errorMessage.value()) };
	return { false, TRANSLATION_ERROR };
}
