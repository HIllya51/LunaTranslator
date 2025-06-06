#pragma once
#define _CRT_SECURE_NO_WARNINGS
#define NOMINMAX
#define _CRT_STDIO_ARBITRARY_WIDE_SPECIFIERS 1
#include <windows.h>

#ifndef E_BOUNDS
#define E_BOUNDS _HRESULT_TYPEDEF_(0x8000000BL)
#endif

#include <Shobjidl.h>
#include <malloc.h>
#include <initguid.h>
#include <ShlGuid.h>
#include <strsafe.h>
#include <Audiopolicy.h>
#include <mmdeviceapi.h>
#include <Psapi.h>
#include <atlbase.h>
#include <atlsync.h>
#include <variant>
#include <iostream>
#include <string>
#include <sstream>
#include <vector>
#include <algorithm>
#include <functional>
#include <fstream>
#include <numeric>
#include <filesystem>
#include <stdexcept>
#include <cstdint>
#include <mutex>
#include <queue>
#include <thread>
#include <cmath>
#include <atomic>

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

#include <stdio.h>

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

#include <d3d11.h>
#include <dxgi.h>

#include "common.hpp"
#include "common2.hpp"

#define DECLARE_API extern "C" __declspec(dllexport)
