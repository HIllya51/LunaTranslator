#ifndef WINXP
#include <winstring.h>
#include <roapi.h>
#include <shcore.h>
#include <windows.foundation.collections.h>
#include <windows.globalization.h>
#include <windows.media.ocr.h>
using ABI::Windows::Foundation::AsyncStatus;
using ABI::Windows::Foundation::GetActivationFactory;
using ABI::Windows::Foundation::IAsyncOperation;
using ABI::Windows::Foundation::IAsyncOperationCompletedHandler;
using ABI::Windows::Foundation::Collections::IVectorView;
using ABI::Windows::Globalization::ILanguage;
using ABI::Windows::Globalization::ILanguageFactory;
using ABI::Windows::Globalization::Language;
using ABI::Windows::Graphics::Imaging::BitmapDecoder;
using ABI::Windows::Graphics::Imaging::IBitmapDecoder;
using ABI::Windows::Graphics::Imaging::IBitmapDecoderStatics;
using ABI::Windows::Graphics::Imaging::IBitmapFrameWithSoftwareBitmap;
using ABI::Windows::Graphics::Imaging::ISoftwareBitmap;
using ABI::Windows::Graphics::Imaging::SoftwareBitmap;
using ABI::Windows::Media::Ocr::IOcrEngine;
using ABI::Windows::Media::Ocr::IOcrEngineStatics;
using ABI::Windows::Media::Ocr::IOcrLine;
using ABI::Windows::Media::Ocr::IOcrResult;
using ABI::Windows::Media::Ocr::IOcrWord;
using ABI::Windows::Media::Ocr::OcrLine;
using ABI::Windows::Media::Ocr::OcrResult;
using ABI::Windows::Media::Ocr::OcrWord;
using ABI::Windows::Storage::Streams::IRandomAccessStream;
#else
#include "xp.hpp"
#endif
#include "hstring.hpp"
template <class OperationT, class HandlerT, class ResultT>
struct CompleteCallback : ComImpl<HandlerT>
{
    CoAsyncTaskWaiter &event;
    HRESULT &hrCallback;
    ResultT **ppResult;
    OperationT *pAsync;
    CompleteCallback(OperationT *pAsync, CoAsyncTaskWaiter &event, HRESULT &hrCallback, ResultT **ppResult) : pAsync(pAsync), event(event), hrCallback(hrCallback), ppResult(ppResult) {}
    HRESULT STDMETHODCALLTYPE Invoke(OperationT *asyncInfo, AsyncStatus status)
    {
        hrCallback = (status == AsyncStatus::Completed) ? pAsync->GetResults(ppResult) : E_FAIL;
        event.Set();
        return hrCallback;
    }
};
template <class OperationT, class HandlerT, class ResultT>
HRESULT await(OperationT *pAsync, ResultT **ppResult)
{
    CoAsyncTaskWaiter co;
    HRESULT hrCallback = E_FAIL;
    auto hr = pAsync->put_Completed(new CompleteCallback<OperationT, HandlerT, ResultT>(pAsync, co, hrCallback, ppResult));
    if (FAILED(hr))
        return hr;
    co.Wait();
    return hrCallback;
}
static HRESULT CreateLanguage(ILanguage **language, LPCWSTR Lang)
{
    CComPtr<ILanguageFactory> language_factory;
    CHECK_FAILURE(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Globalization_Language), &language_factory));
    CHECK_FAILURE(language_factory->CreateLanguage(AutoHStringRef(Lang), language));
    return S_OK;
}
DECLARE_API bool winrt_OCR_check_language_valid(LPCWSTR Lang)
{
    boolean is_supported = false;
    auto hr = [&]()
    {
        CComPtr<ILanguage> language;
        CHECK_FAILURE(CreateLanguage(&language, Lang));
        CComPtr<IOcrEngineStatics> engine_factory;
        CHECK_FAILURE(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Media_Ocr_OcrEngine), &engine_factory))
        CHECK_FAILURE(engine_factory->IsLanguageSupported(language, &is_supported));
        return S_OK;
    }();
    if (FAILED(hr))
        return false;
    return is_supported;
}
DECLARE_API void winrt_OCR_get_AvailableRecognizerLanguages(void (*cb)(LPCWSTR, LPCWSTR))
{
    CComPtr<IOcrEngineStatics> engine_factory;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Media_Ocr_OcrEngine), &engine_factory))
    CComPtr<IVectorView<Language *>> languages;
    CHECK_FAILURE_NORET(engine_factory->get_AvailableRecognizerLanguages(&languages));
    UINT size;
    CHECK_FAILURE_NORET(languages->get_Size(&size));
    for (auto i = 0; i < size; i++)
    {
        CComPtr<ILanguage> language;
        CHECK_FAILURE_CONTINUE(languages->GetAt(i, &language));
        AutoHStringRef LanguageTag, DisplayName;
        CHECK_FAILURE_CONTINUE(language->get_LanguageTag(&LanguageTag));
        CHECK_FAILURE_CONTINUE(language->get_DisplayName(&DisplayName));
        cb(LanguageTag, DisplayName);
    }
}
DECLARE_API void winrt_OCR(const BYTE *ptr, size_t size, LPCWSTR lang, void (*cb)(int, int, int, int, LPCWSTR))
{
    CComPtr<ILanguage> language;
    CHECK_FAILURE_NORET(CreateLanguage(&language, lang));
    CComPtr<IOcrEngineStatics> engine_factory;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Media_Ocr_OcrEngine), &engine_factory))
    CComPtr<IOcrEngine> ocrEngine;
    CHECK_FAILURE_NORET(engine_factory->TryCreateFromLanguage(language, &ocrEngine));
    auto ms = SHCreateMemStream(ptr, size);
    if (!ms)
        return;
    CComPtr<IStream> mscom;
    mscom.Attach(ms);
    CComPtr<IRandomAccessStream> memoryStream;
    CHECK_FAILURE_NORET(CreateRandomAccessStreamOverStream(mscom, BSOS_DEFAULT, IID_PPV_ARGS(&memoryStream)));
    CComPtr<IBitmapDecoderStatics> decoderfactory;
    CHECK_FAILURE_NORET(GetActivationFactory(AutoHStringRefX(RuntimeClass_Windows_Graphics_Imaging_BitmapDecoder), &decoderfactory));
    // CComPtr<IAsyncOperation<BitmapDecoder *>> decoder;
    CComPtr<__FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder> decoder;
    CHECK_FAILURE_NORET(decoderfactory->CreateAsync(memoryStream, &decoder));
    CComPtr<IBitmapDecoder> imagedecoder;
    CHECK_FAILURE_NORET((await<__FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder, __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CBitmapDecoder, IBitmapDecoder>(decoder.p, &imagedecoder)));
    CComPtr<IBitmapFrameWithSoftwareBitmap> pBitmapFrameWithSoftwareBitmap;
    CHECK_FAILURE_NORET(imagedecoder.QueryInterface(&pBitmapFrameWithSoftwareBitmap));
    // CComPtr<IAsyncOperation<SoftwareBitmap *>> pAsync2;
    CComPtr<__FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap> pAsync2;
    CHECK_FAILURE_NORET(pBitmapFrameWithSoftwareBitmap->GetSoftwareBitmapAsync(&pAsync2));
    CComPtr<ISoftwareBitmap> softwareBitmap;
    CHECK_FAILURE_NORET((await<__FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap, __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CSoftwareBitmap, ISoftwareBitmap>(pAsync2.p, &softwareBitmap)));
    // CComPtr<IAsyncOperation<OcrResult *>> ocrResult;
    CComPtr<__FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult> ocrResult;
    CHECK_FAILURE_NORET(ocrEngine->RecognizeAsync(softwareBitmap, &ocrResult));
    CComPtr<IOcrResult> pOcrResult;
    CHECK_FAILURE_NORET((await<__FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult, __FIAsyncOperationCompletedHandler_1_Windows__CMedia__COcr__COcrResult, IOcrResult>(ocrResult.p, &pOcrResult)));
    CComPtr<IVectorView<OcrLine *>> pOcrLines;
    CHECK_FAILURE_NORET(pOcrResult->get_Lines(&pOcrLines));
    uint32_t nlines;
    CHECK_FAILURE_NORET(pOcrLines->get_Size(&nlines));
    for (uint32_t i = 0; i < nlines; ++i)
    {
        // IOcrLine::get_Text对于日语句子单词间也tm有空格。但自己用IOcrWord::get_Text然后拼接也不是很好。就这样吧反正效果也是个辣鸡。
        CComPtr<IOcrLine> pOcrLine;
        CHECK_FAILURE_CONTINUE(pOcrLines->GetAt(i, &pOcrLine));

        CComPtr<IVectorView<OcrWord *>> pOcrWords;
        AutoHStringRef htext;
        CHECK_FAILURE_CONTINUE(pOcrLine->get_Words(&pOcrWords));
        CHECK_FAILURE_CONTINUE(pOcrLine->get_Text(&htext));
        uint32_t nwords;
        CHECK_FAILURE_CONTINUE(pOcrWords->get_Size(&nwords));
        unsigned int x1 = -1, x2 = 0, y1 = -1, y2 = 0;
        for (uint32_t j = 0; j < nwords; ++j)
        {
            CComPtr<IOcrWord> pOcrWord;
            CHECK_FAILURE_CONTINUE(pOcrWords->GetAt(j, &pOcrWord));
            ABI::Windows::Foundation::Rect rect;
            CHECK_FAILURE_CONTINUE(pOcrWord->get_BoundingRect(&rect));
            x1 = std::min((unsigned int)rect.X, x1);
            x2 = std::max(x2, (unsigned int)(rect.X + rect.Width));
            y1 = std::min((unsigned int)rect.Y, y1);
            y2 = std::max(y2, (unsigned int)(rect.Y + rect.Height));
        }
        cb(x1, y1, x2, y2, htext);
    }
}