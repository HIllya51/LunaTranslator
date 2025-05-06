typedef struct EventRegistrationToken
{
    __int64 value;
} EventRegistrationToken;
//////////////////////////////////OCR
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

// Declare the HSTRING_HEADER
typedef struct HSTRING_HEADER
{
    union
    {
        PVOID Reserved1;
#if defined(_WIN64)
        char Reserved2[24];
#else
        char Reserved2[20];
#endif
    } Reserved;
} HSTRING_HEADER;

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

extern "C" _Check_return_
    HRESULT
        WINAPI
        RoGetActivationFactory(
            _In_ HSTRING activatableClassId,
            _In_ REFIID iid,
            _COM_Outptr_ void **factory);
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
WindowsCreateStringReference(
    _In_reads_opt_(length + 1) PCWSTR sourceString,
    UINT32 length,
    _Out_ HSTRING_HEADER *hstringHeader,
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
        virtual HRESULT STDMETHODCALLTYPE Invoke(operation * asyncInfo, AsyncStatus status) = 0; \
    };                                                                                           \
    MIDL_INTERFACE(operationid)                                                                  \
    operation:                                                                                   \
public                                                                                           \
    IInspectable                                                                                 \
    {                                                                                            \
    public:                                                                                      \
        virtual HRESULT STDMETHODCALLTYPE put_Completed(handler * handler) = 0;                  \
        virtual HRESULT STDMETHODCALLTYPE get_Completed(handler * *handler) = 0;                 \
        virtual HRESULT STDMETHODCALLTYPE GetResults(resulttype * *results) = 0;                 \
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
//////////////////////////////////OCR
//////////////////////////////////Capture
MIDL_INTERFACE("0bf4a146-13c1-4694-bee3-7abf15eaf586")
IDirect3DSurface : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_Description() = 0;
};
struct __declspec(uuid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1"))
IDirect3DDxgiInterfaceAccess : public IUnknown
{
    IFACEMETHOD(GetInterface)(REFIID iid, _COM_Outptr_ void **p) = 0;
};
MIDL_INTERFACE("814e42a9-f70f-4ad7-939b-fddcc6eb880d")
IGraphicsCaptureSession : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE StartCapture(void) = 0;
};
MIDL_INTERFACE("79c3f95b-31f7-4ec2-a464-632ef5d30760")
IGraphicsCaptureItem : public IInspectable{};
struct __FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable;

MIDL_INTERFACE("fa50c623-38da-4b32-acf3-fa9734ad800e")
IDirect3D11CaptureFrame : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_Surface(
        IDirect3DSurface * *value) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_SystemRelativeTime() = 0;
    virtual HRESULT STDMETHODCALLTYPE get_ContentSize() = 0;
};
MIDL_INTERFACE("24eb6d22-1975-422e-82e7-780dbd8ddf24")
IDirect3D11CaptureFramePool : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE Recreate() = 0;
    virtual HRESULT STDMETHODCALLTYPE TryGetNextFrame(IDirect3D11CaptureFrame * *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE add_FrameArrived(
        __FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable * handler,
        EventRegistrationToken * token) = 0;
    virtual HRESULT STDMETHODCALLTYPE remove_FrameArrived() = 0;
    virtual HRESULT STDMETHODCALLTYPE CreateCaptureSession(
        IGraphicsCaptureItem * item,
        IGraphicsCaptureSession * *result) = 0;
    virtual HRESULT STDMETHODCALLTYPE get_DispatcherQueue() = 0;
};

