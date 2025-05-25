
typedef enum DXGI_GPU_PREFERENCE
{
    DXGI_GPU_PREFERENCE_UNSPECIFIED = 0,
    DXGI_GPU_PREFERENCE_MINIMUM_POWER = (DXGI_GPU_PREFERENCE_UNSPECIFIED + 1),
    DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE = (DXGI_GPU_PREFERENCE_MINIMUM_POWER + 1)
} DXGI_GPU_PREFERENCE;
typedef enum DXGI_FEATURE
{
    DXGI_FEATURE_PRESENT_ALLOW_TEARING = 0
} DXGI_FEATURE;

typedef struct DXGI_PRESENT_PARAMETERS
{
    UINT DirtyRectsCount;
    /* [annotation] */
    _Field_size_full_opt_(DirtyRectsCount) RECT *pDirtyRects;
    RECT *pScrollRect;
    POINT *pScrollOffset;
} DXGI_PRESENT_PARAMETERS;

#ifndef D3DCOLORVALUE_DEFINED
typedef struct _D3DCOLORVALUE
{
    float r;
    float g;
    float b;
    float a;
} D3DCOLORVALUE;

#define D3DCOLORVALUE_DEFINED
#endif

typedef D3DCOLORVALUE DXGI_RGBA;
typedef enum DXGI_ALPHA_MODE
{
    DXGI_ALPHA_MODE_UNSPECIFIED = 0,
    DXGI_ALPHA_MODE_PREMULTIPLIED = 1,
    DXGI_ALPHA_MODE_STRAIGHT = 2,
    DXGI_ALPHA_MODE_IGNORE = 3,
    DXGI_ALPHA_MODE_FORCE_DWORD = 0xffffffff
} DXGI_ALPHA_MODE;
typedef enum DXGI_SCALING
{
    DXGI_SCALING_STRETCH = 0,
    DXGI_SCALING_NONE = 1,
    DXGI_SCALING_ASPECT_RATIO_STRETCH = 2
} DXGI_SCALING;
typedef struct DXGI_SWAP_CHAIN_DESC1
{
    UINT Width;
    UINT Height;
    DXGI_FORMAT Format;
    BOOL Stereo;
    DXGI_SAMPLE_DESC SampleDesc;
    DXGI_USAGE BufferUsage;
    UINT BufferCount;
    DXGI_SCALING Scaling;
    DXGI_SWAP_EFFECT SwapEffect;
    DXGI_ALPHA_MODE AlphaMode;
    UINT Flags;
} DXGI_SWAP_CHAIN_DESC1;
typedef struct DXGI_SWAP_CHAIN_FULLSCREEN_DESC
{
    DXGI_RATIONAL RefreshRate;
    DXGI_MODE_SCANLINE_ORDER ScanlineOrdering;
    DXGI_MODE_SCALING Scaling;
    BOOL Windowed;
} DXGI_SWAP_CHAIN_FULLSCREEN_DESC;
MIDL_INTERFACE("790a45f7-0d42-4876-983a-0a55cfe6f4aa")
IDXGISwapChain1 : public IDXGISwapChain
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetDesc1(
        /* [annotation][out] */
        _Out_ DXGI_SWAP_CHAIN_DESC1 * pDesc) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetFullscreenDesc(
        /* [annotation][out] */
        _Out_ DXGI_SWAP_CHAIN_FULLSCREEN_DESC * pDesc) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetHwnd(
        /* [annotation][out] */
        _Out_ HWND * pHwnd) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetCoreWindow(
        /* [annotation][in] */
        _In_ REFIID refiid,
        /* [annotation][out] */
        _COM_Outptr_ void **ppUnk) = 0;

    virtual HRESULT STDMETHODCALLTYPE Present1(
        /* [in] */ UINT SyncInterval,
        /* [in] */ UINT PresentFlags,
        /* [annotation][in] */
        _In_ const DXGI_PRESENT_PARAMETERS *pPresentParameters) = 0;

    virtual BOOL STDMETHODCALLTYPE IsTemporaryMonoSupported(void) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetRestrictToOutput(
        /* [annotation][out] */
        _Out_ IDXGIOutput * *ppRestrictToOutput) = 0;

    virtual HRESULT STDMETHODCALLTYPE SetBackgroundColor(
        /* [annotation][in] */
        _In_ const DXGI_RGBA *pColor) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetBackgroundColor(
        /* [annotation][out] */
        _Out_ DXGI_RGBA * pColor) = 0;

    virtual HRESULT STDMETHODCALLTYPE SetRotation(
        /* [annotation][in] */
        _In_ DXGI_MODE_ROTATION Rotation) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetRotation(
        /* [annotation][out] */
        _Out_ DXGI_MODE_ROTATION * pRotation) = 0;
};
MIDL_INTERFACE("50c83a1c-e072-4c48-87b0-3630fa36a6d0")
IDXGIFactory2 : public IDXGIFactory1
{
public:
    virtual BOOL STDMETHODCALLTYPE IsWindowedStereoEnabled(void) = 0;

    virtual HRESULT STDMETHODCALLTYPE CreateSwapChainForHwnd(
        /* [annotation][in] */
        _In_ IUnknown * pDevice,
        /* [annotation][in] */
        _In_ HWND hWnd,
        /* [annotation][in] */
        _In_ const DXGI_SWAP_CHAIN_DESC1 *pDesc,
        /* [annotation][in] */
        _In_opt_ const DXGI_SWAP_CHAIN_FULLSCREEN_DESC *pFullscreenDesc,
        /* [annotation][in] */
        _In_opt_ IDXGIOutput *pRestrictToOutput,
        /* [annotation][out] */
        _COM_Outptr_ IDXGISwapChain1 **ppSwapChain) = 0;

    virtual HRESULT STDMETHODCALLTYPE CreateSwapChainForCoreWindow(
        /* [annotation][in] */
        _In_ IUnknown * pDevice,
        /* [annotation][in] */
        _In_ IUnknown * pWindow,
        /* [annotation][in] */
        _In_ const DXGI_SWAP_CHAIN_DESC1 *pDesc,
        /* [annotation][in] */
        _In_opt_ IDXGIOutput *pRestrictToOutput,
        /* [annotation][out] */
        _COM_Outptr_ IDXGISwapChain1 **ppSwapChain) = 0;

    virtual HRESULT STDMETHODCALLTYPE GetSharedResourceAdapterLuid(
        /* [annotation] */
        _In_ HANDLE hResource,
        /* [annotation] */
        _Out_ LUID * pLuid) = 0;

    virtual HRESULT STDMETHODCALLTYPE RegisterStereoStatusWindow(
        /* [annotation][in] */
        _In_ HWND WindowHandle,
        /* [annotation][in] */
        _In_ UINT wMsg,
        /* [annotation][out] */
        _Out_ DWORD * pdwCookie) = 0;

    virtual HRESULT STDMETHODCALLTYPE RegisterStereoStatusEvent(
        /* [annotation][in] */
        _In_ HANDLE hEvent,
        /* [annotation][out] */
        _Out_ DWORD * pdwCookie) = 0;

    virtual void STDMETHODCALLTYPE UnregisterStereoStatus(
        /* [annotation][in] */
        _In_ DWORD dwCookie) = 0;

    virtual HRESULT STDMETHODCALLTYPE RegisterOcclusionStatusWindow(
        /* [annotation][in] */
        _In_ HWND WindowHandle,
        /* [annotation][in] */
        _In_ UINT wMsg,
        /* [annotation][out] */
        _Out_ DWORD * pdwCookie) = 0;

    virtual HRESULT STDMETHODCALLTYPE RegisterOcclusionStatusEvent(
        /* [annotation][in] */
        _In_ HANDLE hEvent,
        /* [annotation][out] */
        _Out_ DWORD * pdwCookie) = 0;

    virtual void STDMETHODCALLTYPE UnregisterOcclusionStatus(
        /* [annotation][in] */
        _In_ DWORD dwCookie) = 0;

    virtual HRESULT STDMETHODCALLTYPE CreateSwapChainForComposition(
        /* [annotation][in] */
        _In_ IUnknown * pDevice,
        /* [annotation][in] */
        _In_ const DXGI_SWAP_CHAIN_DESC1 *pDesc,
        /* [annotation][in] */
        _In_opt_ IDXGIOutput *pRestrictToOutput,
        /* [annotation][out] */
        _COM_Outptr_ IDXGISwapChain1 **ppSwapChain) = 0;
};

