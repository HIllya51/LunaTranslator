#pragma once
namespace HostMsg
{
    template <typename T>
    void Log(const T *text, ...);
    void Log(UINT codepage, LPCSTR text, ...);
    template <typename T>
    void Warning(const T *text, ...);
    template <typename T>
    void EmuConnected(const T *text, ...);
    template <typename T>
    void EmuWarning(const T *text, ...);
    template <typename T>
    void EmuGameName(const T *text, ...);
}

void TextOutput(const ThreadParam &tp, const HookParam &hp, TextOutput_T(*buffer), int len);
void NotifyHookFound(HookParam hp, wchar_t *text);
void NotifyHookRemove(uint64_t addr, LPCSTR name);
bool NewHook(HookParam hp, LPCSTR name);

void RemoveHook(uint64_t addr, int maxOffset = 9);
std::string LoadResData(LPCWSTR pszResID, LPCWSTR _type);
inline SearchParam spDefault;
inline JITTYPE jittypedefault = JITTYPE::PC;
// EOF
int HookStrLen(HookParam *, BYTE *data);

// v141_xp上，定义inline std::map会直接导致dll detach后发生崩溃。
#define EMUADD_MAP_MULTI 0
#if EMUADD_MAP_MULTI
extern std::unordered_map<uint32_t, std::pair<JITTYPE, std::set<uintptr_t>>> emuaddr2jitaddr;
#else
extern std::unordered_map<uint32_t, std::pair<JITTYPE, uintptr_t>> emuaddr2jitaddr;
#endif
extern std::unordered_map<uintptr_t, std::pair<JITTYPE, uint32_t>> jitaddr2emuaddr;
extern std::mutex maplock;

extern std::vector<HookParam> JIT_HP_Records;
extern std::mutex JIT_HP_Records_lock;
void jitaddraddr(uint32_t em_addr, uintptr_t jitaddr, JITTYPE);
void jitaddrclear();

void delayinsertadd(HookParam, std::string);
void delayinsertNewHook(uint32_t);
inline bool dont_detach = false;
inline bool host_connected = false;
using version_t = std::tuple<WORD, WORD, WORD, WORD>;
std::optional<version_t> queryversion();