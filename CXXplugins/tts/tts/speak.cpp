#define _USING_V110_SDK71_
#include<sapi.h>
#include<stdio.h>
#include<iostream>
#include<string>
#include<sphelper.h>
wchar_t const* const digitTables[] =
{
	L"0123456789",
	L"\u0660\u0661\u0662\u0663\u0664\u0665\u0666\u0667\u0668\u0669",
	// ...
};
 
long asNumeric(wchar_t wch)
{
	long result = -1;
	for (wchar_t const* const* p = std::begin(digitTables);
		p != std::end(digitTables) && result == -1;
		++p) {
		wchar_t const* q = std::find(*p, *p + 10, wch);
		if (q != *p + 10) {
			result = q - *p;
		}
		return result;
	}
}
int wmain(int argc,wchar_t *argv[]) {
	setlocale(LC_CTYPE, "");
	for (int i = 0; i < argc; i++)
	{
		wprintf(L"[%d]:%s\n", i, argv[i]);
	}
	::CoInitialize(NULL);
	ISpVoice* pSpVoice = NULL;
	IEnumSpObjectTokens* pSpEnumTokens = NULL;
	if (FAILED(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_INPROC_SERVER, IID_ISpVoice, (void**)&pSpVoice))) {
		 
		return -1;
	}

	if (SUCCEEDED(SpEnumTokens(SPCAT_VOICES, NULL, NULL, &pSpEnumTokens))) {
		 
		ULONG ulTokensNumber = 0;
		pSpEnumTokens->GetCount(&ulTokensNumber); 
		ISpObjectToken* m_pISpObjectToken;
		 
		pSpEnumTokens->Item(asNumeric(argv[1][0]), &m_pISpObjectToken);
		WCHAR* pChar;
		m_pISpObjectToken->GetId(&pChar);
		std::wstring strVoicePackageName = pChar;
		std::wcout << strVoicePackageName << std::endl;
		pSpVoice->SetVoice(m_pISpObjectToken); 
		pSpVoice->SetRate(_wtoi(argv[2]));
		pSpVoice->SetVolume(_wtoi(argv[3]));
		pSpVoice->Speak(LPCWSTR( argv[4]), SPF_DEFAULT, NULL);
		pSpEnumTokens->Release();
		 
		 
	}
	pSpVoice->Release();
	::CoUninitialize();
	return 0;
}