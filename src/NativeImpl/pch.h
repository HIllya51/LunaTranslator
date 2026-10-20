#pragma once
#define NOMINMAX
#define _CRT_STDIO_ARBITRARY_WIDE_SPECIFIERS 1

#ifdef _WIN32
#include <windows.h>

#ifndef E_BOUNDS
#define E_BOUNDS _HRESULT_TYPEDEF_(0x8000000BL)
#endif

#include <winternl.h>
#include <Shobjidl.h>
#include <malloc.h>
#include <initguid.h>
#include <ShlGuid.h>
#include <strsafe.h>
#include <Audiopolicy.h>
#include <mmdeviceapi.h>
#include <Psapi.h>
#include <mmreg.h>
#include <atlbase.h>
#include <atlsync.h>
#include <comdef.h>
#include <shlwapi.h>
#include <mshtmhst.h>
#include <exdisp.h>
#include <mshtml.h>
#include <winbase.h>
#include <wincon.h>
#include <windowsx.h>
#include <commctrl.h>
#include <commdlg.h>
#include <mmsystem.h>
#include <shlobj.h>
#include <mshtmcid.h>
#include <process.h>
#include <dwmapi.h>
#include <tlhelp32.h>
#include <io.h>
#include <fcntl.h>
#include <crtdefs.h>
#include <d3d11.h>
#include <dxgi.h>

extern "C" IMAGE_DOS_HEADER __ImageBase;
#endif

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
#include <string_view>
#include <tuple>
#include <iterator>

#include <cwchar>
#include <cstdio>
#include <cstring>
#include <cassert>
#include <stdlib.h>
#include <stdio.h>
#include <map>
#include <cctype>
#include <stdint.h>
#include <optional>
#include <unordered_set>
#include <set>
#include <cwctype>
#include <memory>

#ifdef _WIN32
#include "common.hpp"
#include "common2.hpp"
#endif

#if defined(_WIN32)
#define SHAREFUNCTION __declspec(dllexport)
#else
#define SHAREFUNCTION __attribute__((visibility("default")))
#endif
#define DECLARE_API extern "C" SHAREFUNCTION