MIDL_INTERFACE("25483823-cd46-4c7d-86ca-47aa95b837bd")
IDXGIFactory3 : public IDXGIFactory2
{
public:
    virtual UINT STDMETHODCALLTYPE GetCreationFlags(void) = 0;
};
MIDL_INTERFACE("1bc6ea02-ef36-464f-bf0c-21ca39e5168a")
IDXGIFactory4 : public IDXGIFactory3
{
public:
    virtual HRESULT STDMETHODCALLTYPE EnumAdapterByLuid(
        /* [annotation] */
        _In_ LUID AdapterLuid,
        /* [annotation] */
        _In_ REFIID riid,
        /* [annotation] */
        _COM_Outptr_ void **ppvAdapter) = 0;

    virtual HRESULT STDMETHODCALLTYPE EnumWarpAdapter(
        /* [annotation] */
        _In_ REFIID riid,
        /* [annotation] */
        _COM_Outptr_ void **ppvAdapter) = 0;
};

MIDL_INTERFACE("7632e1f5-ee65-4dca-87fd-84cd75f8838d")
IDXGIFactory5 : public IDXGIFactory4
{
public:
    virtual HRESULT STDMETHODCALLTYPE CheckFeatureSupport(
        DXGI_FEATURE Feature,
        /* [annotation] */
        _Inout_updates_bytes_(FeatureSupportDataSize) void *pFeatureSupportData,
        UINT FeatureSupportDataSize) = 0;
};

MIDL_INTERFACE("c1b6694f-ff09-44a9-b03c-77900a0a1d17")
IDXGIFactory6 : public IDXGIFactory5
{
public:
    virtual HRESULT STDMETHODCALLTYPE EnumAdapterByGpuPreference(
        /* [annotation] */
        _In_ UINT Adapter,
        /* [annotation] */
        _In_ DXGI_GPU_PREFERENCE GpuPreference,
        /* [annotation] */
        _In_ REFIID riid,
        /* [annotation] */
        _COM_Outptr_ void **ppvAdapter) = 0;
};
MIDL_INTERFACE("a4966eed-76db-44da-84c1-ee9a7afb20a8")
IDXGIFactory7 : public IDXGIFactory6
{
public:
    virtual HRESULT STDMETHODCALLTYPE RegisterAdaptersChangedEvent(
        /* [annotation][in] */
        _In_ HANDLE hEvent,
        /* [annotation][out] */
        _Out_ DWORD * pdwCookie) = 0;

    virtual HRESULT STDMETHODCALLTYPE UnregisterAdaptersChangedEvent(
        /* [annotation][in] */
        _In_ DWORD dwCookie) = 0;
};

extern "C"
HRESULT WINAPI CreateDXGIFactory2(UINT Flags, REFIID riid, _COM_Outptr_ void **ppFactory);
#define DXGI_ADAPTER_FLAG_SOFTWARE 2