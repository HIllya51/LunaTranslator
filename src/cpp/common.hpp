
inline SECURITY_ATTRIBUTES allAccess = std::invoke([] // allows non-admin processes to access kernel objects made by admin processes
                                                   {
	static SECURITY_DESCRIPTOR sd = {};
	InitializeSecurityDescriptor(&sd, SECURITY_DESCRIPTOR_REVISION);
	SetSecurityDescriptorDacl(&sd, TRUE, NULL, FALSE);
	return SECURITY_ATTRIBUTES{ sizeof(SECURITY_ATTRIBUTES), &sd, FALSE }; });

inline std::wstring StringToWideString(const std::string &text, UINT encoding = CP_UTF8)
{
    std::vector<wchar_t> buffer(text.size() + 1);
    int length = MultiByteToWideChar(encoding, 0, text.c_str(), text.size() + 1, buffer.data(), buffer.size());
    return std::wstring(buffer.data(), length - 1);
}
inline std::string WideStringToString(const std::wstring &text, UINT cp = CP_UTF8)
{
    std::vector<char> buffer((text.size() + 1) * 4);

    WideCharToMultiByte(cp, 0, text.c_str(), -1, buffer.data(), buffer.size(), nullptr, nullptr);
    return buffer.data();
}

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
    virtual ~ComImpl() {}
};

#ifdef WINXP
#define COWAIT_INPUTAVAILABLE 4
#define COWAIT_DISPATCH_CALLS 8
#define COWAIT_DISPATCH_WINDOW_MESSAGES 0x10
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