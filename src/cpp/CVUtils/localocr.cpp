
#include "dbcrnn.hpp"

DECLARE_API OcrLite *OcrInit(const wchar_t *szDetModel, const wchar_t *szRecModel, const wchar_t *szKeyPath, int nThreads, bool gpu, int device, void (*cb2)(const char *))
{
    OcrLite *pOcrObj = nullptr;
    try
    {
        pOcrObj = new OcrLite(szDetModel, szRecModel, szKeyPath, nThreads, gpu, device);
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

static std::optional<std::wstring> SearchDllPath(const std::wstring &dll)
{
    auto len = SearchPathW(NULL, dll.c_str(), NULL, 0, NULL, NULL);
    if (!len)
        return {};
    std::wstring buff;
    buff.resize(len);
    len = SearchPathW(NULL, dll.c_str(), NULL, len, buff.data(), NULL);
    if (!len)
        return {};
    return std::move(buff);
}
extern "C" bool QueryVersion(const wchar_t *exe, WORD *_1, WORD *_2, WORD *_3, WORD *_4);
using version_t = std::tuple<DWORD, DWORD, DWORD, DWORD>;
static std::optional<version_t> QueryVersion(const std::optional<std::wstring> &exe)
{
    if (!exe)
        return {};
    WORD _1, _2, _3, _4;
    if (!QueryVersion(exe.value().c_str(), &_1, &_2, &_3, &_4))
        return {};
    std::cout << _1 << "," << _2 << "," << _3 << "," << _4 << "\t" << WideStringToString(exe.value()) << "\n";
    return std::make_tuple(_1, _2, _3, _4);
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
        return QueryVersion(path) < std::make_tuple(14u, 40u, 0u, 0u);
    };
    return checkversion(L"msvcp140.dll") || checkversion(L"vcruntime140.dll");
}
static std::optional<version_t> checkfileversion(const std::optional<std::wstring> &exe)
{
    // 如果vcrt版本<14.40，那么最多只能加载onnxruntime到v1.20.1版本，v1.21.0开始会不兼容。
    //  https://github.com/microsoft/onnxruntime/releases/tag/v1.21.0
    //  All the prebuilt Windows packages now require VC++ Runtime version >= 14.40(instead of 14.38). If your VC++ runtime version is lower than that, you may see a crash when ONNX Runtime was initializing. See https://github.com/microsoft/STL/wiki/Changelog#vs-2022-1710 for more details.
    //  不过实测在更古老py37(14.00)上是没问题的，但在py311(14.38)或pyqt(14.26)上确实会崩溃，保险起见不要加载。
    auto vermy = QueryVersion(exe);
    if (!vermy)
        return {};
    static bool _isvcrtlessthan1440 = isvcrtlessthan1440();
    if (_isvcrtlessthan1440)
    {
        vermy = (vermy < std::make_tuple(1u, 21u, 0u, 0u)) ? vermy : std::nullopt;
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
#ifndef WIN10ABOVE
    // 尝试加载系统onnxruntime，版本更高，并可以支持DML
    auto sysonnx = SearchDllPath(L"onnxruntime.dll");
    auto ver = checkfileversion(sysonnx);
    if (ver > vermy)
    {
        myonnx = sysonnx.value();
        vermy = ver;
    }
#endif
    if (!vermy)
        return false;
    std::cout << WideStringToString(myonnx) << "\n";
    if (!LoadLibrary(myonnx.c_str()))
        return false;
    _InitApi();
    return true;
}

DECLARE_API bool OcrLoadRuntime()
{
    static bool __ = __OcrLoadRuntime();
    return __;
}

DECLARE_API bool OcrIsDMLAvailable()
{
    if (!OcrLoadRuntime())
        return false;

    for (auto &&p : OrtGetAvailableProviders())
    {
        std::cout << p << "\n";
    }
    return isDMLAvailable();
}
