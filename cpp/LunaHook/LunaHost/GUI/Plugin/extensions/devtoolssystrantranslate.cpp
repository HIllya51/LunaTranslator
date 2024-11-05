#include "qtcommon.h"
#include "translatewrapper.h"
#include "devtools.h"

extern const wchar_t* ERROR_START_CHROME;
extern const wchar_t* TRANSLATION_ERROR;

const char* TRANSLATION_PROVIDER = "DevTools Systran Translate";
const char* GET_API_KEY_FROM = nullptr;

extern const QStringList languagesTo
{
	"Albanian",
	"Arabic",
	"Bengali",
	"Bulgarian",
	"Burmese",
	"Catalan",
	"Chinese (Simplified)",
	"Chinese (Traditional)",
	"Croatian",
	"Czech",
	"Danish",
	"Dutch",
	"English",
	"Estonian",
	"Finnish",
	"French",
	"German",
	"Greek",
	"Hebrew",
	"Hindi",
	"Hungarian",
	"Indonesian",
	"Italian",
	"Japanese",
	"Korean",
	"Latvian",
	"Lithuanian",
	"Malay",
	"Norwegian",
	"Pashto",
	"Persian",
	"Polish",
	"Portuguese",
	"Romanian",
	"Russian",
	"Serbian",
	"Slovak",
	"Slovenian",
	"Somali",
	"Spanish",
	"Swedish",
	"Tagalog",
	"Tamil",
	"Thai",
	"Turkish",
	"Ukrainian",
	"Urdu",
	"Vietnamese"
}, languagesFrom = languagesTo;
extern const std::unordered_map<std::wstring, std::wstring> codes
{
	{ { L"Albanian" }, { L"sq" } },
	{ { L"Arabic" }, { L"ar" } },
	{ { L"Bengali" }, { L"bn" } },
	{ { L"Bulgarian" }, { L"bg" } },
	{ { L"Burmese" }, { L"my" } },
	{ { L"Catalan" }, { L"ca" } },
	{ { L"Chinese (Simplified)" }, { L"zh" } },
	{ { L"Chinese (Traditional)" }, { L"zt" } },
	{ { L"Croatian" }, { L"hr" } },
	{ { L"Czech" }, { L"cs" } },
	{ { L"Danish" }, { L"da" } },
	{ { L"Dutch" }, { L"nl" } },
	{ { L"English" }, { L"en" } },
	{ { L"Estonian" }, { L"et" } },
	{ { L"Finnish" }, { L"fi" } },
	{ { L"French" }, { L"fr" } },
	{ { L"German" }, { L"de" } },
	{ { L"Greek" }, { L"el" } },
	{ { L"Hebrew" }, { L"he" } },
	{ { L"Hindi" }, { L"hi" } },
	{ { L"Hungarian" }, { L"hu" } },
	{ { L"Indonesian" }, { L"id" } },
	{ { L"Italian" }, { L"it" } },
	{ { L"Japanese" }, { L"ja" } },
	{ { L"Korean" }, { L"ko" } },
	{ { L"Latvian" }, { L"lv" } },
	{ { L"Lithuanian" }, { L"lt" } },
	{ { L"Malay" }, { L"ms" } },
	{ { L"Norwegian" }, { L"no" } },
	{ { L"Pashto" }, { L"ps" } },
	{ { L"Persian" }, { L"fa" } },
	{ { L"Polish" }, { L"pl" } },
	{ { L"Portuguese" }, { L"pt" } },
	{ { L"Romanian" }, { L"ro" } },
	{ { L"Russian" }, { L"ru" } },
	{ { L"Serbian" }, { L"sr" } },
	{ { L"Slovak" }, { L"sk" } },
	{ { L"Slovenian" }, { L"sl" } },
	{ { L"Somali" }, { L"so" } },
	{ { L"Spanish" }, { L"es" } },
	{ { L"Swedish" }, { L"sv" } },
	{ { L"Tagalog" }, { L"tl" } },
	{ { L"Tamil" }, { L"ta" } },
	{ { L"Thai" }, { L"th" } },
	{ { L"Turkish" }, { L"tr" } },
	{ { L"Ukrainian" }, { L"uk" } },
	{ { L"Urdu" }, { L"ur" } },
	{ { L"Vietnamese" }, { L"vi" } },
	{ { L"?" }, { L"autodetect" } }
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

	DevTools::SendRequest(
		"Page.navigate",
		FormatString(LR"({"url":"https://translate.systran.net/?source=%s&target=%s&input=%s"})", codes.at(tlp.translateFrom), codes.at(tlp.translateTo), Escape(text))
	);
	for (int retry = 0; ++retry < 100; Sleep(100))
		if (auto translation = Copy(DevTools::SendRequest("Runtime.evaluate",
			LR"({"expression":"document.querySelector('#outputEditor').textContent.trim() ","returnByValue":true})"
		)[L"result"][L"value"].String())) if (!translation->empty()) return { true, translation.value() };
	return { false, TRANSLATION_ERROR };
}
