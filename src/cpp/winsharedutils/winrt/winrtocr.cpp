#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Storage.Pickers.h>
#include <winrt/Windows.Storage.Streams.h>
#include <winrt/Windows.Graphics.Imaging.h>
#include <winrt/Windows.Media.Ocr.h>
#include <winrt/Windows.Foundation.Collections.h>
#include <winrt/Windows.Security.Cryptography.h>
#include <winrt/Windows.Globalization.h>

bool unsafe_check_language_valid(wchar_t *language)
{
    std::wstring l = language;
    auto ocrEngine = winrt::Windows::Media::Ocr::OcrEngine::TryCreateFromUserProfileLanguages();
    winrt::Windows::Globalization::Language language1(l);
    return ocrEngine.IsLanguageSupported(language1);
}
void unsafe_getlanguagelist(void (*cb)(LPCWSTR, LPCWSTR))
{
    auto ocrEngine = winrt::Windows::Media::Ocr::OcrEngine::TryCreateFromUserProfileLanguages();
    auto languages = ocrEngine.AvailableRecognizerLanguages();

    for (auto &&language : languages)
    {
        cb(language.LanguageTag().c_str(), language.DisplayName().c_str());
    }
}
void unsafe_OCR(void *ptr, size_t size, wchar_t *lang, wchar_t *space, void (*cb)(int, int, int, int, LPCWSTR))
{
    auto buffer = winrt::Windows::Security::Cryptography::CryptographicBuffer::CreateFromByteArray(
        winrt::array_view<uint8_t>(static_cast<uint8_t *>(ptr), size));
    winrt::Windows::Storage::Streams::InMemoryRandomAccessStream memoryStream;
    memoryStream.WriteAsync(buffer).get();
    auto decoder = winrt::Windows::Graphics::Imaging::BitmapDecoder::CreateAsync(memoryStream).get();

    auto softwareBitmap = decoder.GetSoftwareBitmapAsync().get();
    std::wstring l = lang;
    winrt::Windows::Globalization::Language language(l);
    auto ocrEngine = winrt::Windows::Media::Ocr::OcrEngine::TryCreateFromLanguage(language);
    auto ocrResult = ocrEngine.RecognizeAsync(softwareBitmap).get();
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
DECLARE_API void OCR(void *ptr, size_t size, wchar_t *lang, wchar_t *space, void (*cb)(int, int, int, int, LPCWSTR))
{
    try
    {
        unsafe_OCR(ptr, size, lang, space, cb);
    }
    catch (...)
    {
    }
}
DECLARE_API bool check_language_valid(wchar_t *language)
{
    try
    {
        return unsafe_check_language_valid(language);
    }
    catch (...)
    {
        return false;
    }
}
DECLARE_API void getlanguagelist(void (*cb)(LPCWSTR, LPCWSTR))
{
    try
    {
        unsafe_getlanguagelist(cb);
    }
    catch (...)
    {
    }
}