#include "Lang_private.h"

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
