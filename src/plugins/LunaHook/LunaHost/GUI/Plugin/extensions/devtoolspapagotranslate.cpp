#include "qtcommon.h"
#include "translatewrapper.h"
#include "devtools.h"

extern const wchar_t* ERROR_START_CHROME;
extern const wchar_t* TRANSLATION_ERROR;

const char* TRANSLATION_PROVIDER = "DevTools Papago Translate";
const char* GET_API_KEY_FROM = nullptr;

extern const QStringList languagesTo
{
	"Chinese (Simplified)",
	"Chinese (Traditional)",
	"English",
	"French",
	"German",
	"Hindi",
	"Indonesian",
	"Italian",
	"Japanese",
	"Korean",
	"Portuguese",
	"Russian",
	"Spanish",
	"Thai",
	"Vietnamese",
}, languagesFrom = languagesTo;
extern const std::unordered_map<std::wstring, std::wstring> codes
{
	{ { L"Chinese (Simplified)" }, { L"zh-CN" } },
	{ { L"Chinese (Traditional)" }, { L"zt-TW" } },
	{ { L"English" }, { L"en" } },
	{ { L"French" }, { L"fr" } },
	{ { L"German" }, { L"de" } },
	{ { L"Hindi" }, { L"hi" } },
	{ { L"Indonesian" }, { L"id" } },
	{ { L"Italian" }, { L"it" } },
	{ { L"Japanese" }, { L"ja" } },
	{ { L"Korean" }, { L"ko" } },
	{ { L"Portuguese" }, { L"pt" } },
	{ { L"Russian" }, { L"ru" } },
	{ { L"Spanish" }, { L"es" } },
	{ { L"Thai" }, { L"th" } },
	{ { L"Vietnamese" }, { L"vi" } },
	{ { L"?" }, { L"auto" } }
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
	DevTools::SendRequest("Page.navigate", FormatString(LR"({"url":"https://papago.naver.com/?sk=%s&tk=%s&st=%s"})", codes.at(tlp.translateFrom), codes.at(tlp.translateTo), Escape(text)));
	for (int retry = 0; ++retry < 100; Sleep(100))
		if (auto translation = Copy(DevTools::SendRequest("Runtime.evaluate",
			LR"({"expression":"document.querySelector('#txtTarget').textContent.trim() ","returnByValue":true})"
		)[L"result"][L"value"].String())) if (!translation->empty()) return { true, translation.value() };
	return { false, TRANSLATION_ERROR };
}
