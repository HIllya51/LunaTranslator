#ifndef INFOSTRINGS_BCA3473A_08FE_4D5C_A0A2_D4265570C476
#define INFOSTRINGS_BCA3473A_08FE_4D5C_A0A2_D4265570C476

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
    PROC_CONN,
    PROC_DISCONN,
    UNMATCHABLEVERSION,
    T_WARNING,
};
enum LANG_STRINGS_HOOK
{
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
    IsEmuNotify,
};
enum SUPPORT_LANG;

template <typename CharT>
class i18nString
{
    std::basic_string<CharT> i18n;
    const CharT *defaults;

public:
    void set(std::basic_string<CharT> && s)
    {
        if (!s.empty())
        {
            i18n = std::move(s);
        }
    }
    void set(const CharT *s)
    {
        if (s && *s)
        {
            i18n = s;
        }
    }
    const CharT *get()
    {
        if (i18n.empty())
            return defaults;
        return i18n.c_str();
    }
    const CharT *raw()
    {
        return defaults;
    }
    i18nString() {}
    i18nString(const CharT *d) : defaults(d) {}
};

struct langhelper
{
    const char *operator[](LANG_STRINGS_HOOK);
    const wchar_t *operator[](LANG_STRINGS_HOST);
    const wchar_t *operator[](LANG_STRINGS_UI);
    std::unordered_map<LANG_STRINGS_HOOK, i18nString<char>> &get_hook();
    std::unordered_map<LANG_STRINGS_HOST, i18nString<wchar_t>> &get_host();
    std::unordered_map<LANG_STRINGS_UI, i18nString<wchar_t>> &get_ui();
};

extern langhelper TR;

#endif