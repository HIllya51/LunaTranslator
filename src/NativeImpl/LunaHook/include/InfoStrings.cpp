#include "InfoStrings.h"
#include <unordered_map>
#include <string>

#define DEFINEFUNCTION(type, mp, ret, which)                         \
    const ret *langhelper::operator[](type langstring)               \
    {                                                                \
        auto &&_ = mp[langstring];                                   \
        return _.get();                                              \
    }                                                                \
    std::unordered_map<type, i18nString<ret>> &langhelper::##which() \
    {                                                                \
        return mp;                                                   \
    }

langhelper TR;

#if defined(BUILD_HOST) && BUILD_HOST
std::unordered_map<LANG_STRINGS_HOST, i18nString<wchar_t>>
    _internal_lang_strings_host = {
        {T_WARNING, L"警告"},
        {ALREADY_INJECTED, L"已经注入"},
        {INJECT_FAILED, L"注入失败"},
        {INVALID_CODEPAGE, L"无法转换文本 (无效的代码页?)"},
        {PROC_CONN, L"进程 %d 已连接"},
        {PROC_DISCONN, L"进程 %d 已断开连接"},
        {UNMATCHABLEVERSION, L"文件版本无法匹配，可能无法正常工作，请重新下载！"},
};

DEFINEFUNCTION(LANG_STRINGS_HOST, _internal_lang_strings_host, wchar_t, get_host)
#endif
#if defined(BUILD_HOOK) && BUILD_HOOK
std::unordered_map<LANG_STRINGS_HOOK, i18nString<char>> _internal_lang_strings_hook = {
    {INSERTING_HOOK, u8"注入钩子: %s %p"},
    {REMOVING_HOOK, u8"移除钩子: %s"},
    {TOO_MANY_HOOKS, u8"钩子数量已达上限: 无法注入"},
    {HOOK_SEARCH_STARTING, u8"开始搜索钩子"},
    {HOOK_SEARCH_INITIALIZING, u8"初始化钩子搜索 (%f%%)"},
    {NOT_ENOUGH_TEXT, u8"文本长度不足, 无法精确搜索"},
    {HOOK_SEARCH_INITIALIZED, u8"搜索初始化完成, 创建了 %zd 个钩子"},
    {MAKE_GAME_PROCESS_TEXT, u8"请点击游戏区域, 在接下来的 %d 秒内使游戏强制处理文本"},
    {HOOK_SEARCH_FINISHED, u8"钩子搜索完毕, 找到了 %d 条结果"},
    {OUT_OF_RECORDS_RETRY, u8"搜索结果已达上限, 如果结果不理想, 请重试(默认最大记录数增加)"},
    {FUNC_MISSING, u8"函数不存在"},
    {MODULE_MISSING, u8"模块不存在"},
    {GARBAGE_MEMORY, u8"内存一直在改变，无法有效读取"},
    {SEND_ERROR, u8"Sender 错误 (可能是由于错误或不稳定的 H-code) ： %s"},
    {READ_ERROR, u8"Reader 错误 (可能是由于错误或不稳定的 R-code) ： %s"},
    {SearchForHooks_ERROR, u8"搜索钩子错误 : 内存溢出，尝试重新分配 %d"},
    {ResultsNum, u8"%d 个结果被找到"},
    {HIJACK_ERROR, u8"Hijack ERROR"},
    {COULD_NOT_FIND, u8"无法找到文本"},
    {InvalidLength, u8"可能存在错误 (无效的文本长度 %d 出现在 %s)"},
    {InsertHookFailed, u8"钩子注入失败 %s"},
    {Match_Error, u8"匹配 %s 引擎时发生错误"},
    {Attach_Error, u8"连接到 %s 引擎时发生错误"},
    {MatchedEngine, u8"匹配到 %s 引擎"},
    {ConfirmStop, u8"确认是 %s 引擎"},
    {Attach_Stop, u8"成功连接到 %s 引擎"},
    {ProcessRange, u8"获取到进程内存地址范围 0x%p 到 0x%p"},
    {WarningDummy, u8"警告，注入的进程内存很小，可能是无用进程!"},
    {RYUJINXUNSUPPORT, u8"不支持ryujinx，请使用yuzu/sudachi/Citron/Eden"},
    {EMUVERSIONTOOOLD, u8"模拟器版本过旧，请使用新版模拟器"},
    {IsEmuNotify, u8"检测到模拟器: %s\n请在模拟器加载游戏之前，先让翻译器HOOK模拟器，否则将无法识别模拟器内加载的游戏"}};

DEFINEFUNCTION(LANG_STRINGS_HOOK, _internal_lang_strings_hook, char, get_hook)
#endif