
struct LRProfile
{
	UINT CodePage;
	UINT LCID;
	long Bias;
	int HookIME;
	int HookLCID;
};
int WrtieConfigFileMap(LRProfile *profile)
{
	SetEnvironmentVariableW(L"LRCodePage", (LPCWSTR)&profile->CodePage);
	SetEnvironmentVariableW(L"LRLCID", (LPCWSTR)&profile->LCID);
	SetEnvironmentVariableW(L"LRBIAS", (LPCWSTR)&profile->Bias);
	SetEnvironmentVariableW(L"LRHookIME", (LPCWSTR)&profile->HookIME);
	SetEnvironmentVariableW(L"LRHookLCID", (LPCWSTR)&profile->HookLCID);
	return 0;
}
// https://github.com/InWILL/Locale_Remulator/blob/master/LRProc/LRProc.cpp
int LRwmain(int argc, wchar_t *wargv[])
{
	char current[2048];
	GetModuleFileNameA(NULL, current, 2048);
	std::string _s = current;
	_s = _s.substr(0, _s.find_last_of("\\"));
	auto dllpath = _s + "\\Locale_Remulator\\";
	auto targetexe = wargv[1];
	std::wstring cmd = L"";
	for (int i = 1; i < argc; i++)
	{
		cmd += L"\"";
		cmd += wargv[i];
		cmd += L"\" ";
	}
	auto cmd_x = new wchar_t[cmd.size() + 1];
	wcscpy(cmd_x, cmd.c_str());
	DWORD type;
	GetBinaryTypeW(targetexe, &type);
	if (type == 6)
		dllpath += "LRHookx64.dll";
	else
		dllpath += "LRHookx32.dll";
	LRProfile beta;
	beta.CodePage = 932;
	beta.LCID = 0x0411;
	beta.Bias = 540; // Bias will become negative in HookGetTimeZoneInformation
	beta.HookIME = false;
	beta.HookLCID = true;

	WrtieConfigFileMap(&beta);
	STARTUPINFOW si;
	PROCESS_INFORMATION pi;
	ZeroMemory(&si, sizeof(STARTUPINFO));
	ZeroMemory(&pi, sizeof(PROCESS_INFORMATION));
	si.cb = sizeof(STARTUPINFO);
	DetourCreateProcessWithDllExW(NULL, cmd_x, NULL,
								  NULL, FALSE, CREATE_DEFAULT_ERROR_MODE, NULL, NULL,
								  &si, &pi, dllpath.c_str(), NULL);

	return 0;
}