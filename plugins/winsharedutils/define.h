#pragma once
#include<string>
#include<vector>
#include <Audiopolicy.h>
namespace SAPI {
    bool Speak(std::wstring& Content, int version,int voiceid, int rate, int volume, std::wstring& FileName);
    std::vector<std::wstring>List(int version);
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

    __declspec(dllexport) bool SAPI_Speak(const wchar_t* Content, int version, int voiceid, int rate, int volume, const wchar_t* Filename);
    __declspec(dllexport) wchar_t** SAPI_List(int version,size_t*);
    __declspec(dllexport) BOOL SetProcessMute(DWORD Pid, bool mute);
    __declspec(dllexport) bool GetProcessMute(DWORD Pid);
    

    __declspec(dllexport) size_t levenshtein_distance(size_t len1, const wchar_t* string1,
        size_t len2, const wchar_t* string2);
    __declspec(dllexport)  double levenshtein_ratio(size_t len1, const wchar_t* string1,
        size_t len2, const wchar_t* string2);

    __declspec(dllexport) void freewstringlist(wchar_t**, int);
    __declspec(dllexport) void free_all(void* str);
    __declspec(dllexport) void freestringlist(char**, int);


    __declspec(dllexport) void* mecab_init(char* utf8path, wchar_t*);
    __declspec(dllexport) bool mecab_parse(void* trigger, char* utf8string, char*** surface, char*** features, int* num);


    __declspec(dllexport) wchar_t* clipboard_get();
    __declspec(dllexport) bool clipboard_set(wchar_t* text);
    __declspec(dllexport) void GetLnkTargetPath(wchar_t* lnkFilePath,wchar_t *path,wchar_t*tgtpath,wchar_t*iconpath,wchar_t*dirpath) ;
    __declspec(dllexport) bool otsu_binary(const void*image,int thresh);
}
char** vecstr2c(std::vector<std::string>& vs);
int* vecint2c(std::vector<int>& vs);
wchar_t** vecwstr2c(std::vector<std::wstring>& vs);