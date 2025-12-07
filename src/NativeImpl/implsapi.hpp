#include <sapi.h>
#include <sphelper.h>
namespace
{
    const wchar_t SPCAT_VOICES_7[] = LR"(HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices)";
    const wchar_t SPCAT_VOICES_10[] = LR"(HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices)";

    std::optional<std::vector<byte>> Speak(const std::wstring &Content, LPCWSTR voiceid, int rate, int pitch, int volume = 100)
    {
        std::optional<std::vector<byte>> ret = {};
        [&]()
        {
            CO_INIT co;
            CHECK_FAILURE_NORET(co);
            CComPtr<ISpVoice> pVoice = NULL;
            CHECK_FAILURE_NORET(pVoice.CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL));
            CComPtr<ISpObjectToken> m_pISpObjectToken;
            CHECK_FAILURE_NORET(SpCreateNewToken(voiceid, &m_pISpObjectToken));
            pVoice->SetVoice(m_pISpObjectToken);
            pVoice->SetRate(rate);
            pVoice->SetVolume(volume);

            CComPtr<ISpStream> cpWavStream;
            CComPtr<ISpStreamFormat> cpOldStream;
            CSpStreamFormat originalFmt;
            CComPtr<IStream> pMemStream;
            CHECK_FAILURE_NORET(pVoice->GetOutputStream(&cpOldStream));
            originalFmt.AssignFormat(cpOldStream);
            CHECK_FAILURE_NORET(CreateStreamOnHGlobal(NULL, TRUE, &pMemStream));
            CHECK_FAILURE_NORET(cpWavStream.CoCreateInstance(CLSID_SpStream));
            CHECK_FAILURE_NORET(cpWavStream->SetBaseStream(pMemStream, SPDFID_WaveFormatEx, originalFmt.WaveFormatExPtr()));
            pVoice->SetOutput(cpWavStream, TRUE);
            if (pitch != 0)
            {
                std::wstring _ = L"<pitch absmiddle=\"" + std::to_wstring(pitch) + L"\">" + Content + L"</pitch>";
                pVoice->Speak(_.c_str(), SPF_IS_XML, NULL);
            }
            else
            {
                pVoice->Speak(Content.c_str(), SPF_IS_XML, NULL);
            }

            /*To verify that the data has been written correctly, uncomment this, you should hear the voice.
            cpVoice->SetOutput(NULL, FALSE);
            cpVoice->SpeakStream(cpStream, SPF_DEFAULT, NULL);
            */

            // After SAPI writes the stream, the stream position is at the end, so we need to set it to the beginning.
            _LARGE_INTEGER a = {0};
            CHECK_FAILURE_NORET(cpWavStream->Seek(a, STREAM_SEEK_SET, NULL));

            // get the base istream from the ispstream
            CComPtr<IStream> pIstream;
            cpWavStream->GetBaseStream(&pIstream);

            // calculate the size that is to be read
            STATSTG stats;
            pIstream->Stat(&stats, STATFLAG_NONAME);

            ULONG sSize = stats.cbSize.QuadPart; // size of the data to be read

            ULONG bytesRead; //	this will tell the number of bytes that have been read
            std::vector<byte> datas;
            datas.resize(sSize + 46);
            auto pBuffer = datas.data(); // buffer to read the data
            // memcpy(pBuffer,&wavHeader,sizeof(WAV_HEADER));
            int fsize = sSize + 46;
            int ptr = 0;
            memcpy(pBuffer, "RIFF", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &fsize, 4);
            ptr += 4;
            memcpy(pBuffer + ptr, "WAVEfmt ", 8);
            ptr += 8;
            memcpy(pBuffer + ptr, "\x12\x00\x00\x00", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, originalFmt.WaveFormatExPtr(), sizeof(WAVEFORMATEX));
            ptr += sizeof(WAVEFORMATEX);
            memcpy(pBuffer + ptr, "data", 4);
            ptr += 4;
            memcpy(pBuffer + ptr, &sSize, 4);
            ptr += 4;
            // read the data into the buffer
            pIstream->Read(pBuffer + ptr, sSize, &bytesRead);

            ret = std::move(datas);
        }();

        return ret;
    }

    std::vector<std::pair<std::wstring, std::wstring>> List(const wchar_t *token)
    {
        std::vector<std::pair<std::wstring, std::wstring>> ret;
        [&]()
        {
            CO_INIT co;
            CHECK_FAILURE_NORET(co);
            CComPtr<ISpVoice> pSpVoice = NULL;
            CComPtr<IEnumSpObjectTokens> pSpEnumTokens = NULL;
            CHECK_FAILURE_NORET(CoCreateInstance(CLSID_SpVoice, NULL, CLSCTX_ALL, IID_ISpVoice, (void **)&pSpVoice));
            CHECK_FAILURE_NORET(SpEnumTokens(token, NULL, NULL, &pSpEnumTokens));
            ULONG ulTokensNumber = 0;
            pSpEnumTokens->GetCount(&ulTokensNumber);
            CComPtr<ISpObjectToken> m_pISpObjectToken;
            for (ULONG i = 0; i < ulTokensNumber; i++)
            {
                pSpEnumTokens->Item(i, &m_pISpObjectToken);
                CComHeapPtr<WCHAR> pszVoiceId;
                CComHeapPtr<WCHAR> pszVoiceName;
                CHECK_FAILURE_CONTINUE(m_pISpObjectToken->GetId(&pszVoiceId));
                CHECK_FAILURE_CONTINUE(m_pISpObjectToken->GetStringValue(NULL, &pszVoiceName));
                ret.emplace_back(std::move(pszVoiceId), std::move(pszVoiceName));
            }
        }();
        return ret;
    }
}
namespace SAPI
{
    std::optional<std::vector<byte>> Speak(const std::wstring &Content, LPCWSTR voiceid, int rate, int pitch, int volume = 100)
    {
        return ::Speak(Content, voiceid, rate, pitch, volume);
    }
    std::vector<std::pair<std::wstring, std::wstring>> List(int version)
    {
        if (version == 7)
        {
            return ::List(SPCAT_VOICES_7);
        }
        else if (version == 10)
        {
            return ::List(SPCAT_VOICES_10);
        }
        else
        {
            return {};
        }
    }
}