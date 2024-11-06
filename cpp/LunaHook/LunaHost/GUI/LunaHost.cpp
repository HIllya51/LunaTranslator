
#include <CommCtrl.h>
#include <TlHelp32.h>
#include <stdio.h>
#include <thread>
#include <fstream>
#include "host.h"
#include "textthread.h"
#include "LunaHost.h"
#include "Lang/Lang.h"
#include "http.hpp"

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
    configs->set("ToClipboardSelection", check_toclipboard_selection);
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
}
void LunaHost::loadsettings()
{
    uifont.italic = configs->get("font_italic", false);
    uifont.bold = configs->get("font_bold", false);
    uifont.fontsize = configs->get("fontsize", 14);
    uifont.fontfamily = StringToWideString(configs->get("DefaultFont2", WideStringToString(std::wstring(DefaultFont))));
    check_toclipboard_selection = configs->get("ToClipboardSelection", false);
    check_toclipboard = configs->get("ToClipboard", false);
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
                Host::InjectProcess(pid);
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

bool queryversion(WORD *_1, WORD *_2, WORD *_3, WORD *_4)
{
    wchar_t fileName[MAX_PATH];
    GetModuleFileNameW(NULL, fileName, MAX_PATH);
    DWORD dwHandle;
    DWORD dwSize = GetFileVersionInfoSizeW(fileName, &dwHandle);
    if (dwSize == 0)
    {
        return false;
    }

    std::vector<char> versionInfoBuffer(dwSize);
    if (!GetFileVersionInfoW(fileName, dwHandle, dwSize, versionInfoBuffer.data()))
    {
        return false;
    }

    VS_FIXEDFILEINFO *pFileInfo;
    UINT fileInfoSize;
    if (!VerQueryValueW(versionInfoBuffer.data(), L"\\", reinterpret_cast<LPVOID *>(&pFileInfo), &fileInfoSize))
    {
        return false;
    }

    DWORD ms = pFileInfo->dwFileVersionMS;
    DWORD ls = pFileInfo->dwFileVersionLS;

    WORD majorVersion = HIWORD(ms);
    WORD minorVersion = LOWORD(ms);
    WORD buildNumber = HIWORD(ls);
    WORD revisionNumber = LOWORD(ls);
    *_1 = majorVersion;
    *_2 = minorVersion;
    *_3 = buildNumber;
    *_4 = revisionNumber;
    return true;
}

LunaHost::LunaHost()
{

    configs = new confighelper;
    loadsettings();

    setfont(uifont);
    btnshowsettionwindow = new button(this, BtnShowSettingWindow);
    g_selectprocessbutton = new button(this, BtnSelectProcess);

    // btnsavehook=new button(this,BtnSaveHook,10,10,10,10);
    // btnsavehook->onclick=std::bind(&LunaHost::btnsavehookscallback,this);
    btndetachall = new button(this, BtnDetach);
    btndetachall->onclick = [&]()
    {
        for (auto pid : attachedprocess)
        {
            Host::DetachProcess(pid);
            userdetachedpids.insert(pid);
        }
    };

    g_hEdit_userhook = new lineedit(this);
    btnplugin = new button(this, BtnPlugin);

    plugins = new Pluginmanager(this);
    btnplugin->onclick = [&]()
    {
        if (pluginwindow == 0)
            pluginwindow = new Pluginwindow(this, plugins);
        pluginwindow->show();
    };
    g_hButton_insert = new button(this, BtnInsertUserHook);
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
            showtext(NotifyInvalidHookCode, false);
        }
    };

    g_hListBox_listtext = new listview(this, false, false);
    g_hListBox_listtext->setheader({LIST_HOOK, LIST_TEXT});
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
        menu.add(MenuCopyHookCode, [&, tt]()
                 { sendclipboarddata(tt->hp.hookcode, winId); });
        menu.add_sep();
        menu.add(MenuRemoveHook, [&, tt]()
                 { Host::RemoveHook(tt->tp.processId, tt->tp.addr); });
        menu.add(MenuDetachProcess, [&, tt]()
                 {
         
            Host::DetachProcess(tt->tp.processId);
            userdetachedpids.insert(tt->tp.processId); });
        menu.add_sep();
        menu.add(MenuRemeberSelect, [&, tt]()
                 {
            if(auto pexe=getModuleFilename(tt->tp.processId))
                savedhookcontext[WideStringToString(pexe.value())]={
                    {"hookcode",WideStringToString(tt->hp.hookcode)},
                    {"ctx1",tt->tp.ctx},
                    {"ctx2",tt->tp.ctx2},
                    {"name",WideStringToString(tt->name)}
                }; });
        menu.add(MenuForgetSelect, [&, tt]()
                 {
                if(auto pexe=getModuleFilename(tt->tp.processId))
                        savedhookcontext.erase(WideStringToString(pexe.value())); });
        return menu;
    };

    g_showtexts = new multilineedit(this);
    g_showtexts->setreadonly(true);

    btnsearchhooks = new button(this, BtnSearchHook);
    btnsearchhooks->onclick = [&]()
    {
        if (hooksearchwindow == 0)
            hooksearchwindow = new Hooksearchwindow(this);
        hooksearchwindow->show();
    };

    Host::StartEx(
        std::bind(&LunaHost::on_proc_connect, this, std::placeholders::_1),
        std::bind(&LunaHost::on_proc_disconnect, this, std::placeholders::_1),
        std::bind(&LunaHost::on_thread_create, this, std::placeholders::_1),
        std::bind(&LunaHost::on_thread_delete, this, std::placeholders::_1),
        std::bind(&LunaHost::on_text_recv, this, std::placeholders::_1, std::placeholders::_2),
        {},
        {},
        {},
        std::bind(&LunaHost::on_warning, this, std::placeholders::_1));

    mainlayout = new gridlayout();
    mainlayout->addcontrol(g_selectprocessbutton, 0, 0);
    mainlayout->addcontrol(btndetachall, 0, 1);
    mainlayout->addcontrol(btnshowsettionwindow, 0, 2);
    mainlayout->addcontrol(btnplugin, 0, 3);
    mainlayout->addcontrol(g_hEdit_userhook, 1, 0, 1, 2);
    mainlayout->addcontrol(g_hButton_insert, 1, 2);
    mainlayout->addcontrol(btnsearchhooks, 1, 3);

    mainlayout->addcontrol(g_hListBox_listtext, 2, 0, 1, 4);
    mainlayout->addcontrol(g_showtexts, 3, 0, 1, 4);

    mainlayout->setfixedheigth(0, 30);
    mainlayout->setfixedheigth(1, 30);
    setlayout(mainlayout);
    setcentral(1200, 800);
    std::wstring title = WndLunaHostGui;
    settext(title);

    std::thread([&]()
                {
        std::wstring sel;
        while(1)
        {
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
            if(check_toclipboard_selection)
            {
                    
                auto _sel=g_showtexts->getsel();
                if(_sel!=sel){
                    sel=_sel;
                    sendclipboarddata(sel,winId);
                }
            }
        } })
        .detach();

    std::thread([&]
                {
        while(1){
            doautoattach();
            std::this_thread::sleep_for(std::chrono::seconds(2));
        } })
        .detach();

    WORD _1, _2, _3, _4;
    WCHAR vs[32];
    if (queryversion(&_1, &_2, &_3, &_4))
    {
        wsprintf(vs, L" | %s v%d.%d.%d", VersionCurrent, _1, _2, _3);
        title += vs;
        settext(title);
        std::thread([&]()
                    {
            if (HttpRequest httpRequest{
                L"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                L"lunatranslator.org",
                L"GET",
                L"/version_lunahook"
            }){
                
                try{
                    auto resp=nlohmann::json::parse(WideStringToString(httpRequest.response));
                    std::string ver=resp["version"];
                    settext(text()+L" | "+VersionLatest+L" "+ StringToWideString(ver));
                }
                catch(std::exception&e){}
            } })
            .detach();
    }
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
bool LunaHost::on_text_recv(TextThread &thread, std::wstring &output)
{
    if (hasstoped)
        return true;
    if (!plugins->dispatch(thread, output))
        return false;

    updatelisttext(output, (LONG_PTR)&thread);

    if (currentselect == (LONG_PTR)&thread)
    {
        showtext(output, false);
    }
    return true;
}
void LunaHost::on_warning(const std::wstring &warning)
{
    MessageBoxW(winId, warning.c_str(), L"warning", 0);
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

    ckbfilterrepeat = new checkbox(this, LblFilterRepeat);
    ckbfilterrepeat->onclick = [=]()
    {
        TextThread::filterRepetition = ckbfilterrepeat->ischecked();
    };
    ckbfilterrepeat->setcheck(TextThread::filterRepetition);

    g_check_clipboard = new checkbox(this, BtnToClipboard);
    g_check_clipboard->onclick = [=]()
    {
        host->check_toclipboard = g_check_clipboard->ischecked();
    };
    g_check_clipboard->setcheck(host->check_toclipboard);

    // copyselect=new checkbox(this,COPYSELECTION);
    // copyselect->onclick=[=](){
    //     host->check_toclipboard_selection=copyselect->ischecked();
    // };
    // copyselect->setcheck(host->check_toclipboard_selection);

    autoattach = new checkbox(this, LblAutoAttach);
    autoattach->onclick = [=]()
    {
        host->autoattach = autoattach->ischecked();
    };
    autoattach->setcheck(host->autoattach);

    autoattach_so = new checkbox(this, LblAutoAttach_savedonly);
    autoattach_so->onclick = [=]()
    {
        host->autoattach_savedonly = autoattach_so->ischecked();
    };
    autoattach_so->setcheck(host->autoattach_savedonly);

    readonlycheck = new checkbox(this, BtnReadOnly);
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
    selectfont = new button(this, FONTSELECT);
    selectfont->onclick = [=]()
    {
        FontSelector(winId, host->uifont, [=](const Font &f)
                     {
            host->uifont=f;
            showfont->settext(f.fontfamily);
            host->setfont(f); });
    };

    mainlayout = new gridlayout();
    mainlayout->addcontrol(new label(this, LblFlushDelay), 0, 0);
    mainlayout->addcontrol(g_timeout, 0, 1);

    mainlayout->addcontrol(new label(this, LblCodePage), 1, 0);
    mainlayout->addcontrol(g_codepage, 1, 1);

    mainlayout->addcontrol(new label(this, LblMaxBuff), 2, 0);
    mainlayout->addcontrol(spinmaxbuffsize, 2, 1);

    mainlayout->addcontrol(new label(this, LblMaxHist), 3, 0);
    mainlayout->addcontrol(spinmaxhistsize, 3, 1);

    mainlayout->addcontrol(ckbfilterrepeat, 4, 0, 1, 2);
    mainlayout->addcontrol(g_check_clipboard, 5, 0, 1, 2);
    mainlayout->addcontrol(autoattach, 6, 0, 1, 2);
    mainlayout->addcontrol(autoattach_so, 7, 0, 1, 2);
    mainlayout->addcontrol(readonlycheck, 8, 0, 1, 2);
    mainlayout->addcontrol(showfont, 9, 1);
    mainlayout->addcontrol(selectfont, 9, 0);

    setlayout(mainlayout);
    setcentral(600, 500);
    settext(WndSetting);
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
        menu.add(MenuAddPlugin, [&]()
                 {
        if(auto f=pluginmanager->selectpluginfile())
            switch (auto res=pluginmanager->addplugin(f.value()))
            {
            case addpluginresult::success:
                listadd(f.value());
                break;
            default:
                std::map<addpluginresult,LPCWSTR> errorlog={
                    {addpluginresult::isnotaplugins,InvalidPlugin},
                    {addpluginresult::invaliddll,InvalidDll},
                    {addpluginresult::dumplicate,InvalidDump},
                };
                MessageBoxW(winId,errorlog[res],MsgError,0);
            } });
        auto idx = listplugins->currentidx();
        if (idx != -1)
        {
            menu.add(MenuRemovePlugin, [&, idx]()
                     {
                pluginmanager->remove((LPCWSTR)listplugins->getdata(idx));
                listplugins->deleteitem(idx); });
            menu.add_sep();
            menu.add(MenuPluginRankUp, std::bind(&Pluginwindow::pluginrankmove, this, -1));
            menu.add(MenuPluginRankDown, std::bind(&Pluginwindow::pluginrankmove, this, 1));
            menu.add_sep();
            menu.add_checkable(MenuPluginEnable, pluginmanager->getenable(idx), [&, idx](bool check)
                               {
                pluginmanager->setenable(idx,check);
                if(check)
                    pluginmanager->load((LPCWSTR)listplugins->getdata(idx));
                else
                    pluginmanager->unload((LPCWSTR)listplugins->getdata(idx)); });
            if (pluginmanager->getvisible_setable(idx))
                menu.add_checkable(MenuPluginVisSetting, pluginmanager->getvisible(idx), [&, idx](bool check)
                                   { pluginmanager->setvisible(idx, check); });
        }
        return menu;
    };

    for (int i = 0; i < pluginmanager->count(); i++)
    {
        listadd(pluginmanager->getname(i));
    }
    settext(WndPlugins);
    setcentral(500, 400);
}

