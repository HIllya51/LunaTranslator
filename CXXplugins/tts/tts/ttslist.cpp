#define _USING_V110_SDK71_
#include<sapi.h>
#include<stdio.h>
#include<iostream>
#include<string>
#include<sphelper.h>
int main() {

	::CoInitialize(NULL);
	ISpVoice* pSpVoice = NULL;
	IEnumSpObjectTokens* pSpEnumTokens = NULL;
	if (FAILED(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_INPROC_SERVER, IID_ISpVoice, (void**)&pSpVoice))) {
		std::cout << 0 << std::endl;
		return -1;
	}
	if (SUCCEEDED(SpEnumTokens(SPCAT_VOICES, NULL, NULL, &pSpEnumTokens))) {
		 
		ULONG ulTokensNumber = 0;
		pSpEnumTokens->GetCount(&ulTokensNumber);
		std::cout << ulTokensNumber<<std::endl;
		ISpObjectToken *m_pISpObjectToken;
		for (ULONG i = 0; i < ulTokensNumber; i++)
		{
			pSpEnumTokens->Item(i, &m_pISpObjectToken);
			WCHAR * pChar; 
			m_pISpObjectToken->GetId(&pChar); 
			std::wstring strVoicePackageName = pChar;
			std::wcout << strVoicePackageName<<std::endl; 
		}
		m_pISpObjectToken->Release();
		 
		pSpEnumTokens->Release();
	}
	pSpVoice->Release();
	::CoUninitialize(); 
	return 0;
}