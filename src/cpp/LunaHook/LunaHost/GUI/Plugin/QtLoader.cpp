#include <Windows.h>
#include <QApplication>
#include <QFont>
#include <QDir>
#include <thread>
#include <queue>
#include <mutex>
#include <Shlwapi.h>
#include <filesystem>
#include "../lockedqueue.hpp"

lockedqueue<std::wstring> waitingtask;
lockedqueue<HMODULE> waitingresult;

extern "C" __declspec(dllexport) int QtStartUp(std::vector<std::wstring> *dlls)
{
    static bool once = false;
    if (once)
        return 0;
    once = true;
    std::thread([=]()
                {
                    for (int i = 0; i < dlls->size(); i++)
                        QApplication::addLibraryPath(QString::fromStdWString(std::filesystem::path(dlls->at(i)).parent_path()));

                    int _ = 0;
                    QApplication app(_, nullptr);
                    app.setFont(QFont("MS Shell Dlg 2", 10));

                    while (true)
                    {
                        if (!waitingtask.empty())
                        {
                            auto top = waitingtask.pop();
                            waitingresult.push(LoadLibraryW(top.c_str()));
                        }
                        app.processEvents(0);
                    }
                })
        .detach();
    return 0;
}
std::mutex loadmutex;

extern "C" __declspec(dllexport) std::vector<HMODULE> *QtLoadLibraryBatch(std::vector<std::wstring> *dlls)
{
    std::lock_guard _(loadmutex);
    static auto once = QtStartUp(dlls);
    auto hdlls = new std::vector<HMODULE>;
    for (int i = 0; i < dlls->size(); i++)
    {
        waitingtask.push(dlls->at(i));
        hdlls->push_back(waitingresult.pop());
    }
    return hdlls;
}
#if 0
extern "C" __declspec(dllexport) std::vector<HMODULE>* QtLoadLibrary(std::vector<std::wstring>* dlls){
    auto hdlls=new std::vector<HMODULE>;
    auto mutex=CreateSemaphoreW(0,0,1,0);
    std::thread([=](){
        for(int i=0;i<dlls->size();i++)
            QApplication::addLibraryPath(QString::fromStdWString(std::filesystem::path(dlls->at(i)).parent_path()));
        
        int _=0;
        QApplication app(_, nullptr);
        app.setFont(QFont("MS Shell Dlg 2", 10));
        for(int i=0;i<dlls->size();i++)
            hdlls->push_back(LoadLibraryW(dlls->at(i).c_str()));
        ReleaseSemaphore(mutex,1,0);
        app.exec();
        
    }).detach();
    WaitForSingleObject(mutex,INFINITE);
    return hdlls;
}
#endif