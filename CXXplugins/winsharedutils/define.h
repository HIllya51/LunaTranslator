#pragma once
#include<string>
#include<vector>
#include <Audiopolicy.h>
namespace SAPI {
    bool Speak(std::wstring& Content, int voiceid, int rate, int volume, std::wstring& FileName);
    std::vector<std::wstring>List();
    constexpr wchar_t SPCAT_VOICES_7[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices";
    constexpr wchar_t SPCAT_VOICES_10[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices";
}; 
class CAudioMgr
{
public:
    CAudioMgr();
    ~CAudioMgr(); 
public:
    BOOL    SetProcessMute(DWORD Pid, bool mute);
    bool    GetProcessMute(DWORD Pid);
private:
    BOOL    __GetAudioSessionMgr2();
private:
    HRESULT                 m_hRes;
    IAudioSessionManager2* m_lpAudioSessionMgr;
};

extern "C" {

    __declspec(dllexport) bool SAPI_Speak(const wchar_t* Content, int voiceid, int rate, int volume, const wchar_t* Filename);
    __declspec(dllexport) wchar_t** SAPI_List(size_t*);
    __declspec(dllexport) BOOL SetProcessMute(DWORD Pid, bool mute);
    __declspec(dllexport) bool GetProcessMute(DWORD Pid);

}