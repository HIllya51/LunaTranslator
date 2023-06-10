#include"pch.h"
#include"define.h"
#include<iostream>
bool SAPI_Speak(const wchar_t* Content, int version, int voiceid, int rate, int volume, const wchar_t* Filename) {
	auto _c = std::wstring(Content);
	auto _f = std::wstring(Filename);
	return SAPI::Speak(_c,version, voiceid,  rate, volume,_f );

}
wchar_t** SAPI_List(int version,size_t* num) {
    auto _list = SAPI::List(version); 
    *num = _list.size();
    return vecwstr2c(_list);
}

BOOL SetProcessMute(DWORD Pid, bool mute) {
	CAudioMgr AudioMgr;
	return AudioMgr.SetProcessMute(Pid, mute);
}

bool GetProcessMute(DWORD Pid) {
	CAudioMgr AudioMgr;
	return AudioMgr.GetProcessMute(Pid);
}

void free_all(void* str) {
    delete str;
}
void freewstringlist(wchar_t** strlist, int num) {
    for (int i = 0; i < num; i++) {
        delete strlist[i];
    }
    delete strlist;
}
void freestringlist(char** strlist, int num) {
    for (int i = 0; i < num; i++) {
        delete strlist[i];
    }
    delete strlist;
}
 
int* vecint2c(std::vector<int>& vs) {
    int* argv = new int [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = vs[i]; 
    }
    return argv;
}

char** vecstr2c(std::vector<std::string>& vs) {
    char** argv = new char* [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = new char[vs[i].size() + 1];
        strcpy_s(argv[i], vs[i].size()+1, vs[i].c_str());
        argv[i][vs[i].size()] = 0;
    }
    return argv;
}


wchar_t** vecwstr2c(std::vector<std::wstring>& vs) {
    wchar_t** argv = new wchar_t* [vs.size() + 1];

    for (size_t i = 0; i < vs.size(); i++) {
        argv[i] = new wchar_t[vs[i].size() + 1];
        wcscpy_s(argv[i], vs[i].size()+1, vs[i].c_str());
        argv[i][vs[i].size()] = 0;
    }
    return argv;
}
