#include "window.h"
#include "controls.h"
#include "textthread.h"
#include "pluginmanager.h"
#include "confighelper.h"
class LunaHost;
class Pluginwindow : public mainwindow
{
    listbox *listplugins;
    Pluginmanager *pluginmanager;

public:
    Pluginwindow(mainwindow *, Pluginmanager *);
    void on_size(int w, int h);
    void pluginrankmove(int);
};
class Settingwindow : public mainwindow
{
    checkbox *ckbfilterrepeat;
    spinbox *g_timeout;
    spinbox *g_codepage;
    checkbox *g_check_clipboard;
    checkbox *readonlycheck;
    checkbox *autoattach;
    checkbox *autoattach_so;
    checkbox *copyselect;
    spinbox *spinmaxbuffsize;
    spinbox *spinmaxhistsize;
    gridlayout *mainlayout;
    lineedit *showfont;
    button *selectfont;
    combobox *language;

public:
    Settingwindow(LunaHost *);
};

class processlistwindow : public mainwindow
{
    gridlayout *mainlayout;
    lineedit *g_hEdit;
    button *g_hButton;
    listview *g_hListBox;
    button *g_refreshbutton;
    std::unordered_map<std::wstring, std::vector<int>> g_exe_pid;
    void PopulateProcessList(listview *, std::unordered_map<std::wstring, std::vector<int>> &);

public:
    processlistwindow(mainwindow *parent = 0);
    void on_show();
};
class HooksearchText : public mainwindow
{
    gridlayout *layout;
    lineedit *edittext;
    button *checkok;
    spinbox *codepage;

public:
    HooksearchText(mainwindow *);
    void call(std::set<DWORD> pids);
};
class Hooksearchsetting : public mainwindow
{
    gridlayout *layout;
    spinbox *spinduration;
    spinbox *spinoffset;
    spinbox *spincap;
    spinbox *spincodepage;
    lineedit *editpattern;
    lineedit *editmodule;
    lineedit *editmaxaddr;
    lineedit *editminaddr;
    spinbox *spinpadding;
    lineedit *editregex;
    button *start;

public:
    Hooksearchsetting(mainwindow *);
    void call(std::set<DWORD> pids, std::wstring);
};
class LunaHost : public mainwindow
{
    Pluginwindow *pluginwindow = 0;
    std::set<DWORD> attachedprocess;
    lineedit *g_hEdit_userhook;
    gridlayout *mainlayout;
    button *g_hButton_insert;
    button *btnplugin;
    // listbox* g_hListBox_listtext;
    listview *g_hListBox_listtext;
    multilineedit *g_showtexts;
    button *g_selectprocessbutton;
    button *btndetachall;
    button *btnshowsettionwindow;
    // button* btnsavehook;
    processlistwindow *_processlistwindow = 0;
    Settingwindow *settingwindow = 0;
    Pluginmanager *plugins;
    std::atomic<bool> hasstoped = false;
    void on_text_recv(TextThread &thread, std::wstring &sentence);
    void on_text_recv_checkissaved(TextThread &thread);
    void on_thread_create(TextThread &thread);
    void on_thread_delete(TextThread &thread);
    void on_proc_connect(DWORD pid);
    void on_proc_disconnect(DWORD pid);
    void on_info(HOSTINFO type, const std::wstring &);

    void showtext(const std::wstring &text, bool clear);
    void updatelisttext(const std::wstring &text, LONG_PTR data);

public:
    confighelper *configs;
    int64_t currentselect = 0;
    bool check_toclipboard;
    Font uifont;
    bool autoattach;
    bool autoattach_savedonly;
    std::set<std::string> autoattachexes;
    std::unordered_map<std::string, nlohmann::json> savedhookcontext;
    std::set<int> userdetachedpids;
    void on_close();
    LunaHost();
    friend class Settingwindow;

private:
    void loadsettings();
    void savesettings();

    void doautoattach();
};
