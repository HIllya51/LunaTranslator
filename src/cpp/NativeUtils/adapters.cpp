// Magpie\AdaptersService.cpp
#ifndef WINXP
#include <dxgi1_6.h>
#else
#include "../xpundef/xp_dxgi.h"
#endif
struct AdapterInfo
{
    uint32_t idx = 0;
    uint32_t vendorId = 0;
    uint32_t deviceId = 0;
    std::wstring description;
};

class AdaptersService
{
public:
    static AdaptersService &Get() noexcept
    {
        static AdaptersService instance;
        return instance;
    }

    AdaptersService(const AdaptersService &) = delete;
    AdaptersService(AdaptersService &&) = delete;

    bool Initialize(void (*callback)()) noexcept;

    void Uninitialize() noexcept;

    void StartMonitor() noexcept;

    const std::vector<AdapterInfo> &AdapterInfos() const noexcept
    {
        return _adapterInfos;
    }

    // Event<> AdaptersChanged;
    void (*AdaptersChanged)();

private:
    AdaptersService() = default;

    bool _GatherAdapterInfos(
        CComPtr<IDXGIFactory7> &dxgiFactory,
        CEvent &adaptersChangedEvent,
        DWORD &adaptersChangedCookie) noexcept;

    void _MonitorThreadProc() noexcept;

    std::thread _monitorThread;
    std::vector<AdapterInfo> _adapterInfos;
};
struct DirectXHelper
{
    static bool IsWARP(const DXGI_ADAPTER_DESC1 &desc) noexcept
    {
        // 不要检查 DXGI_ADAPTER_FLAG_SOFTWARE 标志，如果系统没有安装任何显卡，WARP 没有这个标志。
        // 这两个值来自 https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi#new-info-about-enumerating-adapters-for-windows-8
        return desc.VendorId == 0x1414 && desc.DeviceId == 0x8c;
    }
};
bool AdaptersService::Initialize(void (*callback)()) noexcept
{
    AdaptersChanged = callback;
    CComPtr<IDXGIFactory7> dxgiFactory;

    HRESULT hr = CreateDXGIFactory1(IID_PPV_ARGS(&dxgiFactory));
    if (FAILED(hr))
    {
        return false;
    }

    CComPtr<IDXGIAdapter1> curAdapter;
    for (UINT adapterIdx = 0;
         SUCCEEDED(dxgiFactory->EnumAdapters1(adapterIdx, &curAdapter));
         ++adapterIdx)
    {
        DXGI_ADAPTER_DESC1 desc;
        hr = curAdapter->GetDesc1(&desc);
        if (FAILED(hr) || DirectXHelper::IsWARP(desc))
        {
            continue;
        }

        // 初始化时不检查是否支持 FL11，有些设备上 D3D11CreateDevice 相当慢
        _adapterInfos.push_back({adapterIdx, desc.VendorId, desc.DeviceId, desc.Description});
    }

    AdaptersChanged();

    return true;
}
namespace wil
{
    inline bool handle_wait(HANDLE hEvent, DWORD dwMilliseconds = INFINITE, BOOL bAlertable = FALSE) // WI_NOEXCEPT
    {
        DWORD status = ::WaitForSingleObjectEx(hEvent, dwMilliseconds, bAlertable);
        // __FAIL_FAST_ASSERT__((status == WAIT_TIMEOUT) || (status == WAIT_OBJECT_0) || (bAlertable && (status == WAIT_IO_COMPLETION)));
        return (status == WAIT_OBJECT_0);
    }
}
void AdaptersService::Uninitialize() noexcept
{
    if (!_monitorThread.joinable())
    {
        return;
    }

    const HANDLE hToastThread = _monitorThread.native_handle();
    if (!wil::handle_wait(hToastThread, 0))
    {
        const DWORD threadId = GetThreadId(hToastThread);

        // 持续尝试直到 _monitorThread 创建了消息队列
        while (!PostThreadMessage(threadId, WM_QUIT, 0, 0))
        {
            if (wil::handle_wait(hToastThread, 1))
            {
                break;
            }
        }
    }

    _monitorThread.join();
}
void AdaptersService::StartMonitor() noexcept
{
    _monitorThread = std::thread(std::bind(&AdaptersService::_MonitorThreadProc, this));
}

struct TPContext
{
    std::function<void(uint32_t)> func;
    std::atomic<uint32_t> id;
};

