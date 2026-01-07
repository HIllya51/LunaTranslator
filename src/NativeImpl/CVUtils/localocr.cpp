#include "dbcrnn.hpp"
#ifndef WINXP
#include <dxgi.h>
#include <dxgi1_6.h>
#include <d3d12.h>
#else
#include "../xpundef/xp_dxgi.h"
#include "../xpundef/xp_d3d12.h"
#endif
#include "shared.hpp"

inline uint64_t GetLuidKey(LUID luid)
{
    return (uint64_t(luid.HighPart) << 32) | luid.LowPart;
}
static std::vector<std::pair<int, DXGI_ADAPTER_DESC1>> get_descs(std::function<bool(IDXGIAdapter1 *, const DXGI_ADAPTER_DESC1 &)> check)
{
    CComPtr<IDXGIFactory4> factory;
    if (FAILED(CreateDXGIFactory2(0, IID_PPV_ARGS(&factory))))
        return {};

    std::vector<std::pair<int, DXGI_ADAPTER_DESC1>> decs;

    CComPtr<IDXGIAdapter1> adapter;
    for (UINT i = 0; SUCCEEDED(factory->EnumAdapters1(i, &adapter)); ++i)
    {
        DXGI_ADAPTER_DESC1 desc;
        CHECK_FAILURE_CONTINUE(adapter->GetDesc1(&desc));
        if (!check(adapter, desc))
            continue;
        std::wstringstream wss;
        wss << i << L"\t" << desc.Description << L"\t" << std::hex << GetLuidKey(desc.AdapterLuid);
        std::wcout << wss.str() << std::endl;
        decs.push_back(std::make_pair(i, desc));
    }
    return decs;
}
static std::optional<DXGI_ADAPTER_DESC1> get_best_gpu()
{
    // 获取最好gpu后，没必要去检查是否符合Flags和D3D_FEATURE_LEVEL_11_0，因为如果最好的设备都不行的话，拉闸算了。
    CComPtr<IDXGIFactory6> factory;
    if (FAILED(CreateDXGIFactory2(0, IID_PPV_ARGS(&factory))))
        return {};
    // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/platform/windows/device_discovery.cc#L344
    CComPtr<IDXGIAdapter1> adapter;
    for (UINT i = 0; SUCCEEDED(factory->EnumAdapterByGpuPreference(
             i, DXGI_GPU_PREFERENCE_HIGH_PERFORMANCE,
             IID_PPV_ARGS(&adapter)));
         ++i)
    {
        DXGI_ADAPTER_DESC1 desc;
        CHECK_FAILURE_CONTINUE(adapter->GetDesc1(&desc));
        std::wstringstream wss;
        wss << desc.Description << L"\t" << std::hex << GetLuidKey(desc.AdapterLuid);
        std::wcout << wss.str() << std::endl;
        return desc;
    }
    return {};
}
int findDeviceId(uint64_t &luid)
{
    if (luid == 0)
    {
        auto desc = get_best_gpu();
        if (!desc)
            return 0;
        luid = GetLuidKey(desc.value().AdapterLuid);
    }
    auto descs = get_descs([](auto *, auto &)
                           { return true; });
    for (auto &&[i, desc] : descs)
    {
        if (luid == GetLuidKey(desc.AdapterLuid))
            return i;
    }
    return 0;
}

DECLARE_API void OcrDetect(OcrLite *pOcrObj, const cv::Mat *mat,
                           Directional mode, void (*cb)(float, float, float, float, float, float, float, float, const char *), void (*cb2)(const char *))
{
    if (!pOcrObj)
        return;

    try
    {
        auto result = pOcrObj->detect(*mat, mode);

        for (auto item : result)
        {
            cb(item.first[0].x, item.first[0].y,
               item.first[1].x, item.first[1].y,
               item.first[2].x, item.first[2].y,
               item.first[3].x, item.first[3].y,
               item.second.c_str());
        }
    }
    catch (std::exception &e)
    {
        cb2(e.what());
    }
}

DECLARE_API void OcrDestroy(OcrLite *pOcrObj)
{
    if (pOcrObj)
        delete pOcrObj;
}

