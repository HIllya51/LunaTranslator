#include "qtcommon.h"
#include "translatewrapper.h"
#include "network.h"
#include <random>

extern const wchar_t* TRANSLATION_ERROR;

const char* TRANSLATION_PROVIDER = "DeepL Translate";
const char* GET_API_KEY_FROM = "https://www.deepl.com/pro.html#developer";
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
	"Indonesian",
	"Italian",
	"Japanese",
	"Latvian",
	"Lithuanian",
	"Polish",
	"Portuguese (Brazil)",
	"Portuguese (Portugal)",
	"Romanian",
	"Russian",
	"Slovak",
	"Slovenian",
	"Spanish",
	"Swedish",
	"Turkish"
},
languagesFrom
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
	"Indonesian",
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
	"Swedish",
	"Turkish"
};
extern const std::unordered_map<std::wstring, std::wstring> codes
{
	{ { L"Bulgarian" }, { L"BG" } },
	{ { L"Chinese" }, { L"ZH" } },
	{ { L"Chinese (Simplified)" }, { L"ZH" } },
	{ { L"Czech" }, { L"CS" } },
	{ { L"Danish" }, { L"DA" } },
	{ { L"Dutch" }, { L"NL" } },
	{ { L"English" }, { L"EN" } },
	{ { L"English (American)" }, { L"EN-US" } },
	{ { L"English (British)" }, { L"EN-GB" } },
	{ { L"Estonian" }, { L"ET" } },
	{ { L"Finnish" }, { L"FI" } },
	{ { L"French" }, { L"FR" } },
	{ { L"German" }, { L"DE" } },
	{ { L"Greek" }, { L"EL" } },
	{ { L"Hungarian" }, { L"HU" } },
	{ { L"Indonesian" }, { L"ID" } },
	{ { L"Italian" }, { L"IT" } },
	{ { L"Japanese" }, { L"JA" } },
	{ { L"Latvian" }, { L"LV" } },
	{ { L"Lithuanian" }, { L"LT" } },
	{ { L"Polish" }, { L"PL" } },
	{ { L"Portuguese" }, { L"PT" } },
	{ { L"Portuguese (Brazil)" }, { L"PT-BR" } },
	{ { L"Portuguese (Portugal)" }, { L"PT-PT" } },
	{ { L"Romanian" }, { L"RO" } },
	{ { L"Russian" }, { L"RU" } },
	{ { L"Slovak" }, { L"SK" } },
	{ { L"Slovenian" }, { L"SL" } },
	{ { L"Spanish" }, { L"ES" } },
	{ { L"Swedish" }, { L"SV" } },
	{ { L"Turkish" }, { L"TR" } },
	{ { L"?" }, { L"auto" } }
};

bool translateSelectedOnly = true, useRateLimiter = true, rateLimitSelected = true, useCache = true, useFilter = true;
int tokenCount = 10, rateLimitTimespan = 60000, maxSentenceSize = 1000;

enum KeyType { CAT, REST };
int keyType = REST;

std::pair<bool, std::wstring> Translate(const std::wstring& text, TranslationParam tlp)
{
	if (!tlp.authKey.empty())
	{
		std::string translateFromComponent = tlp.translateFrom == L"?" ? "" : "&source_lang=" + WideStringToString(codes.at(tlp.translateFrom));
		if (HttpRequest httpRequest{
			L"Mozilla/5.0 Textractor",
			tlp.authKey.find(L":fx") == std::string::npos ? L"api.deepl.com" : L"api-free.deepl.com",
			L"POST",
			keyType == CAT ? L"/v1/translate" : L"/v2/translate",
			FormatString("text=%S&auth_key=%S&target_lang=%S", Escape(text), tlp.authKey, codes.at(tlp.translateTo)) + translateFromComponent,
			L"Content-Type: application/x-www-form-urlencoded"
		}; httpRequest && (httpRequest.response.find(L"translations") != std::string::npos || (httpRequest = HttpRequest{
			L"Mozilla/5.0 Textractor",
			tlp.authKey.find(L":fx") == std::string::npos ? L"api.deepl.com" : L"api-free.deepl.com",
			L"POST",
			(keyType = !keyType) == CAT ? L"/v1/translate" : L"/v2/translate",
			FormatString("text=%S&auth_key=%S&target_lang=%S", Escape(text), tlp.authKey, codes.at(tlp.translateTo)) + translateFromComponent,
			L"Content-Type: application/x-www-form-urlencoded"
		})))
			// Response formatted as JSON: translation starts with text":" and ends with "}]
			if (auto translation = Copy(JSON::Parse(httpRequest.response)[L"translations"][0][L"text"].String())) return { true, translation.value() };
			else return { false, FormatString(L"%s: %s", TRANSLATION_ERROR, httpRequest.response) };
		else return { false, FormatString(L"%s (code=%u)", TRANSLATION_ERROR, httpRequest.errorCode) };
	}

	// the following code was reverse engineered from the DeepL website; it's as close as I could make it but I'm not sure what parts of this could be removed and still have it work
	int id = 10000 * std::uniform_int_distribution(0, 9999)(std::random_device()) + 1;
	int64_t r = _time64(nullptr), n = std::count(text.begin(), text.end(), L'i') + 1;
	// user_preferred_langs? what should priority be? does timestamp do anything? other translation quality options?
	auto body = FormatString(R"(
{
	"id": %d,
	"jsonrpc": "2.0",
	"method": "LMT_handle_jobs",
	"params": {
		"priority": -1,
		"timestamp": %lld,
		"lang": {
			"target_lang": "%.2S",
			"source_lang_user_selected": "%S"
		},
		"jobs": [{
			"raw_en_sentence": "%s",
			"raw_en_context_before": [],
			"kind": "default",
			"preferred_num_beams": 1,
			"quality": "fast",
			"raw_en_context_after": []
		}]
	}
}
	)", id, r + (n - r % n), codes.at(tlp.translateTo), codes.at(tlp.translateFrom), JSON::Escape(WideStringToString(text)));
	// missing accept-encoding header since it fucks up HttpRequest
	if (HttpRequest httpRequest{
		L"Mozilla/5.0 Textractor",
		L"www2.deepl.com",
		L"POST",
		L"/jsonrpc",
		body,
		L"Host: www2.deepl.com\r\nAccept-Language: en-US,en;q=0.5\r\nContent-type: application/json; charset=utf-8\r\nOrigin: https://www.deepl.com\r\nTE: Trailers",
		INTERNET_DEFAULT_PORT,
		L"https://www.deepl.com/translator",
		WINHTTP_FLAG_SECURE
	})
		if (auto translation = Copy(JSON::Parse(httpRequest.response)[L"result"][L"translations"][0][L"beams"][0][L"postprocessed_sentence"].String())) return { true, translation.value() };
		else return { false, FormatString(L"%s: %s", TRANSLATION_ERROR, httpRequest.response) };
	else return { false, FormatString(L"%s (code=%u)", TRANSLATION_ERROR, httpRequest.errorCode) };
}