static void CALLBACK TPCallback(PTP_CALLBACK_INSTANCE, PVOID context, PTP_WORK)
{
    TPContext *ctxt = (TPContext *)context;
    const uint32_t id = ctxt->id.fetch_add(1, std::memory_order_relaxed) + 1;
    ctxt->func(id);
}
struct Win32Helper
{
    static void RunParallel(std::function<void(uint32_t)> func, uint32_t times) noexcept;
};
void Win32Helper::RunParallel(std::function<void(uint32_t)> func, uint32_t times) noexcept
{
#ifdef _DEBUG
    // 为了便于调试，DEBUG 模式下不使用线程池
    for (UINT i = 0; i < times; ++i)
    {
        func(i);
    }
#else
    if (times == 0)
    {
        return;
    }

    if (times == 1)
    {
        return func(0);
    }

    TPContext ctxt = {func, 0};
    PTP_WORK work = CreateThreadpoolWork(TPCallback, &ctxt, nullptr);
    if (work)
    {
        // 在线程池中执行 times - 1 次
        for (uint32_t i = 1; i < times; ++i)
        {
            SubmitThreadpoolWork(work);
        }

        func(0);

        WaitForThreadpoolWorkCallbacks(work, FALSE);
        CloseThreadpoolWork(work);
    }
    else
    {

        // 回退到单线程
        for (uint32_t i = 0; i < times; ++i)
        {
            func(i);
        }
    }
#endif // _DEBUG
}
bool AdaptersService::_GatherAdapterInfos(
    CComPtr<IDXGIFactory7> &dxgiFactory,
    CEvent &adaptersChangedEvent,
    DWORD &adaptersChangedCookie) noexcept
{
    // 显卡变化后需要重新创建 DXGI 工厂
    HRESULT hr = CreateDXGIFactory1(IID_PPV_ARGS(&dxgiFactory));
    if (FAILED(hr))
    {
        return false;
    }

    hr = dxgiFactory->RegisterAdaptersChangedEvent(
        adaptersChangedEvent, &adaptersChangedCookie);
    if (FAILED(hr))
    {
        return false;
    }

    std::vector<AdapterInfo> adapterInfos;
    std::vector<CComPtr<IDXGIAdapter1>> adapters;

    CComPtr<IDXGIAdapter1> curAdapter;
    for (UINT adapterIdx = 0;
         SUCCEEDED(dxgiFactory->EnumAdapters1(adapterIdx, &curAdapter));
         ++adapterIdx)
    {
        DXGI_ADAPTER_DESC1 desc;
        hr = curAdapter->GetDesc1(&desc);
        if (FAILED(hr) || DirectXHelper::IsWARP(desc))
        {
            continue;
        }

        adapterInfos.push_back({adapterIdx, desc.VendorId, desc.DeviceId, desc.Description});

        adapters.push_back(std::move(curAdapter));
    }

    // 删除不支持功能级别 11 的显卡
    std::vector<AdapterInfo> compatibleAdapterInfos;
    std::mutex lock;
    Win32Helper::RunParallel([&](uint32_t i)
                             {
		D3D_FEATURE_LEVEL fl = D3D_FEATURE_LEVEL_11_0;
		if (FAILED(D3D11CreateDevice(adapters[i], D3D_DRIVER_TYPE_UNKNOWN,
			NULL, 0, &fl, 1, D3D11_SDK_VERSION, nullptr, nullptr, nullptr))) {
			std::unique_lock _(lock);
			adapterInfos[i].idx = std::numeric_limits<uint32_t>::max();
		} }, (uint32_t)adapters.size());
    adapterInfos.erase(
        std::remove_if(adapterInfos.begin(), adapterInfos.end(),
                       [](const AdapterInfo &info)
                       {
                           return info.idx == std::numeric_limits<uint32_t>::max();
                       }),
        adapterInfos.end());
    AdaptersChanged();
    return true;
}

void AdaptersService::_MonitorThreadProc() noexcept
{
#ifdef _DEBUG
    SetThreadDescription(GetCurrentThread(), L"AdaptersService 线程");
#endif

    CEvent adaptersChangedEvent;
    CHECK_FAILURE_NORET(adaptersChangedEvent.Create(NULL, FALSE, FALSE, NULL));

    CComPtr<IDXGIFactory7> dxgiFactory;
    DWORD adaptersChangedCookie = 0;
    if (!_GatherAdapterInfos(dxgiFactory, adaptersChangedEvent, adaptersChangedCookie))
    {
        return;
    }

    while (true)
    {
        MSG msg;
        while (PeekMessage(&msg, nullptr, 0, 0, PM_REMOVE))
        {
            if (msg.message == WM_QUIT)
            {
                break;
            }

            TranslateMessage(&msg);
            DispatchMessage(&msg);
        }

        if (msg.message == WM_QUIT)
        {
            break;
        }

        HANDLE hAdaptersChangedEvent = adaptersChangedEvent.m_h;
        if (MsgWaitForMultipleObjectsEx(1, &hAdaptersChangedEvent,
                                        INFINITE, QS_ALLINPUT, MWMO_INPUTAVAILABLE) == WAIT_OBJECT_0)
        {
            // WAIT_OBJECT_0 表示显卡变化
            // WAIT_OBJECT_0 + 1 表示有新消息
            if (!_GatherAdapterInfos(dxgiFactory, adaptersChangedEvent, adaptersChangedCookie))
            {
                break;
            }
        }
    }

    dxgiFactory->UnregisterAdaptersChangedEvent(adaptersChangedCookie);
}
DECLARE_API void AdaptersServiceStartMonitor(void (*callback)())
{
    if (!AdaptersService::Get().Initialize(callback))
    {
        AdaptersService::Get().Uninitialize();
        return;
    }
    AdaptersService::Get().StartMonitor();
}
DECLARE_API void AdaptersServiceUninitialize()
{
    AdaptersService::Get().Uninitialize();
}

DECLARE_API void AdaptersServiceAdapterInfos(void (*callback)(uint32_t, uint32_t, uint32_t, LPCWSTR))
{
    for (auto &&info : AdaptersService::Get().AdapterInfos())
    {
        callback(info.idx, info.vendorId, info.deviceId, info.description.c_str());
    }
}
