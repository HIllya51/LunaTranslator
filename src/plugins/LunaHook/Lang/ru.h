﻿
#define ALREADY_INJECTED L"Уже внедрено" 
#define NEED_32_BIT L"Неверная архетектура: тут нужно x86" 
#define NEED_64_BIT L"Неверная архетектура: тут нужно x64" 
#define INJECT_FAILED L"Не удалось внедрить" 
#define INVALID_CODEPAGE L"Не удалось преобразовать текст (неверная кодовая страница?)" 
#define PIPE_CONNECTED u8"Канал подключен" 
#define INSERTING_HOOK u8"установка хука: %s %p" 
#define REMOVING_HOOK u8"Удаление хука: %s" 
#define TOO_MANY_HOOKS u8"Слишком много хуков: невозможно добавить" 
#define HOOK_SEARCH_STARTING u8"Запущен поиск хуков" 
#define HOOK_SEARCH_INITIALIZING u8"Инициализация поиска хуков (%f%%)" 
#define NOT_ENOUGH_TEXT u8"Недостаточно текста для точного поиска" 
#define HOOK_SEARCH_INITIALIZED u8"Поиск хуков инициализирован, найдено %zd хуков" 
#define MAKE_GAME_PROCESS_TEXT u8"Пожалуйста, пощелкайте в игре, чтобы заставить ее обработать текст в течение следующих %d секунд" 
#define HOOK_SEARCH_FINISHED u8"Поиск хуков завершен, найдено %d результатов" 
#define OUT_OF_RECORDS_RETRY u8"Закончились записи поиска, попробуйте еще раз, если результаты неудовлетворительны (количество записей по умолчанию увеличено)" 
#define FUNC_MISSING u8"Функция не найдена" 
#define MODULE_MISSING u8"Модуль не найден" 
#define GARBAGE_MEMORY u8"Данные в памяти постоянно меняются, чтение бесполезно" 
#define SEND_ERROR u8"Ошибка отправки (возможен нестабильный/неверный H-код) в %s" 
#define READ_ERROR u8"Ошибка чтения (возможен неверный R-код) в %s" 
#define SearchForHooks_ERROR u8"Ошибка SearchForHooks: недостаточно памяти, повторная попытка выделения %d" 
#define ResultsNum u8"Обработано %d результатов" 
#define HIJACK_ERROR u8"Ошибка перехвата" 
#define COULD_NOT_FIND u8"Не удалось найти текст" 
#define CONSOLE L"Консоль" 
#define InvalidLength  u8"Произошла критическая ошибка (неверная длина %d в %s)" 
#define InsertHookFailed u8"Не удалось установить хук %s" 
#define Match_Error u8"Ошибка при сопоставлении с движком %s" 
#define Attach_Error u8"Ошибка при подключении к движку %s" 
#define MatchedEngine u8"Сопоставлен движок %s" 
#define ConfirmStop u8"Подтвержден движок %s, поиск остановлен" 
#define Attach_Stop u8"Движок %s успешно подключен, поиск остановлен" 
#define ProcessRange u8"Перехват процесса в диапазоне адресов с 0x%p по 0x%p" 
#define WarningDummy u8"ПРЕДУПРЕЖДЕНИЕ: внедренный процесс очень мал, возможно, это пустышка!" 
#define WndSelectProcess L"Выбор процесса" 
#define WndLunaHostGui L"LunaHost - GUI" 
#define WndSetting L"Настройки" 
#define WndPlugins L"Плагины" 
#define NotifyInvalidHookCode L"Неверный код хука" 
#define BtnSelectProcess L"Выбрать процесс" 
#define BtnDetach L"Отключить" 
#define BtnSaveHook L"Сохранить хук" 
#define BtnShowSettingWindow L"Настройки" 
#define BtnAttach L"Подключить" 
#define BtnRefresh L"Обновить" 
#define BtnToClipboard L"Скопировать в буфер обмена" 
#define BtnReadOnly L"Текстовое поле доступно только для чтения" 
#define BtnInsertUserHook L"Добавить польз. хук" 
#define BtnSearchHook L"Найти хуки" 
#define BtnPlugin L"Плагины" 
#define LblFlushDelay L"Задержка сброса" 
#define LblFilterRepeat L"Фильтр повторов" 
#define LblCodePage L"Кодовая страница по умолчанию" 
#define LblMaxBuff L"Максимальный размер буфера"
#define LblMaxHist L"Максимальный размер истории"
#define LblAutoAttach L"Автоподключение"
#define LblAutoAttach_savedonly L"Автоподключение (только сохраненные)"
#define MenuCopyHookCode L"Скопировать код хука" 
#define MenuRemoveHook L"Удалить хук" 
#define MenuDetachProcess L"Отключиться от процесса" 
#define MenuRemeberSelect L"Запомнить выбранный хук" 
#define MenuForgetSelect L"Забыть выбранный хук" 
#define MenuAddPlugin L"Добавить плагин" 
#define MenuRemovePlugin L"Удалить плагин" 
#define MenuPluginRankUp L"Вверх" 
#define MenuPluginRankDown L"Вниз" 
#define MenuPluginEnable L"Включить" 
#define MenuPluginVisSetting L"Показать настройки" 
#define DefaultFont L"Arial" 
#define CantLoadQtLoader L"Не удалось загрузить QtLoader.dll"
#define InvalidPlugin L"Неверный плагин!"
#define InvalidDll L"Неверная DLL!"
#define InvalidDump L"Дубликат!"
#define MsgError L"Ошибка"
#define SEARCH_CJK L"Искать китайские/японские/корейские символы"
#define HS_SETTINGS L"Настройки"
#define BtnOk L"OK"
#define HS_START_HOOK_SEARCH L"Начать поиск хуков"
#define HS_SEARCH_PATTERN L"Шаблон поиска (массив шестнадцатеричных байтов)"
#define HS_SEARCH_DURATION L"Длительность поиска (мс)"
#define HS_SEARCH_MODULE L"Искать внутри модуля"
#define HS_PATTERN_OFFSET L"Смещение от начала шаблона"
#define HS_MAX_HOOK_SEARCH_RECORDS L"Максимальное количество результатов поиска"
#define HS_MIN_ADDRESS L"Минимальный адрес (шестнадцатеричный)"
#define HS_MAX_ADDRESS L"Максимальный адрес (шестнадцатеричный)"
#define HS_STRING_OFFSET L"Смещение строки (шестнадцатеричное)"
#define HS_HOOK_SEARCH_FILTER L"Результаты должны соответствовать этому регулярному выражению"
#define HS_TEXT L"Текст"
#define HS_CODEPAGE L"Кодовая страница"
#define HS_SEARCH_FOR_TEXT L"Искать определенный текст"
#define VersionLatest L"Последняя версия"
#define VersionCurrent L"Текущая версия"
#define ProjectHomePage L"Github: https://github.com/HIllya51/LunaHook\nСтраница проекта: https://lunatranslator.org\npatreon: https://patreon.com/HIllya51\nDiscord: https://discord.com/invite/ErtDwVeAbB\n\nЭта программа является основным подмодулем LunaTranslator и полностью интегрирована в Lunatranslator. Эта программа содержит только некоторые простые функции. Если вам нужны дополнительные функции, используйте LunaTranslator.\nЕсли вы обнаружите какие-либо неподдерживаемые игры, сообщите о проблеме."
#define LIST_HOOK L"Хук"
#define LIST_TEXT L"Текст"
#define PROC_CONN L"Процесс подключен %d"
#define PROC_DISCONN L"Процесс отключен %d"
#define COPYSELECTION L"Автоматически копировать выделенный текст в буфер обмена"
#define FONTSELECT L"Выбрать шрифт"