MIDL_INTERFACE("51a947f7-79cf-5a3e-a3a5-1289cfa6dfe8")
__FITypedEventHandler_2_Windows__CGraphics__CCapture__CDirect3D11CaptureFramePool_IInspectable : IUnknown
{
    virtual HRESULT STDMETHODCALLTYPE Invoke(_In_ IDirect3D11CaptureFramePool * sender, _In_ IInspectable * args) = 0;
};
MIDL_INTERFACE("a37624ab-8d5f-4650-9d3e-9eae3d9bc670")
IDirect3DDevice : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE Trim(void) = 0;
};
enum DirectXPixelFormat : int
{
    DirectXPixelFormat_Unknown = 0,
    DirectXPixelFormat_R32G32B32A32Typeless = 1,
    DirectXPixelFormat_R32G32B32A32Float = 2,
    DirectXPixelFormat_R32G32B32A32UInt = 3,
    DirectXPixelFormat_R32G32B32A32Int = 4,
    DirectXPixelFormat_R32G32B32Typeless = 5,
    DirectXPixelFormat_R32G32B32Float = 6,
    DirectXPixelFormat_R32G32B32UInt = 7,
    DirectXPixelFormat_R32G32B32Int = 8,
    DirectXPixelFormat_R16G16B16A16Typeless = 9,
    DirectXPixelFormat_R16G16B16A16Float = 10,
    DirectXPixelFormat_R16G16B16A16UIntNormalized = 11,
    DirectXPixelFormat_R16G16B16A16UInt = 12,
    DirectXPixelFormat_R16G16B16A16IntNormalized = 13,
    DirectXPixelFormat_R16G16B16A16Int = 14,
    DirectXPixelFormat_R32G32Typeless = 15,
    DirectXPixelFormat_R32G32Float = 16,
    DirectXPixelFormat_R32G32UInt = 17,
    DirectXPixelFormat_R32G32Int = 18,
    DirectXPixelFormat_R32G8X24Typeless = 19,
    DirectXPixelFormat_D32FloatS8X24UInt = 20,
    DirectXPixelFormat_R32FloatX8X24Typeless = 21,
    DirectXPixelFormat_X32TypelessG8X24UInt = 22,
    DirectXPixelFormat_R10G10B10A2Typeless = 23,
    DirectXPixelFormat_R10G10B10A2UIntNormalized = 24,
    DirectXPixelFormat_R10G10B10A2UInt = 25,
    DirectXPixelFormat_R11G11B10Float = 26,
    DirectXPixelFormat_R8G8B8A8Typeless = 27,
    DirectXPixelFormat_R8G8B8A8UIntNormalized = 28,
    DirectXPixelFormat_R8G8B8A8UIntNormalizedSrgb = 29,
    DirectXPixelFormat_R8G8B8A8UInt = 30,
    DirectXPixelFormat_R8G8B8A8IntNormalized = 31,
    DirectXPixelFormat_R8G8B8A8Int = 32,
    DirectXPixelFormat_R16G16Typeless = 33,
    DirectXPixelFormat_R16G16Float = 34,
    DirectXPixelFormat_R16G16UIntNormalized = 35,
    DirectXPixelFormat_R16G16UInt = 36,
    DirectXPixelFormat_R16G16IntNormalized = 37,
    DirectXPixelFormat_R16G16Int = 38,
    DirectXPixelFormat_R32Typeless = 39,
    DirectXPixelFormat_D32Float = 40,
    DirectXPixelFormat_R32Float = 41,
    DirectXPixelFormat_R32UInt = 42,
    DirectXPixelFormat_R32Int = 43,
    DirectXPixelFormat_R24G8Typeless = 44,
    DirectXPixelFormat_D24UIntNormalizedS8UInt = 45,
    DirectXPixelFormat_R24UIntNormalizedX8Typeless = 46,
    DirectXPixelFormat_X24TypelessG8UInt = 47,
    DirectXPixelFormat_R8G8Typeless = 48,
    DirectXPixelFormat_R8G8UIntNormalized = 49,
    DirectXPixelFormat_R8G8UInt = 50,
    DirectXPixelFormat_R8G8IntNormalized = 51,
    DirectXPixelFormat_R8G8Int = 52,
    DirectXPixelFormat_R16Typeless = 53,
    DirectXPixelFormat_R16Float = 54,
    DirectXPixelFormat_D16UIntNormalized = 55,
    DirectXPixelFormat_R16UIntNormalized = 56,
    DirectXPixelFormat_R16UInt = 57,
    DirectXPixelFormat_R16IntNormalized = 58,
    DirectXPixelFormat_R16Int = 59,
    DirectXPixelFormat_R8Typeless = 60,
    DirectXPixelFormat_R8UIntNormalized = 61,
    DirectXPixelFormat_R8UInt = 62,
    DirectXPixelFormat_R8IntNormalized = 63,
    DirectXPixelFormat_R8Int = 64,
    DirectXPixelFormat_A8UIntNormalized = 65,
    DirectXPixelFormat_R1UIntNormalized = 66,
    DirectXPixelFormat_R9G9B9E5SharedExponent = 67,
    DirectXPixelFormat_R8G8B8G8UIntNormalized = 68,
    DirectXPixelFormat_G8R8G8B8UIntNormalized = 69,
    DirectXPixelFormat_BC1Typeless = 70,
    DirectXPixelFormat_BC1UIntNormalized = 71,
    DirectXPixelFormat_BC1UIntNormalizedSrgb = 72,
    DirectXPixelFormat_BC2Typeless = 73,
    DirectXPixelFormat_BC2UIntNormalized = 74,
    DirectXPixelFormat_BC2UIntNormalizedSrgb = 75,
    DirectXPixelFormat_BC3Typeless = 76,
    DirectXPixelFormat_BC3UIntNormalized = 77,
    DirectXPixelFormat_BC3UIntNormalizedSrgb = 78,
    DirectXPixelFormat_BC4Typeless = 79,
    DirectXPixelFormat_BC4UIntNormalized = 80,
    DirectXPixelFormat_BC4IntNormalized = 81,
    DirectXPixelFormat_BC5Typeless = 82,
    DirectXPixelFormat_BC5UIntNormalized = 83,
    DirectXPixelFormat_BC5IntNormalized = 84,
    DirectXPixelFormat_B5G6R5UIntNormalized = 85,
    DirectXPixelFormat_B5G5R5A1UIntNormalized = 86,
    DirectXPixelFormat_B8G8R8A8UIntNormalized = 87,
    DirectXPixelFormat_B8G8R8X8UIntNormalized = 88,
    DirectXPixelFormat_R10G10B10XRBiasA2UIntNormalized = 89,
    DirectXPixelFormat_B8G8R8A8Typeless = 90,
    DirectXPixelFormat_B8G8R8A8UIntNormalizedSrgb = 91,
    DirectXPixelFormat_B8G8R8X8Typeless = 92,
    DirectXPixelFormat_B8G8R8X8UIntNormalizedSrgb = 93,
    DirectXPixelFormat_BC6HTypeless = 94,
    DirectXPixelFormat_BC6H16UnsignedFloat = 95,
    DirectXPixelFormat_BC6H16Float = 96,
    DirectXPixelFormat_BC7Typeless = 97,
    DirectXPixelFormat_BC7UIntNormalized = 98,
    DirectXPixelFormat_BC7UIntNormalizedSrgb = 99,
    DirectXPixelFormat_Ayuv = 100,
    DirectXPixelFormat_Y410 = 101,
    DirectXPixelFormat_Y416 = 102,
    DirectXPixelFormat_NV12 = 103,
    DirectXPixelFormat_P010 = 104,
    DirectXPixelFormat_P016 = 105,
    DirectXPixelFormat_Opaque420 = 106,
    DirectXPixelFormat_Yuy2 = 107,
    DirectXPixelFormat_Y210 = 108,
    DirectXPixelFormat_Y216 = 109,
    DirectXPixelFormat_NV11 = 110,
    DirectXPixelFormat_AI44 = 111,
    DirectXPixelFormat_IA44 = 112,
    DirectXPixelFormat_P8 = 113,
    DirectXPixelFormat_A8P8 = 114,
    DirectXPixelFormat_B4G4R4A4UIntNormalized = 115,
    DirectXPixelFormat_P208 = 130,
    DirectXPixelFormat_V208 = 131,
    DirectXPixelFormat_V408 = 132,
#if WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
    DirectXPixelFormat_SamplerFeedbackMinMipOpaque = 189,
#endif // WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
#if WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
    DirectXPixelFormat_SamplerFeedbackMipRegionUsedOpaque = 190,
#endif // WINDOWS_FOUNDATION_UNIVERSALAPICONTRACT_VERSION >= 0xa0000
};
struct SizeInt32
{
    INT32 Width;
    INT32 Height;
};
MIDL_INTERFACE("7784056a-67aa-4d53-ae54-1088d5a8ca21")
IDirect3D11CaptureFramePoolStatics : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE Create(
        IDirect3DDevice * device,
        DirectXPixelFormat pixelFormat,
        INT32 numberOfBuffers,
        SizeInt32 size,
        IDirect3D11CaptureFramePool * *result) = 0;
};
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Capture_Direct3D11CaptureFramePool[] = L"Windows.Graphics.Capture.Direct3D11CaptureFramePool";
DECLARE_INTERFACE_IID_(IGraphicsCaptureItemInterop, IUnknown, "3628E81B-3CAC-4C60-B7F4-23CE0E0C3356")
{
    IFACEMETHOD(CreateForWindow)(
        HWND window,
        REFIID riid,
        _COM_Outptr_ void **result) PURE;

    IFACEMETHOD(CreateForMonitor)(
        HMONITOR monitor,
        REFIID riid,
        _COM_Outptr_ void **result) PURE;
};
extern const __declspec(selectany) _Null_terminated_ WCHAR RuntimeClass_Windows_Graphics_Capture_GraphicsCaptureItem[] = L"Windows.Graphics.Capture.GraphicsCaptureItem";
MIDL_INTERFACE("2c39ae40-7d2e-5044-804e-8b6799d4cf9e")
IGraphicsCaptureSession2 : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE get_IsCursorCaptureEnabled(
        boolean * value) = 0;
    virtual HRESULT STDMETHODCALLTYPE put_IsCursorCaptureEnabled(
        boolean value) = 0;
};
MIDL_INTERFACE("30d5a829-7fa4-4026-83bb-d75bae4ea99e")
IClosable : public IInspectable
{
public:
    virtual HRESULT STDMETHODCALLTYPE Close(void) = 0;
};

STDAPI CreateDirect3D11DeviceFromDXGIDevice(
    _In_ IDXGIDevice *dxgiDevice,
    _COM_Outptr_ IInspectable **graphicsDevice);
//////////////////////////////////Capture