
typedef BOOL (*Initialize)(
	UINT logLevel,
	const char *logFileName,
	int logArchiveAboveSize,
	int logMaxArchiveFiles);
typedef const char *(*Run)(
	HWND hwndSrc,
	const char *effectsJson,
	UINT flags,
	UINT captureMode,
	float cursorZoomFactor,		  // 负数和 0：和源窗口相同，正数：缩放比例
	UINT cursorInterpolationMode, // 0：最近邻，1：双线性
	int adapterIdx,
	UINT multiMonitorUsage, // 0：最近 1：相交 2：所有
	UINT cropLeft,
	UINT cropTop,
	UINT cropRight,
	UINT cropBottom);
int magpiewmain(int argc, wchar_t *wargv[])
{
	UINT codepage = GetACP();

	char **argv = new char *[argc];
	for (int i = 0; i < argc; i++)
	{
		int length = WideCharToMultiByte(codepage, 0, wargv[i], -1, NULL, 0, NULL, NULL);
		argv[i] = new char[length];
		WideCharToMultiByte(codepage, 0, wargv[i], -1, argv[i], length, NULL, NULL);
	}

	FILE *fp;
	fopen_s(&fp, argv[1], "r");
	if (fp == 0)
		return 0;
	char cache[4096] = {0};
	char magpiepath[4096] = {0};
	HWND m_hWnd;
	char effect[4096] = {0};
	int flags, captureMode, CursorInterpolationMode, AdapterIdx, MultiMonitorUsage;
	float CursorZoomFactor;
	fgets(magpiepath, 4096, fp);
	magpiepath[strlen(magpiepath) - 1] = 0;
	fgets(cache, 4096, fp);
	sscanf_s(cache, "%lld\n", (__int64 *)&m_hWnd);
	fgets(effect, 4096, fp);
	effect[strlen(effect) - 1] = 0;
	fgets(cache, 4096, fp);
	sscanf_s(cache, "%d,%d,%f,%d,%d,%d",
			 &flags, &captureMode, &CursorZoomFactor, &CursorInterpolationMode, &AdapterIdx, &MultiMonitorUsage);

	fclose(fp);

	/*printf("%s\n%s\n", magpiepath, effect);
	printf("%d,%d,%d,%d,%d,%d,%d", m_hWnd, flags, captureMode, CursorInterpolationMode, AdapterIdx, MultiMonitorUsage, CursorZoomFactor);*/
	SetForegroundWindow(m_hWnd);
	SetCurrentDirectoryA(magpiepath);
	SetDllDirectoryA(magpiepath);
	HMODULE h = LoadLibrary(L".\\MagpieRT.dll");
	// printf("%d\n", h);
	if (h == 0)
		return 0;
	Initialize Initialize_f = (Initialize)GetProcAddress(h, "Initialize");
	Run Run_f = (Run)GetProcAddress(h, "Run");
	SetProcessDPIAware();
	auto _1 = Initialize_f(6, "./Runtime.log", 100000, 1);
	auto _2 = Run_f(m_hWnd, effect, flags, captureMode, CursorZoomFactor, CursorInterpolationMode, AdapterIdx, MultiMonitorUsage, 0, 0, 0, 0);
	// printf("%d %s\n", _1, _2);
	return 0;
}
