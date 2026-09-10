#pragma once

// texthook/defs.h
// 8/23/2013 jichi

// Pipes

constexpr auto HOOK_PIPE = L"\\\\.\\pipe\\LUNA_HOOK";
constexpr auto HOST_PIPE = L"\\\\.\\pipe\\LUNA_HOST";

// Sections

constexpr auto EMBED_SHARED_MEM = L"EMBED_SHARED_MEM"; // _%d
constexpr auto HOOK_SEARCH_SHARED_MEM = L"HOOK_SEARCH_SHARED_MEM";

// Mutexes

constexpr auto ITH_HOOKMAN_MUTEX_ = L"LUNA_VNR_HOOKMAN_"; // ITH_HOOKMAN_%d
constexpr auto CONNECTING_MUTEX = L"LUNA_CONNECTING_PIPES";

// Events
constexpr auto LUNA_EMBED_notify_event = "LUNA_NOTIFY.%lu.%llu";

constexpr auto PIPE_AVAILABLE_EVENT = L"LUNA_PIPE_AVAILABLE";

// Files
constexpr auto LUNA_HOOK_DLL_64 = L"LunaHook64";
constexpr auto LUNA_HOOK_DLL_32 = L"LunaHook32";


extern WORD LUNA_VERSION[4];

struct DECLSPEC_UUID("253bf1be-e941-47d3-ae40-a2c6c88054d6") _COMPATIBLE_HELPER;
inline const GUID &compatible_sig = __uuidof(_COMPATIBLE_HELPER);
// EOF
