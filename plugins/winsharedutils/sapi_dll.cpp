
#include "define.h"
#include "cinterface.h"
bool _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume, std::wstring &FileName)
{
    ISpVoice *pVoice = NULL;
    if (FAILED(::CoInitialize(NULL)))
        return false;
    bool ret = true;
    do
    {
        HRESULT hr = CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void **)&pVoice);
        if (FAILED(hr) || (NULL == pVoice))
        {
            ret = false;
            break;
        }
        IEnumSpObjectTokens *pSpEnumTokens = NULL;
        if (SUCCEEDED(SpEnumTokens(token, NULL, NULL, &pSpEnumTokens)))
        {
            ULONG ulTokensNumber = 0;
            pSpEnumTokens->GetCount(&ulTokensNumber);
            ISpObjectToken *m_pISpObjectToken;

            pSpEnumTokens->Item(voiceid, &m_pISpObjectToken);
            pVoice->SetVoice(m_pISpObjectToken);
            pVoice->SetRate(rate);
            pVoice->SetVolume(volume);

            CComPtr<ISpStream> cpWavStream;
            CComPtr<ISpStreamFormat> cpOldStream;
            CSpStreamFormat originalFmt;
            hr = pVoice->GetOutputStream(&cpOldStream);
            if (FAILED(hr) || (NULL == cpOldStream))
            {
                ret = false;
                break;
            }
            originalFmt.AssignFormat(cpOldStream);
            hr = SPBindToFile(FileName.c_str(), SPFM_CREATE_ALWAYS, &cpWavStream, &originalFmt.FormatId(), originalFmt.WaveFormatExPtr());
            if (FAILED(hr))
            {
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

std::vector<std::wstring> _List(const wchar_t *token)
{
    if (FAILED(::CoInitialize(NULL)))
        return {};
    ISpVoice *pSpVoice = NULL;
    std::vector<std::wstring> ret;
    IEnumSpObjectTokens *pSpEnumTokens = NULL;
    if (FAILED(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void **)&pSpVoice)))
    {
        return {};
    }
    if (SUCCEEDED(SpEnumTokens(token, NULL, NULL, &pSpEnumTokens)))
    {
        ULONG ulTokensNumber = 0;
        pSpEnumTokens->GetCount(&ulTokensNumber);
        ISpObjectToken *m_pISpObjectToken;
        for (ULONG i = 0; i < ulTokensNumber; i++)
        {
            pSpEnumTokens->Item(i, &m_pISpObjectToken);
            WCHAR *pszVoiceId = NULL;
            LPWSTR pszVoiceName;
            if (SUCCEEDED(m_pISpObjectToken->GetId(&pszVoiceId)))
            {
                // ͨ��ID�ַ�����ȡ������Դ������
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
namespace SAPI
{
    bool Speak(std::wstring &Content, int version, int voiceid, int rate, int volume, std::wstring &FileName);
    std::vector<std::wstring> List(int version);
    constexpr wchar_t SPCAT_VOICES_7[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices";
    constexpr wchar_t SPCAT_VOICES_10[] = L"HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech_OneCore\\Voices";
};

bool SAPI::Speak(std::wstring &Content, int version, int voiceid, int rate, int volume, std::wstring &FileName)
{
    if (version == 7)
    {
        return _Speak(Content, SPCAT_VOICES_7, voiceid, rate, volume, FileName);
    }
    else if (version == 10)
    {
        return _Speak(Content, SPCAT_VOICES_10, voiceid, rate, volume, FileName);
    }
    else
    {
        return false;
    }
}
std::vector<std::wstring> SAPI::List(int version)
{
    if (version == 7)
    {
        return _List(SPCAT_VOICES_7);
    }
    else if (version == 10)
    {
        return _List(SPCAT_VOICES_10);
    }
    else
    {
        return {};
    }
}

bool SAPI_Speak(const wchar_t *Content, int version, int voiceid, int rate, int volume, const wchar_t *Filename)
{
    auto _c = std::wstring(Content);
    auto _f = std::wstring(Filename);
    return SAPI::Speak(_c, version, voiceid, rate, volume, _f);
}

wchar_t **SAPI_List(int version, size_t *num)
{
    auto _list = SAPI::List(version);
    *num = _list.size();
    return vecwstr2c(_list);
}