void HooksearchText::call(std::set<DWORD> pids)
{
    edittext->settext(L"");
    checkok->onclick = [&, pids]()
    {
        close();
        auto cp = codepage->getcurr();
        if (!IsValidCodePage(cp))
            return;
        SearchParam sp = {};
        sp.codepage = cp;
        wcsncpy_s(sp.text, edittext->text().c_str(), PATTERN_SIZE - 1);
        for (auto pid : pids)
            Host::FindHooks(pid, sp);
    };
    show();
}
HooksearchText::HooksearchText(mainwindow *p) : mainwindow(p)
{
    codepage = new spinbox(this, Host::defaultCodepage);
    codepage->setminmax(0, CP_UTF8);

    edittext = new lineedit(this);
    checkok = new button(this, BtnOk);
    layout = new gridlayout();
    layout->addcontrol(new label(this, HS_TEXT), 0, 0);
    layout->addcontrol(new label(this, HS_CODEPAGE), 1, 0);
    layout->addcontrol(edittext, 0, 1);
    layout->addcontrol(codepage, 1, 1);
    layout->addcontrol(checkok, 2, 1);

    setlayout(layout);
    setcentral(500, 200);
}
std::wstring tohex(BYTE *bs, int len)
{
    std::wstring buffer;
    for (int i = 0; i < len; i += 1)
    {
        buffer.append(FormatString(L"%02hX ", bs[i]));
    }
    return buffer;
}
std::wstring addr2hex(uintptr_t addr)
{
    return FormatString(L"%p", addr);
}
void realcallsearchhooks(std::set<DWORD> pids, std::wstring filter, SearchParam sp)
{

    auto hooks = std::make_shared<std::vector<std::wstring>>();

    try
    {
        for (auto processId : pids)
            Host::FindHooks(processId, sp,
                            [hooks, filter](HookParam hp, std::wstring text)
                            {
                                std::wsmatch matches;
                                if (std::regex_search(text, matches, std::wregex(filter)))
                                {
                                    hooks->emplace_back(std::wstring(hp.hookcode) + L"=>" + text);
                                }
                            });
    }
    catch (std::exception &e)
    {
        // std::wcout<<e.what();
        return;
    }

    std::thread([hooks]
                {
        for (int lastSize = 0; hooks->size() == 0 || hooks->size() != lastSize; Sleep(2000)) lastSize = hooks->size();

        std::ofstream of;
        of.open("savehooks.txt");
        for (auto line:*hooks) of<<WideStringToString(line)<<"\n"; 
        of.close(); 
        hooks->clear(); })
        .detach();
}
Hooksearchsetting::Hooksearchsetting(mainwindow *p) : mainwindow(p)
{
    layout = new gridlayout();
    SearchParam sp{};
    spinduration = new spinbox(this, sp.searchTime);
    spinoffset = new spinbox(this, sp.offset);
    spincap = new spinbox(this, sp.maxRecords);
    spincodepage = new spinbox(this, Host::defaultCodepage);
    editpattern = new lineedit(this);
    editpattern->settext(tohex(sp.pattern, sp.length));
    editmodule = new lineedit(this);
    editmaxaddr = new lineedit(this);
    editmaxaddr->settext(addr2hex(sp.maxAddress));
    editminaddr = new lineedit(this);
    editminaddr->settext(addr2hex(sp.minAddress));
    spinpadding = new spinbox(this, 0);
    editregex = new lineedit(this);
    start = new button(this, HS_START_HOOK_SEARCH);
    layout->addcontrol(new label(this, HS_SEARCH_PATTERN), 0, 0);
    layout->addcontrol(new label(this, HS_SEARCH_DURATION), 1, 0);
    layout->addcontrol(new label(this, HS_PATTERN_OFFSET), 2, 0);
    layout->addcontrol(new label(this, HS_MAX_HOOK_SEARCH_RECORDS), 3, 0);
    layout->addcontrol(new label(this, HS_CODEPAGE), 4, 0);
    layout->addcontrol(new label(this, HS_SEARCH_MODULE), 5, 0);
    layout->addcontrol(new label(this, HS_MIN_ADDRESS), 6, 0);
    layout->addcontrol(new label(this, HS_MAX_ADDRESS), 7, 0);
    layout->addcontrol(new label(this, HS_STRING_OFFSET), 8, 0);
    layout->addcontrol(new label(this, HS_HOOK_SEARCH_FILTER), 9, 0);
    layout->addcontrol(start, 10, 1);

    layout->addcontrol(editpattern, 0, 1);
    layout->addcontrol(spinduration, 1, 1);
    layout->addcontrol(spinoffset, 2, 1);
    layout->addcontrol(spincap, 3, 1);
    layout->addcontrol(spincodepage, 4, 1);
    layout->addcontrol(editmodule, 5, 1);
    layout->addcontrol(editminaddr, 6, 1);
    layout->addcontrol(editmaxaddr, 7, 1);
    layout->addcontrol(spinpadding, 8, 1);
    layout->addcontrol(editregex, 9, 1);

    setlayout(layout);
    setcentral(1000, 600);
}
std::vector<BYTE> hexStringToBytes(const std::wstring &hexString_)
{
    auto hexString = hexString_;
    strReplace(hexString, L" ", L"");
    strReplace(hexString, L"??", FormatString(L"%02hX", XX));
    std::vector<BYTE> bytes;
    if (hexString.length() % 2 != 0)
    {
        return {};
    }
    for (int i = 0; i < hexString.size() / 2; i++)
    {
        auto byteValue = std::stoi(hexString.substr(i * 2, 2), nullptr, 16);
        bytes.push_back(byteValue);
    }

    return bytes;
}
void Hooksearchsetting::call(std::set<DWORD> pids, std::wstring reg)
{
    if (pids.empty())
        return;

    if (auto filename = getModuleFilename(*pids.begin()))
        editmodule->settext(std::filesystem::path(filename.value()).filename().wstring());
    editregex->settext(reg);
    spincodepage->setcurr(Host::defaultCodepage);

    start->onclick = [&, pids]()
    {
        close();
        SearchParam sp{};
        sp.searchTime = spinduration->getcurr();
        sp.offset = spinoffset->getcurr();
        sp.maxRecords = spincap->getcurr();
        sp.codepage = spincodepage->getcurr();

        if (editpattern->text().find(L".") == std::wstring::npos)
        {
            auto hex = hexStringToBytes(editpattern->text());
            memcpy(sp.pattern, hex.data(), hex.size());
            sp.length = hex.size();
        }
        else
        {
            wcsncpy_s(sp.exportModule, editpattern->text().c_str(), MAX_MODULE_SIZE - 1);
            sp.length = 1;
        }

        wcscpy(sp.boundaryModule, editmodule->text().c_str());
        sp.minAddress = std::stoull(editminaddr->text(), nullptr, 16);
        sp.maxAddress = std::stoull(editmaxaddr->text(), nullptr, 16);
        sp.padding = spinpadding->getcurr();
        realcallsearchhooks(pids, editregex->text(), sp);
    };
    show();
}
Hooksearchwindow::Hooksearchwindow(LunaHost *host) : mainwindow(host)
{

    cjkcheck = new checkbox(this, SEARCH_CJK);
    hs_default = new button(this, HS_START_HOOK_SEARCH);
    hs_text = new button(this, HS_SEARCH_FOR_TEXT);
    hs_user = new button(this, HS_SETTINGS);

    layout = new gridlayout();
    layout->addcontrol(cjkcheck, 0, 0, 1, 3);
    layout->addcontrol(hs_default, 1, 0);
    layout->addcontrol(hs_text, 1, 1);
    layout->addcontrol(hs_user, 1, 2);

    setlayout(layout);

    settext(BtnSearchHook);
    setcentral(800, 200);

    auto dohooksearchdispatch = [&, host](int type)
    {
        close();
        if (type == 1)
        {
            if (hooksearchText == 0)
                hooksearchText = new HooksearchText(this);
            hooksearchText->call(host->attachedprocess);
            return;
        }

        auto filter = (cjkcheck->ischecked() ? L"[\\u3000-\\ua000]{4,}" : L"[\\u0020-\\u1000]{4,}");

        if (type == 0)
        {
            SearchParam sp = {};
            sp.codepage = Host::defaultCodepage;
            sp.length = 0;
            realcallsearchhooks(host->attachedprocess, filter, sp);
        }
        else if (type == 2)
        {
            if (hooksearchsetting == 0)
                hooksearchsetting = new Hooksearchsetting(this);
            hooksearchsetting->call(host->attachedprocess, filter);
            return;
        }
    };

    hs_default->onclick = std::bind(dohooksearchdispatch, 0);
    hs_text->onclick = std::bind(dohooksearchdispatch, 1);
    hs_user->onclick = std::bind(dohooksearchdispatch, 2);
}