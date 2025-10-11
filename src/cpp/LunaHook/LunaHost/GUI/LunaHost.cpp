
#include <CommCtrl.h>
#include <TlHelp32.h>
#include <stdio.h>
#include <thread>
#include <fstream>
#include "host.h"
#include "textthread.h"
#include "LunaHost.h"
#include "http.hpp"
extern std::vector<std::tuple<SUPPORT_LANG, std::wstring, std::vector<std::string>>> lang_map;
bool sendclipboarddata_i(const std::wstring &text, HWND hwnd)
{
    if (!OpenClipboard((HWND)hwnd))
        return false;
    HGLOBAL hMem = GlobalAlloc(GMEM_MOVEABLE, (text.size() + 1) * sizeof(wchar_t));
    memcpy(GlobalLock(hMem), text.c_str(), (text.size() + 1) * sizeof(wchar_t));
    EmptyClipboard();
    SetClipboardData(CF_UNICODETEXT, hMem);
    GlobalUnlock(hMem);
    CloseClipboard();
    return true;
}
bool sendclipboarddata(const std::wstring &text, HWND hwnd)
{
    for (int loop = 0; loop < 10; loop++)
    {
        auto succ = sendclipboarddata_i(text, hwnd);
        if (succ)
            return true;
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }
    return false;
}
void LunaHost::on_close()
{
    hasstoped = true;
    savesettings();
    delete configs;
    auto _attachedprocess = attachedprocess;
    for (auto pid : _attachedprocess)
    {
        Host::DetachProcess(pid);
    }
    if (_attachedprocess.size())
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
}

void LunaHost::savesettings()
{
    configs->set("ToClipboard", check_toclipboard);
    configs->set("AutoAttach", autoattach);
    configs->set("AutoAttach_SavedOnly", autoattach_savedonly);
    configs->set("flushDelay", TextThread::flushDelay);
    configs->set("filterRepetition", TextThread::filterRepetition);
    configs->set("maxBufferSize", TextThread::maxBufferSize);
    configs->set("maxHistorySize", TextThread::maxHistorySize);
    configs->set("defaultCodepage", Host::defaultCodepage);
    configs->set("autoattachexes", autoattachexes);
    configs->set("savedhookcontext", savedhookcontext);
    configs->set("DefaultFont2", WideStringToString(uifont.fontfamily));
    configs->set("fontsize", uifont.fontsize);
    configs->set("font_italic", uifont.italic);
    configs->set("font_bold", uifont.bold);
    configs->set("Language", map_from_support_lang(curr_lang));
}

std::string getdefaultlang()
{
    LANGID langid = GetUserDefaultUILanguage();
    CHAR szLang[100];
    std::string lang;
    GetLocaleInfoA(MAKELCID(langid, SORT_DEFAULT), LOCALE_SISO639LANGNAME, szLang, 100);
    lang += szLang;
    GetLocaleInfoA(MAKELCID(langid, SORT_DEFAULT), LOCALE_SISO3166CTRYNAME, szLang, 100);
    lang += "-";
    lang += szLang;
    return lang;
}
void LunaHost::loadsettings()
{
    curr_lang = map_to_support_lang(configs->get("Language", getdefaultlang()).c_str());
    uifont.italic = configs->get("font_italic", false);
    uifont.bold = configs->get("font_bold", false);
    uifont.fontsize = configs->get("fontsize", 14);
    uifont.fontfamily = StringToWideString(configs->get("DefaultFont2", WideStringToString(TR[DefaultFont])));
    check_toclipboard = configs->get("ToClipboard", true);
    autoattach = configs->get("AutoAttach", false);
    autoattach_savedonly = configs->get("AutoAttach_SavedOnly", true);
    TextThread::flushDelay = configs->get("flushDelay", TextThread::flushDelay);
    TextThread::filterRepetition = configs->get("filterRepetition", TextThread::filterRepetition);
    TextThread::maxBufferSize = configs->get("maxBufferSize", TextThread::maxBufferSize);
    TextThread::maxHistorySize = configs->get("maxHistorySize", TextThread::maxHistorySize);
    Host::defaultCodepage = configs->get("defaultCodepage", Host::defaultCodepage);
    autoattachexes = configs->get("autoattachexes", std::set<std::string>{});
    savedhookcontext = configs->get("savedhookcontext", decltype(savedhookcontext){});
}

