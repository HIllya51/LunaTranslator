#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Storage.Pickers.h>
#include <winrt/Windows.Storage.Streams.h>
#include <winrt/Windows.Graphics.Imaging.h>
#include <winrt/Windows.Media.FaceAnalysis.h>
#include <winrt/Windows.Media.Ocr.h>

#include <winrt/Windows.Foundation.Collections.h>
#include <winrt/Windows.Devices.Enumeration.h>
#include <winrt/Windows.Media.Devices.h>

#include <winrt/Windows.Security.Cryptography.h>
#include <winrt/Windows.Globalization.h>
using namespace winrt;

using namespace Windows::Foundation;
using namespace Windows::Storage;
using namespace Windows::Storage::Streams;
using namespace Windows::Graphics::Imaging;
using namespace Windows::Media::Ocr;

using namespace Windows::Devices::Enumeration;
using namespace Windows::Media::Devices;

using namespace Windows::Security::Cryptography;
using namespace Windows::Globalization;
using namespace Windows::Foundation::Collections;
DECLARE_API bool check_language_valid(wchar_t *language)
{
    OcrEngine ocrEngine = OcrEngine::TryCreateFromUserProfileLanguages();
    std::wstring l = language;
    try
    {
        Language language1(l);
        return ocrEngine.IsLanguageSupported(language1);
    }
    catch (...)
    {
        return false;
    }
}
DECLARE_API void getlanguagelist(void (*cb)(LPCWSTR))
{
    OcrEngine ocrEngine = OcrEngine::TryCreateFromUserProfileLanguages();
    auto languages = ocrEngine.AvailableRecognizerLanguages();

    for (auto &&language : languages)
    {
        auto lang = language.LanguageTag();
        cb(lang.c_str());
    }
}
DECLARE_API void OCR(void *ptr, size_t size, wchar_t *lang, wchar_t *space, void (*cb)(int, int, int, int, LPCWSTR))
{
    IBuffer buffer = CryptographicBuffer::CreateFromByteArray(
        winrt::array_view<uint8_t>(static_cast<uint8_t *>(ptr), size));
    InMemoryRandomAccessStream memoryStream;
    memoryStream.WriteAsync(buffer).get();
    BitmapDecoder decoder = BitmapDecoder::CreateAsync(memoryStream).get();

    SoftwareBitmap softwareBitmap = decoder.GetSoftwareBitmapAsync().get();
    std::wstring l = lang;
    Language language(l);
    OcrEngine ocrEngine = OcrEngine::TryCreateFromLanguage(language);
    OcrResult ocrResult = ocrEngine.RecognizeAsync(softwareBitmap).get();
    auto res = ocrResult.Lines();
    for (auto line : res)
    {
        std::wstring xx = L"";
        bool start = true;
        unsigned int x1 = -1, x2 = 0, y1 = -1, y2 = 0;

        for (auto word : line.Words())
        {
            if (!start)
                xx += space;
            start = false;
            xx += word.Text();
            auto &&rect = word.BoundingRect();
            x1 = std::min((unsigned int)rect.X, x1);
            x2 = std::max(x2, (unsigned int)(rect.X + rect.Width));
            y1 = std::min((unsigned int)rect.Y, y1);
            y2 = std::max(y2, (unsigned int)(rect.Y + rect.Height));
        }
        cb(x1, y1, x2, y2, xx.c_str());
    }
}
