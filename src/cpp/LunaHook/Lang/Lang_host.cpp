#include "Lang_private.h"

std::unordered_map<LANG_STRINGS_HOST, std::unordered_map<SUPPORT_LANG, const wchar_t *>>
    _internal_lang_strings_host = {
        {T_WARNING, {
                        {English, L"Warning"},
                        {Chinese, L"警告"},
                        {TradChinese, L"警告"},
                        {Russian, L"ПРЕДУПРЕЖДЕНИЕ"},
                    }},
        {ALREADY_INJECTED, {
                               {English, L"already injected"},
                               {Chinese, L"已经注入"},
                               {TradChinese, L"已經注入"},
                               {Russian, L"Уже внедрено"},
                           }},
        {INJECT_FAILED, {
                            {English, L"couldn't inject"},
                            {Chinese, L"注入失败"},
                            {TradChinese, L"注入失敗"},
                            {Russian, L"Не удалось внедрить"},
                        }},
        {INVALID_CODEPAGE, {
                               {English, L"couldn't convert text (invalid codepage?)"},
                               {Chinese, L"无法转换文本 (无效的代码页?)"},
                               {TradChinese, L"無法轉換文字（無效的字碼頁？）"},
                               {Russian, L"Не удалось преобразовать текст (неверная кодовая страница?)"},
                           }},
        {PROC_CONN, {
                        {English, L"process connected %d"},
                        {Chinese, L"进程 %d 已连接"},
                        {TradChinese, L"處理程序已連接 %d"},
                        {Russian, L"Процесс подключен %d"},
                    }},
        {PROC_DISCONN, {
                           {English, L"process disconnected %d"},
                           {Chinese, L"进程 %d 已断开连接"},
                           {TradChinese, L"處理程序已中斷連接 %d"},
                           {Russian, L"Процесс отключен %d"},
                       }},
        {UNMATCHABLEVERSION, {
                                 {English, L"The file version cannot be matched, may not work properly, please re-download again!"},
                                 {Chinese, L"文件版本无法匹配，可能无法正常工作，请重新下载！"},
                                 {TradChinese, L"檔案版本不匹配，可能無法正常運作，請重新下載！"},
                                 {Russian, L"Версии файлов не совпадают и могут не работать должным образом, пожалуйста, загрузите их снова!"},
                             }},
};

DEFINEFUNCTION(LANG_STRINGS_HOST, _internal_lang_strings_host, wchar_t)

std::vector<std::tuple<SUPPORT_LANG, std::wstring, std::vector<std::string>>> lang_map = {
    {Chinese, L"简体中文", {"zh"}},
    {TradChinese, L"繁體中文", {"cht", "zh-TW"}},
    {English, L"English", {"en"}},
    {Russian, L"Русский язык", {"ru"}},
};

const char *map_from_support_lang(SUPPORT_LANG _c)
{
    for (auto &&[c, _, ls] : lang_map)
    {
        if (c == _c)
            return ls[0].c_str();
    }
    return "en";
}
SUPPORT_LANG map_to_support_lang(const char *s)
{
    for (auto &&[c, _, ls] : lang_map)
        for (auto &&l : ls)
            if (l == s)
                return c;

    std::string sub = s;
    auto _fnd = sub.find('-');
    if (_fnd != sub.npos)
    {
        sub = sub.substr(0, _fnd);
        for (auto &&[c, _, ls] : lang_map)
            for (auto &&l : ls)
                if (l == sub)
                    return c;
    }
    return English;
}