static std::optional<version_t> __QueryVersion(const std::wstring &exe)
{
    auto _ = QueryVersion(exe);
    if (_)
    {
        auto &&[_1, _2, _3, _4] = _.value();
        std::wcout << _1 << L"," << _2 << L"," << _3 << L"," << _4 << L"\t" << exe << L"\n";
    }
    return _;
}
static bool isvcrtlessthan1440()
{
    // 实测之和msvcp140有关，低版本的vcruntime140.dll不影响。
    // 但稳妥起见，都检查一下。
    auto checkversion = [](LPCWSTR dll)
    {
        auto hdll = GetModuleHandle(dll);
        if (!hdll)
            return false;
        WCHAR path[MAX_PATH];
        GetModuleFileNameW(hdll, path, MAX_PATH);
        return __QueryVersion(path) < std::make_tuple(14u, 40u, 0u, 0u);
    };
    return checkversion(L"msvcp140.dll") || checkversion(L"vcruntime140.dll");
}
static std::optional<version_t> checkfileversion(const std::optional<std::wstring> &exe)
{
    // 如果vcrt版本<14.40，那么最多只能加载onnxruntime到v1.20.1版本，v1.21.0开始会不兼容。
    // https://github.com/microsoft/onnxruntime/releases/tag/v1.21.0
    // All the prebuilt Windows packages now require VC++ Runtime version >= 14.40(instead of 14.38). If your VC++ runtime version is lower than that, you may see a crash when ONNX Runtime was initializing. See https://github.com/microsoft/STL/wiki/Changelog#vs-2022-1710 for more details.
    // 不过实测在更古老py37(14.00)上是没问题的，但在py311(14.38)或pyqt(14.26)上确实会崩溃，保险起见不要加载。
    if (!exe)
        return {};
    auto vermy = __QueryVersion(exe.value());
    if (!vermy)
        return {};
    if (vermy >= std::make_tuple(1u, 21u, 0u, 0u))
    {
        static bool _isvcrtlessthan1440 = isvcrtlessthan1440();
        if (_isvcrtlessthan1440)
            return {};
    }
    return vermy;
}
static bool __OcrLoadRuntime()
{
    if (GetModuleHandleW(L"onnxruntime.dll"))
        return true;
    WCHAR path[MAX_PATH];
    HMODULE hmodule;
    GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCWSTR)&__OcrLoadRuntime, &hmodule);
    GetModuleFileNameW(hmodule, path, MAX_PATH);
    auto currdir = std::filesystem::path(path).parent_path();
    auto myonnx = (currdir / "onnxruntime.dll").wstring();
    auto vermy = checkfileversion(myonnx);

    // 尝试加载系统onnxruntime，版本可能更高，并可以支持DML
    auto sysonnx = SearchDllPath(L"onnxruntime.dll");
    auto ver = checkfileversion(sysonnx);
    if (ver > vermy)
    {
        myonnx = sysonnx.value();
        vermy = ver;
    }

    if (!vermy)
        return false;
    std::wcout << myonnx << L"\n";
    if (!LoadLibrary(myonnx.c_str()))
        return false;
    _InitApi();
    for (auto &&p : OrtGetAvailableProviders())
    {
        std::cout << p << std::endl;
    }
    return true;
}

DECLARE_API bool OcrLoadRuntime()
{
    static bool __ = __OcrLoadRuntime();
    return __;
}

DECLARE_API bool OcrIsProviderAvailable(const wchar_t *provider)
{
    if (!OcrLoadRuntime())
        return false;
    if (wcscmp(provider, L"DML") == 0)
        return isDMLAvailable();
    if (wcscmp(provider, L"OpenVINO") == 0)
        return isOpenVINOAvailable();
    return false;
}

