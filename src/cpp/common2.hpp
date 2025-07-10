
#define CHECK_FAILURE(x) \
    if (FAILED((x)))     \
        return (HRESULT)x;
#define CHECK_FAILURE_NORET(x) \
    if (FAILED((x)))           \
        return;
#define CHECK_FAILURE_CONTINUE(x) \
    if (FAILED((x)))              \
        continue;

struct CO_INIT
{
    HRESULT hr;
    CO_INIT()
    {
        hr = ::CoInitialize(NULL);
    }
    operator HRESULT()
    {
        return hr;
    }
    ~CO_INIT()
    {
        if (SUCCEEDED(hr))
            CoUninitialize();
    }
};

template <typename... Bases>
class ComImpl : public Bases...
{
private:
    ULONG m_ref_count{0};
    template <typename First, typename... Rest>
    void *get_interface(REFIID riid)
    {
        if (IsEqualGUID(riid, __uuidof(First)))
            return static_cast<First *>(this);
        if constexpr (sizeof...(Rest) > 0)
        {
            return get_interface<Rest...>(riid);
        }
        else if (IsEqualGUID(riid, __uuidof(IUnknown)))
            return this;
        return nullptr;
    }

public:
    void operator delete(void *ptr) noexcept
    {
        CoTaskMemFree(ptr);
    }
    void *operator new(size_t size)
    {
        return CoTaskMemAlloc(size);
    }
    ULONG STDMETHODCALLTYPE AddRef() { return InterlockedIncrement(&m_ref_count); }
    ULONG STDMETHODCALLTYPE Release()
    {
        ULONG tmp = InterlockedDecrement(&m_ref_count);
        if (!tmp)
        {
            delete this;
        }
        return tmp;
    }
    HRESULT STDMETHODCALLTYPE QueryInterface(REFIID riid, void **ppvObj)
    {
        if (ppvObj == nullptr)
            return E_POINTER;
        *ppvObj = nullptr;
        void *pInterface = get_interface<Bases...>(riid);
        if (!pInterface)
            return E_NOINTERFACE;
        *ppvObj = pInterface;
        AddRef();
        return S_OK;
    }
    virtual ~ComImpl() = default;
};

#ifdef WINXP
#define COWAIT_INPUTAVAILABLE 4
#define COWAIT_DISPATCH_CALLS 8
#define COWAIT_DISPATCH_WINDOW_MESSAGES 0x10

extern "C" WINUSERAPI
    UINT
        WINAPI
        GetDpiForWindow(
            _In_ HWND hwnd);
#endif

struct CoAsyncTaskWaiter
{
    CEvent event;
    CoAsyncTaskWaiter()
    {
        event.Create(nullptr, false, false, nullptr);
    }
    void Set()
    {
        SetEvent(event);
    }
    void Wait()
    {
        DWORD handleIndex = 0;
        CoWaitForMultipleHandles(COWAIT_DISPATCH_WINDOW_MESSAGES | COWAIT_DISPATCH_CALLS | COWAIT_INPUTAVAILABLE, INFINITE, 1, &event.m_h, &handleIndex);
    }
};

struct AutoFreeString
{
    LPWSTR ptr;
    AutoFreeString(LPWSTR ptr) : ptr(ptr)
    {
    }
    ~AutoFreeString()
    {
        delete[] ptr;
    }
    operator LPWSTR()
    {
        return ptr;
    }
};

template <typename T, auto initor, auto clearer>
struct AutoVariantBase
{
    T var;
    operator T()
    {
        return var;
    }
    T *operator&()
    {
        return &var;
    }
    T *operator->()
    {
        return &var;
    }
    AutoVariantBase()
    {
        initor(&var);
    }
    ~AutoVariantBase()
    {
        clearer(&var);
    }
};
using AutoVariant = AutoVariantBase<VARIANT, VariantInit, VariantClear>;
using AutoPropVariant = AutoVariantBase<PROPVARIANT, PropVariantInit, PropVariantClear>;