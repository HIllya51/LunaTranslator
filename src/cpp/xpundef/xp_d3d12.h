
MIDL_INTERFACE("c4fec28f-7966-4e95-9f94-f431cb56c3b8")
ID3D12Object : public IUnknown
{
public:
    virtual HRESULT STDMETHODCALLTYPE GetPrivateData(
        _In_ REFGUID guid,
        _Inout_ UINT * pDataSize,
        _Out_writes_bytes_opt_(*pDataSize) void *pData) = 0;

    virtual HRESULT STDMETHODCALLTYPE SetPrivateData(
        _In_ REFGUID guid,
        _In_ UINT DataSize,
        _In_reads_bytes_opt_(DataSize) const void *pData) = 0;

    virtual HRESULT STDMETHODCALLTYPE SetPrivateDataInterface(
        _In_ REFGUID guid,
        _In_opt_ const IUnknown *pData) = 0;

    virtual HRESULT STDMETHODCALLTYPE SetName(
        _In_z_ LPCWSTR Name) = 0;
};
MIDL_INTERFACE("189819f1-1db6-4b57-be54-1821339b85f7")
ID3D12Device : public ID3D12Object{
    public :
};
extern "C"
HRESULT WINAPI
D3D12CreateDevice(
    _In_opt_ IUnknown *pAdapter,
    D3D_FEATURE_LEVEL MinimumFeatureLevel,
    _In_ REFIID riid, // Expected: ID3D12Device
    _COM_Outptr_opt_ void **ppDevice);