std::unordered_map<std::wstring, std::vector<int>> getprocesslist();
void LunaHost::doautoattach()
{

    if (autoattach == false && autoattach_savedonly == false)
        return;

    if (autoattachexes.empty())
        return;

    for (auto [pexe, pids] : getprocesslist())
    {
        auto &&u8procname = WideStringToString(pexe);
        if (autoattachexes.find(u8procname) == autoattachexes.end())
            continue;
        if (autoattach_savedonly && savedhookcontext.find(u8procname) == savedhookcontext.end())
            continue;
        for (auto pid : pids)
        {
            if (userdetachedpids.find(pid) != userdetachedpids.end())
                continue;

            if (attachedprocess.find(pid) == attachedprocess.end())
                Host::ConnectAndInjectProcess(pid);
        }

        break;
    }
}

void LunaHost::on_proc_disconnect(DWORD pid)
{
    attachedprocess.erase(pid);
}

void LunaHost::on_proc_connect(DWORD pid)
{
    attachedprocess.insert(pid);

    if (auto pexe = getModuleFilename(pid))
    {
        autoattachexes.insert(WideStringToString(pexe.value()));
        auto u8procname = WideStringToString(pexe.value());
        if (savedhookcontext.find(u8procname) != savedhookcontext.end())
        {
            std::string name = safequeryjson(savedhookcontext[u8procname], "name", std::string());
            if (startWith(name, "UserHook"))
            {
                if (auto hp = HookCode::Parse(StringToWideString(std::string_view(savedhookcontext[u8procname]["hookcode"]))))
                    Host::InsertHook(pid, hp.value());
            }
        }
    }
}

