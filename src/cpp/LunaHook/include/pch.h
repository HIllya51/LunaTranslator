#pragma once
#include <Winsock2.h>
#define _WINSOCKAPI_
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

#ifndef E_BOUNDS
#define E_BOUNDS _HRESULT_TYPEDEF_(0x8000000BL)
#endif

#include <windowsx.h>
#include <concrt.h>
#include <string>
#include <vector>
#include <deque>
#include <array>
#include <map>
#include <unordered_map>
#include <set>
#include <unordered_set>
#include <Psapi.h>
#include <functional>
#include <algorithm>
#include <regex>
#include <memory>
#include <optional>
#include <thread>
#include <mutex>
#include <atomic>
#include <filesystem>
#include <iostream>
#include <sstream>
#include <locale>
#include <cstdint>
#include <list>
#include <type_traits>
#include <utility>
#include <cassert>
#include <variant>
#include <shlobj.h>
#include <Shlwapi.h>

#include "stringutils.h"
#include "utils.h"
#include "defs.h"
#include "const.h"
#include "types.h"
#include "hookcode.h"
#include "winevent.hpp"
#include "lrucache.hpp"
#include "Lang/Lang.h"