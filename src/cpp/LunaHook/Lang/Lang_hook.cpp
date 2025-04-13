#include "Lang_private.h"

std::unordered_map<LANG_STRINGS_HOOK, std::unordered_map<SUPPORT_LANG, const char *>> _internal_lang_strings_hook = {
    {PIPE_CONNECTED, {
                         {English, u8"pipe connected"},
                         {Chinese, u8"管道已连接"},
                         {TradChinese, u8"管道已連接"},
                         {Russian, u8"Канал подключен"},
                     }},
    {INSERTING_HOOK, {
                         {English, u8"inserting hook: %s %p"},
                         {Chinese, u8"注入钩子: %s %p"},
                         {TradChinese, u8"注入勾點：%s %p"},
                         {Russian, u8"установка хука: %s %p"},
                     }},
    {REMOVING_HOOK, {
                        {English, u8"removing hook: %s"},
                        {Chinese, u8"移除钩子: %s"},
                        {TradChinese, u8"移除勾點：%s"},
                        {Russian, u8"Удаление хука: %s"},
                    }},
    {TOO_MANY_HOOKS, {
                         {English, u8"too many hooks: can't insert"},
                         {Chinese, u8"钩子数量已达上限: 无法注入"},
                         {TradChinese, u8"勾點數量已達上限：無法注入"},
                         {Russian, u8"Слишком много хуков: невозможно добавить"},
                     }},
    {HOOK_SEARCH_STARTING, {
                               {English, u8"starting hook search"},
                               {Chinese, u8"开始搜索钩子"},
                               {TradChinese, u8"開始搜尋勾點"},
                               {Russian, u8"Запущен поиск хуков"},
                           }},
    {HOOK_SEARCH_INITIALIZING, {
                                   {English, u8"initializing hook search (%f%%)"},
                                   {Chinese, u8"初始化钩子搜索 (%f%%)"},
                                   {TradChinese, u8"初始化勾點搜尋（%f%%）"},
                                   {Russian, u8"Инициализация поиска хуков (%f%%)"},
                               }},
    {NOT_ENOUGH_TEXT, {
                          {English, u8"not enough text to search accurately"},
                          {Chinese, u8"文本长度不足, 无法精确搜索"},
                          {TradChinese, u8"文字長度不足，無法精確搜尋"},
                          {Russian, u8"Недостаточно текста для точного поиска"},
                      }},
    {HOOK_SEARCH_INITIALIZED, {
                                  {English, u8"initialized hook search with %zd hooks"},
                                  {Chinese, u8"搜索初始化完成, 创建了 %zd 个钩子"},
                                  {TradChinese, u8"搜尋初始化完成，建立了 %zd 個勾點"},
                                  {Russian, u8"Поиск хуков инициализирован, найдено %zd хуков"},
                              }},
    {MAKE_GAME_PROCESS_TEXT, {
                                 {English, u8"please click around in the game to force it to process text during the next %d seconds"},
                                 {Chinese, u8"请点击游戏区域, 在接下来的 %d 秒内使游戏强制处理文本"},
                                 {TradChinese, u8"請點擊遊戲區域，在接下來的 %d 秒內使遊戲強制處理文字"},
                                 {Russian, u8"Пожалуйста, пощелкайте в игре, чтобы заставить ее обработать текст в течение следующих %d секунд"},
                             }},
    {HOOK_SEARCH_FINISHED, {
                               {English, u8"hook search finished, %d results found"},
                               {Chinese, u8"钩子搜索完毕, 找到了 %d 条结果"},
                               {TradChinese, u8"勾點搜尋完畢，找到了 %d 條結果"},
                               {Russian, u8"Поиск хуков завершен, найдено %d результатов"},
                           }},
    {OUT_OF_RECORDS_RETRY, {
                               {English, u8"out of search records, please retry if results are poor (default record count increased)"},
                               {Chinese, u8"搜索结果已达上限, 如果结果不理想, 请重试(默认最大记录数增加)"},
                               {TradChinese, u8"搜尋結果已達上限，如果結果不理想，請重試（預設最大紀錄數增加）"},
                               {Russian, u8"Закончились записи поиска, попробуйте еще раз, если результаты неудовлетворительны (количество записей по умолчанию увеличено)"},
                           }},
    {FUNC_MISSING, {
                       {English, u8"function not present"},
                       {Chinese, u8"函数不存在"},
                       {TradChinese, u8"函式不存在"},
                       {Russian, u8"Функция не найдена"},
                   }},
    {MODULE_MISSING, {
                         {English, u8"module not present"},
                         {Chinese, u8"模块不存在"},
                         {TradChinese, u8"模組不存在"},
                         {Russian, u8"Модуль не найден"},
                     }},
    {GARBAGE_MEMORY, {
                         {English, u8"memory inline constantly changing, useless to read"},
                         {Chinese, u8"内存一直在改变，无法有效读取"},
                         {TradChinese, u8"記憶體一直在改變，無法有效讀取"},
                         {Russian, u8"Данные в памяти постоянно меняются, чтение бесполезно"},
                     }},
    {SEND_ERROR, {
                     {English, u8"Send ERROR (likely an unstable/incorrect H-code) in %s"},
                     {Chinese, u8"Sender 错误 (可能是由于错误或不稳定的 H-code) ： %s"},
                     {TradChinese, u8"Sender 錯誤（可能是由於錯誤或不穩定的 H-code）：%s"},
                     {Russian, u8"Ошибка отправки (возможен нестабильный/неверный H-код) в %s"},
                 }},
    {READ_ERROR, {
                     {English, u8"Reader ERROR (likely an incorrect R-code) in %s"},
                     {Chinese, u8"Reader 错误 (可能是由于错误或不稳定的 R-code) ： %s"},
                     {TradChinese, u8"Reader 錯誤（可能是由於錯誤或不穩定的 R-code）：%s"},
                     {Russian, u8"Ошибка чтения (возможен неверный R-код) в %s"},
                 }},
    {SearchForHooks_ERROR, {
                               {English, u8"SearchForHooks ERROR: out of memory, retrying to allocate %d"},
                               {Chinese, u8"搜索钩子错误 : 内存溢出，尝试重新分配 %d"},
                               {TradChinese, u8"搜尋勾點錯誤：記憶體溢出，嘗試重新分配 %d"},
                               {Russian, u8"Ошибка SearchForHooks: недостаточно памяти, повторная попытка выделения %d"},
                           }},
    {ResultsNum, {
                     {English, u8"%d results processed"},
                     {Chinese, u8"%d 个结果被找到"},
                     {TradChinese, u8"%d 個結果被找到"},
                     {Russian, u8"Обработано %d результатов"},
                 }},
    {HIJACK_ERROR, {
                       {English, u8"Hijack ERROR"},
                   }},
    {COULD_NOT_FIND, {
                         {English, u8"could not find text"},
                         {Chinese, u8"无法找到文本"},
                         {TradChinese, u8"無法找到文字"},
                         {Russian, u8"Не удалось найти текст"},
                     }},
    {InvalidLength, {
                        {English, u8"something went very wrong (invalid length %d in %s)"},
                        {Chinese, u8"可能存在错误 (无效的文本长度 %d 出现在 %s)"},
                        {TradChinese, u8"可能存在錯誤（無效的文字長度 %d 出現 %s）"},
                        {Russian, u8"Произошла критическая ошибка (неверная длина %d в %s)"},
                    }},
    {InsertHookFailed, {
                           {English, u8"failed to insert hook %s"},
                           {Chinese, u8"钩子注入失败 %s"},
                           {TradChinese, u8"勾點注入失敗 %s"},
                           {Russian, u8"Не удалось установить хук %s"},
                       }},
    {Match_Error, {
                      {English, u8"ERROR happened when matching engine %s "},
                      {Chinese, u8"匹配 %s 引擎时发生错误"},
                      {TradChinese, u8"匹配 %s 引擎時發生錯誤"},
                      {Russian, u8"Ошибка при сопоставлении с движком %s"},
                  }},
    {Attach_Error, {
                       {English, u8"ERROR happened when attaching engine %s ERROR"},
                       {Chinese, u8"连接到 %s 引擎时发生错误"},
                       {TradChinese, u8"連接到 %s 引擎時發生錯誤"},
                       {Russian, u8"Ошибка при подключении к движку %s"},
                   }},
    {MatchedEngine, {
                        {English, u8"Matched engine %s"},
                        {Chinese, u8"匹配到 %s 引擎"},
                        {TradChinese, u8"匹配到 %s 引擎"},
                        {Russian, u8"Сопоставлен движок %s"},
                    }},
    {ConfirmStop, {
                      {English, "Confirmed engine %s, stop checking"},
                      {Chinese, u8"确认是 %s 引擎, 停止匹配"},
                      {TradChinese, u8"確認是 %s 引擎，停止匹配"},
                      {Russian, u8"Подтвержден движок %s, поиск остановлен"},
                  }},
    {Attach_Stop, {
                      {English, "Attach engine %s success and stop"},
                      {Chinese, u8"成功连接到 %s 引擎"},
                      {TradChinese, u8"成功連接到 %s 引擎"},
                      {Russian, u8"Движок %s успешно подключен, поиск остановлен"},
                  }},
    {ProcessRange, {
                       {English, "hijacking process located from 0x%p to 0x%p"},
                       {Chinese, u8"获取到进程内存地址范围 0x%p 到 0x%p"},
                       {TradChinese, u8"取得處理程序記憶體位址範圍 0x%p 到 0x%p"},
                       {Russian, u8"Перехват процесса в диапазоне адресов с 0x%p по 0x%p"},
                   }},
    {WarningDummy, {
                       {English, "WARNING injected process is very small, possibly a dummy!"},
                       {Chinese, u8"警告，注入的进程内存很小，可能是无用进程!"},
                       {TradChinese, u8"警告，注入的處理程序記憶體很小，可能是無用處理程序！"},
                       {Russian, u8"ПРЕДУПРЕЖДЕНИЕ: внедренный процесс очень мал, возможно, это пустышка!"},
                   }},
    {RYUJINXUNSUPPORT, {
                           {English, "not support ryujinx, please use yuzu/sudachi/Citron instead."},
                           {Chinese, u8"不支持ryujinx，请使用yuzu/sudachi/Citron"},
                           {TradChinese, u8"不支援 Ryujinx，請使用 yuzu／Sudachi／Citron"},
                           {Russian, u8"Не поддерживайте ryujinx, используйте yuzu / sudachi / Citron"},
                       }},
    {EMUVERSIONTOOOLD, {
                           {English, "The emulator version is too old, please use the latest version"},
                           {Chinese, u8"模拟器版本过旧，请使用新版模拟器"},
                           {TradChinese, u8"模擬器版本過舊，請使用新版模擬器"},
                           {Russian, u8"Устаревшая версия симулятора, используйте новую версию симулятора"},
                       }}};

DEFINEFUNCTION(LANG_STRINGS_HOOK, _internal_lang_strings_hook, char)