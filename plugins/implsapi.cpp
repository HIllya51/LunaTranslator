
bool _Speak(std::wstring &Content, const wchar_t *token, int voiceid, int rate, int volume, int *length, char **buffer)
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
            CComPtr<IStream> pMemStream;
            hr = pVoice->GetOutputStream(&cpOldStream);
            if (FAILED(hr) || (NULL == cpOldStream))
            {
                ret = false;
                break;
            }
            originalFmt.AssignFormat(cpOldStream);
            // hr = SPBindToFile(FileName.c_str(), SPFM_CREATE_ALWAYS, &cpWavStream, &originalFmt.FormatId(), originalFmt.WaveFormatExPtr());
            // if (FAILED(hr))
            // {
            //     ret = false;
            //     break;
            // }
            {
                hr = ::CreateStreamOnHGlobal(NULL, TRUE, &pMemStream);
                if (SUCCEEDED(hr))
                {
                    hr = cpWavStream.CoCreateInstance(CLSID_SpStream);
                    if (SUCCEEDED(hr))
                    {
                        hr = cpWavStream->SetBaseStream(pMemStream, SPDFID_WaveFormatEx, originalFmt.WaveFormatExPtr());
                        if (FAILED(hr))
                        {
                            ret = false;
                            break;
                        }
                    }
                }
            }
            pVoice->SetOutput(cpWavStream, TRUE);
            pVoice->Speak(Content.c_str(), SPF_IS_XML, NULL);
            pVoice->Release();
            pSpEnumTokens->Release();
            pVoice = NULL;

            /*To verify that the data has been written correctly, uncomment this, you should hear the voice.
            cpVoice->SetOutput(NULL, FALSE);
            cpVoice->SpeakStream(cpStream, SPF_DEFAULT, NULL);
            */

            // After SAPI writes the stream, the stream position is at the end, so we need to set it to the beginning.
            _LARGE_INTEGER a = {0};
            hr = cpWavStream->Seek(a, STREAM_SEEK_SET, NULL);

            // get the base istream from the ispstream
            IStream *pIstream;
            cpWavStream->GetBaseStream(&pIstream);

            // calculate the size that is to be read
            STATSTG stats;
            pIstream->Stat(&stats, STATFLAG_NONAME);

            ULONG sSize = stats.cbSize.QuadPart; // size of the data to be read
            auto wavfmt = *originalFmt.WaveFormatExPtr();

            ULONG bytesRead;                         //	this will tell the number of bytes that have been read
            char *pBuffer = new char[sSize + 0x3ea]; // buffer to read the data
            // memcpy(pBuffer,&wavHeader,sizeof(WAV_HEADER));
            int fsize = sSize + 0x3ea;
            int ptr = 0;
            memcpy(pBuffer, "RIFF", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &fsize, 4);
            ptr += 4;
            memcpy(pBuffer + ptr, "WAVEfmt ", 8);
            ptr += 8;
            memcpy(pBuffer + ptr, "\x12\x00\x00\x00", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &wavfmt.wFormatTag, 2);
            ptr += 2;
            memcpy(pBuffer + ptr, &wavfmt.nChannels, 2);
            ptr += 2;
            int freq = wavfmt.nSamplesPerSec;
            memcpy(pBuffer + ptr, &freq, 4);
            ptr += 4;
            freq = wavfmt.nAvgBytesPerSec;
            memcpy(pBuffer + ptr, &freq, 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &wavfmt.nBlockAlign, 4);
            ptr += 2;
            memcpy(pBuffer + ptr, &wavfmt.wBitsPerSample, 2);
            ptr += 2;
            WORD _0 = 0;

            memcpy(pBuffer + ptr, &_0, 2);
            ptr += 2;
            memcpy(pBuffer + ptr, "data", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &sSize, 4);

            // read the data into the buffer
            pIstream->Read(pBuffer + 46, sSize, &bytesRead);

            /*uncomment the following to print the contents of the buffer
                cout << "following data read \n";
                for (int i = 0; i < sSize; i++)
                    cout << pBuffer[i] << " ";
                cout << endl;
            */
            *buffer = pBuffer;
            *length = fsize;
            pIstream->Release();
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