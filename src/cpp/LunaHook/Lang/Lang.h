

enum LANG_STRINGS_UI
{
    WndSelectProcess,
    WndLunaHostGui,
    TSetting,
    TPlugins,
    NotifyInvalidHookCode,
    BtnDetach,
    BtnSaveHook,
    BtnAttach,
    BtnRefresh,
    BtnToClipboard,
    BtnReadOnly,
    BtnInsertUserHook,
    LblFlushDelay,
    LblFilterRepeat,
    LblCodePage,
    LblMaxBuff,
    LblMaxHist,
    LblLanguage,
    LblAutoAttach,
    LblAutoAttach_savedonly,
    MenuCopyHookCode,
    MenuRemoveHook,
    MenuDetachProcess,
    MenuRemeberSelect,
    MenuForgetSelect,
    MenuAddPlugin,
    MenuRemovePlugin,
    MenuPluginRankUp,
    MenuPluginRankDown,
    MenuPluginEnable,
    MenuPluginVisSetting,
    DefaultFont,
    InvalidPlugin,
    InvalidDll,
    InvalidDump,
    MsgError,
    BtnOk,
    HS_TEXT,
    VersionLatest,
    VersionCurrent,
    LIST_HOOK,
    COPYSELECTION,
    FONTSELECT,
};
enum LANG_STRINGS_HOST
{
    ALREADY_INJECTED,
    INJECT_FAILED,
    INVALID_CODEPAGE,
    CONSOLE,
    PROC_CONN,
    PROC_DISCONN,
    ProjectHomePage,
    UNMATCHABLEVERSION,
    T_WARNING,
};
enum LANG_STRINGS_HOOK
{
    PIPE_CONNECTED,
    INSERTING_HOOK,
    REMOVING_HOOK,
    TOO_MANY_HOOKS,
    HOOK_SEARCH_STARTING,
    HOOK_SEARCH_INITIALIZING,
    NOT_ENOUGH_TEXT,
    HOOK_SEARCH_INITIALIZED,
    MAKE_GAME_PROCESS_TEXT,
    HOOK_SEARCH_FINISHED,
    OUT_OF_RECORDS_RETRY,
    FUNC_MISSING,
    MODULE_MISSING,
    GARBAGE_MEMORY,
    SEND_ERROR,
    READ_ERROR,
    SearchForHooks_ERROR,
    ResultsNum,
    HIJACK_ERROR,
    COULD_NOT_FIND,
    InvalidLength,
    InsertHookFailed,
    Match_Error,
    Attach_Error,
    MatchedEngine,
    ConfirmStop,
    Attach_Stop,
    ProcessRange,
    WarningDummy,
    RYUJINXUNSUPPORT,
    EMUVERSIONTOOOLD,
};
enum SUPPORT_LANG;
SUPPORT_LANG map_to_support_lang(const char *);
const char *map_from_support_lang(SUPPORT_LANG);
struct langhelper
{
    const char *operator[](LANG_STRINGS_HOOK);
    const wchar_t *operator[](LANG_STRINGS_HOST);
    const wchar_t *operator[](LANG_STRINGS_UI);
};

extern langhelper TR;
extern SUPPORT_LANG curr_lang;