LunaHost::LunaHost()
{

    configs = new confighelper;
    loadsettings();

    setfont(uifont);
    btnshowsettionwindow = new button(this, TR[TSetting]);
    g_selectprocessbutton = new button(this, TR[WndSelectProcess]);

    // btnsavehook=new button(this,BtnSaveHook,10,10,10,10);
    // btnsavehook->onclick=std::bind(&LunaHost::btnsavehookscallback,this);
    btndetachall = new button(this, TR[BtnDetach]);
    btndetachall->onclick = [&]()
    {
        for (auto pid : attachedprocess)
        {
            Host::DetachProcess(pid);
            userdetachedpids.insert(pid);
        }
    };

    g_hEdit_userhook = new lineedit(this);
    btnplugin = new button(this, TR[TPlugins]);

    plugins = new Pluginmanager(this);
    btnplugin->onclick = [&]()
    {
        if (pluginwindow == 0)
            pluginwindow = new Pluginwindow(this, plugins);
        pluginwindow->show();
    };
    g_hButton_insert = new button(this, TR[BtnInsertUserHook]);
    btnshowsettionwindow->onclick = [&]()
    {
        if (settingwindow == 0)
            settingwindow = new Settingwindow(this);
        settingwindow->show();
    };
    g_selectprocessbutton->onclick = [&]()
    {
        if (_processlistwindow == 0)
            _processlistwindow = new processlistwindow(this);
        _processlistwindow->show();
    };
    g_hButton_insert->onclick = [&]()
    {
        auto hp = HookCode::Parse(std::move(g_hEdit_userhook->text()));
        if (hp)
        {
            for (auto _ : attachedprocess)
            {
                Host::InsertHook(_, hp.value());
            }
        }
        else
        {
            showtext(TR[NotifyInvalidHookCode], false);
        }
    };

    g_hListBox_listtext = new listview(this, false, false);
    g_hListBox_listtext->setheader({TR[LIST_HOOK], TR[HS_TEXT]});
    g_hListBox_listtext->oncurrentchange = [&](int idx)
    {
        auto thread_p = g_hListBox_listtext->getdata(idx);
        std::wstring get;
        currentselect = thread_p;
        std::wstring copy = ((TextThread *)thread_p)->storage->c_str();
        strReplace(copy, L"\n", L"\r\n");
        showtext(copy, true);
    };
    g_hListBox_listtext->on_menu = [&]() -> maybehavemenu
    {
        auto tt = (TextThread *)g_hListBox_listtext->getdata(g_hListBox_listtext->currentidx());

        Menu menu;
        menu.add(TR[MenuCopyHookCode], [&, tt]()
                 { sendclipboarddata(tt->hp.hookcode, winId); });
        menu.add_sep();
        menu.add(TR[MenuRemoveHook], [&, tt]()
                 { Host::RemoveHook(tt->tp.processId, tt->tp.addr); });
        menu.add(TR[MenuDetachProcess], [&, tt]()
                 {
         
            Host::DetachProcess(tt->tp.processId);
            userdetachedpids.insert(tt->tp.processId); });
        menu.add_sep();
        menu.add(TR[MenuRemeberSelect], [&, tt]()
                 {
            if(auto pexe=getModuleFilename(tt->tp.processId))
                savedhookcontext[WideStringToString(pexe.value())]={
                    {"hookcode",WideStringToString(tt->hp.hookcode)},
                    {"ctx1",tt->tp.ctx},
                    {"ctx2",tt->tp.ctx2},
                    {"name",WideStringToString(tt->name)}
                }; });
        menu.add(TR[MenuForgetSelect], [&, tt]()
                 {
                if(auto pexe=getModuleFilename(tt->tp.processId))
                        savedhookcontext.erase(WideStringToString(pexe.value())); });
        return menu;
    };

    g_showtexts = new multilineedit(this);
    g_showtexts->setreadonly(true);

    Host::Start(
        std::bind(&LunaHost::on_proc_connect, this, std::placeholders::_1),
        std::bind(&LunaHost::on_proc_disconnect, this, std::placeholders::_1),
        std::bind(&LunaHost::on_thread_create, this, std::placeholders::_1),
        std::bind(&LunaHost::on_thread_delete, this, std::placeholders::_1),
        std::bind(&LunaHost::on_text_recv, this, std::placeholders::_1, std::placeholders::_2),
        [=](HOSTINFO type, const std::wstring &output)
        { on_info(type, output); },
        {},
        {});

    mainlayout = new gridlayout();
    mainlayout->addcontrol(g_selectprocessbutton, 0, 0);
    mainlayout->addcontrol(btndetachall, 0, 1);
    mainlayout->addcontrol(btnshowsettionwindow, 0, 2);
    // mainlayout->addcontrol(btnplugin, 0, 3);
    mainlayout->addcontrol(g_hEdit_userhook, 1, 0, 1, 2);
    mainlayout->addcontrol(g_hButton_insert, 1, 2);

    mainlayout->addcontrol(g_hListBox_listtext, 2, 0, 1, 3);
    mainlayout->addcontrol(g_showtexts, 3, 0, 1, 3);

    mainlayout->setfixedheigth(0, 30);
    mainlayout->setfixedheigth(1, 30);
    setlayout(mainlayout);
    setcentral(1200, 800);
    std::wstring title = TR[WndLunaHostGui];
    settext(title);

    std::thread([&]
                {
        while(1){
            doautoattach();
            std::this_thread::sleep_for(std::chrono::seconds(2));
        } })
        .detach();

    WCHAR vs[32];

    wsprintf(vs, L" | %s v%d.%d.%d", TR[VersionCurrent], LUNA_VERSION[0], LUNA_VERSION[1], LUNA_VERSION[2]);
    title += vs;
    settext(title);
    std::thread([&]()
                {
            if (HttpRequest httpRequest{
                L"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                L"lunatranslator.org",
                L"GET",
                L"/version"
            }){
                
                try{
                    auto resp=nlohmann::json::parse(WideStringToString(httpRequest.response));
                    std::string ver=resp["version"];
                    settext(text()+L" | "+TR[VersionLatest]+L" "+ StringToWideString(ver));
                }
                catch(std::exception&e){}
            } })
        .detach();
}
void LunaHost::on_text_recv_checkissaved(TextThread &thread)
{
    if (auto exe = getModuleFilename(thread.tp.processId))
    {
        auto exea = WideStringToString(exe.value());
        if (savedhookcontext.find(exea) == savedhookcontext.end())
            return;

        std::string hc = savedhookcontext[exea]["hookcode"];
        uint64_t ctx1 = savedhookcontext[exea]["ctx1"];
        uint64_t ctx2 = savedhookcontext[exea]["ctx2"];
        if (((ctx1 & 0xffff) == (thread.tp.ctx & 0xffff)) && (ctx2 == thread.tp.ctx2) && (hc == WideStringToString(thread.hp.hookcode)))
        {
            for (int i = 0; i < g_hListBox_listtext->count(); i++)
            {
                auto handle = g_hListBox_listtext->getdata(i);
                if (handle == (LONG_PTR)&thread)
                {
                    g_hListBox_listtext->setcurrent(i);
                    break;
                }
            }
        }
    }
}

