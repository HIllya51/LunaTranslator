#pragma once

// main.h
// 8/23/2013 jichi
// Branch: ITH/IHF_DLL.h, rev 66

void TextOutput(const ThreadParam &tp, const HookParam &hp, TextOutput_T(*buffer), int len);
void HostInfo(HOSTINFO type, LPCSTR text, ...);
#define ConsoleOutput(text, ...) HostInfo(HOSTINFO::Console, text, ##__VA_ARGS__, -1)
void NotifyHookFound(HookParam hp, wchar_t *text);
void NotifyHookRemove(uint64_t addr, LPCSTR name);
bool NewHook(HookParam hp, LPCSTR name);
bool NewHookJit(HookParam hp, LPCSTR name);

void RemoveHook(uint64_t addr, int maxOffset = 9);
std::string LoadResData(LPCWSTR pszResID, LPCWSTR _type);
inline SearchParam spDefault;
// EOF
int HookStrLen(HookParam *, BYTE *data);

// v141_xp上，定义inline std::map会直接导致dll detach后发生崩溃。
extern std::unordered_map<uint64_t, std::pair<JITTYPE, uintptr_t>> emuaddr2jitaddr;
extern std::unordered_map<uintptr_t, std::pair<JITTYPE, uint64_t>> jitaddr2emuaddr;
void jitaddraddr(uint64_t em_addr, uintptr_t jitaddr, JITTYPE);
void jitaddrclear();

void delayinsertadd(HookParam, std::string);
void delayinsertNewHook(uint64_t);
inline bool safeautoleaveveh = false;
inline bool dont_detach = false;
inline bool host_connected = false;