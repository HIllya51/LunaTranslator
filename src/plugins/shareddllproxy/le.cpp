
#define SHIFT_JIS 932
namespace
{
	int GetCharsetFromANSICodepage(int ansicp)
	{
		auto charset = ANSI_CHARSET;

		switch (ansicp)
		{
		case 932: // Japanese
			charset = SHIFTJIS_CHARSET;
			break;
		case 936: // Simplified Chinese
			charset = GB2312_CHARSET;
			break;
		case 949: // Korean
			charset = HANGEUL_CHARSET;
			break;
		case 950: // Traditional Chinese
			charset = CHINESEBIG5_CHARSET;
			break;
		case 1250: // Eastern Europe
			charset = EASTEUROPE_CHARSET;
			break;
		case 1251: // Russian
			charset = RUSSIAN_CHARSET;
			break;
		case 1252: // Western European Languages
			charset = ANSI_CHARSET;
			break;
		case 1253: // Greek
			charset = GREEK_CHARSET;
			break;
		case 1254: // Turkish
			charset = TURKISH_CHARSET;
			break;
		case 1255: // Hebrew
			charset = HEBREW_CHARSET;
			break;
		case 1256: // Arabic
			charset = ARABIC_CHARSET;
			break;
		case 1257: // Baltic
			charset = BALTIC_CHARSET;
			break;
		}

		return charset;
	}

	// https://github.com/xupefei/Locale-Emulator-Core/blob/ae7160dc5deb97947396abcd784f9b98b6ee38b3/LocaleEmulator/LocaleEmulator.h#L131

	typedef struct
	{
		USHORT Length;
		USHORT MaximumLength;
		union
		{
			PWSTR Buffer;
			ULONG64 Dummy;
		};

	} UNICODE_STRING3264, *PUNICODE_STRING3264;

	typedef UNICODE_STRING3264 UNICODE_STRING64;
	typedef PUNICODE_STRING3264 PUNICODE_STRING64;
	typedef struct
	{
		ULONG64 Root;
		UNICODE_STRING64 SubKey;
		UNICODE_STRING64 ValueName;
		ULONG DataType;
		PVOID64 Data;
		ULONG64 DataSize;

	} REGISTRY_ENTRY64;

	typedef struct
	{
		REGISTRY_ENTRY64 Original;
		REGISTRY_ENTRY64 Redirected;

	} REGISTRY_REDIRECTION_ENTRY64, *PREGISTRY_REDIRECTION_ENTRY64;
	typedef struct
	{
		ULONG AnsiCodePage;
		ULONG OemCodePage;
		ULONG LocaleID;
		ULONG DefaultCharset;
		ULONG HookUILanguageApi;
		WCHAR DefaultFaceName[LF_FACESIZE];
		TIME_ZONE_INFORMATION Timezone;
		ULONG64 NumberOfRegistryRedirectionEntries;
		REGISTRY_REDIRECTION_ENTRY64 RegistryReplacement[1];

	} LOCALE_ENUMLATOR_ENVIRONMENT_BLOCK, *PLOCALE_ENUMLATOR_ENVIRONMENT_BLOCK, LEB, *PLEB;

}
int lewmain(int argc, wchar_t *argv[])
{
	/*
	argv[0] le
	argv[1] ANSICodePage
	argv[2] OEMCodePage
	argv[3] LCID
	argv[4] dirname
	argv[5] RedirectRegistry
	argv[6] HookUILanguageAPI
	argvx exe
	... args
	*/
#define exeargi 7
	std::wstring cmd = L"";
	for (int i = exeargi; i < argc; i++)
	{
		cmd += L"\"";
		cmd += argv[i];
		cmd += L"\" ";
	}
	std::wstring process = argv[exeargi];
	auto ANSICodePage = std::stoi(argv[1]);//932 SHIFT_JIS
	auto OEMCodePage = std::stoi(argv[2]);//932 SHIFT_JIS
	auto LCID = std::stoi(argv[3]);//0x11 LANG_JAPANESE
	auto dirname = argv[4];
	auto RedirectRegistry = std::stoi(argv[5]);
	auto HookUILanguageAPI = std::stoi(argv[6]);

	PROCESS_INFORMATION info = {};
	if (HMODULE localeEmulator = LoadLibraryW(L".\\LoaderDll"))
	{

		LEB _leb;
		ZeroMemory(&_leb, sizeof(LEB));
		_leb.AnsiCodePage = ANSICodePage;
		_leb.OemCodePage = OEMCodePage;
		_leb.LocaleID = LCID;
		_leb.DefaultCharset = GetCharsetFromANSICodepage(ANSICodePage);
		_leb.HookUILanguageApi = HookUILanguageAPI;
		GetTimeZoneInformation(&_leb.Timezone);
		auto ret = ((LONG(__stdcall *)(LEB *, LPCWSTR appName, LPWSTR commandLine, LPCWSTR currentDir, void *, void *, PROCESS_INFORMATION *, void *, void *, void *, void *))
						GetProcAddress(localeEmulator, "LeCreateProcess"))(&_leb, process.c_str(), cmd.data(), dirname, NULL, NULL, &info, NULL, NULL, NULL, NULL);
		if (ret == 0)
		{
			WaitForSingleObject(info.hProcess, INFINITE);
			CloseHandle(info.hProcess);
			CloseHandle(info.hThread);
		}
	}
	return 1;
}