std::wstring sanitize(const std::wstring &s1)
{
    std::wstring s = s1;
    s.erase(std::remove_if(s.begin(), s.end(), [](wchar_t ch)
                           { return (ch >= 0xD800 && ch <= 0xDBFF) || (ch >= 0xDC00 && ch <= 0xDFFF); }),
            s.end());
    return s;
}
void LunaHost::showtext(const std::wstring &text, bool clear)
{
    auto output = sanitize(text);
    strReplace(output, L"\n", L"\r\n");
    if (clear)
    {
        g_showtexts->settext(output);
        g_showtexts->scrolltoend();
    }
    else
    {
        g_showtexts->scrolltoend();
        g_showtexts->appendtext(output);
    }
}
void LunaHost::updatelisttext(const std::wstring &text, LONG_PTR data)
{
    auto idx = g_hListBox_listtext->querydataidx(data);
    if (idx >= 0)
    {
        auto __output = sanitize(text);
        strReplace(__output, L"\n", L" ");
        if (__output.size() > 0x40)
        {
            __output = __output.substr(0, 0x40) + L"...";
        }
        g_hListBox_listtext->settext(idx, 1, __output);
    }
}
void LunaHost::on_text_recv(TextThread &thread, std::wstring &output)
{
    if (hasstoped)
        return;
    if (!plugins->dispatch(thread, output))
        return;

    updatelisttext(output, (LONG_PTR)&thread);

    if (currentselect == (LONG_PTR)&thread)
    {
        showtext(output, false);
    }
}
void LunaHost::on_info(HOSTINFO type, const std::wstring &warning)
{
    switch (type)
    {
    case HOSTINFO::EmuWarning:
        MessageBoxW(winId, warning.c_str(), TR[T_WARNING], 0);
        break;
    default:
        showtext(warning, false);
    }
}
void LunaHost::on_thread_create(TextThread &thread)
{
    wchar_t buff[65535];
    swprintf_s(buff, L"%I64X:%s:%s:%I32X:%I64X:%I64X",
               thread.handle,
               thread.name.c_str(),
               thread.hp.hookcode,
               thread.tp.processId,
               thread.tp.ctx,
               thread.tp.ctx2);
    int index = g_hListBox_listtext->additem(buff, NULL);
    g_hListBox_listtext->setdata(index, (LONG_PTR)&thread);
    on_text_recv_checkissaved(thread);
}
void LunaHost::on_thread_delete(TextThread &thread)
{
    if (currentselect == (LONG_PTR)&thread)
        currentselect = 0;
    int count = g_hListBox_listtext->count();
    for (int i = 0; i < count; i++)
    {
        auto thread_p = g_hListBox_listtext->getdata(i);

        if (thread_p == (LONG_PTR)&thread)
        {
            g_hListBox_listtext->deleteitem(i);
            break;
        }
    }
}

