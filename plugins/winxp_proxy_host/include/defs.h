#pragma once

// texthook/defs.h
// 8/23/2013 jichi

// Pipes

constexpr auto HOOK_PIPE = L"\\\\.\\pipe\\LUNA_HOOK";
constexpr auto HOST_PIPE = L"\\\\.\\pipe\\LUNA_HOST";

// Sections

constexpr auto ITH_SECTION_ = L"LUNA_VNR_SECTION_"; // _%d
constexpr auto HOOKCODE_ = L"LUNA_HOOKCODE_"; // _%d

// Mutexes

constexpr auto ITH_HOOKMAN_MUTEX_ = L"LUNA_VNR_HOOKMAN_"; // ITH_HOOKMAN_%d
constexpr auto CONNECTING_MUTEX = L"LUNA_CONNECTING_PIPES";

// Events

constexpr auto PIPE_AVAILABLE_EVENT = L"LUNA_PIPE_AVAILABLE";

// Files

#ifdef _WIN64
constexpr auto ITH_DLL = L"LunaHook64"; // .dll but LoadLibrary automatically adds that
#else
constexpr auto ITH_DLL = L"LunaHook32"; // .dll but LoadLibrary automatically adds that
#endif
constexpr auto& GAME_CONFIG_FILE = L"TextractorConfig.txt";

// EOF
