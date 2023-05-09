#include"pch.h"
#include"define.h"
#include<iostream>
bool SAPI_Speak(const wchar_t* Content, int voiceid, int rate, int volume, const wchar_t* Filename) {
	auto _c = std::wstring(Content);
	auto _f = std::wstring(Filename);
	return SAPI::Speak(_c, voiceid,  rate, volume,_f );

}
wchar_t** SAPI_List(size_t* num) {
    auto _list = SAPI::List();
    auto ret = new wchar_t* [_list.size()];
    for (int i = 0; i < _list.size(); i++) {
        ret[i] = new wchar_t[_list[i].size() + 1];  
        wcscpy(ret[i], _list[i].c_str());
        ret[i][_list[i].size()] = L'\0';  
    }
    *num = _list.size();
    return ret;
}

BOOL SetProcessMute(DWORD Pid, bool mute) {
	CAudioMgr AudioMgr;
	return AudioMgr.SetProcessMute(Pid, mute);
}

bool GetProcessMute(DWORD Pid) {
	CAudioMgr AudioMgr;
	return AudioMgr.GetProcessMute(Pid);
}