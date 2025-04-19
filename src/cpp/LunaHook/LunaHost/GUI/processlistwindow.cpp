
#include <CommCtrl.h>
#include <TlHelp32.h>
#include "host.h"
#include "LunaHost.h"
#include <shellapi.h>
std::unordered_map<std::wstring, std::vector<int>> getprocesslist()
{
    std::unordered_map<std::wstring, std::vector<int>> exe_pid;
    AutoHandle<> hSnapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnapshot == INVALID_HANDLE_VALUE)
        return {};

    PROCESSENTRY32 pe32;
    pe32.dwSize = sizeof(PROCESSENTRY32);
    wchar_t buff[65535];
    auto currpid = GetCurrentProcessId();
    if (Process32First(hSnapshot, &pe32))
    {
        do
        {
            auto PROCESS_INJECT_ACCESS = (PROCESS_CREATE_THREAD |
                                          PROCESS_QUERY_INFORMATION |
                                          PROCESS_VM_OPERATION |
                                          PROCESS_VM_WRITE |
                                          PROCESS_VM_READ);
            if (pe32.th32ProcessID == currpid)
                continue;
            AutoHandle<> handle = OpenProcess(PROCESS_INJECT_ACCESS, 0, pe32.th32ProcessID);
            if (handle == 0)
                continue;
            DWORD sz = 65535;
            QueryFullProcessImageNameW(handle, 0, buff, &sz);

            auto buffs = std::wstring(buff);
            auto str = stolower(buffs);
            if (str.find(L":\\windows\\") != str.npos || str.find(L"\\microsoft") != str.npos || str.find(L"\\windowsapps") != str.npos)
                continue;

            if (exe_pid.find(buffs) == exe_pid.end())
            {
                exe_pid.insert({buffs, {}});
            }
            exe_pid[buffs].push_back(pe32.th32ProcessID);
        } while (Process32Next(hSnapshot, &pe32));
    }
    return exe_pid;
}

void processlistwindow::PopulateProcessList(listview *_listbox, std::unordered_map<std::wstring, std::vector<int>> &exe_pid)
{
    _listbox->clear();
    for (auto &exe : exe_pid)
    {
        auto hicon = GetExeIcon(exe.first);
        _listbox->additem(exe.first, hicon);
        DestroyIcon(hicon);
    }
}

processlistwindow::processlistwindow(mainwindow *p) : mainwindow(p)
{
    g_hEdit = new lineedit(this);
    g_hButton = new button(this, TR[BtnAttach]);
    g_refreshbutton = new button(this, TR[BtnRefresh]);
    g_hButton->onclick = [&]()
    {
        auto str = g_hEdit->text();
        if (str.size())
        {
            close();

            for (auto _s : strSplit(str, L","))
            {
                DWORD pid = 0;
                try
                {
                    pid = std::stoi(_s);
                }
                catch (std::exception &)
                {
                }
                if (pid)
                    Host::ConnectAndInjectProcess(pid);
            }
        }
    };
    g_refreshbutton->onclick = [&]()
    {
        g_exe_pid = getprocesslist();
        PopulateProcessList(g_hListBox, g_exe_pid);
    };
    g_hListBox = new listview(this, true, true);
    g_hListBox->setheader({L""});
    g_hListBox->oncurrentchange = [&](int idx)
    {
        auto pids = g_exe_pid[g_hListBox->text(idx)];

        std::wstring _;
        bool _1 = false;
        for (auto &p : pids)
        {
            if (_1)
                _ += L",";
            _ += std::to_wstring(p);
            _1 = true;
        }
        g_hEdit->settext(_);
    };
    settext(TR[WndSelectProcess]);
    mainlayout = new gridlayout();
    mainlayout->addcontrol(g_hEdit, 0, 0, 1, 2);
    mainlayout->addcontrol(g_hButton, 0, 2);
    mainlayout->addcontrol(g_refreshbutton, 0, 3);
    mainlayout->addcontrol(g_hListBox, 1, 0, 1, 4);
    mainlayout->setfixedheigth(0, 30);
    setlayout(mainlayout);
    setcentral(800, 400);
}
void processlistwindow::on_show()
{
    g_hEdit->settext(L"");
    g_exe_pid = getprocesslist();
    PopulateProcessList(g_hListBox, g_exe_pid);
}