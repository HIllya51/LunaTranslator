#include "qtcommon.h"
#include "translatewrapper.h"
#include "network.h"

extern const wchar_t* TRANSLATION_ERROR;

const char* TRANSLATION_PROVIDER = "Bing Translate";
const char* GET_API_KEY_FROM = "https://www.microsoft.com/en-us/translator/business/trial/#get-started";
extern const QStringList languagesTo
{
   "Afrikaans",
   "Albanian",
   "Amharic",
   "Arabic",
   "Armenian",
   "Assamese",
   "Azerbaijani",
   "Bangla",
   "Bosnian (Latin)",
   "Bulgarian",
   "Cantonese (Traditional)",
   "Catalan",
   "Chinese (Simplified)",
   "Chinese (Traditional)",
   "Croatian",
   "Czech",
   "Danish",
   "Dari",
   "Dutch",
   "English",
   "Estonian",
   "Fijian",
   "Filipino",
   "Finnish",
   "French",
   "French (Canada)",
   "German",
   "Greek",
   "Gujarati",
   "Haitian Creole",
   "Hebrew",
   "Hindi",
   "Hmong Daw",
   "Hungarian",
   "Icelandic",
   "Indonesian",
   "Inuktitut",
   "Irish",
   "Italian",
   "Japanese",
   "Kannada",
   "Kazakh",
   "Khmer",
   "Klingon",
   "Korean",
   "Kurdish (Central)",
   "Kurdish (Northern)",
   "Lao",
   "Latvian",
   "Lithuanian",
   "Malagasy",
   "Malay",
   "Malayalam",
   "Maltese",
   "Maori",
   "Marathi",
   "Myanmar",
   "Nepali",
   "Norwegian",
   "Odia",
   "Pashto",
   "Persian",
   "Polish",
   "Portuguese (Brazil)",
   "Portuguese (Portugal)",
   "Punjabi",
   "Queretaro Otomi",
   "Romanian",
   "Russian",
   "Samoan",
   "Serbian (Cyrillic)",
   "Serbian (Latin)",
   "Slovak",
   "Slovenian",
   "Spanish",
   "Swahili",
   "Swedish",
   "Tahitian",
   "Tamil",
   "Telugu",
   "Thai",
   "Tigrinya",
   "Tongan",
   "Turkish",
   "Ukrainian",
   "Urdu",
   "Vietnamese",
   "Welsh",
   "Yucatec Maya"
}, languagesFrom = languagesTo;
extern const std::unordered_map<std::wstring, std::wstring> codes
{
	{ { L"Afrikaans" }, { L"af" } },
	{ { L"Albanian" }, { L"sq" } },
	{ { L"Amharic" }, { L"am" } },
	{ { L"Arabic" }, { L"ar" } },
	{ { L"Armenian" }, { L"hy" } },
	{ { L"Assamese" }, { L"as" } },
	{ { L"Azerbaijani" }, { L"az" } },
	{ { L"Bangla" }, { L"bn" } },
	{ { L"Bosnian (Latin)" }, { L"bs" } },
	{ { L"Bulgarian" }, { L"bg" } },
	{ { L"Cantonese (Traditional)" }, { L"yue" } },
	{ { L"Catalan" }, { L"ca" } },
	{ { L"Chinese (Simplified)" }, { L"zh-Hans" } },
	{ { L"Chinese (Traditional)" }, { L"zh-Hant" } },
	{ { L"Croatian" }, { L"hr" } },
	{ { L"Czech" }, { L"cs" } },
	{ { L"Danish" }, { L"da" } },
	{ { L"Dari" }, { L"prs" } },
	{ { L"Dutch" }, { L"nl" } },
	{ { L"English" }, { L"en" } },
	{ { L"Estonian" }, { L"et" } },
	{ { L"Fijian" }, { L"fj" } },
	{ { L"Filipino" }, { L"fil" } },
	{ { L"Finnish" }, { L"fi" } },
	{ { L"French" }, { L"fr" } },
	{ { L"French (Canada)" }, { L"fr-ca" } },
	{ { L"German" }, { L"de" } },
	{ { L"Greek" }, { L"el" } },
	{ { L"Gujarati" }, { L"gu" } },
	{ { L"Haitian Creole" }, { L"ht" } },
	{ { L"Hebrew" }, { L"he" } },
	{ { L"Hindi" }, { L"hi" } },
	{ { L"Hmong Daw" }, { L"mww" } },
	{ { L"Hungarian" }, { L"hu" } },
	{ { L"Icelandic" }, { L"is" } },
	{ { L"Indonesian" }, { L"id" } },
	{ { L"Inuktitut" }, { L"iu" } },
	{ { L"Irish" }, { L"ga" } },
	{ { L"Italian" }, { L"it" } },
	{ { L"Japanese" }, { L"ja" } },
	{ { L"Kannada" }, { L"kn" } },
	{ { L"Kazakh" }, { L"kk" } },
	{ { L"Khmer" }, { L"km" } },
	{ { L"Klingon" }, { L"tlh-Latn" } },
	{ { L"Korean" }, { L"ko" } },
	{ { L"Kurdish (Central)" }, { L"ku" } },
	{ { L"Kurdish (Northern)" }, { L"kmr" } },
	{ { L"Lao" }, { L"lo" } },
	{ { L"Latvian" }, { L"lv" } },
	{ { L"Lithuanian" }, { L"lt" } },
	{ { L"Malagasy" }, { L"mg" } },
	{ { L"Malay" }, { L"ms" } },
	{ { L"Malayalam" }, { L"ml" } },
	{ { L"Maltese" }, { L"mt" } },
	{ { L"Maori" }, { L"mi" } },
	{ { L"Marathi" }, { L"mr" } },
	{ { L"Myanmar" }, { L"my" } },
	{ { L"Nepali" }, { L"ne" } },
	{ { L"Norwegian" }, { L"nb" } },
	{ { L"Odia" }, { L"or" } },
	{ { L"Pashto" }, { L"ps" } },
	{ { L"Persian" }, { L"fa" } },
	{ { L"Polish" }, { L"pl" } },
	{ { L"Portuguese (Brazil)" }, { L"pt" } },
	{ { L"Portuguese (Portugal)" }, { L"pt-pt" } },
	{ { L"Punjabi" }, { L"pa" } },
	{ { L"Queretaro Otomi" }, { L"otq" } },
	{ { L"Romanian" }, { L"ro" } },
	{ { L"Russian" }, { L"ru" } },
	{ { L"Samoan" }, { L"sm" } },
	{ { L"Serbian (Cyrillic)" }, { L"sr-Cyrl" } },
	{ { L"Serbian (Latin)" }, { L"sr-Latn" } },
	{ { L"Slovak" }, { L"sk" } },
	{ { L"Slovenian" }, { L"sl" } },
	{ { L"Spanish" }, { L"es" } },
	{ { L"Swahili" }, { L"sw" } },
	{ { L"Swedish" }, { L"sv" } },
	{ { L"Tahitian" }, { L"ty" } },
	{ { L"Tamil" }, { L"ta" } },
	{ { L"Telugu" }, { L"te" } },
	{ { L"Thai" }, { L"th" } },
	{ { L"Tigrinya" }, { L"ti" } },
	{ { L"Tongan" }, { L"to" } },
	{ { L"Turkish" }, { L"tr" } },
	{ { L"Ukrainian" }, { L"uk" } },
	{ { L"Urdu" }, { L"ur" } },
	{ { L"Vietnamese" }, { L"vi" } },
	{ { L"Welsh" }, { L"cy" } },
	{ { L"Yucatec Maya" }, { L"yua" } },
	{ { L"?" }, { L"auto-detect" } }
};

