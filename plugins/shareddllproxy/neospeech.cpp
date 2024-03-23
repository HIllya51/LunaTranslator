
#define _CRT_SECURE_NO_WARNINGS
#include <iostream>
#include <fstream>
#include<Windows.h>
#include <io.h>
#include <fcntl.h> 
#include<vector>
#include<sapi.h>
#include<stdio.h>
#include<iostream>
#include<string>
#include<sphelper.h>
bool _Speak(std::wstring& Content, const wchar_t* token, int voiceid, int rate, int volume, std::wstring& FileName) {
    ISpVoice* pVoice = NULL;
    if (FAILED(::CoInitialize(NULL)))
        return false;
    bool ret = true;
    do
    {
        HRESULT hr = CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void**)&pVoice);
        if (FAILED(hr) || (NULL == pVoice)) {
            ret = false;
            break;
        }
        IEnumSpObjectTokens* pSpEnumTokens = NULL;
        if (SUCCEEDED(SpEnumTokens(token, NULL, NULL, &pSpEnumTokens))) {
            ULONG ulTokensNumber = 0;
            pSpEnumTokens->GetCount(&ulTokensNumber);
            ISpObjectToken* m_pISpObjectToken;

            pSpEnumTokens->Item(voiceid, &m_pISpObjectToken);
            pVoice->SetVoice(m_pISpObjectToken);
            pVoice->SetRate(rate);
            pVoice->SetVolume(volume);

            CComPtr <ISpStream> cpWavStream;
            CComPtr <ISpStreamFormat> cpOldStream;
            CSpStreamFormat originalFmt;
            hr = pVoice->GetOutputStream(&cpOldStream);
            if (FAILED(hr) || (NULL == cpOldStream)) {
                ret = false;
                break;
            }
            originalFmt.AssignFormat(cpOldStream);
            hr = SPBindToFile(FileName.c_str(), SPFM_CREATE_ALWAYS, &cpWavStream, &originalFmt.FormatId(), originalFmt.WaveFormatExPtr());
            if (FAILED(hr)) {
                ret = false;
                break;
            }
            pVoice->SetOutput(cpWavStream, TRUE);
            pVoice->Speak(Content.c_str(), SPF_IS_XML, NULL);
            pVoice->Release();
            pSpEnumTokens->Release();
            pVoice = NULL;
        }

    } while (0);

    ::CoUninitialize();
    return ret;
}

std::vector<std::wstring>_List(const wchar_t* token) {
    if (FAILED(::CoInitialize(NULL)))
        return {};
    ISpVoice* pSpVoice = NULL;
    std::vector<std::wstring> ret;
    IEnumSpObjectTokens* pSpEnumTokens = NULL;
    if (FAILED(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void**)&pSpVoice))) {
        return {};
    }
    if (SUCCEEDED(SpEnumTokens(token, NULL, NULL, &pSpEnumTokens))) {
        ULONG ulTokensNumber = 0;
        pSpEnumTokens->GetCount(&ulTokensNumber);
        ISpObjectToken* m_pISpObjectToken;
        for (ULONG i = 0; i < ulTokensNumber; i++)
        {
            pSpEnumTokens->Item(i, &m_pISpObjectToken);
            WCHAR* pszVoiceId = NULL;
            LPWSTR pszVoiceName;
            if (SUCCEEDED(m_pISpObjectToken->GetId(&pszVoiceId)))
            { 
                if (SUCCEEDED(m_pISpObjectToken->GetStringValue(NULL, &pszVoiceName)))
                {
                    ret.emplace_back(pszVoiceName);
                    CoTaskMemFree(pszVoiceName);
                }

                CoTaskMemFree(pszVoiceId);
            }

        }
        m_pISpObjectToken->Release();

        pSpEnumTokens->Release();
    }
    pSpVoice->Release();
    ::CoUninitialize();
    return ret;
}


int neospeechlist(int argc, wchar_t* argv[]) { 
    FILE* f=_wfopen(argv[1],L"wb");
    for(auto key:{L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices",L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices"})
    {
        auto speechs=_List(key);
        for (int i = 0; i < speechs.size(); i++) {
            if (speechs[i].substr(0,2) == L"VW") {
                fwrite(speechs[i].c_str(),1,speechs[i].size()*2,f);
                fwrite(L"\n",1,2,f);
                fwrite(key,1,wcslen(key)*2,f);
                fwrite(L"\n",1,2,f);
                auto idx=std::to_wstring(i);
                fwrite(idx.c_str(),1,idx.size()*2,f);
                fwrite(L"\n",1,2,f);
            }
        }
    }
     fclose(f);
    return 0;
    
}
int neospeech(int argc, wchar_t* argv[]) { 
    auto hkey=argv[4];
    auto idx=std::stoi(argv[5]);
    

    HANDLE hPipe = CreateNamedPipe(argv[1], PIPE_ACCESS_DUPLEX, PIPE_TYPE_MESSAGE | PIPE_READMODE_MESSAGE | PIPE_WAIT
        , PIPE_UNLIMITED_INSTANCES, 65535, 65535, NMPWAIT_WAIT_FOREVER, 0);
        
    SECURITY_DESCRIPTOR sd = {};
    InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
    SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
    SECURITY_ATTRIBUTES allAccess = SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE };
    SetEvent(CreateEvent(&allAccess, FALSE, FALSE, argv[2]));
    if (ConnectNamedPipe(hPipe, NULL) != NULL) {
        DWORD len = 0;

    } 
    int II = 0;
    while (true) {
        wchar_t text[10000]; 
        II += 1;
        DWORD _;
        int speed;
        if (!ReadFile(hPipe, (unsigned char*)&speed,4, &_, NULL))break;
        if (!ReadFile(hPipe, (unsigned char*)text, 10000*2, &_, NULL))break;
        std::wstring content = text;
        wchar_t newname[1024] = { 0 };
        wsprintf(newname, L"%s%d.wav", argv[3], II);
        std::wstring newname_ = newname;
        _Speak(content, hkey, idx, speed, 100, newname_);
        WriteFile(hPipe, newname, wcslen(newname)*2, &_, NULL);
    } 
    return 0; 
}