std::vector<std::string> ListpenVINODeviceTypes()
{
    auto hopenvino = GetModuleHandle(L"openvino.dll");
    if (!hopenvino)
        return {};
    auto ctor = GetProcAddress(hopenvino, "??0Core@ov@@QEAA@AEBV?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@Z");
    auto dtor = GetProcAddress(hopenvino, "??1Core@ov@@QEAA@XZ");
    auto get_available_devices = GetProcAddress(hopenvino, "?get_available_devices@Core@ov@@QEBA?AV?$vector@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@V?$allocator@V?$basic_string@DU?$char_traits@D@std@@V?$allocator@D@2@@std@@@2@@std@@XZ");
    if (!dtor || !dtor || !get_available_devices)
        return {};
    // ov::Core core;
    // std::vector<std::string> devices = core.get_available_devices();
    // core.get_property(device, ov::device::capabilities);
    alignas(16) char core[16];
    ((void (*)(void *, const std::string &))ctor)(core, "");
    std::vector<std::string> devices;
    ((void (*)(const void *, std::vector<std::string> *))(get_available_devices))(core, &devices);
    ((void (*)(void *))dtor)(core);
    return devices;
}

DECLARE_API void GetOpenVINODeviceTypes(void (*cb)(LPCSTR))
{
    for (auto &d : ListpenVINODeviceTypes())
    {
        cb(d.c_str());
    }
}

#ifndef _GAMING_XBOX
#define IID_GRAPHICS_PPV_ARGS IID_PPV_ARGS
#endif

DECLARE_API void GetDeviceInfoD3D12(void (*cb)(uint64_t, LPCWSTR))
{
    // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/platform/windows/device_discovery.cc#L308
    // std::unordered_map<uint64_t, DeviceInfo> GetDeviceInfoD3D12()
    // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/providers/dml/dml_provider_factory.cc#L468
    // Microsoft::WRL::ComPtr<ID3D12Device> DMLProviderFactoryCreator::CreateD3D12Device(int device_id, bool skip_software_device_check)

    auto checker = [](IDXGIAdapter1 *adapter, const DXGI_ADAPTER_DESC1 &desc)
    {
        // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/providers/dml/dml_provider_factory.cc#L491
        // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/platform/windows/device_discovery.cc#L324
        if ((desc.Flags & DXGI_ADAPTER_FLAG_SOFTWARE) != 0 ||
            (desc.Flags & DXGI_ADAPTER_FLAG_REMOTE) != 0)
        {
            // software or remote. skip
            return false;
        }

        // https://github.com/microsoft/onnxruntime/blob/main/onnxruntime/core/providers/dml/dml_provider_factory.cc#L494C4-L495C145
        CComPtr<ID3D12Device> d3d12_device;
        if (FAILED(D3D12CreateDevice(adapter, D3D_FEATURE_LEVEL_11_0, IID_GRAPHICS_PPV_ARGS(&d3d12_device))))
            return false;

        return true;
    };
    auto gpus = get_descs(checker);
    if (gpus.size())
    {
        auto bestdesc = get_best_gpu().value_or(gpus[0].second);
        cb(0, bestdesc.Description);
        for (auto &&[_, desc] : gpus)
        {
            cb(GetLuidKey(desc.AdapterLuid), desc.Description);
        }
    }
}


DECLARE_API OcrLite *OcrInit(const wchar_t *szDetModel, const wchar_t *szRecModel, const wchar_t *szKeyPath, int nThreads, bool gpu, uint64_t luid, const char *device_type, void (*cb2)(const char *))
{
    OcrLite *pOcrObj = nullptr;
    DeviceInfo info;
    if (gpu && isDMLAvailable())
    {
        int device = findDeviceId(luid);
        std::wstringstream wss;
        wss << device << L"\t" << std::hex << luid;
        std::wcout << wss.str() << std::endl;
        info.info = DeviceInfo::dml{device};
    }
    else if (isOpenVINOAvailable())
    {
        std::string __;
        for (auto &&_ : ListpenVINODeviceTypes())
        {
            __ = std::move(_);
            if (__ == device_type)
                break;
        }
        info.info = DeviceInfo::openvino{std::move(__)};
    }

    try
    {
        pOcrObj = new OcrLite(szDetModel, szRecModel, szKeyPath, nThreads, info);
    }
    catch (std::exception &e)
    {
        cb2(e.what());
    }
    if (pOcrObj)
    {
        return pOcrObj;
    }
    else
    {
        return nullptr;
    }
}