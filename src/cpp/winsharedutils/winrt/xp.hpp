enum class AsyncStatus
{
    Started = 0,
    Completed,
    Canceled,
    Error,
};

namespace ABI
{
    namespace Windows
    {
        namespace Foundation
        {
            struct Rect
            {
                FLOAT X;
                FLOAT Y;
                FLOAT Width;
                FLOAT Height;
            };
        } /* Foundation */
    } /* Windows */
} /* ABI */
typedef enum
{
    BSOS_DEFAULT = 0,            // when creating a byte seeker over a stream, base randomaccessstream behavior on the STGM mode from IStream::Stat.
    BSOS_PREFERDESTINATIONSTREAM // in addition, utilize IDestinationStreamFactory::GetDestinationStream.
} BSOS_OPTIONS;
typedef struct HSTRING__
{
    int unused;
} HSTRING__;

// Declare the HSTRING handle for C/C++
typedef __RPC_unique_pointer HSTRING__ *HSTRING;

typedef /* [v1_enum] */
    enum TrustLevel
{
    BaseTrust = 0,
    PartialTrust = (BaseTrust + 1),
    FullTrust = (PartialTrust + 1)
} TrustLevel;
MIDL_INTERFACE("AF86E2E0-B12D-4c6a-9C5A-D7AA65101E90")
IInspectable : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetIids(
        /* [out] */ __RPC__out ULONG * iidCount,
        /* [size_is][size_is][out] */ __RPC__deref_out_ecount_full_opt(*iidCount) IID * *iids) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetRuntimeClassName(
        /* [out] */ __RPC__deref_out_opt HSTRING * className) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetTrustLevel(
        /* [out] */ __RPC__out TrustLevel * trustLevel) = 0;
};