Settingwindow::Settingwindow(LunaHost *host) : mainwindow(host)
{
    int height = 30;
    int curry = 10;
    int space = 10;
    int labelwidth = 300;
    int spinwidth = 200;
    g_timeout = new spinbox(this, TextThread::flushDelay);

    g_codepage = new spinbox(this, Host::defaultCodepage);

    spinmaxbuffsize = new spinbox(this, TextThread::maxBufferSize);
    ;
    curry += height + space;

    spinmaxbuffsize->onvaluechange = [=](int v)
    {
        TextThread::maxBufferSize = v;
    };

    spinmaxhistsize = new spinbox(this, TextThread::maxHistorySize);
    ;
    curry += height + space;

    spinmaxhistsize->onvaluechange = [=](int v)
    {
        TextThread::maxHistorySize = v;
    };

    ckbfilterrepeat = new checkbox(this, TR[LblFilterRepeat]);
    ckbfilterrepeat->onclick = [=]()
    {
        TextThread::filterRepetition = ckbfilterrepeat->ischecked();
    };
    ckbfilterrepeat->setcheck(TextThread::filterRepetition);

    g_check_clipboard = new checkbox(this, TR[BtnToClipboard]);
    g_check_clipboard->onclick = [=]()
    {
        host->check_toclipboard = g_check_clipboard->ischecked();
    };
    g_check_clipboard->setcheck(host->check_toclipboard);

    autoattach = new checkbox(this, TR[LblAutoAttach]);
    autoattach->onclick = [=]()
    {
        host->autoattach = autoattach->ischecked();
    };
    autoattach->setcheck(host->autoattach);

    autoattach_so = new checkbox(this, TR[LblAutoAttach_savedonly]);
    autoattach_so->onclick = [=]()
    {
        host->autoattach_savedonly = autoattach_so->ischecked();
    };
    autoattach_so->setcheck(host->autoattach_savedonly);

    readonlycheck = new checkbox(this, TR[BtnReadOnly]);
    readonlycheck->onclick = [=]()
    {
        host->g_showtexts->setreadonly(readonlycheck->ischecked());
    };
    readonlycheck->setcheck(true);

    g_timeout->onvaluechange = [=](int v)
    {
        TextThread::flushDelay = v;
    };

    g_codepage->onvaluechange = [=](int v)
    {
        if (IsValidCodePage(v))
        {
            Host::defaultCodepage = v;
        }
    };
    g_codepage->setminmax(0, CP_UTF8);

    showfont = new lineedit(this);
    showfont->settext(host->uifont.fontfamily);
    showfont->setreadonly(true);
    selectfont = new button(this, TR[FONTSELECT]);
    selectfont->onclick = [=]()
    {
        FontSelector(winId, host->uifont, [=](const Font &f)
                     {
            host->uifont=f;
            showfont->settext(f.fontfamily);
            host->setfont(f); });
    };
    language = new combobox(this);
    for (auto &&[_, l, __] : lang_map)
    {
        language->additem(l);
    }
    language->setcurrent(curr_lang);
    language->oncurrentchange = [](int idx)
    {
        curr_lang = (decltype(curr_lang))idx;
    };
    mainlayout = new gridlayout();
    mainlayout->addcontrol(new label(this, TR[LblLanguage]), 0, 0);
    mainlayout->addcontrol(language, 0, 1);
    mainlayout->addcontrol(new label(this, TR[LblFlushDelay]), 1, 0);
    mainlayout->addcontrol(g_timeout, 1, 1);

    mainlayout->addcontrol(new label(this, TR[LblCodePage]), 2, 0);
    mainlayout->addcontrol(g_codepage, 2, 1);

    mainlayout->addcontrol(new label(this, TR[LblMaxBuff]), 3, 0);
    mainlayout->addcontrol(spinmaxbuffsize, 3, 1);

    mainlayout->addcontrol(new label(this, TR[LblMaxHist]), 4, 0);
    mainlayout->addcontrol(spinmaxhistsize, 4, 1);

    mainlayout->addcontrol(ckbfilterrepeat, 5, 0, 1, 2);
    mainlayout->addcontrol(g_check_clipboard, 6, 0, 1, 2);
    mainlayout->addcontrol(autoattach, 7, 0, 1, 2);
    mainlayout->addcontrol(autoattach_so, 8, 0, 1, 2);
    mainlayout->addcontrol(readonlycheck, 9, 0, 1, 2);
    mainlayout->addcontrol(showfont, 10, 1);
    mainlayout->addcontrol(selectfont, 10, 0);

    setlayout(mainlayout);
    setcentral(600, 500);
    settext(TR[TSetting]);
}
void Pluginwindow::on_size(int w, int h)
{
    listplugins->setgeo(10, 10, w - 20, h - 20);
}
void Pluginwindow::pluginrankmove(int moveoffset)
{
    auto idx = listplugins->currentidx();
    if (idx == -1)
        return;
    auto idx2 = idx + moveoffset;
    auto a = min(idx, idx2), b = max(idx, idx2);
    if (a < 0 || b >= listplugins->count())
        return;
    pluginmanager->swaprank(a, b);

    auto pa = ((LPCWSTR)listplugins->getdata(a));
    auto pb = ((LPCWSTR)listplugins->getdata(b));

    listplugins->deleteitem(a);
    listplugins->insertitem(b, std::filesystem::path(pa).stem());
    listplugins->setdata(b, (LONG_PTR)pa);
}
Pluginwindow::Pluginwindow(mainwindow *p, Pluginmanager *pl) : mainwindow(p), pluginmanager(pl)
{

    static auto listadd = [&](const std::wstring &s)
    {
        auto idx = listplugins->additem(std::filesystem::path(s).stem());
        auto _s = new wchar_t[s.size() + 1];
        wcscpy(_s, s.c_str());
        listplugins->setdata(idx, (LONG_PTR)_s);
    };
    listplugins = new listbox(this);

    listplugins->on_menu = [&]()
    {
        Menu menu;
        menu.add(TR[MenuAddPlugin], [&]()
                 {
        if(auto f=pluginmanager->selectpluginfile())
            switch (auto res=pluginmanager->addplugin(f.value()))
            {
            case addpluginresult::success:
                listadd(f.value());
                break;
            default:
                std::map<addpluginresult,LPCWSTR> errorlog={
                    {addpluginresult::isnotaplugins,TR[InvalidPlugin]},
                    {addpluginresult::invaliddll,TR[InvalidDll]},
                    {addpluginresult::dumplicate,TR[InvalidDump]},
                };
                MessageBoxW(winId,errorlog[res],TR[MsgError],0);
            } });
        auto idx = listplugins->currentidx();
        if (idx != -1)
        {
            menu.add(TR[MenuRemovePlugin], [&, idx]()
                     {
                pluginmanager->remove((LPCWSTR)listplugins->getdata(idx));
                listplugins->deleteitem(idx); });
            menu.add_sep();
            menu.add(TR[MenuPluginRankUp], std::bind(&Pluginwindow::pluginrankmove, this, -1));
            menu.add(TR[MenuPluginRankDown], std::bind(&Pluginwindow::pluginrankmove, this, 1));
            menu.add_sep();
            menu.add_checkable(TR[MenuPluginEnable], pluginmanager->getenable(idx), [&, idx](bool check)
                               {
                pluginmanager->setenable(idx,check);
                if(check)
                    pluginmanager->load((LPCWSTR)listplugins->getdata(idx));
                else
                    pluginmanager->unload((LPCWSTR)listplugins->getdata(idx)); });
            if (pluginmanager->getvisible_setable(idx))
                menu.add_checkable(TR[MenuPluginVisSetting], pluginmanager->getvisible(idx), [&, idx](bool check)
                                   { pluginmanager->setvisible(idx, check); });
        }
        return menu;
    };

    for (int i = 0; i < pluginmanager->count(); i++)
    {
        listadd(pluginmanager->getname(i));
    }
    settext(TR[TPlugins]);
    setcentral(500, 400);
}