bool translateSelectedOnly = false, useRateLimiter = true, rateLimitSelected = false, useCache = true, useFilter = true;
int tokenCount = 30, rateLimitTimespan = 60000, maxSentenceSize = 1000;

std::pair<bool, std::wstring> Translate(const std::wstring& text, TranslationParam tlp)
{
	if (!tlp.authKey.empty())
	{
		std::wstring translateFromComponent = tlp.translateFrom == L"?" ? L"" : L"&from=" + codes.at(tlp.translateFrom);
		if (HttpRequest httpRequest{
			L"Mozilla/5.0 Textractor",
			L"api.cognitive.microsofttranslator.com",
			L"POST",
			FormatString(L"/translate?api-version=3.0&to=%s%s", codes.at(tlp.translateTo), translateFromComponent).c_str(),
			FormatString(R"([{"text":"%s"}])", JSON::Escape(WideStringToString(text))),
			FormatString(L"Content-Type: application/json; charset=UTF-8\r\nOcp-Apim-Subscription-Key:%s", tlp.authKey).c_str()
		})
			if (auto translation = Copy(JSON::Parse(httpRequest.response)[0][L"translations"][0][L"text"].String())) return { true, translation.value() };
			else return { false, FormatString(L"%s: %s", TRANSLATION_ERROR, httpRequest.response) };
		else return { false, FormatString(L"%s (code=%u)", TRANSLATION_ERROR, httpRequest.errorCode) };
	}

	static std::atomic<int> i = 0;
	static Synchronized<std::wstring> token;
	if (token->empty()) if (HttpRequest httpRequest{ L"Mozilla/5.0 Textractor", L"www.bing.com", L"GET", L"translator" })
	{
		std::wstring tokenBuilder;
		if (auto tokenPos = httpRequest.response.find(L"[" + std::to_wstring(time(nullptr) / 100)); tokenPos != std::string::npos)
			tokenBuilder = FormatString(L"&key=%s&token=%s", httpRequest.response.substr(tokenPos + 1, 13), httpRequest.response.substr(tokenPos + 16, 32));
		if (auto tokenPos = httpRequest.response.find(L"IG:\""); tokenPos != std::string::npos)
			tokenBuilder += L"&IG=" + httpRequest.response.substr(tokenPos + 4, 32);
		if (auto tokenPos = httpRequest.response.find(L"data-iid=\""); tokenPos != std::string::npos)
			tokenBuilder += L"&IID=" + httpRequest.response.substr(tokenPos + 10, 15);
		if (!tokenBuilder.empty()) token->assign(tokenBuilder);
		else return { false, FormatString(L"%s: %s\ntoken not found", TRANSLATION_ERROR, httpRequest.response) };
	}
	else return { false, FormatString(L"%s: could not acquire token", TRANSLATION_ERROR) };

	if (HttpRequest httpRequest{
		L"Mozilla/5.0 Textractor",
		L"www.bing.com",
		L"POST",
		FormatString(L"/ttranslatev3?fromLang=%s&to=%s&text=%s%s.%d", codes.at(tlp.translateFrom), codes.at(tlp.translateTo), Escape(text), token.Copy(), i++).c_str()
	})
		if (auto translation = Copy(JSON::Parse(httpRequest.response)[0][L"translations"][0][L"text"].String())) return { true, translation.value() };
		else return { false, FormatString(L"%s (token=%s): %s", TRANSLATION_ERROR, std::exchange(token.Acquire().contents, L""), httpRequest.response) };
	else return { false, FormatString(L"%s (code=%u)", TRANSLATION_ERROR, httpRequest.errorCode) };
}
