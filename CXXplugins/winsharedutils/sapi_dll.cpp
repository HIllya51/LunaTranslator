#include"pch.h"
#include<sapi.h>
#include<stdio.h>
#include<iostream>
#include<string>
#include<sphelper.h>
#include"define.h"

bool SAPI::Speak(std::wstring& Content, int voiceid, int rate, int volume, std::wstring& FileName) {
    ISpVoice* pVoice = NULL;
    if (FAILED(::CoInitialize(NULL)))
        return false;
    bool ret = true; 
    do
    {
        HRESULT hr = CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void**)&pVoice);
        if (FAILED(hr) || (NULL == pVoice)){ 
            ret = false;
            break;
        }
        IEnumSpObjectTokens* pSpEnumTokens = NULL;
        if (SUCCEEDED(SpEnumTokens(SPCAT_VOICES_10, NULL, NULL, &pSpEnumTokens)) || SUCCEEDED(SpEnumTokens(SPCAT_VOICES_7, NULL, NULL, &pSpEnumTokens))) {
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
            if (FAILED(hr) || (NULL == cpOldStream)){
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
std::vector<std::wstring>SAPI::List() { 
    if (FAILED(::CoInitialize(NULL)))
        return {};
	ISpVoice* pSpVoice = NULL;
	std::vector<std::wstring> ret;
	IEnumSpObjectTokens* pSpEnumTokens = NULL;
	if (FAILED(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_INPROC_SERVER, IID_ISpVoice, (void**)&pSpVoice))) {
		return {};
	}
	if (SUCCEEDED(SpEnumTokens(SPCAT_VOICES_10, NULL, NULL, &pSpEnumTokens))|| SUCCEEDED(SpEnumTokens(SPCAT_VOICES_7, NULL, NULL, &pSpEnumTokens))) {
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
                // 通过ID字符串获取语音资源的名称
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