MIDL_INTERFACE("ea79a752-f7c2-4265-b1bd-c4dec4e4f080")
ILanguage : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_LanguageTag(
        HSTRING * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_DisplayName(
        HSTRING * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_NativeName(
        HSTRING * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_Script(
        HSTRING * value) = 0;
};
MIDL_INTERFACE("9b0252ac-0c27-44f8-b792-9793fb66c63e")
ILanguageFactory : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE CreateLanguage(
        HSTRING languageTag,
        ILanguage * *result) = 0;
};
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Globalization_Language[] = L"Windows.Globalization.Language";

MIDL_INTERFACE("acef22ba-1d74-4c91-9dfc-9620745233e6")
IBitmapDecoder : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_BitmapContainerProperties(
        void **value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_DecoderInformation(
        void **value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_FrameCount(
        UINT32 * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetPreviewAsync(
        void **asyncInfo) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetFrameAsync(
        UINT32 frameIndex,
        void **asyncInfo) = 0;
};
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Media_Ocr_OcrEngine[] = L"Windows.Media.Ocr.OcrEngine";

extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Imaging_BitmapDecoder[] = L"Windows.Graphics.Imaging.BitmapDecoder";
MIDL_INTERFACE("689e0708-7eef-483f-963f-da938818e073")
ISoftwareBitmap : public IInspectable{};

void *loadproc(LPCWSTR lib, LPCSTR func);
_Check_return_
    HRESULT
        WINAPI
        RoGetActivationFactory(
            _In_ HSTRING activatableClassId,
            _In_ REFIID iid,
            _COM_Outptr_ void **factory)

{
    auto func = loadproc(L"Combase.dll", "RoGetActivationFactory");
    if (!func)
        return E_NOTIMPL;
    return ((decltype(&RoGetActivationFactory))(func))(activatableClassId, iid, factory);
}
template <class T>
_Check_return_ __inline HRESULT GetActivationFactory(
    _In_ HSTRING activatableClassId,
    _COM_Outptr_ T **factory)
{
    return RoGetActivationFactory(activatableClassId, IID_PPV_ARGS(factory));
}

MIDL_INTERFACE("905a0fe1-bc53-11df-8c49-001e4fc686da")
IRandomAccessStream : public IInspectable{

                      };

#define SoftwareBitmap ISoftwareBitmap

#define Language ILanguage
MIDL_INTERFACE("3c2a477a-5cd9-3525-ba2a-23d1e0a68a1d")
IOcrWord : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_BoundingRect(
        ABI::Windows::Foundation::Rect * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_Text(
        HSTRING * value) = 0;
};
#define OcrWord IOcrWord

template <class LogicalType, class AbiType>
struct AggregateType
{
};

// Gets the ABI type.  See AggregateType for description.
template <class T>
struct GetAbiType
{
    typedef T type;
};

template <class L, class A>
struct GetAbiType<AggregateType<L, A>>
{
    typedef A type;
};

// Gets the LogicalType.  See AggregateType for description.
template <class T>
struct GetLogicalType
{
    typedef T type;
};

template <class L, class A>
struct GetLogicalType<AggregateType<L, A>>
{
    typedef L type;
};

STDAPI
WindowsCreateString(
    _In_reads_opt_(length) PCNZWCH sourceString,
    UINT32 length,
    _Outptr_result_maybenull_ _Result_nullonfailure_ HSTRING *string);

STDAPI
WindowsDeleteString(
    _In_opt_ HSTRING string);

STDAPI_(PCWSTR)
WindowsGetStringRawBuffer(
    _In_opt_ HSTRING string,
    _Out_opt_ UINT32 *length);

#define BitmapDecoder IBitmapDecoder

template <class T>
struct IVectorView : ComImpl<IInspectable> /* requires IIterable<T> */
{
private:
public:
    typedef T T_complex;

    virtual HRESULT STDMETHODCALLTYPE GetAt(_In_ unsigned index, _Out_ T *item) = 0;
    virtual /* propget */ HRESULT STDMETHODCALLTYPE get_Size(_Out_ unsigned *size) = 0;
    virtual HRESULT STDMETHODCALLTYPE IndexOf(_In_opt_ T value, _Out_ unsigned *index, _Out_ boolean *found) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetMany(_In_ unsigned startIndex, _In_ unsigned capacity, _Out_writes_to_(capacity, *actual) T *value, _Out_ unsigned *actual) = 0;
};

#define DEFINE_IASYNC_OPERATION_CALLBACK(operation, operationid, handler, handlerid, resulttype) \
    struct operation;                                                                            \
    MIDL_INTERFACE(handlerid)                                                                    \
    handler:                                                                                     \
    IUnknown                                                                                     \
    {                                                                                            \
    public:                                                                                      \
        virtual HRESULT STDMETHODCALLTYPE Invoke(operation *asyncInfo, AsyncStatus status) = 0;  \
    };                                                                                           \
    MIDL_INTERFACE(operationid)                                                                  \
    operation:                                                                                   \
public                                                                                           \
    IInspectable                                                                                 \
    {                                                                                            \
    public:                                                                                      \
        virtual HRESULT STDMETHODCALLTYPE put_Completed(handler *handler) = 0;                   \
        virtual HRESULT STDMETHODCALLTYPE get_Completed(handler **handler) = 0;                  \
        virtual HRESULT STDMETHODCALLTYPE GetResults(resulttype **results) = 0;                  \
    };

DEFINE_IASYNC_OPERATION_CALLBACK(__FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder, "aa94d8e9-caef-53f6-823d-91b6e8340510", __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CBitmapDecoder, "bb6514f2-3cfb-566f-82bc-60aabd302d53", BitmapDecoder)

DEFINE_IASYNC_OPERATION_CALLBACK(__FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap, "c4a10980-714b-5501-8da2-dbdacce70f73", __FIAsyncOperationCompletedHandler_1_Windows__CGraphics__CImaging__CSoftwareBitmap, "b699b653-33ed-5e2d-a75f-02bf90e32619", SoftwareBitmap)

MIDL_INTERFACE("438ccb26-bcef-4e95-bad6-23a822e58d01")
IBitmapDecoderStatics : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_BmpDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_JpegDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_PngDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_TiffDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_GifDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_JpegXRDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_IcoDecoderId(
        GUID * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetDecoderInformationEnumerator(
        void **decoderInformationEnumerator) = 0;
    virtual HRESULT STDMETHODCALLTYPE CreateAsync(
        IRandomAccessStream * stream,
        __FIAsyncOperation_1_Windows__CGraphics__CImaging__CBitmapDecoder * *asyncInfo) = 0;
    virtual HRESULT STDMETHODCALLTYPE CreateWithIdAsync(
        GUID decoderId,
        IRandomAccessStream * stream,
        void **asyncInfo) = 0;
};

MIDL_INTERFACE("0043a16f-e31f-3a24-899c-d444bd088124")
IOcrLine : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_Words(
        IVectorView<OcrWord *> * *value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_Text(
        HSTRING * value) = 0;
};
#define OcrLine IOcrLine
MIDL_INTERFACE("9bd235b2-175b-3d6a-92e2-388c206e2f63")
IOcrResult : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_Lines(
        IVectorView<OcrLine *> * *value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_TextAngle(
        void **value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_Text(
        HSTRING * value) = 0;
};

#define OcrResult IOcrResult

DEFINE_IASYNC_OPERATION_CALLBACK(__FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult, "c7d7118e-ae36-59c0-ac76-7badee711c8b", __FIAsyncOperationCompletedHandler_1_Windows__CMedia__COcr__COcrResult, "989c1371-444a-5e7e-b197-9eaaf9d2829a", IOcrResult)

MIDL_INTERFACE("5a14bc41-5b76-3140-b680-8825562683ac")
IOcrEngine : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE RecognizeAsync(
        ISoftwareBitmap * bitmap,
        __FIAsyncOperation_1_Windows__CMedia__COcr__COcrResult * *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_RecognizerLanguage(
        ILanguage * *value) = 0;
};

MIDL_INTERFACE("5bffa85a-3384-3540-9940-699120d428a8")
IOcrEngineStatics : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_MaxImageDimension(
        UINT32 * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_AvailableRecognizerLanguages(
        IVectorView<Language *> * *value) = 0;
    virtual HRESULT STDMETHODCALLTYPE IsLanguageSupported(
        ILanguage * language,
        boolean * result) = 0;
    virtual HRESULT STDMETHODCALLTYPE TryCreateFromLanguage(
        ILanguage * language,
        IOcrEngine * *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE TryCreateFromUserProfileLanguages(
        IOcrEngine * *result) = 0;
};
STDAPI CreateRandomAccessStreamOverStream(_In_ IStream *stream, _In_ BSOS_OPTIONS options, _In_ REFIID riid, _COM_Outptr_ void **ppv);

MIDL_INTERFACE("fe287c9a-420c-4963-87ad-691436e08383")
IBitmapFrameWithSoftwareBitmap : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapAsync(
        __FIAsyncOperation_1_Windows__CGraphics__CImaging__CSoftwareBitmap * *value) = 0;
    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapConvertedAsync() = 0;
    virtual HRESULT STDMETHODCALLTYPE GetSoftwareBitmapTransformedAsync() = 0;
};