#pragma once
#define _CRT_SECURE_NO_WARNINGS
#define NOMINMAX   
#define _CRT_STDIO_ARBITRARY_WIDE_SPECIFIERS 1
#include <windows.h>
#include <Shobjidl.h>
#include <malloc.h>
#include <initguid.h>
#include <ShlGuid.h>
#include <strsafe.h>
#include <Audiopolicy.h>
#include <mmdeviceapi.h>
#include <Psapi.h>
#include <atlbase.h>

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <functional>
#include <fstream>
#include <filesystem>
#include <stdexcept>
#include <cstdint>
#include <mutex>
#include <queue>
#include <thread>
#include <cmath>

#include <cwchar>
#include <comdef.h>
#include <shlwapi.h>
#include <cstdio>
#include <cstring>
#include <cassert>
#include <mshtmhst.h>
#include <exdisp.h>
#include <mshtml.h>
#include <stdlib.h>
#include <iostream>
#include <map>
#include <winbase.h>
#include <wincon.h>

#include <sapi.h>
#include <stdio.h>
#include <sphelper.h>

#include <windowsx.h>
#include <commctrl.h>
#include <commdlg.h>
#include <mmsystem.h>
#include <shlobj.h>
#include <cctype>
#include <cassert>
#include <mshtmcid.h>
#include <process.h>

#include <stdint.h>
#include <dwmapi.h>

#include <optional>
#include <unordered_set>
#include <set>
#include <tlhelp32.h>

#include <io.h>
#include <fcntl.h>
#include <crtdefs.h>

#include <memory>
#include <nlohmann/json.hpp>


#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "winmm.lib")
#pragma comment(lib, "dwmapi.lib")
#pragma comment(lib, "Psapi.lib")
#pragma comment(lib, "Version.lib")

#include"common.hpp"